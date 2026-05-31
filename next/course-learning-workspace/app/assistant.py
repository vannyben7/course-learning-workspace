from __future__ import annotations

import html
import json
import os
import re
import urllib.parse
import urllib.error
import urllib.request
from typing import Any


DEFAULT_DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEFAULT_DEEPSEEK_MODEL = "deepseek-v4-flash"
DEFAULT_PROVIDER = "local"
PROVIDER_PRESETS = {
    "local": {"label": "Local citations only", "base_url": "", "model": ""},
    "deepseek": {"label": "DeepSeek", "base_url": "https://api.deepseek.com", "model": "deepseek-v4-flash"},
    "openai": {"label": "OpenAI", "base_url": "https://api.openai.com/v1", "model": "gpt-5.2"},
    "gemini": {"label": "Google Gemini", "base_url": "https://generativelanguage.googleapis.com/v1beta/openai", "model": "gemini-2.5-flash"},
    "openrouter": {"label": "OpenRouter", "base_url": "https://openrouter.ai/api/v1", "model": "openai/gpt-5.2"},
    "kimi": {"label": "Kimi / Moonshot", "base_url": "https://api.moonshot.ai/v1", "model": "kimi-k2.6"},
    "custom": {"label": "Custom OpenAI-compatible", "base_url": "", "model": ""},
}
PROVIDER_ENV_KEYS = {
    "deepseek": "CLW_DEEPSEEK_API_KEY",
    "openai": "CLW_OPENAI_API_KEY",
    "gemini": "CLW_GEMINI_API_KEY",
    "openrouter": "CLW_OPENROUTER_API_KEY",
    "kimi": "CLW_KIMI_API_KEY",
    "custom": "CLW_CUSTOM_API_KEY",
}
PROVIDER_MODEL_ENV_KEYS = {
    "deepseek": "CLW_DEEPSEEK_MODEL",
    "openai": "CLW_OPENAI_MODEL",
    "gemini": "CLW_GEMINI_MODEL",
    "openrouter": "CLW_OPENROUTER_MODEL",
    "kimi": "CLW_KIMI_MODEL",
    "custom": "CLW_CUSTOM_MODEL",
}
PROVIDER_BASE_URL_ENV_KEYS = {
    "deepseek": "CLW_DEEPSEEK_BASE_URL",
    "openai": "CLW_OPENAI_BASE_URL",
    "gemini": "CLW_GEMINI_BASE_URL",
    "openrouter": "CLW_OPENROUTER_BASE_URL",
    "kimi": "CLW_KIMI_BASE_URL",
    "custom": "CLW_CUSTOM_BASE_URL",
}


class AssistantProviderError(ValueError):
    pass


def provider_config(payload: dict[str, Any]) -> dict[str, str]:
    provider = str(payload.get("api_provider") or os.getenv("CLW_ASSISTANT_PROVIDER") or DEFAULT_PROVIDER).strip().lower()
    if provider not in PROVIDER_PRESETS:
        raise AssistantProviderError(f"Unsupported AI provider: {provider}")
    preset = PROVIDER_PRESETS[provider]
    api_key = str(
        payload.get("api_key")
        or os.getenv(PROVIDER_ENV_KEYS.get(provider, ""))
        or os.getenv("CLW_ASSISTANT_API_KEY")
        or ""
    ).strip()
    base_url = str(
        payload.get("api_base_url")
        or os.getenv(PROVIDER_BASE_URL_ENV_KEYS.get(provider, ""))
        or os.getenv("CLW_ASSISTANT_BASE_URL")
        or preset["base_url"]
    ).strip().rstrip("/")
    model = str(
        payload.get("api_model")
        or os.getenv(PROVIDER_MODEL_ENV_KEYS.get(provider, ""))
        or os.getenv("CLW_ASSISTANT_MODEL")
        or preset["model"]
    ).strip()
    return {
        "provider": provider,
        "api_key": api_key,
        "base_url": base_url,
        "model": model,
    }


def build_study_prompt(
    *,
    language: str,
    action: str,
    question: str,
    scope: str,
    course_name: str,
    active_material_title: str,
    citations: list[dict[str, Any]],
) -> list[dict[str, str]]:
    language_name = "Chinese" if language == "zh" else "English"
    action_guidance = {
        "explain": (
            "Make a simple current-file summary, similar in length and hierarchy to the first overview a source notebook gives "
            "after loading a document. Identify what the file is, its course/week/topic clues, and the main content sections. "
            "Use a clear numbered structure with short section headings and concrete learning points. Do not over-police the "
            "student at the top. Do not split a field name such as Development Studies into artificial word relationships. "
            "Synthesize the source pack; do not merely list excerpts or turn it into assignment-ready prose."
        ),
        "connect": (
            "Explain what role the current material plays across the whole course. Treat it as a node in the course map: "
            "what earlier topics it draws on, what core transition or tension it introduces, and what later files it prepares. "
            "Use a concise numbered structure with section headings, similar in length to a source-notebook overview."
        ),
        "review": (
            "Create source-grounded review questions for active recall. Questions should help the student go back to the source, "
            "not provide finished homework answers."
        ),
        "ask": (
            "Answer the student's question using only the supplied sources. If the student asks how to understand a phrase, sentence, "
            "slide title, or selected passage, unpack it as a tutor: give a plain-language meaning, define key terms, explain how the "
            "parts relate, place it back into the material's argument, and end with one source-checking question for the student. "
            "If the student asks how the file presents, develops, or explains a concept/theory/viewpoint, describe the material's "
            "teaching sequence: where it starts, what contrast or transition it uses, how the key concepts relate, and what the student "
            "should verify in the source. If the student asks about a book/author/editor's contribution or standing in a field, first "
            "identify the book title and author/editor clues from course sources, then use web sources only as external background; avoid "
            "claiming 'outstanding contribution' unless the provided web sources support that strength."
        ),
    }.get(action, "Answer the student's question using only the supplied sources.")
    sources = "\n\n".join(format_source(citation) for citation in citations)
    system = f"""
You are the Course Learning Workspace study assistant.

Core role:
- Help university students understand uploaded course materials before and during reading.
- Use the supplied sources as the only evidence.
- Course sources are primary. Web sources are external background only when the student explicitly selected an Internet scope.
- Clearly distinguish uploaded course material from Internet search results.
- Respond in {language_name}; keep important English course terms when useful.
- Prefer learning scaffolds: preview outline, concept explanation, connections, review questions, and source checking.
- Act like a source notebook for a course: organize what is already in the materials so the student can enter the reading.
- Encourage thinking: explain enough to help the student continue reading, then give a small prompt that sends them back to the source.

Academic integrity boundary:
- Do not write, draft, complete, or polish essays, papers, reports, homework, or assignment submissions.
- If asked to do assignment writing, return status "refused" and offer source-grounded study help instead.
- Do not invent facts, page numbers, URLs, course claims, or source support.

Good learning support means:
- enough structure for pre-class preparation and comprehension;
- not a complete substitute for reading;
- every substantive claim must be traceable to source ids.
- Do not refuse broad preview questions merely because they are broad. If useful excerpts are supplied, make a careful source-grounded preview and state its limits.
- For explain/pre-class preview, treat the sources as a preview pack: title, opening pages, headings, and representative passages may be enough to give a cautious reading map.

Prefer returning only JSON with this shape:
{{
  "status": "ok" | "not_found" | "refused",
  "answer": "student-facing answer",
  "used_source_ids": ["C1", "W1"]
}}
If your runtime cannot produce JSON, still answer naturally with inline source ids like [C1]. The application will normalize the answer.
""".strip()
    user = f"""
Action: {action}
Scope: {scope}
Course: {course_name or "Current course"}
Current material: {active_material_title or "None selected"}
Student request: {question}

Action-specific instruction:
{action_guidance}

Sources:
{sources}

Rules for the JSON:
- If the supplied sources do not support the request, status must be "not_found".
- If status is "ok", cite source ids inline like [C1] or [W1] and include those ids in used_source_ids.
- For phrase/sentence comprehension questions, structure the answer as: plain meaning, key terms, how the terms connect, why it matters in this material, and one thinking question.
- For material-structure questions such as "how does this file discuss X", structure the answer as: one-sentence overview, teaching/argument sequence, key contrast, what to check in the source, and one thinking prompt.
- For explain/current-file summary, write a concise source summary: what this file is, the main topic, and the core content sections. Match the hierarchy and approximate length of a NotebookLM-style document overview.
- For connect/course-role actions, answer: what role does the current file play in the whole course? Cover prior-course bridge, core theory/tension, and later-course setup when sources support it.
- For long documents, do not force title words into concept relationships. Treat book titles and field names as entities unless the source itself analyzes the words.
- For review, ask questions instead of answering them.
- For explain/review actions, prefer status "ok" when the sources contain enough text to preview or question; reserve "not_found" for genuinely unrelated or empty sources.
- When web sources are present, mark them as external context and do not treat them as course requirements. Web sources may provide real-world examples when the student asks for cases; course sources provide the concept or frame.
- For book/author/editor contribution questions, identify title and author/editor clues from course sources before using Internet background. If the sources only support a weak claim, say so.
- If a source title looks like a filename, course code, or administrative label, refer to it as "this material" and infer the meaningful topic from the source excerpt instead of repeating the filename.
- For Chinese, include the exact sentence "当前课程资料无法支持这个回答。" when status is "not_found".
""".strip()
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def format_source(citation: dict[str, Any]) -> str:
    title = citation.get("display_title") or citation.get("title")
    return "\n".join(
        [
            f"[{citation.get('source_id')}]",
            f"Title: {title}",
            f"Type: {citation.get('source_type')}",
            f"Location: {citation.get('locator') or citation.get('page') or 'text'}",
            f"Path: {citation.get('relative_path')}",
            f"Excerpt: {citation.get('quote')}",
        ]
    )


def call_chat_completions(config: dict[str, str], messages: list[dict[str, str]], timeout: int = 45, max_tokens: int = 900) -> dict[str, Any]:
    api_key = config.get("api_key", "").strip()
    if not api_key:
        raise AssistantProviderError(f"{provider_label(config)} API key is required.")
    base_url = (config.get("base_url") or "").rstrip("/")
    if not base_url:
        raise AssistantProviderError(f"{provider_label(config)} base URL is required.")
    model = config.get("model") or ""
    if not model:
        raise AssistantProviderError(f"{provider_label(config)} model is required.")
    url = f"{base_url}/chat/completions"
    body = {
        "model": model,
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": max_tokens,
        "response_format": {"type": "json_object"},
    }
    request = urllib.request.Request(
        url,
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")[:360]
        raise AssistantProviderError(f"{provider_label(config)} API error {exc.code}: {detail}") from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise AssistantProviderError(f"{provider_label(config)} API request failed: {exc}") from exc
    try:
        choice = payload["choices"][0]
        content = choice["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise AssistantProviderError(f"{provider_label(config)} API returned an unexpected response.") from exc
    if str(choice.get("finish_reason") or "").lower() == "length":
        raise AssistantProviderError(f"{provider_label(config)} response was cut off before completion.")
    try:
        result = parse_provider_json_content(content)
    except AssistantProviderError:
        answer = provider_content_text(content)
        if not answer:
            raise AssistantProviderError(f"{provider_label(config)} response was not usable text or JSON.")
        if provider_text_looks_like_json_payload(answer):
            extracted = extract_jsonish_answer_field(answer)
            if extracted:
                return {"status": "ok", "answer": extracted, "used_source_ids": extract_source_ids(extracted)}
            raise AssistantProviderError(f"{provider_label(config)} response was malformed JSON.")
        return {"status": "ok", "answer": answer, "used_source_ids": extract_source_ids(answer)}
    if not isinstance(result, dict):
        raise AssistantProviderError(f"{provider_label(config)} response JSON must be an object.")
    return result


def normalize_provider_result(content: Any, citations: list[dict[str, Any]]) -> dict[str, Any]:
    try:
        result = parse_provider_json_content(content)
    except AssistantProviderError:
        text = provider_content_text(content)
        if not text:
            raise
        known_ids = {str(citation.get("source_id") or "") for citation in citations}
        text = normalize_answer_text(text)
        try:
            nested = parse_provider_json_content(text)
        except AssistantProviderError:
            nested_answer = extract_jsonish_answer_field(text)
            if nested_answer:
                used_ids = [source_id for source_id in re.findall(r"\[((?:C|W)\d+)\]", nested_answer) if source_id in known_ids]
                return {"status": "ok", "answer": nested_answer, "used_source_ids": list(dict.fromkeys(used_ids))}
            used_ids = [source_id for source_id in re.findall(r"\[((?:C|W)\d+)\]", text) if source_id in known_ids]
            return {"status": "ok", "answer": text, "used_source_ids": list(dict.fromkeys(used_ids))}
        return normalize_provider_payload(nested, citations)
    return normalize_provider_payload(result, citations)


def normalize_provider_payload(result: dict[str, Any], citations: list[dict[str, Any]]) -> dict[str, Any]:
    if not isinstance(result, dict):
        raise AssistantProviderError("Provider response JSON must be an object.")
    normalized = dict(result)
    if "status" not in normalized and "statue" in normalized:
        normalized["status"] = normalized.get("statue")

    answer_value = normalized.get("answer")
    if isinstance(answer_value, str):
        answer = normalize_answer_text(answer_value)
        try:
            nested = parse_provider_json_content(answer)
        except AssistantProviderError:
            nested_answer = extract_jsonish_answer_field(answer)
            if nested_answer:
                answer = nested_answer
        else:
            if isinstance(nested, dict) and nested.get("answer"):
                return normalize_provider_payload(nested, citations)
        normalized["answer"] = answer
    elif answer_value is not None:
        normalized["answer"] = normalize_answer_text(provider_content_text(answer_value))
    else:
        normalized["answer"] = ""

    if not normalized.get("used_source_ids"):
        known_ids = {str(citation.get("source_id") or "") for citation in citations}
        normalized["used_source_ids"] = [
            source_id
            for source_id in extract_source_ids(str(normalized.get("answer") or ""))
            if not known_ids or source_id in known_ids
        ]
    return normalized


def normalize_answer_text(text: str) -> str:
    clean = str(text or "").strip()
    clean = clean.replace("\\n", "\n")
    clean = clean.replace('\\"', '"')
    clean = re.sub(r"^```(?:json|markdown|md)?\s*", "", clean, flags=re.I)
    clean = re.sub(r"\s*```$", "", clean)
    return clean.strip()


def extract_jsonish_answer_field(text: str) -> str:
    raw = str(text or "").strip()
    if not raw.startswith("{") or '"answer"' not in raw:
        return ""
    match = re.search(r'"answer"\s*:\s*"(?P<answer>(?:\\.|[^"\\])*)"', raw, flags=re.S)
    if not match:
        return ""
    answer = match.group("answer")
    try:
        answer = json.loads(f'"{answer}"')
    except json.JSONDecodeError:
        answer = answer.replace("\\n", "\n").replace('\\"', '"').replace("\\/", "/")
    return normalize_answer_text(answer)


def provider_text_looks_like_json_payload(text: str) -> bool:
    clean = str(text or "").strip()
    clean = re.sub(r"^```(?:json)?\s*", "", clean, flags=re.I).strip()
    return clean.startswith("{") and any(key in clean for key in ('"answer"', '"status"', '"used_source_ids"'))


def provider_content_text(content: Any) -> str:
    if isinstance(content, list):
        return "\n".join(str(part.get("text") or part.get("content") or "") if isinstance(part, dict) else str(part) for part in content).strip()
    if isinstance(content, dict):
        for key in ("answer", "text", "content"):
            value = content.get(key)
            if value:
                return str(value).strip()
        return ""
    return str(content or "").strip()


def extract_source_ids(text: str) -> list[str]:
    return list(dict.fromkeys(re.findall(r"\[((?:C|W)\d+)\]", text or "")))


def call_deepseek_chat(config: dict[str, str], messages: list[dict[str, str]], timeout: int = 45) -> dict[str, Any]:
    return call_chat_completions(config, messages, timeout=timeout)


def provider_label(config: dict[str, str]) -> str:
    provider = config.get("provider", DEFAULT_PROVIDER)
    return PROVIDER_PRESETS.get(provider, PROVIDER_PRESETS[DEFAULT_PROVIDER])["label"]


def parse_provider_json_content(content: Any) -> dict[str, Any]:
    if isinstance(content, dict):
        return content
    if isinstance(content, list):
        content = "".join(str(part.get("text") or part.get("content") or "") if isinstance(part, dict) else str(part) for part in content)
    text = str(content or "").strip()
    candidates = [text]
    fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.I | re.S)
    if fence_match:
        candidates.append(fence_match.group(1).strip())
    balanced = first_balanced_json_object(text)
    if balanced:
        candidates.append(balanced)
    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return parsed
    raise AssistantProviderError("Provider response was not valid JSON.")


def first_balanced_json_object(text: str) -> str:
    start = text.find("{")
    while start != -1:
        depth = 0
        in_string = False
        escaped = False
        for index in range(start, len(text)):
            char = text[index]
            if in_string:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    in_string = False
                continue
            if char == '"':
                in_string = True
            elif char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    return text[start : index + 1]
        start = text.find("{", start + 1)
    return ""


def search_web(query: str, max_results: int = 5, timeout: int = 8) -> list[dict[str, str]]:
    clean_query = query.strip()
    if not clean_query:
        return []
    errors: list[str] = []
    endpoints = [
        ("https://lite.duckduckgo.com/lite/?", parse_duckduckgo_lite_results),
        ("https://html.duckduckgo.com/html/?", parse_duckduckgo_results),
    ]
    for base_url, parser in endpoints:
        url = base_url + urllib.parse.urlencode({"q": clean_query})
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 CourseLearningWorkspace/1.0",
                "Accept": "text/html,application/xhtml+xml",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                text = response.read().decode("utf-8", errors="ignore")
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            errors.append(str(exc))
            continue
        results = parser(text, max_results=max_results)
        if results:
            return results
    if errors:
        raise AssistantProviderError(f"Internet search failed: {'; '.join(errors[:2])}")
    return []


def parse_duckduckgo_lite_results(text: str, max_results: int = 5) -> list[dict[str, str]]:
    results: list[dict[str, str]] = []
    pattern = re.compile(
        r"(<a[^>]+class=['\"]result-link['\"][^>]*>|<a(?=[^>]+class=['\"]result-link['\"])[^>]*>)(.*?)</a>(.*?)(?=<a(?=[^>]+class=['\"]result-link['\"])|</html>)",
        flags=re.I | re.S,
    )
    for match in pattern.finditer(text):
        href_match = re.search(r"href=['\"]([^'\"]+)['\"]", match.group(1), flags=re.I)
        if not href_match:
            continue
        raw_url = html.unescape(href_match.group(1))
        title = clean_html(match.group(2))
        tail = match.group(3)
        snippet_match = re.search(r"<td[^>]+class=['\"]result-snippet['\"][^>]*>(.*?)</td>", tail, flags=re.I | re.S)
        snippet = clean_html(snippet_match.group(1)) if snippet_match else ""
        result_url = unwrap_duckduckgo_url(raw_url)
        if result_url.startswith("//"):
            result_url = "https:" + result_url
        if not title or not result_url:
            continue
        results.append({"title": title, "url": result_url, "snippet": snippet})
        if len(results) >= max_results:
            break
    return results


def parse_duckduckgo_results(text: str, max_results: int = 5) -> list[dict[str, str]]:
    results: list[dict[str, str]] = []
    blocks = re.split(r'<div[^>]+class="[^"]*result[^"]*"[^>]*>', text)
    for block in blocks[1:]:
        title_match = re.search(r"<a[^>]+class=['\"][^'\"]*result__a[^'\"]*['\"][^>]+href=['\"]([^'\"]+)['\"][^>]*>(.*?)</a>", block, flags=re.I | re.S)
        if not title_match:
            continue
        raw_url = html.unescape(title_match.group(1))
        title = clean_html(title_match.group(2))
        snippet_match = re.search(r"<a[^>]+class=['\"][^'\"]*result__snippet[^'\"]*['\"][^>]*>(.*?)</a>|<div[^>]+class=['\"][^'\"]*result__snippet[^'\"]*['\"][^>]*>(.*?)</div>", block, flags=re.I | re.S)
        snippet = clean_html(next((group for group in (snippet_match.groups() if snippet_match else []) if group), "")) if snippet_match else ""
        result_url = unwrap_duckduckgo_url(raw_url)
        if not title or not result_url:
            continue
        results.append({"title": title, "url": result_url, "snippet": snippet})
        if len(results) >= max_results:
            break
    return results


def clean_html(value: str) -> str:
    text = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def unwrap_duckduckgo_url(value: str) -> str:
    parsed = urllib.parse.urlparse(value)
    params = urllib.parse.parse_qs(parsed.query)
    if "uddg" in params and params["uddg"]:
        return params["uddg"][0]
    return value
