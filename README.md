# Course Learning Workspace

English version follows the Chinese version.

## 中文说明

Course Learning Workspace 是一个本地优先的课程学习空间。它面向学生和教学团队，把课程资料、阅读、笔记、批注、复习和基于来源的学习辅助放在同一个工作区里。

这个项目不是写作代工工具，也不是论文生成器。它的核心目标是帮助学生围绕已经导入的课程资料进行理解、整理、追问和复习。

### 项目适合什么场景

- 学生把一门课的讲义、PPT、论文、阅读材料放进一个本地课程空间。
- 阅读 PDF、PPT、Word、Markdown、纯文本、CSV 等课程文件。
- 在阅读时写笔记、做批注，并把 AI 回答保存为阅读笔记。
- 让学习辅助概括当前文件，说明当前文件在整门课程中的位置，或回答课程相关问题。
- 在需要时启用互联网搜索，把外部信息作为背景资料，而不是当成课程要求。
- 教学团队或开发者基于一个干净的本地原型继续扩展课程学习系统。

### 当前能力

- 本地课程仪表盘和课程创建流程。
- 浏览器上传课程文件，不需要学生手动粘贴本机路径。
- 学习单元管理，可以把资料移动到不同单元。
- 课程阅读器，支持文本提取和 PDF/Office 预览。
- 阅读笔记、文字批注、定位批注。
- 当前文件概括。
- 当前文件与整门课程的关系说明。
- 课程资料问答和可选互联网搜索问答。
- 来源引用展示。
- 将 AI 的问题和回答保存为笔记。
- Docker 部署和本机 Python 直接运行。

### 仓库结构

```text
docs/
  migration/         迁移说明
  redesign/          产品与界面设计文档
  school-facing/     面向教学团队的定位说明

next/
  course-learning-workspace/
    主应用、Docker 配置、浏览器界面、测试

scripts/
  docker-start.sh         使用 Docker 构建并启动应用
  docker-stop.sh          停止 Docker 服务
  docker-status.sh        查看 Docker 服务状态
  local-start.sh          在本机 Python 环境直接启动
  clean-local-data.sh     删除本地生成数据和缓存
  check.sh                运行语法检查和测试
```

本仓库不会提交本地课程文件、提取文本、预览图、内部交接文档、虚拟环境、浏览器自动化缓存、`.env` 文件或 API key。

### 使用 Docker 启动

前置条件：

- Docker Desktop，或 Docker Engine + Compose v2。

从仓库根目录运行：

```bash
scripts/docker-start.sh
```

然后打开：

```text
http://127.0.0.1:8780
```

停止服务：

```bash
scripts/docker-stop.sh
```

查看状态：

```bash
scripts/docker-status.sh
```

默认端口是 `8780`。如果要换成本机其他端口：

```bash
CLW_HOST_PORT=8888 scripts/docker-start.sh
```

默认只绑定 `127.0.0.1`。如果要在可信局域网中访问：

```bash
CLW_BIND_IP=0.0.0.0 CLW_ALLOW_NETWORK=1 scripts/docker-start.sh
```

请只在可信网络中这样做，因为课程文件和笔记属于个人学习数据。

### 本机直接运行

如果你不想使用 Docker，可以直接运行：

```bash
scripts/local-start.sh
```

然后打开：

```text
http://127.0.0.1:8780
```

该脚本会创建 `.venv/`，安装 `next/course-learning-workspace/requirements.txt`，并启动 Python 服务。

本机直接运行时，如需完整 PDF 和 Office 预览，请在系统中安装：

- Poppler：提供 `pdftotext`、`pdftoppm`、`pdfinfo`
- LibreOffice：提供 `soffice`

Docker 镜像已经包含这些预览工具。

### 配置 AI Provider

应用默认可以在本地引用模式下运行，不需要 API key。

如需启用云端模型，可以复制示例配置：

```bash
cp next/course-learning-workspace/.env.example next/course-learning-workspace/.env
```

然后只填写你需要的项目。`.env` 已被 Git 忽略，不要提交。

也可以在网页右上角的设置中选择 Provider。当前界面支持：

- DeepSeek
- OpenAI
- Google Gemini
- OpenRouter
- Kimi / Moonshot
- 自定义 OpenAI-compatible endpoint

网页设置中的 API key 只保存在当前浏览器的 local storage。后端的课程工作区状态不会保存 API key。

### 互联网搜索

互联网搜索默认关闭：

```text
CLW_WEB_SEARCH_ENABLED=0
```

如果你确实需要让学习辅助检索外部背景资料，可以启动时显式开启：

```bash
CLW_WEB_SEARCH_ENABLED=1 scripts/docker-start.sh
```

外部搜索结果只应被理解为背景资料，不代表课程资料、教师要求或作业标准。

### 本地数据与隐私

本地生成数据默认位于：

```text
next/course-learning-workspace/data/
```

这里可能包含：

- 上传的课程资料副本
- 提取后的文本
- 预览图或转换结果
- 阅读笔记
- 批注
- NotebookLM 相关授权状态或缓存
- 运行时索引和工作区状态

该目录被 Git 忽略，不会进入公开仓库。

删除本地生成数据和仓库内缓存：

```bash
scripts/clean-local-data.sh --yes
```

这是一个破坏性操作，只处理仓库内约定的本地生成数据和缓存路径。

### 开发与检查

运行检查：

```bash
scripts/check.sh
```

当前检查包括：

- Python 代码编译检查
- 浏览器 JavaScript 语法检查
- 课程资料工作流测试

### 常见问题

**打开哪个地址？**

默认统一使用：

```text
http://127.0.0.1:8780
```

**课程文件会被上传到 GitHub 吗？**

不会。课程数据目录、缓存和 `.env` 文件都被 `.gitignore` 和 `.dockerignore` 排除。

**没有 API key 可以用吗？**

可以。系统可以在本地引用模式下运行；云端 AI provider 是可选能力。

**Docker 和本机运行有什么区别？**

Docker 更容易复现，并且内置 PDF/Office 预览依赖。本机运行更方便调试，但你需要自己安装部分系统工具。

**可以部署到服务器吗？**

可以，但默认配置是本机学习空间。对外部署前，请先确认网络访问控制、数据目录权限、API key 管理和备份策略。

### License

This project is released under the MIT License. See [LICENSE](LICENSE).

---

## English

Course Learning Workspace is a local-first study workspace for students and teaching teams. It brings course materials, reading, notes, annotations, review, and source-grounded learning assistance into one place.

This project is not an essay-writing service or an assignment generator. Its purpose is to help students understand, organize, question, and review the course materials they have imported.

### What It Is For

- Students can put lecture slides, PDFs, readings, handouts, and notes for one course into a local workspace.
- Course files can be read in a browser-based reader.
- Students can write notes and annotations while reading.
- AI answers can be saved directly as reading notes.
- The assistant can summarize the current file, explain how it fits into the course, or answer course-related questions.
- Optional Internet search can be enabled for external background context.
- Teaching teams and developers can extend the project as a clean local prototype.

### Current Features

- Local course dashboard and course creation flow.
- Browser-based file upload.
- Learning unit management.
- Reader for extracted course text and rendered previews.
- Reading notes, text annotations, and location annotations.
- Current-file summaries.
- Course-position summaries.
- Course-material Q&A and optional Internet-search Q&A.
- Citation display.
- Save AI questions and answers as notes.
- Docker deployment and direct local Python runtime.

### Repository Layout

```text
docs/
  migration/         Migration notes
  redesign/          Product and interface design notes
  school-facing/     Teaching-team positioning notes

next/
  course-learning-workspace/
    Main application, Docker config, browser UI, and tests

scripts/
  docker-start.sh         Build and run the app with Docker
  docker-stop.sh          Stop the Docker service
  docker-status.sh        Show Docker service status
  local-start.sh          Run directly with a local Python environment
  clean-local-data.sh     Remove local generated data and caches
  check.sh                Run syntax checks and tests
```

The public repository intentionally excludes local course files, extracted text, rendered previews, internal handoff notes, virtual environments, browser automation caches, `.env` files, and API keys.

### Run With Docker

Prerequisites:

- Docker Desktop, or Docker Engine with Compose v2.

From the repository root:

```bash
scripts/docker-start.sh
```

Then open:

```text
http://127.0.0.1:8780
```

Stop the service:

```bash
scripts/docker-stop.sh
```

Check status:

```bash
scripts/docker-status.sh
```

The default host port is `8780`. To use another local port:

```bash
CLW_HOST_PORT=8888 scripts/docker-start.sh
```

The default binding is local-only. To expose the app on a trusted local network:

```bash
CLW_BIND_IP=0.0.0.0 CLW_ALLOW_NETWORK=1 scripts/docker-start.sh
```

Only do this on a trusted network because course files and notes are personal study data.

### Run Directly On Your Computer

If you do not want Docker, run:

```bash
scripts/local-start.sh
```

Then open:

```text
http://127.0.0.1:8780
```

The script creates `.venv/`, installs `next/course-learning-workspace/requirements.txt`, and starts the Python server.

For full PDF and Office previews outside Docker, install:

- Poppler: `pdftotext`, `pdftoppm`, `pdfinfo`
- LibreOffice: `soffice`

The Docker image already includes these preview dependencies.

### Configure AI Providers

The app runs without an API key in local citation mode.

To enable a cloud model, copy the example environment file:

```bash
cp next/course-learning-workspace/.env.example next/course-learning-workspace/.env
```

Fill only the values you need. `.env` files are ignored by Git and should not be committed.

You can also choose a provider in the browser Settings page. The current interface supports:

- DeepSeek
- OpenAI
- Google Gemini
- OpenRouter
- Kimi / Moonshot
- Custom OpenAI-compatible endpoint

API keys entered in the Settings page are stored only in the current browser's local storage. They are not persisted in the backend workspace state.

### Internet Search

Internet search is disabled by default:

```text
CLW_WEB_SEARCH_ENABLED=0
```

Enable it explicitly when you want the assistant to fetch external background sources:

```bash
CLW_WEB_SEARCH_ENABLED=1 scripts/docker-start.sh
```

External search results should be treated as background context only. They do not represent course materials, teacher instructions, or assignment requirements.

### Local Data And Privacy

Generated local data is stored under:

```text
next/course-learning-workspace/data/
```

It may contain:

- Uploaded course-material copies
- Extracted text
- Rendered previews or conversion outputs
- Reading notes
- Annotations
- NotebookLM-related auth state or caches
- Runtime indexes and workspace state

This directory is ignored by Git and is not part of the public repository.

To remove generated data and repository-local caches:

```bash
scripts/clean-local-data.sh --yes
```

This is destructive and only targets the repository-local generated data and cache paths.

### Development And Checks

Run:

```bash
scripts/check.sh
```

The current check covers:

- Python compilation checks
- Browser JavaScript syntax checks
- Course-material workflow tests

### FAQ

**Which URL should I open?**

Use the canonical local URL:

```text
http://127.0.0.1:8780
```

**Will course files be pushed to GitHub?**

No. The course data directory, generated caches, and `.env` files are ignored.

**Can I use it without an API key?**

Yes. The app can run in local citation mode. Cloud AI providers are optional.

**What is the difference between Docker and local runtime?**

Docker is easier to reproduce and includes PDF/Office preview dependencies. The direct local runtime is convenient for development but requires some system tools to be installed separately.

**Can this be deployed on a server?**

Yes, but the default configuration is designed for a local study workspace. Before exposing it publicly, review network access control, data directory permissions, API-key handling, and backups.

### License

This project is released under the MIT License. See [LICENSE](LICENSE).
