# Reader and Annotation Design v1

生成时间：2026-05-29  
适用范围：`next/course-learning-workspace`

## 设计目标

Reader 不是简单显示抽取文本，而应接近学生真实阅读资料的方式：

- PDF、课件、Word、Excel 应尽量保留原始图片、版式和分页。
- 学生可以对整份文件写阅读笔记。
- 学生可以选中文字、公式、表格区域或图片区域创建批注。
- 批注可以支持高亮、下划线、删除线和评论。
- AI 问答仍基于课程资料和学生主动提问，不主动替代阅读。

## 为什么不能继续用 iframe PDF

浏览器原生 PDF iframe 有三个问题：

- 性能不可控，大 PDF 或课件型 PDF 容易卡顿。
- 页面内部文本、图片坐标不容易被应用稳定读取。
- 批注层无法可靠保存到应用自己的数据结构中。

因此 Reader 应改为应用自己的文档预览层。

## 当前落地策略

### PDF

第一阶段：

- 后端用 Poppler 将 PDF 按页渲染成 PNG。
- 前端显示页面图片列表。
- 每页上方叠加 `annotation-layer`。
- 抽取文本继续作为 Ask Materials 和来源检索的索引。

第二阶段：

- 使用 `pdftotext -bbox` 或 PDF.js text layer 生成文字坐标。
- 学生选中文字时，保存文字范围和坐标。
- 学生框选图片或图表时，保存矩形区域。

### Word / PPT / Excel

第一阶段：

- 保留抽取文本阅读。

第二阶段：

- 用 LibreOffice 或文档转换服务将文件转换为 PDF 或 HTML。
- 再复用 PDF 的分页预览和批注层。

## 笔记类型

### Reading Note

面向整份文件的阅读笔记。

字段建议：

```json
{
  "id": "note-0001",
  "course_id": "...",
  "material_id": "...",
  "type": "reading_note",
  "body": "学生自己的理解",
  "created_at": "...",
  "updated_at": "..."
}
```

### Anchored Annotation

绑定到文件中某个位置的批注。

字段建议：

```json
{
  "id": "anno-0001",
  "course_id": "...",
  "material_id": "...",
  "type": "annotation",
  "target_type": "text | region | image",
  "style": "highlight | underline | strike | comment",
  "page": 3,
  "rects": [
    { "x": 0.12, "y": 0.25, "w": 0.34, "h": 0.04 }
  ],
  "selected_text": "原文片段，可选",
  "comment": "学生批注",
  "created_at": "...",
  "updated_at": "..."
}
```

坐标使用页面归一化比例，避免缩放后批注错位。

## Reader UI 建议

默认结构：

- 左侧：学习单元 / 文件树，可隐藏。
- 中间：大阅读器，显示分页文件预览。
- 右侧：笔记区，可后续拆成 tabs：
  - 文件阅读笔记。
  - 当前页批注。
  - 课程资料问答。

交互建议：

- 拖选文字：出现迷你工具条，高亮 / 下划线 / 删除线 / 批注。
- 拖拽框选区域：创建图片或表格区域批注。
- 点击已有批注：右侧显示批注内容和来源位置。
- 所有批注都归入当前文件，同时也能在课程笔记总览中检索。

## 与 AI 的关系

AI 不直接生成学生笔记。

AI 可以在学生主动触发时：

- 解释选中的原文。
- 提示该段和课程中其他资料的关系。
- 根据学生已有批注提出复习问题。

回答必须显示来源，无法从资料支持时必须说明。
