# v1 到新一代系统迁移说明

生成时间：2026-05-29

## 背景

上一代 Open Academic OS 已经验证了本地资料扫描、引用问答、Markdown 笔记、双语界面、DeepSeek / OpenAI-compatible provider、Docker 和基础隐私边界。

经过重新讨论，新一代系统的定位不再是泛化的 academic workflow，而是围绕课程资料、阅读、学生学习笔记、理解、复习和拓展建立学习过程。

## 目录调整

上一代系统已归档到：

```text
legacy/open-academic-os-v1/
```

新一代系统从这里开始：

```text
next/course-learning-workspace/
```

内部交接文档保留在：

```text
docs/handoffs/
```

学校展示材料只放在：

```text
docs/school-facing/
```

## 迁移原则

- 旧系统不删除，作为内部参考。
- 学校展示不展示旧系统内容。
- 新系统默认 Docker-first。
- 桌面安装包在新系统稳定后再考虑。
- 新系统 UI 和文案不再沿用上一代的 workflow / research / writing 叙事。
- 可复用上一代的本地扫描、引用、笔记保存、provider 和隐私机制，但需要按新产品语言重新包装。

## 可复用资产

- 文件扫描和 parser 思路。
- 本地 SQLite / manifest 经验。
- 引用对象和 source-grounded QA 思路。
- API key 不进入课程目录的隐私设计。
- 云端请求双重同意设计。
- Markdown notes / Obsidian 兼容方向。
- DeepSeek 作为普通学生主要云端入口的经验。

## 不再作为新系统重点的资产

- 桌面端签名、封包、公证、SmartScreen。
- 旧的 Source -> Understanding -> Memory -> Research -> Writing -> Output 流程。
- 旧的静态网页 UI。
- 面向开发者的自定义 provider 作为默认入口。
