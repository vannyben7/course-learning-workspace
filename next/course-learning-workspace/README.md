# Course Learning Workspace App

English version follows the Chinese version.

## 中文说明

这是 Course Learning Workspace 的主应用目录。这里包含 Python 后端、浏览器前端、Docker 配置、测试和本地运行所需依赖。

本目录适合开发者、部署者和希望了解应用内部结构的人阅读。如果你只是想快速使用，请先看仓库根目录的 `README.md`。

### 应用定位

Course Learning Workspace 是一个本地优先的课程学习空间。学生可以把一门课程的资料导入到本地工作区中，然后围绕这些资料阅读、做笔记、批注、复习，并使用基于来源的学习辅助。

系统的默认出发点是课程阅读和课程理解，而不是替学生完成作业。

### 主要模块

```text
app/
  server.py              HTTP API、静态文件服务、课程工作流
  materials.py           文件识别、文本提取、预览生成
  assistant.py           课程资料检索、答案结构、引用整理
  notebooklm_bridge.py   NotebookLM 相关桥接逻辑
  store.py               本地 JSON 工作区存储

web/
  index.html             单页应用入口
  app.js                 前端交互逻辑
  styles.css             界面样式

tests/
  test_material_workflow.py

Dockerfile
docker-compose.yml
requirements.txt
.env.example
```

### 快速启动：Docker

从仓库根目录运行：

```bash
scripts/docker-start.sh
```

打开：

```text
http://127.0.0.1:8780
```

停止：

```bash
scripts/docker-stop.sh
```

查看状态：

```bash
scripts/docker-status.sh
```

Docker 适合普通使用和展示，因为镜像已经安装 PDF 与 Office 预览所需的系统工具。

### 快速启动：本机 Python

从仓库根目录运行：

```bash
scripts/local-start.sh
```

该脚本会：

- 创建 `.venv/`
- 安装 `next/course-learning-workspace/requirements.txt`
- 设置本地数据目录
- 运行 `python -m app.server`

默认访问地址同样是：

```text
http://127.0.0.1:8780
```

如果你直接在本目录中手动运行，可以参考：

```bash
python -m venv ../../.venv
../../.venv/bin/pip install -r requirements.txt
CLW_DATA_DIR="$PWD/data" ../../.venv/bin/python -m app.server
```

### 端口和网络配置

默认监听：

```text
127.0.0.1:8780
```

更换宿主机端口：

```bash
CLW_HOST_PORT=8888 scripts/docker-start.sh
```

允许可信局域网访问：

```bash
CLW_BIND_IP=0.0.0.0 CLW_ALLOW_NETWORK=1 scripts/docker-start.sh
```

对外部署前请先检查访问控制。课程资料、阅读笔记和批注通常都属于个人学习数据。

### 环境变量

常用配置见 `.env.example`：

```text
CLW_BIND_IP=127.0.0.1
CLW_HOST_PORT=8780
CLW_ALLOW_NETWORK=0
CLW_WEB_SEARCH_ENABLED=0
CLW_LIBREOFFICE_WRAPPER=

DEEPSEEK_API_KEY=
OPENAI_API_KEY=
GOOGLE_API_KEY=
OPENROUTER_API_KEY=
MOONSHOT_API_KEY=
CUSTOM_OPENAI_API_KEY=
CUSTOM_OPENAI_BASE_URL=
CUSTOM_OPENAI_MODEL=
```

说明：

- `CLW_BIND_IP`：Docker 绑定的宿主机 IP。
- `CLW_HOST_PORT`：Docker 暴露到宿主机的端口。
- `CLW_ALLOW_NETWORK`：是否允许非本机访问。
- `CLW_WEB_SEARCH_ENABLED`：是否启用互联网搜索。
- `CLW_LIBREOFFICE_WRAPPER`：本机运行时可选的 LibreOffice 转换包装器。
- 各 provider API key：只在你要启用对应云端模型时填写。

不要提交 `.env` 文件。它已经被 Git 忽略。

### 数据目录

默认数据目录：

```text
next/course-learning-workspace/data/
```

该目录可能包含：

- 课程和学习单元状态
- 上传的课程资料副本
- 提取文本
- PDF/Office 预览产物
- 阅读笔记
- 批注
- NotebookLM 授权状态或缓存
- 运行时索引

该目录不会提交到 GitHub。

清理本地数据：

```bash
scripts/clean-local-data.sh --yes
```

### 课程文件流程

学生侧的基本流程是：

1. 在首页创建课程。
2. 进入课程。
3. 打开课程文件管理。
4. 通过浏览器文件选择器上传资料。
5. 创建学习单元。
6. 将资料移动到对应学习单元。
7. 在阅读器中打开资料，写笔记或批注。
8. 使用文件概括、连接到课程或问答功能辅助学习。

支持的主要资料类型：

- `.pdf`
- `.docx`
- `.pptx`
- `.md`
- `.txt`
- `.csv`

文本型 PDF 效果最好。扫描版 PDF 可能需要额外 OCR 能力，当前项目不默认提供完整 OCR 流程。

### 学习辅助行为

当前学习辅助围绕三个入口：

- 文件概括：概括当前打开的课程文件。
- 连接到课程：说明当前文件在整门课程材料中的角色和位置。
- 问课程问题：让学生自己提问，可选择课程资料模式或互联网搜索模式。

回答应尽量包含来源引用。课程资料不足时，界面和回答应明确说明依据不足，而不是编造内容。

互联网搜索只作为外部背景，不等同于课程资料、老师要求或作业标准。

### API key 处理

有两种配置方式：

- `.env`：适合部署者或本机开发。
- 浏览器设置页：适合临时使用。

浏览器设置页输入的 API key 只保存在当前浏览器的 local storage。后端的 `workspace.json` 不保存这些 key。

如果要清理浏览器中的 key，可以在设置页点击清除密钥，或清除该站点的浏览器数据。

### 开发检查

从仓库根目录运行：

```bash
scripts/check.sh
```

当前会执行：

- `compileall` 检查 Python 语法
- JavaScript 语法检查
- `tests/test_material_workflow.py`

### 故障排查

**页面打不开**

先确认服务是否启动：

```bash
scripts/docker-status.sh
```

如果端口被占用，换一个端口：

```bash
CLW_HOST_PORT=8888 scripts/docker-start.sh
```

**PDF 或 Office 预览不完整**

Docker 版本通常更稳定。本机运行时请确认 Poppler 和 LibreOffice 已安装并在 `PATH` 中。

**互联网搜索没有结果**

确认启动时设置了：

```bash
CLW_WEB_SEARCH_ENABLED=1
```

**AI provider 连接失败**

检查 provider、模型名、base URL 和 API key。自定义 OpenAI-compatible endpoint 需要确认接口兼容 chat completions。

### 设计约束

- 课程资料是中心。
- 学生笔记是核心学习资产。
- AI 行为由学生主动触发。
- 回答必须尽量基于来源。
- 外部互联网资料需要和课程资料区分展示。
- 本地数据默认不进入 Git。

---

## English

This is the main application directory for Course Learning Workspace. It contains the Python backend, browser frontend, Docker configuration, tests, and runtime dependencies.

This README is intended for developers, deployers, and anyone who wants to understand the internal application structure. If you only want to run the project quickly, start with the repository-level `README.md`.

### Product Positioning

Course Learning Workspace is a local-first course study workspace. Students import course materials into a local workspace, then read, take notes, annotate, review, and use source-grounded learning assistance around those materials.

The default purpose is course reading and course understanding, not doing assignments on behalf of students.

### Main Modules

```text
app/
  server.py              HTTP API, static file serving, course workflow
  materials.py           File detection, text extraction, preview generation
  assistant.py           Course-material retrieval, answer structure, citations
  notebooklm_bridge.py   NotebookLM-related bridge logic
  store.py               Local JSON workspace storage

web/
  index.html             Single-page application entry
  app.js                 Frontend interaction logic
  styles.css             Interface styles

tests/
  test_material_workflow.py

Dockerfile
docker-compose.yml
requirements.txt
.env.example
```

### Quick Start: Docker

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

Docker is the recommended path for ordinary use and demos because the image includes system tools for PDF and Office previews.

### Quick Start: Local Python

From the repository root:

```bash
scripts/local-start.sh
```

The script will:

- Create `.venv/`
- Install `next/course-learning-workspace/requirements.txt`
- Configure the local data directory
- Run `python -m app.server`

The default URL is:

```text
http://127.0.0.1:8780
```

If you want to run manually from this directory:

```bash
python -m venv ../../.venv
../../.venv/bin/pip install -r requirements.txt
CLW_DATA_DIR="$PWD/data" ../../.venv/bin/python -m app.server
```

### Port And Network Configuration

Default listener:

```text
127.0.0.1:8780
```

Use another host port:

```bash
CLW_HOST_PORT=8888 scripts/docker-start.sh
```

Expose on a trusted local network:

```bash
CLW_BIND_IP=0.0.0.0 CLW_ALLOW_NETWORK=1 scripts/docker-start.sh
```

Review access control before public deployment. Course materials, notes, and annotations are usually personal study data.

### Environment Variables

Common configuration is documented in `.env.example`:

```text
CLW_BIND_IP=127.0.0.1
CLW_HOST_PORT=8780
CLW_ALLOW_NETWORK=0
CLW_WEB_SEARCH_ENABLED=0
CLW_LIBREOFFICE_WRAPPER=

DEEPSEEK_API_KEY=
OPENAI_API_KEY=
GOOGLE_API_KEY=
OPENROUTER_API_KEY=
MOONSHOT_API_KEY=
CUSTOM_OPENAI_API_KEY=
CUSTOM_OPENAI_BASE_URL=
CUSTOM_OPENAI_MODEL=
```

Notes:

- `CLW_BIND_IP`: host IP used by Docker binding.
- `CLW_HOST_PORT`: host port exposed by Docker.
- `CLW_ALLOW_NETWORK`: whether non-local access is allowed.
- `CLW_WEB_SEARCH_ENABLED`: whether Internet search is enabled.
- `CLW_LIBREOFFICE_WRAPPER`: optional local LibreOffice conversion wrapper.
- Provider API keys: fill only when enabling a specific cloud model.

Do not commit `.env` files. They are ignored by Git.

### Data Directory

Default data directory:

```text
next/course-learning-workspace/data/
```

It may contain:

- Course and learning-unit state
- Uploaded course-material copies
- Extracted text
- PDF/Office preview artifacts
- Reading notes
- Annotations
- NotebookLM auth state or caches
- Runtime indexes

This directory is not committed to GitHub.

Clean local data:

```bash
scripts/clean-local-data.sh --yes
```

### Course File Workflow

The student-facing flow is:

1. Create a course from the home page.
2. Open the course.
3. Open course file management.
4. Upload materials through the browser file picker.
5. Create learning units.
6. Move materials into the relevant learning units.
7. Open materials in the reader and write notes or annotations.
8. Use file summary, course connection, or Q&A for learning support.

Main supported material types:

- `.pdf`
- `.docx`
- `.pptx`
- `.md`
- `.txt`
- `.csv`

Text-based PDFs work best. Scanned PDFs may need additional OCR support; this project does not ship a full OCR pipeline by default.

### Learning Assistant Behavior

The current assistant has three main entry points:

- File summary: summarize the currently open course file.
- Course connection: explain the role of the current file within the whole course.
- Course Q&A: let students ask their own questions, with either course-material mode or Internet-search mode.

Answers should include citations where possible. When course material is insufficient, the app should say so instead of inventing content.

Internet search is external background only. It is not the same as course material, teacher requirements, or assignment criteria.

### API Key Handling

There are two configuration paths:

- `.env`: useful for deployment or local development.
- Browser Settings page: useful for temporary use.

API keys entered in the browser Settings page are stored only in the current browser's local storage. The backend `workspace.json` does not persist those keys.

To clear browser-stored keys, use the Settings page clear button or clear site data in the browser.

### Development Checks

From the repository root:

```bash
scripts/check.sh
```

The current check runs:

- Python syntax compilation
- JavaScript syntax checks
- `tests/test_material_workflow.py`

### Troubleshooting

**The page does not open**

Check whether the service is running:

```bash
scripts/docker-status.sh
```

If the port is already in use, choose another one:

```bash
CLW_HOST_PORT=8888 scripts/docker-start.sh
```

**PDF or Office previews are incomplete**

Docker is usually more reliable. For local Python runtime, make sure Poppler and LibreOffice are installed and available in `PATH`.

**Internet search returns no results**

Start with:

```bash
CLW_WEB_SEARCH_ENABLED=1
```

**AI provider connection fails**

Check the provider, model name, base URL, and API key. Custom OpenAI-compatible endpoints must support chat completions.

### Design Constraints

- Course materials stay at the center.
- Student notes are core learning assets.
- AI actions are student-triggered.
- Answers should be source-grounded where possible.
- External Internet material should be visually and conceptually separated from course materials.
- Local data is ignored by Git by default.
