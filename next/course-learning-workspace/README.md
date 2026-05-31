# Course Learning Workspace

This is the main local-first course learning workspace application.

## Run With Docker

Prerequisites: Docker Desktop or Docker Engine with Compose v2.

From the repository root:

```bash
scripts/docker-start.sh
```

Open:

```text
http://127.0.0.1:8780
```

Stop:

```bash
scripts/docker-stop.sh
```

Status:

```bash
scripts/docker-status.sh
```

The container stores course data in `next/course-learning-workspace/data/`.
That folder is intentionally not committed, and it remains on disk after the
container is stopped.

Optional provider configuration can be placed in a local `.env` file:

```bash
cp next/course-learning-workspace/.env.example next/course-learning-workspace/.env
```

The default binding is local-only. To use another local port:

```bash
CLW_HOST_PORT=8888 scripts/docker-start.sh
```

To expose the app on a trusted local network, set both:

```bash
CLW_BIND_IP=0.0.0.0 CLW_ALLOW_NETWORK=1 scripts/docker-start.sh
```

## Run Directly On Your Computer

From the repository root:

```bash
scripts/local-start.sh
```

Then open:

```text
http://127.0.0.1:8780
```

The script creates `.venv/`, installs `requirements.txt`, and runs
`python -m app.server`. It uses the same local data directory as Docker unless
you override `CLW_DATA_DIR`.

For full PDF and Office previews outside Docker, install system tools:

- Poppler (`pdftotext`, `pdftoppm`, `pdfinfo`)
- LibreOffice (`soffice`)

On macOS, if headless LibreOffice conversion needs a wrapper, set
`CLW_LIBREOFFICE_WRAPPER=/path/to/wrapper`.

The Docker image already includes these dependencies.

## Develop

Use `http://127.0.0.1:8780` as the canonical browser, screenshot, and QA
interface. After source changes, run:

```bash
scripts/check.sh
```

Then rebuild the Docker preview when needed:

```bash
scripts/docker-start.sh
```

## Optional AI Providers

The browser Settings page can also select DeepSeek, OpenAI, Google Gemini,
OpenRouter, Kimi / Moonshot, or a custom OpenAI-compatible endpoint. It supports
provider-aware model presets, custom model names, base URL overrides, and a
connection-test button. The prototype does not save API keys to `workspace.json`;
the browser keeps the key in local storage and sends it only with assistant
requests or the connection test. When a cloud provider is enabled, selected
course excerpts and selected web-search snippets are sent to the configured chat
completions endpoint for source-grounded learning help.

Internet search scope is disabled by default for privacy. Enable it only when
you want the assistant to fetch external background sources:

```bash
CLW_WEB_SEARCH_ENABLED=1 scripts/docker-start.sh
```

Do not commit `.env` or other key files. They are ignored by Git.

## Course Files

The student-facing flow no longer asks learners to paste folder paths.

1. Create a course from **My Courses**.
2. Open **Course file management**.
3. Upload course materials from the browser file picker.
4. The app copies files into the local course folder under the data directory.
5. Create learning units and move selected materials into unit folders.

## Current Prototype

- Starts from a course dashboard.
- Creates local course folders.
- Copies uploaded materials into each course folder.
- Lets students name learning units and move materials into unit folders.
- Reads `.md`, `.txt`, `.csv`, `.docx`, `.pptx`, and text-based `.pdf` files.
- Lists material status and parser diagnostics.
- Uses a learning-unit/file tree in the course learning view.
- Opens extracted material text in the reader.
- Saves student learning notes locally.
- Answers only from imported course materials, notes, selections, and
  annotations with citations.
- Supports optional OpenAI-compatible API calls for conservative course-study help.
- Supports explicit Internet-background scope with separate Internet citations.
- No student data leaves the container unless a third-party provider is
  explicitly enabled for the assistant.

## Local Data And Cache

Generated local data lives under `next/course-learning-workspace/data/`,
including uploaded materials, extracted text, rendered previews, notes,
annotations, NotebookLM auth state, and NotebookLM cache. The folder is ignored
by Git.

To clear generated data and repository-local caches:

```bash
scripts/clean-local-data.sh --yes
```

## Design Constraints

- Course materials remain the center.
- Student notes are first-class.
- Assistant actions are student-triggered.
- Substantive answers must be source-grounded and show citations.
- The assistant can explain materials, connect course ideas, and suggest review
  questions, but must not write essays, reports, papers, or homework answers.
- External exploration must be visually separated from course materials.
