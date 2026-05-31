# Course Learning Workspace

## Purpose

Course Learning Workspace is a course-centered reading and learning environment
for students and teaching teams.

It helps students work with class materials, read more carefully, keep learning
notes, revisit concepts, and ask source-grounded questions when they need help.

## Why This Exists

Universities need a way to let students benefit from AI without replacing the
learning process. Students often need help entering complex course materials,
especially when readings, slides, textbooks, and cases are spread across many
files.

This system keeps the course materials at the center. The assistant is designed
to be conservative, cited, and student-triggered.

## Student Learning Flow

```text
Course materials -> Reading -> Understanding -> Notes -> Review -> Explore
```

The system supports different course structures:

- Textbook-led courses with chapters, slides, and supporting readings.
- Week-led courses with lecture materials and required or recommended readings.
- Topic-led courses where materials are grouped by theme.

## AI Boundary

The assistant is not the main product. It is a support layer inside the reading
and learning workspace.

It follows these principles:

- It answers from course materials first.
- It shows sources for substantive answers.
- It says when something cannot be found in the provided materials.
- It helps with explanation, translation, connection, and review.
- It does not silently mix external information into course-material answers.
- Cloud AI use can be disabled or restricted by the institution.

## Core Spaces

### Course Home

A student starts from the current course context: recent materials, current
learning unit, recent notes, and review items.

### Materials

Course files are organized by week, chapter, or topic. Students can see what has
been added and whether each material is readable by the system.

### Reader

Students read slides, PDFs, articles, or textbook excerpts with notes beside the
source. They can ask for help on selected text without leaving the material.

### Notes

Students keep their own learning notes. Source excerpts and assistant-supported
explanations are clearly marked so students can distinguish their own thinking
from support material.

### Review

Students revisit concepts through review cards and concept checks linked back to
the original course material.

### Explore

Students can explore related cases or background knowledge. External material is
clearly separated from course materials.

## Deployment Direction

The first institutional direction is Docker-based deployment. This makes pilots
easier to run, isolate, update, and inspect before any desktop installer is
considered.

Default deployment should be private and conservative:

- Local or institution-approved storage.
- Institution-controlled provider settings.
- Clear separation between course materials and optional external exploration.
- Configurable cloud AI permissions.
