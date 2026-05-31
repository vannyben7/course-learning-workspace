# Course Learning Workspace

Course Learning Workspace is a local-first study workspace for students and
teaching teams. It is built around course materials, reading, student notes,
annotations, review, and source-grounded learning help.

## Current Structure

```text
docs/
  migration/         Migration notes
  redesign/          Product and interface design notes
  school-facing/     Teaching-team positioning notes

next/
  course-learning-workspace/
    Main application, Docker config, browser UI, and tests

scripts/
  docker-start.sh    Build and run the app with Docker
  docker-stop.sh     Stop the Docker service
  docker-status.sh   Show Docker service status
  local-start.sh     Run directly on a local Python environment
  check.sh           Run syntax checks and tests
```

The public repository intentionally excludes local course data, extracted text,
rendered previews, internal handoff notes, virtual environments, browser
automation caches, and API keys.

## Run With Docker

Prerequisites: Docker Desktop or Docker Engine with Compose v2.

From the repository root:

```bash
scripts/docker-start.sh
```

Then open:

```text
http://127.0.0.1:8780
```

Stop it when you are done:

```bash
scripts/docker-stop.sh
```

Check whether it is running:

```bash
scripts/docker-status.sh
```

Course files and generated previews are stored under:

```text
next/course-learning-workspace/data/
```

That directory is ignored by Git.

The default Docker binding is local-only. To use another host port:

```bash
CLW_HOST_PORT=8888 scripts/docker-start.sh
```

To expose the app on a trusted local network, set both:

```bash
CLW_BIND_IP=0.0.0.0 CLW_ALLOW_NETWORK=1 scripts/docker-start.sh
```

## Run Directly On Your Computer

Use this when you do not want Docker:

```bash
scripts/local-start.sh
```

Then open the same URL:

```text
http://127.0.0.1:8780
```

The local runner creates a `.venv/` environment, installs
`next/course-learning-workspace/requirements.txt`, and starts the Python server.
For PDF and Office previews outside Docker, install Poppler and LibreOffice on
your operating system. On macOS, if headless LibreOffice conversion needs a
wrapper, set `CLW_LIBREOFFICE_WRAPPER=/path/to/wrapper`. The Docker image
already includes the required preview tools.

## Optional AI Providers

The app works in local citation mode without an API key. Optional providers can
be configured with environment variables or through the browser Settings page.

For Docker, copy the example file and fill only the values you need:

```bash
cp next/course-learning-workspace/.env.example next/course-learning-workspace/.env
scripts/docker-start.sh
```

Do not commit `.env` files. They are ignored by Git.

The browser Settings page stores API keys only in that browser's local storage;
the backend workspace state does not persist them.

Internet search is disabled by default for privacy. Enable it only when you want
the assistant to fetch external background sources:

```bash
CLW_WEB_SEARCH_ENABLED=1 scripts/docker-start.sh
```

## Clean Local Data

To delete local course files, extracted text, previews, NotebookLM auth/cache
files, and development caches:

```bash
scripts/clean-local-data.sh --yes
```

This is destructive and only touches repository-local generated data/cache
paths.

## Verify

```bash
scripts/check.sh
```

This checks the Python server code, JavaScript syntax, and material-workflow
tests.
