# AI Study Assistant v1

## Product Positioning

AI 学习辅助是课程资料内的 source notebook，而不是写作生成器。

参考方向接近 NotebookLM / Open Notebook 的“围绕来源对话”能力，但在高校课程学习场景里要更保守：它帮助学生进入阅读、理解材料、复习和核对来源，不替学生完成 essay、论文、报告、作业答案或课堂提交内容。

## Conservative Does Not Mean Empty

这里的“保守”不是默认拒答，也不是只摘一句原文。

保守的衡量标准：

- 足够帮助学生课前预习：知道资料大概在讲什么、理论或讲授顺序如何推进、哪些概念和证据要重点回到原文查看。
- 不替代阅读全文：解释当前资料时给入口式大纲，不完整展开所有观点，不写成可提交文本。
- 所有实质性判断都必须能回到来源：回答内用 `[S1]`、`[S2]` 标注，界面显示资料名、位置、片段。
- 资料不足时明确说“当前课程资料无法支持这个回答。”，不靠模型常识补全课程观点。
- 遇到代写、生成作业、完成论文或报告的请求时拒绝，并转向学习支持。

## Context Data Flow

`/api/ask-materials` 的上下文只来自当前课程空间：

| Context | Entry | Scope rule | Use |
| --- | --- | --- | --- |
| 当前资料文本 | extracted text chunks | `scope=material` 只取当前资料，`scope=course` 取整门课 | 解释资料、自由问答、复习问题 |
| 当前选中文本 | reader selection | 只在当前资料范围内进入 | 解释选中段落、追问局部含义 |
| 当前阅读笔记草稿 | note editor | 只在当前资料范围内进入 | 帮学生核对自己的理解 |
| 当前批注草稿 | annotation editor | 只在当前资料范围内进入 | 解释批注关注点 |
| 已保存阅读笔记 | workspace notes | 跟随 material/course scope | 连接学生已有理解 |
| 已保存批注 | anchored annotations | 跟随 material/course scope | 回到页面或选区复习 |

进入第三方模型之前，后端会先做本地检索和去噪，只发送选中的少量来源片段，而不是整门课原始文件。

`explain` 有独立的预览检索路径：解释当前资料时默认优先取当前资料正文、开头页、导言/结构性片段和代表性位置，不把学生旧批注或阅读笔记当作资料大纲的主轴。这样学生在没读完长书或长文献之前，可以获得“资料小结 / 入口式源摘要”，而不是随机摘录或旧批注回声。

长书、手册、companion 和阅读资料的 `explain` 不应把书名或领域名拆成词语关系来解释。例如 `Development Studies` 是研究领域名，不应被拆成 `development` 与 `studies` 的关系。系统应优先说明：

- 这是什么资料：书名、作者/编者线索、资料类型。
- 大概在讲什么：领域、主题群、理论/政策/实践议题。
- 第一遍怎么读：目录、导论、章节标题、代表性章节。
- 学生应该回到哪些来源片段继续检查。

## Provider Flow

默认 provider 是 `local`，只做本地引用式回答，保证学校预览和隐私默认安全。

可选 provider：

- DeepSeek
- OpenAI
- Google Gemini
- OpenRouter
- Kimi / Moonshot
- Custom OpenAI-compatible

启用第三方 provider 时：

1. 前端 Settings 选择 provider，填写或选择 model、base URL、API key。
2. API key 只保存在浏览器 localStorage，不写入 `workspace.json`。
3. 可以点击测试按钮；测试请求只发送连接测试 prompt，不发送课程资料。
4. 也可以通过环境变量启动：
   - `CLW_ASSISTANT_PROVIDER=deepseek`
   - `CLW_ASSISTANT_API_KEY=...`
   - `CLW_ASSISTANT_MODEL=...`
   - `CLW_ASSISTANT_BASE_URL=...`
   - 或 provider-specific 环境变量，例如 `CLW_DEEPSEEK_API_KEY`
5. 后端调用 OpenAI-compatible `/chat/completions`，优先要求模型返回 JSON：

```json
{
  "status": "ok",
  "answer": "student-facing answer with [S1]",
  "used_source_ids": ["S1"]
}
```

如果模型返回自然语言而不是 JSON，系统会把自然语言回答标准化为正常回答，而不是把学生可见界面变成 `not JSON` 报错。技术错误只保留在调试字段里；学生看到的是学习可继续的提示或本地引用式回答。

如果 provider 把 JSON 对象错误地包进 `answer` 字段，系统会二次展开，只显示真正的学生答案，不把 `status`、`answer` 等字段残留在回答区。provider 格式不稳定但本地引用回答可用时，默认不向学生显示额外黄色警告；技术原因只留在调试字段。

如果选择第三方 provider 但没有 key，返回 `config_required`，并且不会把课程片段发送给第三方。

## Internet Scope

问答范围包括：

- 当前资料
- 整门课程
- 课程 + 互联网
- 互联网背景

互联网范围是学生主动选择的外部背景，不是课程资料本身。

规则：

- 代写/作业生成请求先拒绝，再检索，避免为了写作请求调用互联网。
- 搜索查询只由学生问题、课程名、当前资料标题组成，不发送阅读笔记、批注、选中文本或全文。
- 当学生在 `互联网背景` 范围内明确说“结合这个文件/当前资料/this material”时，系统会同时带入当前资料的少量课程片段和互联网结果，避免把“结合资料找案例”误判为资料不足。
- 当学生问“这本书/作者/编者在领域里的贡献、影响、地位”时，系统先从当前资料识别书名和作者/编者，再用这些实体构造搜索查询；不能只拿中文问题里的“杰出贡献”等泛词去搜索。
- 对书籍/作者贡献类问题，互联网结果会优先排序学术页、出版社页、书评、课程书单和图书馆/大学来源，降低购物页面权重。
- 互联网结果进入上下文时标记为 `source_group=web`。
- 来源编号区分课程与互联网：`[C1]`、`[W1]`。
- 回答必须说明互联网来源只是背景，不代表老师或课程资料要求。

## Prompt Contract

实际 prompt 在 `next/course-learning-workspace/app/assistant.py` 维护，作为产品内置的 study-assistant skill，而不是 Codex 外部 skill。这样每次产品变更、测试和交接都能跟源码一起版本化。

核心约束：

- 只使用 supplied course sources。
- 中文界面默认中文回答，英文术语可保留。
- explain：生成资料小结/入口式源摘要，说明资料是什么、资料大概在讲什么、第一遍怎么读、哪些主题或章节要回原文查看；长书和长文献不能只罗列来源摘录，也不能把书名拆成伪概念关系。
- connect：只根据来源连接课程重点，不补外部背景。
- review：生成主动回忆问题，不直接给作业答案。
- ask：自由问答，但必须来源支持。
- ask 中的短语/句子理解：按“朴素意思 / 为什么这里重要 / 边读边想 / 回到来源”组织，帮助学生把 slide title、选中文本或句子拆开理解，而不是只复述来源片段。
- ask 中的书籍/作者/编者贡献问题：先识别课程资料中的书名和作者/编者，再结合互联网背景；对“杰出贡献”这类强判断保持谨慎，必须说明证据强弱。
- assignment writing 请求返回 `refused`。

## UI States

回答区必须区分：

- `ok`：基于资料回答，显示来源。
- `not_found`：资料无法支持，明确提示。
- `refused`：学术诚信边界。
- `config_required`：第三方 AI 未配置。
- `error`：第三方 API 调用失败。

来源展示至少包括 source id、资料名、资料类型、位置、片段。来源默认折叠；回答里的 `[C1]` / `[W1]` 是可交互的小标，学生可以悬停预览或点击展开来源。

成功回答提供“添加到阅读笔记”，保存为独立笔记，内容包括问题、回答和来源列表，不覆盖学生正在编辑的阅读笔记。

快捷动作与自由提问文本框保持独立：学生自由提问后，文本框会回到空白；点击“解释当前资料 / 连接到课程重点 / 建议一个复习问题”时，动作使用内置学习提示词，不读取上一条自由问题，避免旧问题污染后续学习动作。

回答正文支持受控 Markdown 渲染：段落、编号列表、项目符号、加粗、行内代码和来源小标会转成安全 HTML；不直接显示 `**`、字面量 `\n` 或 provider JSON 包装。
