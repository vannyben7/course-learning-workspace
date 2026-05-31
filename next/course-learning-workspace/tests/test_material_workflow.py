from __future__ import annotations

import os
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from http import HTTPStatus
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.assistant import AssistantProviderError, build_study_prompt, call_chat_completions, normalize_provider_result, parse_duckduckgo_lite_results, parse_provider_json_content, provider_config  # noqa: E402
from app.materials import parse_pdf, rank_materials, scan_folder, tokenize  # noqa: E402
from app.server import WorkspaceHandler, parse_poppler_bbox  # noqa: E402
from app.store import WorkspaceStore  # noqa: E402


class MaterialWorkflowTests(unittest.TestCase):
    def test_scan_folder_extracts_supported_files_and_ignores_generated_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            course_dir = Path(tmp) / "course"
            course_dir.mkdir()
            (course_dir / "lecture-01.md").write_text(
                "# Sustainable operations\n\n供应链 resilience and carbon reporting are connected.",
                encoding="utf-8",
            )
            self.write_docx(course_dir / "reading.docx", "This reading explains stakeholder pressure and operations strategy.")
            self.write_pptx(course_dir / "week-02.pptx", ["Risk pooling", "Supplier visibility"])
            self.write_xlsx(course_dir / "seminar.xlsx", [["Topic", "Concept"], ["Carbon", "Scope 3"]])
            generated_dir = course_dir / "notes" / "open-academic-os"
            generated_dir.mkdir(parents=True)
            (generated_dir / "generated.md").write_text("Do not ingest generated notes.", encoding="utf-8")
            cache_dir = course_dir / ".academic-os"
            cache_dir.mkdir()
            (cache_dir / "cache.txt").write_text("Do not ingest cache.", encoding="utf-8")

            course, materials, texts = scan_folder(course_dir)

            self.assertEqual(course["materials_seen"], 4)
            self.assertEqual(course["materials_parsed"], 4)
            self.assertTrue(all("open-academic-os" not in item["relative_path"] for item in materials))
            self.assertTrue(all(".academic-os" not in item["relative_path"] for item in materials))
            self.assertEqual(len(texts), 4)
            self.assertTrue(any("供应链" in text for text in texts.values()))
            self.assertTrue(any("Scope 3" in text for text in texts.values()))

    def test_store_notes_and_rank_materials_support_bilingual_course_questions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            course_dir = Path(tmp) / "course"
            course_dir.mkdir()
            (course_dir / "lecture.md").write_text(
                "可持续供应链管理 requires supplier visibility, 排放数据, and operational trade-off analysis.",
                encoding="utf-8",
            )
            course, materials, texts = scan_folder(course_dir)
            store = WorkspaceStore(Path(tmp) / "data")
            state = store.replace_scan(course, materials, texts)

            note = store.add_note(materials[0]["id"], "我需要先理解供应链可见性，再看排放数据。", language="zh")
            matches = rank_materials("供应链和排放数据有什么关系？", state["materials"], store.material_texts())

            self.assertEqual(note["language"], "zh")
            self.assertEqual(store.load()["notes"][0]["body"], note["body"])
            self.assertTrue(matches)
            self.assertIn("排放", matches[0]["quote"])

    def test_ask_materials_refuses_essay_writing_requests(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = WorkspaceStore(Path(tmp) / "data")
            handler = object.__new__(WorkspaceHandler)
            handler.store = store

            result = handler._ask_materials({"question": "请帮我写一篇 essay", "scope": "course", "language": "zh"})

            self.assertEqual(result["status"], "refused")
            self.assertEqual(result["citations"], [])
            self.assertIn("不能代写", result["answer"])

    def test_ask_materials_uses_selection_notes_annotations_and_sources(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            course_dir = Path(tmp) / "course"
            course_dir.mkdir()
            (course_dir / "lecture.txt").write_text(
                "Development as freedom links agency, public reasoning, and substantive capabilities.",
                encoding="utf-8",
            )
            course, materials, texts = scan_folder(course_dir)
            store = WorkspaceStore(Path(tmp) / "data")
            store.replace_scan(course, materials, texts)
            store.add_note(materials[0]["id"], "我的笔记：agency 是理解 freedom 的关键。", language="zh")
            store.add_annotation(
                {
                    "material_id": materials[0]["id"],
                    "target_type": "text",
                    "style": "comment",
                    "selected_text": "agency, public reasoning",
                    "body": "和 freedom 的关系需要复习。",
                    "language": "zh",
                }
            )
            handler = object.__new__(WorkspaceHandler)
            handler.store = store

            result = handler._ask_materials(
                {
                    "question": "agency 和 freedom 有什么关系？",
                    "action": "ask",
                    "scope": "material",
                    "material_id": materials[0]["id"],
                    "selected_text": "Development as freedom",
                    "note_body": "草稿：capabilities 也很重要。",
                    "annotation_body": "这里和 public reasoning 有关。",
                    "language": "zh",
                }
            )

            source_types = {citation["source_type"] for citation in result["citations"]}
            self.assertEqual(result["status"], "ok")
            self.assertIn("selection", source_types)
            self.assertIn("reading_note", source_types)
            self.assertTrue(any(citation["source_type"] == "material" for citation in result["citations"]))

    def test_explicit_neoliberalism_question_is_not_overridden_by_stale_selection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            course_dir = Path(tmp) / "course"
            course_dir.mkdir()
            (course_dir / "week-06.txt").write_text(
                "Week 6 Lecture\nDevelopment theory: what is it?\nModernisation theory and dependency theory explain development.",
                encoding="utf-8",
            )
            (course_dir / "week-10.txt").write_text(
                "\f".join(
                    [
                        "Week 10 Lecture\nNeoliberalism and Post-Development theory",
                        "Overview: neoliberalism and post-development appear after earlier development theory.",
                        (
                            "Neoliberalism: economic and ideological\n"
                            "The different levels of neoliberalism?\n"
                            "Structural: “hollowing out the state”. The state organizes the economy around GDP growth and protects the sovereignty of the market.\n"
                            "Individual agency and responsibility: “pull yourself up by your bootstraps”. People are expected to prioritize and improve their livelihoods through market freedom."
                        ),
                    ]
                ),
                encoding="utf-8",
            )
            course, materials, texts = scan_folder(course_dir)
            store = WorkspaceStore(Path(tmp) / "data")
            store.replace_scan(course, materials, texts)
            week10 = next(material for material in materials if "10" in material["title"])
            handler = object.__new__(WorkspaceHandler)
            handler.store = store

            result = handler._ask_materials(
                {
                    "question": "what is The different levels of neoliberalism",
                    "action": "ask",
                    "scope": "course",
                    "material_id": week10["id"],
                    "selected_text": "Development theory: what is it?",
                    "language": "zh",
                    "api_provider": "local",
                    "include_notes": False,
                }
            )

            self.assertEqual(result["status"], "ok")
            self.assertIn("结构层面", result["answer"])
            self.assertIn("个体层面", result["answer"])
            self.assertIn("hollowing out the state", result["answer"])
            self.assertNotIn("development theory 就是一套", result["answer"])
            self.assertTrue(any(citation.get("material_id") == week10["id"] for citation in result["citations"]))
            self.assertTrue(any("pull yourself up" in citation.get("quote", "") for citation in result["citations"]))

    def test_ask_materials_reports_unsupported_when_sources_do_not_match(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            course_dir = Path(tmp) / "course"
            course_dir.mkdir()
            (course_dir / "lecture.txt").write_text("Supplier visibility supports carbon reporting.", encoding="utf-8")
            course, materials, texts = scan_folder(course_dir)
            store = WorkspaceStore(Path(tmp) / "data")
            store.replace_scan(course, materials, texts)
            store.add_note(materials[0]["id"], '{"status":"ok","answer":"old raw JSON note should not drive this answer"}', language="zh")
            handler = object.__new__(WorkspaceHandler)
            handler.store = store

            result = handler._ask_materials(
                {
                    "question": "量子力学中的波函数坍缩是什么？",
                    "action": "ask",
                    "scope": "material",
                    "material_id": materials[0]["id"],
                    "language": "zh",
                }
            )

            self.assertEqual(result["status"], "not_found")
            self.assertEqual(result["citations"], [])
            self.assertIn("当前课程资料无法支持这个回答", result["answer"])

    def test_course_ask_prefilters_large_irrelevant_materials(self) -> None:
        selected = WorkspaceHandler._candidate_material_ids_for_assistant(
            [
                {"id": "large", "title": "General development reader", "relative_path": "large.pdf"},
                {"id": "relevant", "title": "Human development and capability approach", "relative_path": "capability.pdf"},
            ],
            {
                "large": "unrelated background " * 20000,
                "relevant": "The capability approach is connected to substantive freedoms and human development.",
            },
            "capability approach 是什么？",
            active_material_id=None,
            limit=1,
        )

        self.assertEqual(selected, {"relevant"})

    def test_large_material_ask_uses_query_focused_chunks(self) -> None:
        text = "\f".join(
            ["General background without the target concept."] * 90
            + ["The capability approach connects substantive freedoms with human development and agency."]
            + ["More unrelated background."] * 30
        )

        chunks = WorkspaceHandler._query_focused_material_chunks(text, "capability approach 是什么？")

        self.assertTrue(chunks)
        self.assertTrue(any("capability approach" in chunk["quote"].lower() for chunk in chunks))
        self.assertLessEqual(len(chunks), 3)

    def test_ask_materials_ignores_low_information_annotations(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            course_dir = Path(tmp) / "course"
            course_dir.mkdir()
            (course_dir / "sen.txt").write_text(
                "Economic development is described as an increase in freedom and liberty.",
                encoding="utf-8",
            )
            course, materials, texts = scan_folder(course_dir)
            store = WorkspaceStore(Path(tmp) / "data")
            store.replace_scan(course, materials, texts)
            store.add_annotation(
                {
                    "material_id": materials[0]["id"],
                    "target_type": "region",
                    "style": "comment",
                    "page": 1,
                    "rects": [{"x": 0.1, "y": 0.1, "w": 0.2, "h": 0.1}],
                    "body": "1",
                }
            )
            handler = object.__new__(WorkspaceHandler)
            handler.store = store

            result = handler._ask_materials(
                {
                    "question": "development 和 freedom 有什么关系？",
                    "action": "ask",
                    "scope": "material",
                    "material_id": materials[0]["id"],
                    "language": "zh",
                }
            )

            self.assertEqual(result["status"], "ok")
            self.assertFalse(any(citation["quote"] == "1" for citation in result["citations"]))

    def test_ask_materials_review_action_keeps_page_locator_when_available(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            course_dir = Path(tmp) / "course"
            course_dir.mkdir()
            (course_dir / "reading.txt").write_text(
                "First page introduces development.\fSecond page explains liberty and capabilities.",
                encoding="utf-8",
            )
            course, materials, texts = scan_folder(course_dir)
            store = WorkspaceStore(Path(tmp) / "data")
            store.replace_scan(course, materials, texts)
            store.add_note(materials[0]["id"], '{"status":"ok","answer":"old note should not become the case frame"}', language="zh")
            handler = object.__new__(WorkspaceHandler)
            handler.store = store

            result = handler._ask_materials(
                {
                    "question": "读完这个资料后，我应该尝试回答哪一个复习问题？",
                    "action": "review",
                    "scope": "material",
                    "material_id": materials[0]["id"],
                    "language": "zh",
                }
            )

            self.assertEqual(result["status"], "ok")
            self.assertIn("建议用这些问题自测", result["answer"])
            self.assertTrue(any(citation.get("locator") == "page 2" for citation in result["citations"]))

    def test_ask_materials_local_explain_returns_preclass_outline(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            course_dir = Path(tmp) / "course"
            course_dir.mkdir()
            (course_dir / "reading.txt").write_text(
                "The lecture introduces stakeholder pressure.\n\nIt then connects supplier visibility to carbon reporting.",
                encoding="utf-8",
            )
            course, materials, texts = scan_folder(course_dir)
            store = WorkspaceStore(Path(tmp) / "data")
            store.replace_scan(course, materials, texts)
            handler = object.__new__(WorkspaceHandler)
            handler.store = store

            result = handler._ask_materials(
                {
                    "question": "阅读这个资料时我应该注意什么？",
                    "action": "explain",
                    "scope": "material",
                    "material_id": materials[0]["id"],
                    "language": "zh",
                }
            )

            self.assertEqual(result["status"], "ok")
            self.assertIn("资料小结", result["answer"])
            self.assertIn("第一遍怎么读", result["answer"])
            self.assertIn("[C1]", result["answer"])

    def test_ask_materials_explain_prefers_material_reading_map_over_annotations(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            course_dir = Path(tmp) / "course"
            course_dir.mkdir()
            (course_dir / "Postcolonialism, Decoloniality and Development 26 05 01 14 33 34.txt").write_text(
                "\f".join(
                    [
                        "Postcolonialism, Decoloniality and Development is a course reading about recent debates in development.",
                        "Introduction: the book explains postcolonial approaches, reviews critiques, and sets agendas for students.",
                        "Chapter 1: development theory is introduced through colonial histories, power, knowledge, and institutions.",
                        "Chapter 2: decoloniality asks students to question whose knowledge counts in development practice.",
                    ]
                ),
                encoding="utf-8",
            )
            course, materials, texts = scan_folder(course_dir)
            store = WorkspaceStore(Path(tmp) / "data")
            store.replace_scan(course, materials, texts)
            store.add_annotation(
                {
                    "material_id": materials[0]["id"],
                    "selected_text": "Metaphysical, ethical and political theory",
                    "body": "This old annotation is not a document preview.",
                    "page": 56,
                    "language": "zh",
                }
            )
            handler = object.__new__(WorkspaceHandler)
            handler.store = store

            result = handler._ask_materials(
                {
                    "question": "请解释当前资料",
                    "action": "explain",
                    "scope": "material",
                    "material_id": materials[0]["id"],
                    "language": "zh",
                }
            )

            self.assertEqual(result["status"], "ok")
            self.assertIn("资料小结", result["answer"])
            self.assertIn("第一遍怎么读", result["answer"])
            self.assertIn("Postcolonialism", result["answer"])
            self.assertIn("Postcolonialism 和 Decoloniality", result["answer"])
            self.assertTrue(result["citations"])
            self.assertTrue(all(citation.get("source_type") == "material" for citation in result["citations"]))
            self.assertNotIn("Metaphysical", result["answer"])
            self.assertNotIn("这本资料如何界定 Development Studies", result["answer"])

    def test_explain_companion_book_returns_source_summary_not_title_word_relation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            course_dir = Path(tmp) / "course"
            course_dir.mkdir()
            (course_dir / "The Companion to Development Studies, Third Edition (Vandana Desai, Rob Potter).txt").write_text(
                "\f".join(
                    [
                        "The Companion to Development Studies Third Edition Vandana Desai Rob Potter",
                        "Contents: theories and strategies of development; globalization and development; rural livelihoods; governance; gender and development; environment and development.",
                        "Introduction: Development Studies is an interdisciplinary field concerned with poverty, inequality, social change, policy, and practice.",
                    ]
                ),
                encoding="utf-8",
            )
            course, materials, texts = scan_folder(course_dir)
            store = WorkspaceStore(Path(tmp) / "data")
            store.replace_scan(course, materials, texts)
            handler = object.__new__(WorkspaceHandler)
            handler.store = store

            result = handler._ask_materials(
                {
                    "question": "请解释当前资料",
                    "action": "explain",
                    "scope": "material",
                    "material_id": materials[0]["id"],
                    "language": "zh",
                }
            )

        self.assertEqual(result["status"], "ok")
        self.assertIn("资料小结", result["answer"])
        self.assertIn("Development Studies 这个研究领域", result["answer"])
        self.assertIn("Vandana Desai", result["answer"])
        self.assertNotIn("development”和“studies", result["answer"].lower())
        self.assertNotIn("是什么关系", result["answer"])

    def test_explain_week6_uses_slide_topic_over_filename(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            course_dir = Path(tmp) / "course"
            course_dir.mkdir()
            (course_dir / "DEV100 Week 6 Lecture - Development, Modernisation and Dependency.txt").write_text(
                "\f".join(
                    [
                        "Week 6 Lecture Development theory: Modernisation, Dependency and the Development Impasse DEV100 Global Development Studies",
                        "Development theory: a timeline. Modernisation theory: development through economic growth and social reform. Dependency theory: modernisation is unequal development and underdevelopment.",
                        "Development Impasse: these theories struggle to explain diverse development experiences.",
                    ]
                ),
                encoding="utf-8",
            )
            course, materials, texts = scan_folder(course_dir)
            store = WorkspaceStore(Path(tmp) / "data")
            store.replace_scan(course, materials, texts)
            handler = object.__new__(WorkspaceHandler)
            handler.store = store

            result = handler._ask_materials(
                {
                    "question": "请解释当前资料",
                    "action": "explain",
                    "scope": "material",
                    "material_id": materials[0]["id"],
                    "language": "zh",
                }
            )

        self.assertEqual(result["status"], "ok")
        self.assertIn("Development theory: Modernisation, Dependency and the Development Impasse", result["answer"])
        self.assertIn("Modernisation 与 Dependency", result["answer"])
        self.assertNotIn("DEV100", result["answer"])

    def test_week6_connect_explains_file_role_in_whole_course(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            course_dir = Path(tmp) / "course"
            course_dir.mkdir()
            (course_dir / "Week 4 Colonialism.txt").write_text(
                "Week 4 lecture explains colonialism, postcolonialism, and historical background for development debates.",
                encoding="utf-8",
            )
            (course_dir / "DEV100 Week 6 Lecture - Development, Modernisation and Dependency.txt").write_text(
                "\f".join(
                    [
                        "Week 6 Lecture Development theory: Modernisation, Dependency and the Development Impasse DEV100 Global Development Studies",
                        "Development theory: a timeline. Modernisation theory: development through economic growth and social reform. Dependency theory: modernisation is unequal development and underdevelopment.",
                        "Development Impasse: these theories struggle to explain diverse development experiences.",
                    ]
                ),
                encoding="utf-8",
            )
            (course_dir / "Week 8 Alternative Development.txt").write_text(
                "Week 8 introduces alternative development and human development after the limits of earlier theories.",
                encoding="utf-8",
            )
            course, materials, texts = scan_folder(course_dir)
            store = WorkspaceStore(Path(tmp) / "data")
            store.replace_scan(course, materials, texts)
            week6 = next(item for item in materials if "Week 6" in item["title"])
            handler = object.__new__(WorkspaceHandler)
            handler.store = store

            result = handler._ask_materials(
                {
                    "question": "当前显示的这个文件在课程所有文件中扮演什么角色？",
                    "action": "connect",
                    "scope": "course",
                    "material_id": week6["id"],
                    "language": "zh",
                    "include_notes": False,
                }
            )

        self.assertEqual(result["status"], "ok")
        self.assertIn("从历史转向理论", result["answer"])
        self.assertIn("核心理论奠基", result["answer"])
        self.assertIn("alternative development", result["answer"])
        citation_material_ids = {citation["material_id"] for citation in result["citations"]}
        self.assertIn(week6["id"], citation_material_ids)
        self.assertGreaterEqual(len(citation_material_ids), 2)

    def test_non_week6_connect_is_not_contaminated_by_week6_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            course_dir = Path(tmp) / "course"
            course_dir.mkdir()
            (course_dir / "DEV100 Week 6 Lecture - Development, Modernisation and Dependency.txt").write_text(
                "\f".join(
                    [
                        "Week 6 Lecture Development theory: Modernisation, Dependency and the Development Impasse",
                        "Modernisation theory and Dependency theory explain development and underdevelopment.",
                    ]
                ),
                encoding="utf-8",
            )
            (course_dir / "DEV100 Week 8 Lecture - Alternative Development and Human Development.txt").write_text(
                "\f".join(
                    [
                        "Week 8 Lecture Alternative Development or Alternatives to Development? Human Development theory - the capabilities approach",
                        "Alternative development and human development respond to the limits of earlier development theories.",
                    ]
                ),
                encoding="utf-8",
            )
            course, materials, texts = scan_folder(course_dir)
            store = WorkspaceStore(Path(tmp) / "data")
            store.replace_scan(course, materials, texts)
            week8 = next(item for item in materials if "Week 8" in item["title"])
            handler = object.__new__(WorkspaceHandler)
            handler.store = store

            result = handler._ask_materials(
                {
                    "question": "当前显示的这个文件在课程所有文件中扮演什么角色？",
                    "action": "connect",
                    "scope": "course",
                    "material_id": week8["id"],
                    "language": "zh",
                    "include_notes": False,
                }
            )

        self.assertEqual(result["status"], "ok")
        self.assertIn("Alternative", result["answer"])
        self.assertNotIn("从历史转向理论", result["answer"])
        self.assertNotIn("核心理论奠基", result["answer"])

    def test_summary_and_connect_require_current_material(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = WorkspaceStore(Path(tmp) / "data")
            handler = object.__new__(WorkspaceHandler)
            handler.store = store

            result = handler._ask_materials(
                {
                    "question": "请概括当前文件",
                    "action": "explain",
                    "scope": "material",
                    "language": "zh",
                }
            )

        self.assertEqual(result["status"], "not_found")
        self.assertIn("请先在阅读器中打开一份课程文件", result["answer"])

    def test_course_material_mode_can_exclude_notes_and_annotations(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            course_dir = Path(tmp) / "course"
            course_dir.mkdir()
            (course_dir / "lecture.txt").write_text("Modernisation theory appears in the lecture.", encoding="utf-8")
            course, materials, texts = scan_folder(course_dir)
            store = WorkspaceStore(Path(tmp) / "data")
            store.replace_scan(course, materials, texts)
            store.add_note(materials[0]["id"], "Dependency trap only appears in this private note.", language="zh")
            handler = object.__new__(WorkspaceHandler)
            handler.store = store

            result = handler._ask_materials(
                {
                    "question": "Dependency trap 在课程资料里怎么讲？",
                    "action": "ask",
                    "scope": "course",
                    "material_id": materials[0]["id"],
                    "language": "zh",
                    "include_notes": False,
                }
            )

        self.assertEqual(result["status"], "not_found")
        self.assertEqual(result["citations"], [])

    def test_explain_long_book_filters_back_matter_notes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            course_dir = Path(tmp) / "course"
            course_dir.mkdir()
            pages = [
                "DEVELOPMENT AS FREEDOM\n\nAMARTYA SEN",
                "CONTENTS\nIntroduction: Development as Freedom\n1 The Perspective of Freedom\n2 The Ends and Means of Development\n3 Freedom and the Foundations of Justice",
                "Introduction: Development requires the removal of major sources of unfreedom and asks students to evaluate development through substantive freedoms.",
            ]
            pages.extend(["Chapter passage: development, freedom, public reasoning and social opportunity are discussed here."] * 90)
            pages.append(
                "27. Dreze and Sen, India: Economic Development and Social Opportunity (1995); Amartya Sen, \"Hunger in the Modern World,\" Dr. Rajendra Prasad Memorial Lecture, New Delhi, June 1997; National Sample Survey 1991; chapter 3 statistical appendix."
            )
            (course_dir / "Development as Freedom (Amartya Sen).txt").write_text("\f".join(pages), encoding="utf-8")
            course, materials, texts = scan_folder(course_dir)
            store = WorkspaceStore(Path(tmp) / "data")
            store.replace_scan(course, materials, texts)
            handler = object.__new__(WorkspaceHandler)
            handler.store = store

            result = handler._ask_materials(
                {
                    "question": "请解释当前资料",
                    "action": "explain",
                    "scope": "material",
                    "material_id": materials[0]["id"],
                    "language": "zh",
                }
            )

        self.assertEqual(result["status"], "ok")
        self.assertIn("一本书或章节式阅读资料", result["answer"])
        self.assertIn("substantive freedoms", result["answer"])
        self.assertTrue(any("CONTENTS" in citation.get("quote", "") or "Introduction" in citation.get("quote", "") for citation in result["citations"]))
        self.assertFalse(any("Rajendra Prasad" in citation.get("quote", "") for citation in result["citations"]))

    def test_deepseek_without_key_requests_configuration_without_calling_provider(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            course_dir = Path(tmp) / "course"
            course_dir.mkdir()
            (course_dir / "lecture.txt").write_text("Agency and capabilities are introduced as course concepts.", encoding="utf-8")
            course, materials, texts = scan_folder(course_dir)
            store = WorkspaceStore(Path(tmp) / "data")
            store.replace_scan(course, materials, texts)
            handler = object.__new__(WorkspaceHandler)
            handler.store = store

            with mock.patch.dict(os.environ, {}, clear=True), mock.patch("app.server.call_chat_completions") as provider_call:
                result = handler._ask_materials(
                    {
                        "question": "请解释当前资料",
                        "action": "explain",
                        "scope": "material",
                        "material_id": materials[0]["id"],
                        "language": "zh",
                        "api_provider": "deepseek",
                    }
                )

            provider_call.assert_not_called()
            self.assertEqual(result["status"], "config_required")
            self.assertEqual(result["provider"], "deepseek")
            self.assertIn("配置 DeepSeek API key", result["answer"])
            self.assertTrue(result["citations"])

    def test_deepseek_provider_uses_study_prompt_and_filters_citations(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            course_dir = Path(tmp) / "course"
            course_dir.mkdir()
            (course_dir / "lecture.txt").write_text(
                "First, the course introduces agency as a learning theme.\n\nSecond, it links agency to public reasoning.",
                encoding="utf-8",
            )
            course, materials, texts = scan_folder(course_dir)
            store = WorkspaceStore(Path(tmp) / "data")
            store.replace_scan(course, materials, texts)
            handler = object.__new__(WorkspaceHandler)
            handler.store = store

            with mock.patch(
                "app.server.call_chat_completions",
                return_value={"status": "ok", "answer": "课前先看 agency 的展开 [C1]", "used_source_ids": ["C1"]},
            ) as provider_call:
                result = handler._ask_materials(
                    {
                        "question": "请解释当前资料",
                        "action": "explain",
                        "scope": "material",
                        "material_id": materials[0]["id"],
                        "language": "zh",
                        "api_provider": "deepseek",
                        "api_key": "test-key",
                        "api_model": "deepseek-v4-flash",
                    }
                )

            provider_call.assert_called_once()
            config, messages = provider_call.call_args.args
            prompt_text = "\n".join(message["content"] for message in messages)
            self.assertEqual(config["model"], "deepseek-v4-flash")
            self.assertIn("pre-class preview", prompt_text)
            self.assertIn("Do not write", prompt_text)
            self.assertEqual(result["status"], "ok")
            self.assertEqual(result["provider"], "deepseek")
            self.assertEqual([citation["source_id"] for citation in result["citations"]], ["C1"])

    def test_assistant_provider_config_can_default_to_environment(self) -> None:
        with mock.patch.dict(
            os.environ,
            {
                "CLW_ASSISTANT_PROVIDER": "deepseek",
                "CLW_DEEPSEEK_API_KEY": "env-key",
                "CLW_DEEPSEEK_MODEL": "deepseek-v4-pro",
                "CLW_DEEPSEEK_BASE_URL": "https://api.deepseek.com",
            },
            clear=True,
        ):
            config = provider_config({})

        self.assertEqual(config["provider"], "deepseek")
        self.assertEqual(config["api_key"], "env-key")
        self.assertEqual(config["model"], "deepseek-v4-pro")

    def test_provider_config_supports_openai_compatible_presets_and_rejects_unknown(self) -> None:
        openai = provider_config({"api_provider": "openai", "api_key": "key"})
        custom = provider_config({"api_provider": "custom", "api_key": "key", "api_base_url": "https://example.test/v1", "api_model": "model-x"})

        self.assertEqual(openai["base_url"], "https://api.openai.com/v1")
        self.assertEqual(openai["model"], "gpt-5.2")
        self.assertEqual(custom["base_url"], "https://example.test/v1")
        self.assertEqual(custom["model"], "model-x")
        with self.assertRaisesRegex(AssistantProviderError, "Unsupported AI provider"):
            provider_config({"api_provider": "unknown"})

    def test_provider_json_parser_accepts_fenced_and_prefaced_json(self) -> None:
        direct = '{"status":"ok","answer":"yes","used_source_ids":["C1"]}'
        fenced = '```json\n{"status":"ok","answer":"yes","used_source_ids":["C1"]}\n```'
        prefaced = 'Here is the JSON:\n{"status":"ok","answer":"yes","used_source_ids":["C1"]}\nThanks.'

        self.assertEqual(parse_provider_json_content(direct)["status"], "ok")
        self.assertEqual(parse_provider_json_content(fenced)["used_source_ids"], ["C1"])
        self.assertEqual(parse_provider_json_content(prefaced)["answer"], "yes")

    def test_chat_completion_accepts_natural_language_provider_answer(self) -> None:
        class Response:
            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            @staticmethod
            def read() -> bytes:
                payload = {"choices": [{"message": {"content": "可以这样理解这句话。[C1]"}}]}
                return json.dumps(payload).encode("utf-8")

        config = {"provider": "deepseek", "api_key": "key", "base_url": "https://api.deepseek.com", "model": "deepseek-v4-flash"}

        with mock.patch("app.assistant.urllib.request.urlopen", return_value=Response()):
            result = call_chat_completions(config, [{"role": "user", "content": "test"}])

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["answer"], "可以这样理解这句话。[C1]")
        self.assertEqual(result["used_source_ids"], ["C1"])

    def test_chat_completion_rejects_cut_off_provider_answer(self) -> None:
        class Response:
            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            @staticmethod
            def read() -> bytes:
                payload = {"choices": [{"finish_reason": "length", "message": {"content": '{"status":"ok","answer":"半截'}}]}
                return json.dumps(payload).encode("utf-8")

        config = {"provider": "deepseek", "api_key": "key", "base_url": "https://api.deepseek.com", "model": "deepseek-v4-flash"}

        with mock.patch("app.assistant.urllib.request.urlopen", return_value=Response()):
            with self.assertRaisesRegex(AssistantProviderError, "cut off"):
                call_chat_completions(config, [{"role": "user", "content": "test"}])

    def test_chat_completion_rejects_malformed_jsonish_answer(self) -> None:
        class Response:
            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            @staticmethod
            def read() -> bytes:
                payload = {"choices": [{"finish_reason": "stop", "message": {"content": '{"status":"ok","answer":"半截'}}]}
                return json.dumps(payload).encode("utf-8")

        config = {"provider": "deepseek", "api_key": "key", "base_url": "https://api.deepseek.com", "model": "deepseek-v4-flash"}

        with mock.patch("app.assistant.urllib.request.urlopen", return_value=Response()):
            with self.assertRaisesRegex(AssistantProviderError, "malformed JSON"):
                call_chat_completions(config, [{"role": "user", "content": "test"}])

    def test_duckduckgo_lite_parser_extracts_results(self) -> None:
        html = """
        <a rel="nofollow" href="//duckduckgo.com/l/?uddg=https%3A%2F%2Fexample.edu%2Ftopic&amp;rut=x" class='result-link'>Example Topic</a>
        <td class='result-snippet'>This source explains the topic for students.</td>
        </html>
        """

        results = parse_duckduckgo_lite_results(html, max_results=3)

        self.assertEqual(results[0]["title"], "Example Topic")
        self.assertEqual(results[0]["url"], "https://example.edu/topic")
        self.assertIn("students", results[0]["snippet"])

    def test_provider_test_endpoint_uses_no_course_context_and_sanitizes_missing_key(self) -> None:
        handler = object.__new__(WorkspaceHandler)

        with mock.patch("app.server.call_chat_completions") as provider_call:
            result = handler._test_assistant_provider({"api_provider": "openai", "api_model": "gpt-5.2", "api_base_url": "https://api.openai.com/v1", "language": "zh"})

        provider_call.assert_not_called()
        self.assertEqual(result["status"], "config_required")
        self.assertIn("OpenAI API key", result["answer"])

    def test_provider_test_endpoint_calls_provider_with_connection_prompt_only(self) -> None:
        handler = object.__new__(WorkspaceHandler)

        with mock.patch("app.server.call_chat_completions", return_value={"status": "ok", "answer": "connection ok", "used_source_ids": []}) as provider_call:
            result = handler._test_assistant_provider(
                {
                    "api_provider": "openai",
                    "api_key": "test-key",
                    "api_model": "gpt-5.2",
                    "api_base_url": "https://api.openai.com/v1",
                    "language": "zh",
                }
            )

        provider_call.assert_called_once()
        _config, messages = provider_call.call_args.args
        prompt_text = "\n".join(message["content"] for message in messages)
        self.assertNotIn("Course:", prompt_text)
        self.assertNotIn("Sources:", prompt_text)
        self.assertEqual(result["status"], "ok")
        self.assertIn("没有发送课程资料", result["answer"])

    def test_provider_failure_falls_back_to_local_citation_answer(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            course_dir = Path(tmp) / "course"
            course_dir.mkdir()
            (course_dir / "lecture.txt").write_text("Human development is linked to capabilities and agency.", encoding="utf-8")
            course, materials, texts = scan_folder(course_dir)
            store = WorkspaceStore(Path(tmp) / "data")
            store.replace_scan(course, materials, texts)
            handler = object.__new__(WorkspaceHandler)
            handler.store = store

            with mock.patch("app.server.call_chat_completions", side_effect=AssistantProviderError("response was not valid JSON")):
                result = handler._ask_materials(
                    {
                        "question": "capabilities and agency",
                        "action": "ask",
                        "scope": "course",
                        "material_id": materials[0]["id"],
                        "language": "zh",
                        "api_provider": "deepseek",
                        "api_key": "test-key",
                        "api_model": "deepseek-v4-flash",
                    }
                )

        self.assertEqual(result["status"], "ok")
        self.assertTrue(result["grounded"])
        self.assertFalse(result.get("warning"))
        self.assertEqual(result["citations"][0]["source_id"], "C1")

    def test_comprehension_question_gets_learning_scaffold_without_technical_warning(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            course_dir = Path(tmp) / "course"
            course_dir.mkdir()
            (course_dir / "lecture.txt").write_text(
                "19th century development: agriculture, industrialisation, and 'catching up'. "
                "Marx describes rural workers moving into towns and factory labour during capitalist development.",
                encoding="utf-8",
            )
            course, materials, texts = scan_folder(course_dir)
            store = WorkspaceStore(Path(tmp) / "data")
            store.replace_scan(course, materials, texts)
            handler = object.__new__(WorkspaceHandler)
            handler.store = store

            result = handler._ask_materials(
                {
                    "question": "如何理解19 th century development: agriculture, industrialisation, and ‘catching up’这一句话",
                    "action": "ask",
                    "scope": "material",
                    "material_id": materials[0]["id"],
                    "language": "zh",
                    "api_provider": "local",
                }
            )

        self.assertEqual(result["status"], "ok")
        self.assertIn("朴素意思", result["answer"])
        self.assertIn("边读边想", result["answer"])
        self.assertIn("[C1]", result["answer"])

    def test_provider_failure_warning_is_student_facing_not_json_jargon(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            course_dir = Path(tmp) / "course"
            course_dir.mkdir()
            (course_dir / "lecture.txt").write_text("Human development is linked to capabilities and agency.", encoding="utf-8")
            course, materials, texts = scan_folder(course_dir)
            store = WorkspaceStore(Path(tmp) / "data")
            store.replace_scan(course, materials, texts)
            handler = object.__new__(WorkspaceHandler)
            handler.store = store

            with mock.patch("app.server.call_chat_completions", side_effect=AssistantProviderError("Provider response was not valid JSON.")):
                result = handler._ask_materials(
                    {
                        "question": "如何理解 capabilities and agency 这句话？",
                        "action": "ask",
                        "scope": "course",
                        "material_id": materials[0]["id"],
                        "language": "zh",
                        "api_provider": "deepseek",
                        "api_key": "test-key",
                        "api_model": "deepseek-v4-flash",
                    }
                )

        self.assertEqual(result["status"], "ok")
        self.assertIn("Provider response was not valid JSON", result["provider_error"])
        self.assertFalse(result.get("warning"))

    def test_provider_result_unwraps_nested_json_answer(self) -> None:
        citations = [{"source_id": "C1"}]
        result = normalize_provider_result(
            {
                "status": "ok",
                "answer": '{\n"status":"ok",\n"answer":"这才是学生应该看到的答案。[C1]",\n"used_source_ids":["C1"]\n}',
            },
            citations,
        )

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["answer"], "这才是学生应该看到的答案。[C1]")
        self.assertEqual(result["used_source_ids"], ["C1"])

    def test_provider_result_extracts_answer_from_jsonish_string(self) -> None:
        citations = [{"source_id": "C1"}]
        result = normalize_provider_result(
            '{"status":"ok","answer":"学生应该只看到这一句。[C1]","used_source_ids":["C1"]',
            citations,
        )

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["answer"], "学生应该只看到这一句。[C1]")

    def test_pdf_internal_text_is_skipped_for_assistant_chunks(self) -> None:
        raw = " ".join(["/Type /Pages /Kids 1 0 obj endobj stream xref"] * 4)

        chunks = WorkspaceHandler._material_text_chunks(object.__new__(WorkspaceHandler), raw, action="explain", query="")

        self.assertEqual(chunks, [])

    def test_material_structure_question_gets_teaching_sequence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            course_dir = Path(tmp) / "course"
            course_dir.mkdir()
            (course_dir / "DEV100 Week 6 Lecture.pdf.txt").write_text(
                "\f".join(
                    [
                        "Week 6 Lecture Development theory: Modernisation, Dependency and the Development Impasse DEV100 Global Development Studies",
                        "Development theory: a timeline. Pre-development thinking: agricultural production and industrialisation (catching-up). Modernisation theory: development through economic growth and social reform. Dependency theory: modernisation is unequal development and is underdevelopment.",
                        "Development Impasse. Modernisation and dependency theories struggle to explain diverse development experiences.",
                    ]
                ),
                encoding="utf-8",
            )
            course, materials, texts = scan_folder(course_dir)
            store = WorkspaceStore(Path(tmp) / "data")
            store.replace_scan(course, materials, texts)
            handler = object.__new__(WorkspaceHandler)
            handler.store = store

            result = handler._ask_materials(
                {
                    "question": "这个文件是如何讲述 Development theory: Modernisation, Dependency and the Development Impasse 这个观点？",
                    "action": "ask",
                    "scope": "material",
                    "material_id": materials[0]["id"],
                    "language": "zh",
                }
            )

        self.assertEqual(result["status"], "ok")
        self.assertIn("理论路线", result["answer"])
        self.assertIn("Modernisation theory", result["answer"])
        self.assertIn("Dependency theory", result["answer"])
        self.assertNotIn("DEV100", result["answer"])
        self.assertNotIn("old raw JSON", result["answer"])

    def test_course_web_scope_adds_internet_sources_with_distinct_source_ids(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            course_dir = Path(tmp) / "course"
            course_dir.mkdir()
            (course_dir / "lecture.txt").write_text("Human development is linked to capabilities.", encoding="utf-8")
            course, materials, texts = scan_folder(course_dir)
            store = WorkspaceStore(Path(tmp) / "data")
            store.replace_scan(course, materials, texts)
            handler = object.__new__(WorkspaceHandler)
            handler.store = store

            with mock.patch.dict(os.environ, {"CLW_WEB_SEARCH_ENABLED": "1"}), mock.patch(
                "app.server.search_web",
                return_value=[{"title": "Capability approach overview", "url": "https://example.edu/capabilities", "snippet": "The capability approach is associated with human development."}],
            ) as search:
                result = handler._ask_materials(
                    {
                        "question": "human development 和 capability approach 有什么关系？",
                        "action": "ask",
                        "scope": "course_web",
                        "material_id": materials[0]["id"],
                        "language": "zh",
                    }
                )

        search.assert_called_once()
        source_ids = [citation["source_id"] for citation in result["citations"]]
        self.assertIn("C1", source_ids)
        self.assertIn("W1", source_ids)
        self.assertIn("互联网", result["answer"])

    def test_course_web_definition_question_returns_learning_path_not_only_sources(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            course_dir = Path(tmp) / "course"
            course_dir.mkdir()
            (course_dir / "sen.txt").write_text(
                "The capability approach connects capability set, functionings, income poverty, and substantive freedoms.",
                encoding="utf-8",
            )
            course, materials, texts = scan_folder(course_dir)
            store = WorkspaceStore(Path(tmp) / "data")
            store.replace_scan(course, materials, texts)
            handler = object.__new__(WorkspaceHandler)
            handler.store = store

            with mock.patch.dict(os.environ, {"CLW_WEB_SEARCH_ENABLED": "1"}), mock.patch(
                "app.server.search_web",
                return_value=[
                    {
                        "title": "The Capability Approach - Stanford Encyclopedia of Philosophy",
                        "url": "https://plato.stanford.edu/entries/capability-approach/",
                        "snippet": "The capability approach is a theoretical framework about capabilities, functionings, and well-being.",
                    }
                ],
            ):
                result = handler._ask_materials(
                    {
                        "question": "capability approach 是什么？",
                        "action": "ask",
                        "scope": "course_web",
                        "material_id": materials[0]["id"],
                        "language": "zh",
                    }
                )

        self.assertEqual(result["status"], "ok")
        self.assertIn("一句话定位", result["answer"])
        self.assertIn("在课程资料里怎么读", result["answer"])
        self.assertIn("互联网背景怎么用", result["answer"])
        self.assertIn("substantive freedoms", result["answer"])

    def test_web_scope_can_answer_from_internet_only_sources(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = WorkspaceStore(Path(tmp) / "data")
            handler = object.__new__(WorkspaceHandler)
            handler.store = store

            with mock.patch.dict(os.environ, {"CLW_WEB_SEARCH_ENABLED": "1"}), mock.patch(
                "app.server.search_web",
                return_value=[{"title": "Development background", "url": "https://example.edu/development", "snippet": "Development studies examines economic, political, and social change."}],
            ):
                result = handler._ask_materials({"question": "What is development studies?", "scope": "web", "language": "en"})

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["citations"][0]["source_id"], "W1")
        self.assertIn("Internet background", result["answer"])

    def test_web_scope_can_combine_current_material_when_question_references_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            course_dir = Path(tmp) / "course"
            course_dir.mkdir()
            (course_dir / "week6.txt").write_text(
                "Development theory: Modernisation, Dependency and the Development Impasse. Dependency theory examines unequal development.",
                encoding="utf-8",
            )
            course, materials, texts = scan_folder(course_dir)
            store = WorkspaceStore(Path(tmp) / "data")
            store.replace_scan(course, materials, texts)
            handler = object.__new__(WorkspaceHandler)
            handler.store = store

            with mock.patch.dict(os.environ, {"CLW_WEB_SEARCH_ENABLED": "1"}), mock.patch(
                "app.server.search_web",
                return_value=[{"title": "Manufacturing upgrade case", "url": "https://example.edu/case", "snippet": "A real-world case discusses industrial upgrading and global value-chain dependency."}],
            ):
                result = handler._ask_materials(
                    {
                        "question": "结合这个文件给我一个实际案例",
                        "scope": "web",
                        "material_id": materials[0]["id"],
                        "language": "zh",
                    }
                )

        self.assertEqual(result["status"], "ok")
        source_ids = [citation["source_id"] for citation in result["citations"]]
        self.assertIn("C1", source_ids)
        self.assertIn("W1", source_ids)
        self.assertIn("案例线索", result["answer"])
        self.assertNotIn("old note", result["answer"])

    def test_web_scope_book_contribution_uses_book_title_and_authors_for_search(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            course_dir = Path(tmp) / "course"
            course_dir.mkdir()
            (course_dir / "The Companion to Development Studies, Third Edition (Vandana Desai, Rob Potter).txt").write_text(
                "The Companion to Development Studies Third Edition. Development Studies is an interdisciplinary field.",
                encoding="utf-8",
            )
            course, materials, texts = scan_folder(course_dir)
            store = WorkspaceStore(Path(tmp) / "data")
            store.replace_scan(course, materials, texts)
            handler = object.__new__(WorkspaceHandler)
            handler.store = store

            with mock.patch.dict(os.environ, {"CLW_WEB_SEARCH_ENABLED": "1"}), mock.patch(
                "app.server.search_web",
                return_value=[
                    {
                        "title": "The Companion to Development Studies - publisher page",
                        "url": "https://example.edu/companion",
                        "snippet": "A comprehensive companion that brings together key debates and themes in development studies.",
                    }
                ],
            ) as search:
                result = handler._ask_materials(
                    {
                        "question": "这本书的作业在这领域里面有什么杰出的贡献？",
                        "scope": "web",
                        "material_id": materials[0]["id"],
                        "language": "zh",
                    }
                )

        query = search.call_args.args[0]
        self.assertIn('"The Companion to Development Studies, Third Edition"', query)
        self.assertIn('"Vandana Desai"', query)
        self.assertIn('"Rob Potter"', query)
        self.assertIn("Routledge Taylor Francis", query)
        self.assertNotIn("杰出贡献", query)
        self.assertEqual(result["status"], "ok")
        self.assertIn("实体识别", result["answer"])
        self.assertIn("Vandana Desai", result["answer"])
        self.assertIn("综述/companion 型资源", result["answer"])
        self.assertIn("Taylor & Francis", result["answer"])
        source_ids = [citation["source_id"] for citation in result["citations"]]
        self.assertIn("C1", source_ids)
        self.assertIn("W1", source_ids)

    def test_known_material_web_results_add_publisher_and_university_sources(self) -> None:
        results = WorkspaceHandler._known_material_web_results(
            "The Companion to Development Studies, Third Edition (Vandana Desai, Rob Potter)"
        )

        urls = [result["url"] for result in results]
        self.assertTrue(any("taylorfrancis.com" in url for url in urls))
        self.assertTrue(any("royalholloway.ac.uk" in url for url in urls))

    def test_material_identity_authors_prefer_title_over_reference_places(self) -> None:
        identity = WorkspaceHandler._material_identity_from_citations(
            [
                {
                    "title": "The Companion to Development Studies, Third Edition (Vandana Desai, Rob Potter)",
                    "display_title": "The Companion to Development Studies, Third Edition",
                    "quote": "UN (2003) Human Security Now (New York, May). Oxford University Press reference material.",
                }
            ]
        )

        self.assertEqual(identity["authors"], ["Vandana Desai", "Rob Potter"])
        self.assertNotIn("New York", identity["authors"])

    def test_field_contribution_web_results_prefer_academic_sources_over_shopping_pages(self) -> None:
        ranked = WorkspaceHandler._rank_field_contribution_web_results(
            [
                {
                    "title": "The Companion to Development Studies by Vandana Desai",
                    "url": "https://www.amazon.co.uk/book",
                    "snippet": "Buy the book online.",
                },
                {
                    "title": "Publisher page: The Companion to Development Studies",
                    "url": "https://www.routledge.com/example",
                    "snippet": "A concise and authoritative overview of key theoretical and practical issues in development studies.",
                },
            ]
        )

        self.assertIn("routledge", ranked[0]["url"])

    def test_learning_web_results_prefer_academic_sources_over_low_quality_pages(self) -> None:
        ranked = WorkspaceHandler._rank_learning_web_results(
            [
                {
                    "title": "Development Studies book buy online",
                    "url": "https://www.betterworldbooks.com/book",
                    "snippet": "Buy a copy and compare used copy prices.",
                },
                {
                    "title": "Development Studies course reading list",
                    "url": "https://library.example.edu/libguides/development-studies",
                    "snippet": "University library guide with course readings and academic background.",
                },
            ]
        )

        self.assertIn("library.example.edu", ranked[0]["url"])

    def test_web_scope_refuses_writing_before_searching(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = WorkspaceStore(Path(tmp) / "data")
            handler = object.__new__(WorkspaceHandler)
            handler.store = store

            with mock.patch("app.server.search_web") as search:
                result = handler._ask_materials({"question": "帮我写一篇论文", "scope": "web", "language": "zh"})

        search.assert_not_called()
        self.assertEqual(result["status"], "refused")

    def test_web_scope_reports_disabled_search_without_calling_adapter(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = WorkspaceStore(Path(tmp) / "data")
            handler = object.__new__(WorkspaceHandler)
            handler.store = store

            with mock.patch.dict(os.environ, {"CLW_WEB_SEARCH_ENABLED": "0"}), mock.patch("app.server.search_web") as search:
                result = handler._ask_materials({"question": "capability approach 是什么？", "scope": "web", "language": "zh"})

        search.assert_not_called()
        self.assertEqual(result["status"], "error")
        self.assertIn("互联网搜索暂时不可用", result["answer"])

    def test_study_prompt_states_notebook_like_but_course_safe_boundary(self) -> None:
        prompt = build_study_prompt(
            language="zh",
            action="explain",
            question="解释当前资料",
            scope="material",
            course_name="Course",
            active_material_title="Reading",
            citations=[
                {
                    "source_id": "C1",
                    "title": "Reading",
                    "source_type": "material",
                    "locator": "page 1",
                    "relative_path": "reading.pdf",
                    "quote": "This source introduces a course concept.",
                }
            ],
        )
        text = "\n".join(message["content"] for message in prompt)

        self.assertIn("source notebook", text)
        self.assertIn("not a complete substitute for reading", text)
        self.assertIn("Do not write", text)
        self.assertIn("phrase", text)
        self.assertIn("thinking question", text)

    def test_store_notes_can_be_updated_without_creating_duplicates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            course_dir = Path(tmp) / "course"
            course_dir.mkdir()
            (course_dir / "lecture.md").write_text("Reading notes stay attached to the material.", encoding="utf-8")
            course, materials, texts = scan_folder(course_dir)
            store = WorkspaceStore(Path(tmp) / "data")
            store.replace_scan(course, materials, texts)

            note = store.add_note(materials[0]["id"], "First draft.", language="en")
            updated = store.update_note(note["id"], "Expanded student note.", language="en")
            state = store.load()

            self.assertEqual(updated["body"], "Expanded student note.")
            self.assertEqual(len(state["notes"]), 1)
            self.assertEqual(state["notes"][0]["id"], note["id"])

    def test_store_notes_can_be_deleted_when_student_clears_a_saved_note(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            course_dir = Path(tmp) / "course"
            course_dir.mkdir()
            (course_dir / "lecture.md").write_text("A saved reading note can be removed later.", encoding="utf-8")
            course, materials, texts = scan_folder(course_dir)
            store = WorkspaceStore(Path(tmp) / "data")
            store.replace_scan(course, materials, texts)

            note = store.add_note(materials[0]["id"], "Temporary reading note.", language="en")
            removed = store.delete_note(note["id"])
            state = store.load()

            self.assertEqual(removed["id"], note["id"])
            self.assertEqual(state["notes"], [])

    def test_store_annotations_are_separate_from_reading_notes_and_keep_source_anchor(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            course_dir = Path(tmp) / "course"
            course_dir.mkdir()
            (course_dir / "lecture.md").write_text("Read this paragraph carefully.", encoding="utf-8")
            course, materials, texts = scan_folder(course_dir)
            store = WorkspaceStore(Path(tmp) / "data")
            store.replace_scan(course, materials, texts)

            annotation = store.add_annotation(
                {
                    "material_id": materials[0]["id"],
                    "target_type": "region",
                    "style": "highlight",
                    "page": 2,
                    "rects": [{"x": 0.2, "y": 0.3, "w": 0.25, "h": 0.1}],
                    "body": "Important chart area.",
                    "language": "en",
                }
            )
            state = store.load()

            self.assertEqual(annotation["type"], "annotation")
            self.assertEqual(annotation["page"], 2)
            self.assertEqual(annotation["rects"][0]["x"], 0.2)
            self.assertEqual(state["annotations"][0]["material_id"], materials[0]["id"])
            self.assertEqual(state["notes"], [])

    def test_store_annotations_can_be_updated_and_deleted_for_later_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            course_dir = Path(tmp) / "course"
            course_dir.mkdir()
            (course_dir / "lecture.md").write_text("Read this paragraph carefully.", encoding="utf-8")
            course, materials, texts = scan_folder(course_dir)
            store = WorkspaceStore(Path(tmp) / "data")
            store.replace_scan(course, materials, texts)

            annotation = store.add_annotation(
                {
                    "material_id": materials[0]["id"],
                    "target_type": "text",
                    "style": "highlight",
                    "selected_text": "Read this paragraph",
                    "body": "First pass.",
                }
            )
            updated = store.update_annotation(annotation["id"], {"style": "underline", "body": "Revised note."})
            removed = store.delete_annotation(annotation["id"])
            state = store.load()

            self.assertEqual(updated["style"], "underline")
            self.assertEqual(updated["body"], "Revised note.")
            self.assertEqual(removed["id"], annotation["id"])
            self.assertEqual(state["annotations"], [])

    def test_region_annotations_can_save_without_comment_text(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            course_dir = Path(tmp) / "course"
            course_dir.mkdir()
            (course_dir / "lecture.md").write_text("A chart can be marked first and explained later.", encoding="utf-8")
            course, materials, texts = scan_folder(course_dir)
            store = WorkspaceStore(Path(tmp) / "data")
            store.replace_scan(course, materials, texts)

            annotation = store.add_annotation(
                {
                    "material_id": materials[0]["id"],
                    "target_type": "region",
                    "style": "highlight",
                    "page": 1,
                    "rects": [{"x": 0.1, "y": 0.2, "w": 0.3, "h": 0.1}],
                    "body": "",
                }
            )

            self.assertEqual(annotation["target_type"], "region")
            self.assertEqual(annotation["body"], "")
            self.assertEqual(annotation["rects"][0]["w"], 0.3)

    def test_poppler_bbox_text_layer_normalizes_words_for_selection_overlay(self) -> None:
        parsed = parse_poppler_bbox(
            """
            <html xmlns="http://www.w3.org/1999/xhtml"><body><doc>
              <page width="200" height="100">
                <word xMin="20" yMin="10" xMax="80" yMax="30">Supply</word>
                <word xMin="90" yMin="10" xMax="150" yMax="30">chain</word>
              </page>
            </doc></body></html>
            """
        )

        self.assertEqual(parsed["text"], "Supply chain")
        self.assertEqual(parsed["words"][0]["x"], 0.1)
        self.assertEqual(parsed["words"][0]["w"], 0.3)
        self.assertEqual(parsed["words"][1]["y"], 0.1)

    def test_office_material_pages_reuse_converted_pdf_preview_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            course_dir = Path(tmp) / "course"
            course_dir.mkdir()
            self.write_docx(course_dir / "reading.docx", "Course text should stay selectable after conversion.")
            course, materials, texts = scan_folder(course_dir)
            store = WorkspaceStore(Path(tmp) / "data")
            store.replace_scan(course, materials, texts)
            converted = Path(tmp) / "converted.pdf"
            converted.write_bytes(b"%PDF-1.4\n")
            handler = object.__new__(WorkspaceHandler)
            handler.store = store

            with mock.patch.object(handler, "_office_preview_pdf", return_value=converted) as convert, mock.patch.object(handler, "_pdf_page_count", return_value=2):
                preview = handler._paged_pages(materials[0]["id"])

            convert.assert_called_once()
            self.assertEqual(preview["page_count"], 2)
            self.assertEqual(preview["source_kind"], "docx")
            self.assertEqual(preview["preview_kind"], "converted_pdf")
            self.assertIn("{page}.png", preview["image_template"])
            self.assertIn("{page}.text.json", preview["text_template"])

    def test_pdf_parser_does_not_expose_raw_pdf_objects_as_reading_text(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            broken_pdf = Path(tmp) / "broken.pdf"
            broken_pdf.write_bytes(b"%PDF-1.5\n1 0 obj << /Type /Pages /Kids [2 0 R] >> endobj\n")

            with mock.patch("app.materials.shutil.which", return_value=None):
                result = parse_pdf(broken_pdf, "Broken PDF")

            self.assertEqual(result.status, "needs_parser")
            self.assertFalse(result.text)
            self.assertTrue(any("PDF text extraction failed" in item for item in result.diagnostics))

    def test_pdf_page_count_reports_damaged_pdf_without_leaking_command_repr(self) -> None:
        handler = object.__new__(WorkspaceHandler)
        completed = subprocess.CompletedProcess(
            args=["pdfinfo", "broken.pdf"],
            returncode=1,
            stdout="",
            stderr="Syntax Error: Couldn't read xref table\n",
        )

        with mock.patch("app.server.shutil.which", return_value="/usr/bin/pdfinfo"), mock.patch("app.server.subprocess.run", return_value=completed):
            with self.assertRaisesRegex(ValueError, "PDF preview unavailable"):
                handler._pdf_page_count(Path("broken.pdf"))

    def test_course_creation_upload_and_unit_assignment_manage_local_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = WorkspaceStore(Path(tmp) / "data")

            state = store.create_course("Contemporary Issues")
            course = state["course"]
            course_folder = Path(course["folder_path"])
            self.assertTrue(course_folder.exists())

            state = store.upload_materials(
                course["id"],
                [
                    ("lecture-1.md", b"# Lecture 1\n\nPower and ethics."),
                    ("reading.txt", b"Reading about institutions and decision making."),
                ],
            )
            self.assertEqual(len(state["materials"]), 2)
            self.assertTrue((course_folder / "lecture-1.md").exists())

            state = store.create_unit(course["id"], "Week 1")
            unit = state["course"]["units"][0]
            material_id = next(item["id"] for item in state["materials"] if item["relative_path"] == "lecture-1.md")
            state = store.assign_materials_to_unit(course["id"], unit["id"], [material_id])

            self.assertTrue((course_folder / unit["folder_name"] / "lecture-1.md").exists())
            self.assertTrue(any(item["relative_path"] == f"{unit['folder_name']}/lecture-1.md" for item in state["materials"]))

    def test_course_rename_updates_display_name_without_moving_material_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = WorkspaceStore(Path(tmp) / "data")
            state = store.create_course("Original Name")
            course = state["course"]
            state = store.upload_materials(course["id"], [("lecture.md", b"# Lecture\n\nRename should keep files stable.")])
            before_path = Path(state["materials"][0]["path"])

            state = store.rename_course(course["id"], "Renamed Course")

            self.assertEqual(state["course"]["name"], "Renamed Course")
            self.assertEqual(Path(state["materials"][0]["path"]), before_path)
            self.assertTrue(before_path.exists())

    def test_material_file_route_serves_only_registered_material_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = WorkspaceStore(Path(tmp) / "data")
            state = store.create_course("PDF Course")
            course_id = state["course"]["id"]
            state = store.upload_materials(course_id, [("slides.pdf", b"%PDF-1.4\n% test\n")])
            material_id = state["materials"][0]["id"]
            handler = object.__new__(WorkspaceHandler)
            handler.store = store
            handler.send_response = mock.Mock()
            handler.send_header = mock.Mock()
            handler.end_headers = mock.Mock()
            handler.wfile = mock.Mock()

            handler._serve_material_file(material_id)

            handler.send_response.assert_called_with(HTTPStatus.OK)
            content_type_calls = [call for call in handler.send_header.call_args_list if call.args[:1] == ("Content-Type",)]
            self.assertEqual(content_type_calls[0].args[1], "application/pdf")

    def test_material_paths_rebase_from_host_absolute_paths_inside_docker_data_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = WorkspaceStore(Path(tmp) / "data")
            actual_course_dir = store.courses_dir / "portable-course"
            actual_course_dir.mkdir(parents=True)
            actual_file = actual_course_dir / "week-1.pdf"
            actual_file.write_bytes(b"%PDF-1.4\n% portable\n")
            host_course_dir = "/Users/example/project/next/course-learning-workspace/data/courses/portable-course"
            host_file = f"{host_course_dir}/week-1.pdf"
            state = store.save(
                {
                    "active_course_id": "course-1",
                    "courses": [
                        {
                            "id": "course-1",
                            "name": "Portable Course",
                            "folder_path": host_course_dir,
                            "source_path": host_course_dir,
                            "materials": [
                                {
                                    "id": "material-1",
                                    "title": "Week 1",
                                    "kind": "pdf",
                                    "status": "ok",
                                    "relative_path": "week-1.pdf",
                                    "path": host_file,
                                    "bytes": actual_file.stat().st_size,
                                    "diagnostics": [],
                                    "text_available": False,
                                    "text_preview": "",
                                    "locators": [],
                                }
                            ],
                            "notes": [],
                            "annotations": [],
                            "units": [],
                            "created_at": "2026-05-30T00:00:00+00:00",
                            "updated_at": "2026-05-30T00:00:00+00:00",
                        }
                    ],
                    "settings": {},
                }
            )

            material = state["materials"][0]

            self.assertEqual(store.resolve_course_folder(state["course"]), actual_course_dir.resolve())
            self.assertEqual(store.resolve_material_path(material), actual_file.resolve())

    def test_chinese_tokenizer_uses_short_terms_instead_of_whole_sentence_tokens(self) -> None:
        tokens = tokenize("供应链和排放数据有什么关系")

        self.assertIn("供应", tokens)
        self.assertIn("应链", tokens)
        self.assertNotIn("供应链和排放数据有什么关系", tokens)

    @staticmethod
    def write_docx(path: Path, text: str) -> None:
        xml = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            f"<w:body><w:p><w:r><w:t>{text}</w:t></w:r></w:p></w:body></w:document>"
        )
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("word/document.xml", xml)

    @staticmethod
    def write_pptx(path: Path, slides: list[str]) -> None:
        with zipfile.ZipFile(path, "w") as archive:
            for index, text in enumerate(slides, start=1):
                xml = (
                    '<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
                    'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
                    f"<p:cSld><p:spTree><p:sp><p:txBody><a:p><a:r><a:t>{text}</a:t></a:r></a:p>"
                    "</p:txBody></p:sp></p:spTree></p:cSld></p:sld>"
                )
                archive.writestr(f"ppt/slides/slide{index}.xml", xml)

    @staticmethod
    def write_xlsx(path: Path, rows: list[list[str]]) -> None:
        shared = []
        indexes = {}
        sheet_rows = []
        for row_index, row in enumerate(rows, start=1):
            cells = []
            for column_index, value in enumerate(row):
                if value not in indexes:
                    indexes[value] = len(shared)
                    shared.append(value)
                column = chr(ord("A") + column_index)
                cells.append(f'<c r="{column}{row_index}" t="s"><v>{indexes[value]}</v></c>')
            sheet_rows.append(f'<row r="{row_index}">{"".join(cells)}</row>')
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr(
                "xl/sharedStrings.xml",
                '<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
                + "".join(f"<si><t>{value}</t></si>" for value in shared)
                + "</sst>",
            )
            archive.writestr(
                "xl/worksheets/sheet1.xml",
                '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>'
                + "".join(sheet_rows)
                + "</sheetData></worksheet>",
            )


if __name__ == "__main__":
    unittest.main()
