const translations = {
  en: {
    pageTitle: "Course Learning Workspace",
    brandEyebrow: "Course-centered",
    brandTitle: "Learning Workspace",
    languageLabel: "Interface language",
    settings: "Settings",
    myCoursesEyebrow: "Local learning space",
    myCoursesTitle: "My Courses",
    newCourse: "New course",
    newCoursePlaceholder: "Course name",
    searchCourses: "Search courses",
    searchCoursesPlaceholder: "Search created courses",
    createCourseDialogTitle: "Create a course",
    createCourseDialogHelp: "Name the course first. The system will create a local course folder and open Course file management.",
    courseNameLabel: "Course name",
    cancel: "Cancel",
    createAndManage: "Create and manage files",
    openLearning: "Open learning space",
    courseFiles: "Course files",
    backToCourses: "Back to courses",
    noCourses: "No courses yet. Create one to begin.",
    noSearchResults: "No matching courses.",
    createCourseFirst: "Create a course first.",
    courseCreated: "Course created.",
    courseRenamed: "Course renamed.",
    renameCourseInputLabel: "Rename course",
    fileManagerEyebrow: "Course file management",
    uploadMaterialsTitle: "Add course materials",
    localCopy: "Copied locally",
    uploadMaterialsHelp: "Choose files from your computer. The system copies them into this course folder and checks readability.",
    uploadMaterials: "Upload materials",
    uploading: "Uploading and checking materials...",
    uploadComplete: "Materials uploaded and checked.",
    managerEmpty: "No file action yet.",
    unitPlannerTitle: "Learning units",
    newUnitPlaceholder: "Week 1 / Topic 1",
    createUnit: "Create unit",
    unitCreated: "Learning unit created.",
    assignHelp: "Select materials, choose a learning unit, then move them into that unit folder.",
    assignToUnit: "Move selected to unit",
    assignedToUnit: "Selected materials moved into the unit.",
    chooseUnit: "Choose a learning unit",
    unassignedUnit: "Unassigned materials",
    allCourseNotes: "All course notes",
    coursesHeading: "Course",
    noCourse: "No course selected",
    noCourseMeta: "Create a course to begin",
    courseMeta: "{count} materials · {parsed} readable",
    unitsHeading: "Learning Units",
    assistantPolicyHeading: "Study support",
    assistantPolicyBody: "Summarize the current file, place it in the course, or ask a course question.",
    studyAssistantRailTitle: "Study assistant",
    studyAssistantRailBody: "Use the current file, course materials, and optional Internet search to support understanding.",
    currentCourseLabel: "Current course",
    emptyCourseTitle: "Select a course",
    refresh: "Refresh",
    continueReading: "Continue reading",
    tabHome: "Course Home",
    tabReader: "Reader",
    tabNotes: "Notes",
    tabReview: "Review",
    tabExplore: "Explore",
    sourceGrounded: "Source-grounded",
    materialsTitle: "Materials",
    allNotesTitle: "All Learning Notes",
    unitNotesTitle: "{title} notes",
    materialNotesTitle: "Notes for {title}",
    noMaterials: "No materials yet. Open Course files to upload materials.",
    noNotes: "No learning notes yet.",
    noNotesForMaterial: "No notes saved for this material yet.",
    sourceFileLabel: "Source file",
    readerTitle: "Reader",
    readerEmptyMeta: "No material selected",
    readerEmptyBody: "Choose a material from the learning-unit tree, then double-click it to start reading.",
    noExtractedText: "No readable text was extracted from this material yet. Try another file or check parser diagnostics.",
    pdfPreviewTitle: "Layout preview",
    textIndexHint: "Selectable text loads when the file contains text. Scanned pages remain image-only.",
    pdfRendering: "Preparing pages...",
    pageLabel: "Page {page}",
    pdfLazyHint: "Pages and text layers load as you scroll.",
    readingNotesTitle: "Reading Notes",
    annotationsTitle: "Anchored Annotations",
    annotationToolsTitle: "Annotation",
    annotationCommentLabel: "Annotation note",
    annotationCommentPlaceholder: "Explain why this passage or area matters.",
    selectedSourceLabel: "Selected source",
    noSelection: "Select text in the page, or mark an area.",
    markRegion: "Mark area",
    cancelRegion: "Cancel area",
    saveAnnotation: "Save annotation",
    saveChanges: "Save changes",
    cancelEdit: "Cancel edit",
    editAnnotation: "Edit",
    deleteAnnotation: "Delete",
    locateAnnotation: "Locate",
    confirmDeleteAnnotation: "Delete this annotation?",
    noAnnotations: "No anchored annotations for this material yet.",
    annotationSaved: "Annotation saved.",
    annotationUpdated: "Annotation updated.",
    annotationDeleted: "Annotation deleted.",
    editingAnnotation: "Editing saved annotation.",
    regionReady: "Area selected on page {page}. Add a note and save it.",
    textSelectionReady: "Text selection captured. Add a note and save it.",
    textLayerReady: "Text can be selected and copied on text-based pages.",
    styleComment: "Text annotation",
    styleRegion: "Area annotation",
    myNoteLabel: "My note",
    myNotePlaceholder: "Write your own note here.",
    saveNote: "Save note",
    linkToSource: "Link to source",
    noteSaved: "Note saved.",
    noteDeleted: "Note deleted.",
    noteEmpty: "Write a note before saving.",
    saveReady: "Use Save to sync.",
    saving: "Saving...",
    saved: "Saved.",
    saveFailed: "Save failed.",
    sourceLocated: "Source shown.",
    sourceUnavailable: "No source is selected.",
    learningNotesTitle: "Learning Notes",
    markdownReady: "Markdown-ready later",
    reviewCenterTitle: "Review Center",
    recallFirst: "Recall first",
    conceptCheck: "Concept check",
    conceptCheckPrompt: "Pick one material and explain its main idea in your own words before asking for help.",
    openReader: "Open Reader",
    connectionCheck: "Connection check",
    connectionCheckPrompt: "Use the assistant to place a current file in the course map after reading its first pages.",
    askFromMaterials: "Ask the assistant",
    exploreTitle: "Explore Connections",
    separatedFromMaterials: "Separated from course materials",
    exploreBody: "Exploration is clearly marked as outside the uploaded course materials. Schools can disable it.",
    findSimpleCase: "Find a simple case",
    compareConcepts: "Compare two concepts",
    askBackground: "Ask for background",
    conservativeAssistant: "Study assistant",
    askMaterialsTitle: "Study assistant",
    defaultBehavior: "Default behavior",
    assistantDefaultBody: "Start with the current file and the course materials. Use Internet search only when you choose that mode.",
    studyAssistantEyebrow: "Course study support",
    studyAssistantTitle: "Understand the material",
    fileSummaryAction: "File summary",
    connectCourseAction: "Connect to course",
    explainSelected: "File summary",
    connectPrevious: "Connect to course",
    makeReviewCard: "Suggest a review question",
    explainPrompt: "Please summarize the current file: what it is, what it mainly covers, and the core sections I should understand.",
    connectPrompt: "What role does this currently open file play across all course materials?",
    reviewPrompt: "What is one review question I should answer after reading this material?",
    askQuestionLabel: "Ask about the course",
    askPlaceholder: "Ask about the current file, a course concept, or where this topic fits.",
    askWithCitations: "Ask",
    saveAssistantNote: "Save as note",
    assistantNoteSaved: "Saved to reading notes.",
    assistantNoteFailed: "Could not save note.",
    notebooklmEyebrow: "NotebookLM replacement",
    notebooklmTitle: "NotebookLM",
    notebooklmStatusTitle: "Status",
    notebooklmChecking: "Checking NotebookLM connection...",
    notebooklmCheckStatus: "Check status",
    notebooklmSyncCourse: "Sync course files",
    notebooklmQuestionLabel: "Ask NotebookLM",
    notebooklmPlaceholder: "Ask about the synced notebook.",
    notebooklmAskButton: "Ask NotebookLM",
    notebooklmAnswerTitle: "NotebookLM answer",
    notebooklmAnswerEmpty: "Sync this course first, then ask a question here.",
    notebooklmPackageMissing: "notebooklm-py is not installed in this runtime.",
    notebooklmNeedsAuth: "notebooklm-py is installed, but Google auth is not ready. Run notebooklm login for this app profile, then check status again.",
    notebooklmReady: "NotebookLM is ready.",
    notebooklmSynced: "NotebookLM notebook is linked. {count} source mappings are recorded.",
    notebooklmSyncing: "Syncing course files to NotebookLM...",
    notebooklmSyncDone: "Sync complete: {uploaded} uploaded, {skipped} already linked, {failed} failed.",
    notebooklmAsking: "Asking NotebookLM...",
    notebooklmAskFailed: "NotebookLM request failed.",
    assistantWarning: "Note",
    assistantUsingSelection: "Using selection",
    clearAssistantSelection: "Clear",
    citationGroupToggle: "{title} ({count})",
    scopeTitle: "Mode",
    scopeCourseOnly: "Course materials",
    scopeInternetSearch: "Internet search",
    scopeCurrentMaterial: "Current material",
    scopeWholeCourse: "Whole course",
    scopeCourseInternet: "Course + Internet",
    scopeInternetOnly: "Internet background",
    asking: "Searching selected sources...",
    citations: "Citations",
    courseCitations: "Course sources",
    webCitations: "Internet sources",
    assistantUnable: "Cannot answer from sources",
    assistantRefused: "Academic integrity boundary",
    assistantConfigRequired: "AI setup needed",
    sourceTypeMaterial: "Course material",
    sourceTypeWeb: "Internet source",
    sourceTypeSelection: "Current selection",
    sourceTypeReadingNote: "Reading note",
    sourceTypeAnnotation: "Annotation",
    sourceTypeCurrentNote: "Current note draft",
    sourceTypeCurrentAnnotation: "Annotation draft",
    sourceLocatorLabel: "Location",
    materialStatus: "{kind} · {status}",
    textAvailable: "readable",
    notReadable: "not readable yet",
    settingsEyebrow: "Local preferences",
    storageRootTitle: "Default file storage",
    storageRootHelp: "The web prototype stores course folders inside the local app data directory. A desktop shell can add a native folder picker later.",
    readerSettingsTitle: "Reader",
    autoHideSidebarLabel: "Auto-hide learning-unit sidebar",
    autoHideSidebarHelp: "When a material opens in Reader, collapse the left sidebar by default.",
    hideSidebarTitle: "Hide learning-unit sidebar",
    showSidebarTitle: "Show learning-unit sidebar",
    openSettingsTitle: "Open system settings",
    apiSettingsTitle: "Study assistant model",
    apiSettingsHelp: "Cloud AI is optional. When enabled, selected course excerpts and selected web snippets are sent to the chosen provider for source-grounded study help.",
    apiProviderLabel: "Provider",
    apiProviderLocal: "Local citations only",
    apiProviderDeepSeek: "DeepSeek",
    apiProviderOpenAI: "OpenAI",
    apiProviderGemini: "Google Gemini",
    apiProviderOpenRouter: "OpenRouter",
    apiProviderKimi: "Kimi / Moonshot",
    apiProviderCustom: "Custom OpenAI-compatible",
    apiModelLabel: "Model",
    apiCustomModelLabel: "Custom model",
    apiModelPlaceholder: "deepseek-v4-flash",
    apiBaseUrlLabel: "Base URL",
    apiBaseUrlPlaceholder: "https://api.deepseek.com",
    apiKeyLabel: "API key",
    apiKeyPlaceholder: "Stored in this browser only",
    apiTestButton: "Test API key",
    apiClearKey: "Clear key",
    apiTestReady: "No API test yet.",
    apiTesting: "Testing API connection..."
  },
  zh: {
    pageTitle: "课程学习空间",
    brandEyebrow: "课程资料驱动",
    brandTitle: "学习空间",
    languageLabel: "界面语言",
    settings: "设置",
    myCoursesEyebrow: "本地学习空间",
    myCoursesTitle: "我的课程",
    newCourse: "新增课程",
    newCoursePlaceholder: "课程名称",
    searchCourses: "搜索课程",
    searchCoursesPlaceholder: "搜索已创建的课程",
    createCourseDialogTitle: "创建课程",
    createCourseDialogHelp: "先填写课程名称。系统会创建本地课程文件夹，并进入课程文件管理。",
    courseNameLabel: "课程名称",
    cancel: "取消",
    createAndManage: "创建并管理文件",
    openLearning: "进入课程学习",
    courseFiles: "课程文件管理",
    backToCourses: "返回我的课程",
    noCourses: "还没有课程。先创建一门课程。",
    noSearchResults: "没有匹配的课程。",
    createCourseFirst: "请先创建或选择课程。",
    courseCreated: "课程已创建。",
    courseRenamed: "课程名称已更新。",
    renameCourseInputLabel: "重命名课程",
    fileManagerEyebrow: "课程文件管理",
    uploadMaterialsTitle: "添加课程资料",
    localCopy: "本地复制保存",
    uploadMaterialsHelp: "从电脑选择文件。系统会把文件复制进这门课程的文件夹，并检查是否可阅读。",
    uploadMaterials: "上传资料",
    uploading: "正在上传并检查资料...",
    uploadComplete: "资料已上传并完成检查。",
    managerEmpty: "还没有文件操作。",
    unitPlannerTitle: "学习单元",
    newUnitPlaceholder: "第 1 周 / 主题 1",
    createUnit: "创建单元",
    unitCreated: "学习单元已创建。",
    assignHelp: "选择资料，再选择学习单元，系统会把资料移动到该单元文件夹。",
    assignToUnit: "移动选中资料到单元",
    assignedToUnit: "选中资料已移动到该学习单元。",
    chooseUnit: "选择学习单元",
    unassignedUnit: "未归入单元的资料",
    allCourseNotes: "整门课程笔记",
    coursesHeading: "课程",
    noCourse: "未选择课程",
    noCourseMeta: "先创建一门课程",
    courseMeta: "{count} 个资料 · {parsed} 个可阅读",
    unitsHeading: "学习单元",
    assistantPolicyHeading: "学习辅助",
    assistantPolicyBody: "概括当前文件、定位课程角色，或提问课程问题。",
    studyAssistantRailTitle: "学习辅助",
    studyAssistantRailBody: "围绕当前文件、课程资料和必要的互联网背景帮助理解。",
    currentCourseLabel: "当前课程",
    emptyCourseTitle: "选择课程",
    refresh: "刷新",
    continueReading: "继续阅读",
    tabHome: "课程首页",
    tabReader: "阅读器",
    tabNotes: "笔记",
    tabReview: "复习",
    tabExplore: "拓展",
    sourceGrounded: "基于资料",
    materialsTitle: "课程资料",
    allNotesTitle: "全部学习笔记",
    unitNotesTitle: "{title} 的笔记",
    materialNotesTitle: "{title} 的笔记",
    noMaterials: "还没有资料。打开课程文件管理上传资料。",
    noNotes: "还没有学习笔记。",
    noNotesForMaterial: "这个资料还没有保存过笔记。",
    sourceFileLabel: "来源文件",
    readerTitle: "阅读器",
    readerEmptyMeta: "未选择资料",
    readerEmptyBody: "从左侧学习单元树选择资料，双击后开始阅读。",
    noExtractedText: "这个资料暂时没有提取到可阅读文本。请尝试其他文件，或查看解析提示。",
    pdfPreviewTitle: "原版式预览",
    textIndexHint: "文件含有文本时可直接选择复制；扫描页会保持图片预览。",
    pdfRendering: "正在准备页面...",
    pageLabel: "第 {page} 页",
    pdfLazyHint: "页面和文字层会随滚动逐步加载。",
    readingNotesTitle: "阅读笔记",
    annotationsTitle: "定位批注",
    annotationToolsTitle: "批注",
    annotationCommentLabel: "批注笔记",
    annotationCommentPlaceholder: "写下这段文字或这个区域为什么重要。",
    selectedSourceLabel: "选中的来源",
    noSelection: "在页面中选中文字，或标记一个区域。",
    markRegion: "标记区域",
    cancelRegion: "取消区域",
    saveAnnotation: "保存批注",
    saveChanges: "保存修改",
    cancelEdit: "取消编辑",
    editAnnotation: "编辑",
    deleteAnnotation: "删除",
    locateAnnotation: "定位",
    confirmDeleteAnnotation: "删除这条批注？",
    noAnnotations: "这个资料还没有定位批注。",
    annotationSaved: "批注已保存。",
    annotationUpdated: "批注已更新。",
    annotationDeleted: "批注已删除。",
    editingAnnotation: "正在编辑已保存批注。",
    regionReady: "已选中第 {page} 页区域。添加笔记后保存。",
    textSelectionReady: "已捕捉文字选择。添加笔记后保存。",
    textLayerReady: "文本型页面可直接选择和复制文字。",
    styleComment: "文字批注",
    styleRegion: "区域批注",
    myNoteLabel: "我的笔记",
    myNotePlaceholder: "在这里写下你自己的理解。",
    saveNote: "保存笔记",
    linkToSource: "连接到来源",
    noteSaved: "笔记已保存。",
    noteDeleted: "笔记已删除。",
    noteEmpty: "请先写下笔记内容。",
    saveReady: "点击保存后同步。",
    saving: "正在保存...",
    saved: "已保存。",
    saveFailed: "保存失败。",
    sourceLocated: "已定位到来源。",
    sourceUnavailable: "还没有选择来源。",
    learningNotesTitle: "学习笔记",
    markdownReady: "后续兼容 Markdown",
    reviewCenterTitle: "复习中心",
    recallFirst: "先回忆",
    conceptCheck: "概念自测",
    conceptCheckPrompt: "先选择一个资料，并在寻求帮助前用自己的话说明它的主旨。",
    openReader: "打开阅读器",
    connectionCheck: "连接自测",
    connectionCheckPrompt: "读完当前文件开头后，可以用学习辅助判断它在课程地图里的位置。",
    askFromMaterials: "询问学习辅助",
    exploreTitle: "拓展连接",
    separatedFromMaterials: "和课程资料分开",
    exploreBody: "拓展内容会明确标注为课程资料之外的信息，学校可以关闭这个功能。",
    findSimpleCase: "找一个简单案例",
    compareConcepts: "比较两个概念",
    askBackground: "了解背景知识",
    conservativeAssistant: "学习辅助",
    askMaterialsTitle: "学习辅助",
    defaultBehavior: "默认行为",
    assistantDefaultBody: "先围绕当前文件和课程资料帮助理解；需要外部背景时再选择互联网搜索。",
    studyAssistantEyebrow: "课程学习辅助",
    studyAssistantTitle: "读懂课程资料",
    fileSummaryAction: "文件概括",
    connectCourseAction: "连接到课程",
    explainSelected: "文件概括",
    connectPrevious: "连接到课程",
    makeReviewCard: "建议一个复习问题",
    explainPrompt: "请概括当前文件：它是什么、主要讲什么、核心内容分成哪几部分。",
    connectPrompt: "当前显示的这个文件在课程所有文件中扮演什么角色？",
    reviewPrompt: "读完这个资料后，我应该尝试回答哪一个复习问题？",
    askQuestionLabel: "询问课程问题",
    askPlaceholder: "可以问当前文件、课程概念，或这个主题在课程中的位置。",
    askWithCitations: "提问",
    saveAssistantNote: "保存为笔记",
    assistantNoteSaved: "已保存到阅读笔记。",
    assistantNoteFailed: "无法保存笔记。",
    notebooklmEyebrow: "NotebookLM 替代方案",
    notebooklmTitle: "NotebookLM",
    notebooklmStatusTitle: "状态",
    notebooklmChecking: "正在检查 NotebookLM 连接...",
    notebooklmCheckStatus: "检查状态",
    notebooklmSyncCourse: "同步课程文件",
    notebooklmQuestionLabel: "询问 NotebookLM",
    notebooklmPlaceholder: "向已同步的 NotebookLM 笔记本提问。",
    notebooklmAskButton: "询问 NotebookLM",
    notebooklmAnswerTitle: "NotebookLM 回答",
    notebooklmAnswerEmpty: "请先同步这门课程，然后在这里提问。",
    notebooklmPackageMissing: "当前运行环境还没有安装 notebooklm-py。",
    notebooklmNeedsAuth: "notebooklm-py 已安装，但 Google 登录状态还不可用。请先为本应用 profile 运行 notebooklm login，然后重新检查状态。",
    notebooklmReady: "NotebookLM 已可用。",
    notebooklmSynced: "已关联 NotebookLM 笔记本，记录了 {count} 个来源映射。",
    notebooklmSyncing: "正在把课程文件同步到 NotebookLM...",
    notebooklmSyncDone: "同步完成：上传 {uploaded} 个，已关联 {skipped} 个，失败 {failed} 个。",
    notebooklmAsking: "正在询问 NotebookLM...",
    notebooklmAskFailed: "NotebookLM 请求失败。",
    assistantWarning: "提示",
    assistantUsingSelection: "正在使用选中文本",
    clearAssistantSelection: "清除",
    citationGroupToggle: "{title}（{count}）",
    scopeTitle: "提问模式",
    scopeCourseOnly: "课程资料",
    scopeInternetSearch: "互联网搜索",
    scopeCurrentMaterial: "当前资料",
    scopeWholeCourse: "整门课程",
    scopeCourseInternet: "课程 + 互联网",
    scopeInternetOnly: "互联网背景",
    asking: "正在检索选定来源...",
    citations: "引用来源",
    courseCitations: "课程来源",
    webCitations: "互联网来源",
    assistantUnable: "资料不足，无法回答",
    assistantRefused: "学术诚信边界",
    assistantConfigRequired: "需要配置 AI",
    sourceTypeMaterial: "课程资料",
    sourceTypeWeb: "互联网来源",
    sourceTypeSelection: "当前选中文本",
    sourceTypeReadingNote: "阅读笔记",
    sourceTypeAnnotation: "批注",
    sourceTypeCurrentNote: "当前笔记草稿",
    sourceTypeCurrentAnnotation: "当前批注草稿",
    sourceLocatorLabel: "位置",
    materialStatus: "{kind} · {status}",
    textAvailable: "可阅读",
    notReadable: "暂不可阅读",
    settingsEyebrow: "本地偏好",
    storageRootTitle: "默认文件保存位置",
    storageRootHelp: "网页原型会把课程文件夹保存在本地应用数据目录。后续桌面壳可以加入原生文件夹选择器。",
    readerSettingsTitle: "阅读器",
    autoHideSidebarLabel: "进入阅读器时自动隐藏学习单元栏",
    autoHideSidebarHelp: "双击资料进入阅读器后，默认收起左侧栏，让阅读区更宽。",
    hideSidebarTitle: "隐藏学习单元栏",
    showSidebarTitle: "显示学习单元栏",
    openSettingsTitle: "打开系统设置",
    apiSettingsTitle: "学习辅助模型",
    apiSettingsHelp: "云端 AI 是可选能力。启用后，系统会把选定的课程资料片段和选定的互联网搜索片段发送给所选服务商，用于基于来源的学习辅助。",
    apiProviderLabel: "服务商",
    apiProviderLocal: "仅本地引用",
    apiProviderDeepSeek: "DeepSeek",
    apiProviderOpenAI: "OpenAI",
    apiProviderGemini: "Google Gemini",
    apiProviderOpenRouter: "OpenRouter",
    apiProviderKimi: "Kimi / Moonshot",
    apiProviderCustom: "自定义 OpenAI 兼容接口",
    apiModelLabel: "模型",
    apiCustomModelLabel: "自定义模型",
    apiModelPlaceholder: "deepseek-v4-flash",
    apiBaseUrlLabel: "接口地址",
    apiBaseUrlPlaceholder: "https://api.deepseek.com",
    apiKeyLabel: "API 密钥",
    apiKeyPlaceholder: "只保存在当前浏览器",
    apiTestButton: "测试 API 密钥",
    apiClearKey: "清除密钥",
    apiTestReady: "还没有测试 API。",
    apiTesting: "正在测试 API 连接..."
  }
};

const API_PROVIDER_PRESETS = {
  local: { baseUrl: "", models: [] },
  deepseek: { baseUrl: "https://api.deepseek.com", models: ["deepseek-v4-flash", "deepseek-v4-pro"] },
  openai: { baseUrl: "https://api.openai.com/v1", models: ["gpt-5.2", "gpt-5-mini", "gpt-5-nano"] },
  gemini: { baseUrl: "https://generativelanguage.googleapis.com/v1beta/openai", models: ["gemini-2.5-flash", "gemini-3-pro-preview", "gemini-2.5-pro"] },
  openrouter: { baseUrl: "https://openrouter.ai/api/v1", models: ["openai/gpt-5.2", "openai/gpt-5-mini", "openai/gpt-5-nano"] },
  kimi: { baseUrl: "https://api.moonshot.ai/v1", models: ["kimi-k2.6", "kimi-k2.5", "kimi-k2-thinking"] },
  custom: { baseUrl: "", models: [] }
};

const state = {
  workspace: { courses: [], course: null, materials: [], notes: [], annotations: [], settings: {} },
  activeMaterialId: null,
  activeMaterial: null,
  activeNoteId: null,
  annotationDraft: emptyAnnotationDraft(),
  editingAnnotationId: null,
  selectionCaptureTimer: null,
  textSelectionDrag: null,
  lastSelectionKey: "",
  regionMode: false,
  noteScope: { type: "all", id: null },
  courseQuery: "",
  sidebarCollapsed: initialBooleanSetting("clw.sidebarCollapsed", false),
  autoHideSidebar: initialBooleanSetting("clw.autoHideSidebar", true),
  assistantProvider: initialTextSetting("clw.apiProvider", ""),
  assistantModel: initialTextSetting("clw.apiModel", ""),
  assistantBaseUrl: initialTextSetting("clw.apiBaseUrl", ""),
  assistantApiKey: initialTextSetting("clw.apiKey", ""),
  lastAssistantExchange: null,
  language: initialLanguage()
};

const panels = Array.from(document.querySelectorAll(".panel-grid, .reader-layout"));
const tabs = Array.from(document.querySelectorAll(".mode-tabs button"));

bindEvents();
setLanguage(state.language);
loadWorkspace("dashboard");

function bindEvents() {
  tabs.forEach((tab) => tab.addEventListener("click", () => activatePanel(tab.dataset.panel)));
  document.querySelector("#dashboardSettingsButton")?.addEventListener("click", () => showView("settings"));
  document.querySelector("#settingsBackButton")?.addEventListener("click", () => showView("dashboard"));
  document.querySelector("#managerBackButton")?.addEventListener("click", () => showView("dashboard"));
  document.querySelector("#backToDashboardButton")?.addEventListener("click", () => showView("dashboard"));
  document.querySelector("#manageFilesButton")?.addEventListener("click", () => showView("manager"));
  document.querySelector("#openLearningButton")?.addEventListener("click", enterLearningHome);
  document.querySelector("#courseHomeButton")?.addEventListener("click", () => {
    selectNoteScope("all");
    activatePanel("home");
    setSidebarCollapsed(false);
  });
  document.querySelector("#courseName")?.addEventListener("dblclick", beginCourseRename);
  document.querySelector("#activeTitle")?.addEventListener("dblclick", beginCourseRename);
  document.querySelector("#managerCourseTitle")?.addEventListener("dblclick", beginCourseRename);
  document.querySelector("#searchCoursesButton")?.addEventListener("click", runCourseSearch);
  document.querySelector("#confirmCreateCourseButton")?.addEventListener("click", createCourse);
  document.querySelector("#cancelCreateCourseButton")?.addEventListener("click", closeCreateCourseModal);
  document.querySelector("#closeCreateCourseButton")?.addEventListener("click", closeCreateCourseModal);
  document.querySelector("#createCourseModal")?.addEventListener("click", (event) => {
    if (event.target.id === "createCourseModal") closeCreateCourseModal();
  });
  document.querySelector("#modalCourseNameInput")?.addEventListener("keydown", (event) => {
    if (event.key === "Enter") createCourse();
    if (event.key === "Escape") closeCreateCourseModal();
  });
  document.querySelector("#courseSearchInput")?.addEventListener("input", (event) => {
    state.courseQuery = event.target.value.trim().toLowerCase();
    renderDashboard();
  });
  document.querySelector("#courseSearchInput")?.addEventListener("keydown", (event) => {
    if (event.key === "Enter") runCourseSearch();
  });
  document.querySelector("#sidebarToggleButton")?.addEventListener("click", () => setSidebarCollapsed(!state.sidebarCollapsed));
  document.querySelector("#learningSettingsButton")?.addEventListener("click", () => showView("settings"));
  document.querySelector("#autoHideSidebarInput")?.addEventListener("change", (event) => {
    state.autoHideSidebar = event.target.checked;
    localStorage.setItem("clw.autoHideSidebar", String(state.autoHideSidebar));
    renderSettings();
  });
  document.querySelector("#apiProviderSelect")?.addEventListener("change", (event) => {
    state.assistantProvider = API_PROVIDER_PRESETS[event.target.value] ? event.target.value : "local";
    const preset = API_PROVIDER_PRESETS[state.assistantProvider];
    state.assistantBaseUrl = preset.baseUrl;
    state.assistantModel = preset.models[0] || "";
    localStorage.setItem("clw.apiProvider", state.assistantProvider);
    localStorage.setItem("clw.apiBaseUrl", state.assistantBaseUrl);
    localStorage.setItem("clw.apiModel", state.assistantModel);
    renderSettings();
  });
  document.querySelector("#apiModelSelect")?.addEventListener("change", (event) => {
    if (event.target.value !== "__custom") {
      state.assistantModel = event.target.value;
      localStorage.setItem("clw.apiModel", state.assistantModel);
    }
    renderSettings();
  });
  document.querySelector("#apiModelInput")?.addEventListener("input", (event) => {
    state.assistantModel = event.target.value.trim();
    localStorage.setItem("clw.apiModel", state.assistantModel);
    renderSettings();
  });
  document.querySelector("#apiBaseUrlInput")?.addEventListener("input", (event) => {
    state.assistantBaseUrl = event.target.value.trim();
    localStorage.setItem("clw.apiBaseUrl", state.assistantBaseUrl);
  });
  document.querySelector("#apiKeyInput")?.addEventListener("input", (event) => {
    state.assistantApiKey = event.target.value.trim();
    localStorage.setItem("clw.apiKey", state.assistantApiKey);
    renderSettings();
  });
  document.querySelector("#testApiButton")?.addEventListener("click", testAssistantApi);
  document.querySelector("#clearApiKeyButton")?.addEventListener("click", () => {
    state.assistantApiKey = "";
    localStorage.removeItem("clw.apiKey");
    renderSettings();
    setApiTestStatus(t("apiTestReady"));
  });
  document.querySelector("#uploadMaterialsButton")?.addEventListener("click", uploadMaterials);
  document.querySelector("#createUnitButton")?.addEventListener("click", createUnit);
  document.querySelector("#assignMaterialsButton")?.addEventListener("click", assignSelectedMaterials);
  document.querySelector("#refreshButton")?.addEventListener("click", () => loadWorkspace());
  document.querySelector("#continueReadingButton")?.addEventListener("click", () => {
    if (state.activeMaterialId) openMaterial(state.activeMaterialId);
  });
  document.querySelector("#saveNoteButton")?.addEventListener("click", saveNote);
  document.querySelector("#saveAnnotationButton")?.addEventListener("click", saveAnnotation);
  document.querySelector("#cancelAnnotationEditButton")?.addEventListener("click", cancelAnnotationEdit);
  document.querySelector("#markRegionButton")?.addEventListener("click", toggleRegionMode);
  document.querySelector("#noteInput")?.addEventListener("input", () => {
    updateNoteControls();
    setSaveStatus("#noteSaveStatus", t("saveReady"));
  });
  document.querySelector("#annotationInput")?.addEventListener("input", () => {
    updateAnnotationControls();
    setSaveStatus("#annotationSaveStatus", t("saveReady"));
  });
  document.addEventListener("selectionchange", queueTextSelectionCapture);
  document.addEventListener("mouseup", queueTextSelectionCapture);
  document.addEventListener("keyup", (event) => {
    if (event.key === "Shift" || event.key.startsWith("Arrow")) queueTextSelectionCapture();
  });
  document.querySelector("#languageSelect")?.addEventListener("change", (event) => setLanguage(event.target.value));
  document.querySelector("#assistantAskForm")?.addEventListener("submit", (event) => {
    event.preventDefault();
    askMaterials("ask");
  });
  document.querySelector("#notebooklmStatusButton")?.addEventListener("click", refreshNotebookLMStatus);
  document.querySelector("#notebooklmSyncButton")?.addEventListener("click", syncNotebookLM);
  document.querySelector("#assistantCard")?.addEventListener("click", (event) => {
    const saveButton = event.target.closest("[data-assistant-save-note]");
    if (saveButton) {
      saveAssistantExchangeAsNote();
      return;
    }
    const sourceBadge = event.target.closest("[data-source-id]");
    if (sourceBadge) {
      focusCitation(sourceBadge.dataset.sourceId);
    }
  });
  document.querySelector("#assistantSelectionChip")?.addEventListener("click", (event) => {
    if (!event.target.closest("[data-clear-assistant-selection]")) return;
    state.annotationDraft = emptyAnnotationDraft();
    state.lastSelectionKey = "";
    renderAnnotationTools();
  });
  document.querySelectorAll("[data-action-question]").forEach((button) => {
    button.addEventListener("click", () => {
      const action = button.dataset.actionQuestion || "ask";
      askMaterials(action, assistantQuestionForAction(action), button.dataset.actionScope || null);
    });
  });
}

async function loadWorkspace(viewAfterLoad) {
  state.workspace = await api("/api/workspace");
  if (!state.activeMaterialId && state.workspace.materials.length) {
    state.activeMaterialId = state.workspace.materials[0].id;
  }
  renderAll();
  if (state.activeMaterialId) {
    await loadMaterial(state.activeMaterialId);
  } else {
    renderReader();
  }
  if (viewAfterLoad) showView(viewAfterLoad);
}

async function createCourse() {
  const input = document.querySelector("#modalCourseNameInput");
  const name = input.value.trim();
  if (!name) return;
  state.workspace = await api("/api/courses", { method: "POST", body: { name } });
  input.value = "";
  closeCreateCourseModal();
  setManagerStatus(t("courseCreated"), "success");
  resetCourseSelection();
  renderAll();
  showView("manager");
}

function openCreateCourseModal() {
  const modal = document.querySelector("#createCourseModal");
  modal.classList.remove("hidden");
  document.querySelector("#modalCourseNameInput").focus();
}

function closeCreateCourseModal() {
  document.querySelector("#createCourseModal").classList.add("hidden");
  document.querySelector("#modalCourseNameInput").value = "";
}

function runCourseSearch() {
  const input = document.querySelector("#courseSearchInput");
  state.courseQuery = input?.value.trim().toLowerCase() || "";
  renderDashboard();
  const firstResult = document.querySelector(".course-tile:not(.new-course-tile):not(.empty-course-tile)");
  firstResult?.scrollIntoView({ block: "nearest", behavior: "smooth" });
}

async function selectCourse(courseId, targetView = "learning") {
  state.workspace = await api(`/api/courses/${encodeURIComponent(courseId)}/select`, { method: "POST", body: {} });
  resetCourseSelection();
  renderAll();
  if (targetView === "learning") {
    enterLearningHome();
  } else {
    showView(targetView);
  }
}

function enterLearningHome() {
  activatePanel("home");
  setSidebarCollapsed(false);
  showView("learning");
}

async function beginCourseRename(event) {
  const course = activeCourse();
  const target = event.currentTarget;
  if (!course || target.querySelector?.(".inline-title-input")) return;
  event.preventDefault();
  event.stopPropagation();
  const input = document.createElement("input");
  input.className = "inline-title-input";
  input.value = course.name;
  input.setAttribute("aria-label", t("renameCourseInputLabel"));
  target.textContent = "";
  target.append(input);
  input.focus();
  input.select();
  let finished = false;
  const finish = async (save) => {
    if (finished) return;
    finished = true;
    const nextName = input.value.trim();
    if (!save || !nextName || nextName === course.name) {
      renderAll();
      return;
    }
    try {
      state.workspace = await api(`/api/courses/${encodeURIComponent(course.id)}`, {
        method: "PATCH",
        body: { name: nextName }
      });
      renderAll();
      setManagerStatus(t("courseRenamed"), "success");
    } catch (error) {
      renderAll();
      setManagerStatus(error.message, "warn");
    }
  };
  input.addEventListener("blur", () => finish(true));
  input.addEventListener("keydown", (keyEvent) => {
    if (keyEvent.key === "Enter") {
      keyEvent.preventDefault();
      finish(true);
    }
    if (keyEvent.key === "Escape") {
      keyEvent.preventDefault();
      finish(false);
    }
  });
}

async function uploadMaterials() {
  const course = activeCourse();
  const input = document.querySelector("#materialUploadInput");
  if (!course || !input.files.length) return;
  setManagerStatus(t("uploading"), "active");
  const form = new FormData();
  Array.from(input.files).forEach((file) => form.append("files", file, file.name));
  try {
    state.workspace = await apiForm(`/api/courses/${encodeURIComponent(course.id)}/upload`, form);
    input.value = "";
    resetCourseSelection();
    renderAll();
    setManagerStatus(t("uploadComplete"), "success");
  } catch (error) {
    setManagerStatus(error.message, "warn");
  }
}

async function createUnit() {
  const course = activeCourse();
  const input = document.querySelector("#newUnitNameInput");
  if (!course || !input.value.trim()) return;
  state.workspace = await api("/api/units", { method: "POST", body: { course_id: course.id, name: input.value.trim() } });
  input.value = "";
  renderAll();
  setManagerStatus(t("unitCreated"), "success");
}

async function assignSelectedMaterials() {
  const course = activeCourse();
  const unitId = document.querySelector("#assignUnitSelect").value;
  const materialIds = Array.from(document.querySelectorAll("#managerMaterialList input[type='checkbox']:checked")).map((item) => item.value);
  if (!course || !unitId || !materialIds.length) return;
  state.workspace = await api("/api/units/assign", { method: "POST", body: { course_id: course.id, unit_id: unitId, material_ids: materialIds } });
  resetCourseSelection();
  renderAll();
  setManagerStatus(t("assignedToUnit"), "success");
}

function resetCourseSelection() {
  state.activeMaterialId = state.workspace.materials[0]?.id || null;
  state.activeMaterial = null;
  state.activeNoteId = null;
  state.annotationDraft = emptyAnnotationDraft();
  state.editingAnnotationId = null;
  state.regionMode = false;
  state.lastSelectionKey = "";
  state.textSelectionDrag = null;
  state.noteScope = { type: "all", id: null };
}

function renderAll() {
  renderDashboard();
  renderSettings();
  renderManager();
  renderLearning();
}

function renderDashboard() {
  const grid = document.querySelector("#courseGrid");
  grid.innerHTML = "";
  const newCard = document.createElement("article");
  newCard.className = "course-tile new-course-tile";
  newCard.innerHTML = `<strong>+</strong><span>${escapeHtml(t("newCourse"))}</span>`;
  newCard.addEventListener("click", openCreateCourseModal);
  grid.append(newCard);
  const query = state.courseQuery;
  const courses = query
    ? state.workspace.courses.filter((course) => course.name.toLowerCase().includes(query))
    : state.workspace.courses;
  if (!state.workspace.courses.length) {
    const empty = document.createElement("article");
    empty.className = "course-tile empty-course-tile";
    empty.textContent = t("noCourses");
    grid.append(empty);
    return;
  }
  if (!courses.length) {
    const empty = document.createElement("article");
    empty.className = "course-tile empty-course-tile";
    empty.textContent = t("noSearchResults");
    grid.append(empty);
    return;
  }
  courses.forEach((course) => {
    const card = document.createElement("article");
    card.className = "course-tile";
    card.innerHTML = `
      <small>${escapeHtml((course.updated_at || "").slice(0, 10))} · ${course.materials?.length || 0} ${escapeHtml(t("materialsTitle"))}</small>
      <h3>${escapeHtml(course.name)}</h3>
      <p>${escapeHtml(format(t("courseMeta"), { count: course.materials?.length || 0, parsed: (course.materials || []).filter((item) => item.text_available).length }))}</p>
      <div class="tile-actions">
        <button type="button" data-action="learn">${escapeHtml(t("openLearning"))}</button>
        <button type="button" data-action="files">${escapeHtml(t("courseFiles"))}</button>
      </div>
    `;
    card.querySelector("[data-action='learn']").addEventListener("click", () => selectCourse(course.id, "learning"));
    card.querySelector("[data-action='files']").addEventListener("click", () => selectCourse(course.id, "manager"));
    card.addEventListener("dblclick", () => selectCourse(course.id, "learning"));
    grid.append(card);
  });
}

function renderSettings() {
  const languageSelect = document.querySelector("#languageSelect");
  if (languageSelect) languageSelect.value = state.language;
  document.querySelector("#storageRootDisplay").textContent = state.workspace.settings?.storage_root || "";
  const autoHideInput = document.querySelector("#autoHideSidebarInput");
  if (autoHideInput) autoHideInput.checked = state.autoHideSidebar;
  const activeProvider = state.assistantProvider || state.workspace.settings?.api_provider || "local";
  const providerPreset = API_PROVIDER_PRESETS[activeProvider] || API_PROVIDER_PRESETS.local;
  const activeModel = state.assistantModel || state.workspace.settings?.api_model || providerPreset.models[0] || "";
  const activeBaseUrl = state.assistantBaseUrl || state.workspace.settings?.api_base_url || providerPreset.baseUrl || "";
  const provider = document.querySelector("#apiProviderSelect");
  if (provider) provider.value = activeProvider;
  renderModelSelect(activeProvider, activeModel);
  const model = document.querySelector("#apiModelInput");
  const modelIsPreset = providerPreset.models.includes(activeModel);
  if (model && document.activeElement !== model) model.value = modelIsPreset ? "" : activeModel;
  const baseUrl = document.querySelector("#apiBaseUrlInput");
  if (baseUrl && document.activeElement !== baseUrl) baseUrl.value = activeBaseUrl;
  const apiKey = document.querySelector("#apiKeyInput");
  if (apiKey && document.activeElement !== apiKey) apiKey.value = state.assistantApiKey || "";
  const modelSelect = document.querySelector("#apiModelSelect");
  const customModelActive = modelSelect?.value === "__custom" || !modelIsPreset;
  if (modelSelect) modelSelect.disabled = activeProvider === "local";
  if (model) model.disabled = activeProvider === "local" || !customModelActive;
  [baseUrl, apiKey].forEach((input) => {
    if (input) input.disabled = activeProvider === "local";
  });
  const testButton = document.querySelector("#testApiButton");
  if (testButton) testButton.disabled = activeProvider !== "local" && (!activeBaseUrl || !activeModel);
  const clearKeyButton = document.querySelector("#clearApiKeyButton");
  if (clearKeyButton) clearKeyButton.disabled = !state.assistantApiKey;
}

function renderModelSelect(provider, activeModel) {
  const select = document.querySelector("#apiModelSelect");
  if (!select) return;
  const preset = API_PROVIDER_PRESETS[provider] || API_PROVIDER_PRESETS.local;
  const options = provider === "local"
    ? [`<option value="">${escapeHtml(t("apiProviderLocal"))}</option>`]
    : [
        ...preset.models.map((model) => `<option value="${escapeHtml(model)}">${escapeHtml(model)}</option>`),
        `<option value="__custom">${escapeHtml(t("apiProviderCustom"))}</option>`
      ];
  select.innerHTML = options.join("");
  if (provider === "local") {
    select.value = "";
  } else if (preset.models.includes(activeModel)) {
    select.value = activeModel;
  } else {
    select.value = "__custom";
  }
}

function renderManager() {
  const course = activeCourse();
  document.querySelector("#managerCourseTitle").textContent = course?.name || t("createCourseFirst");
  document.querySelector("#unitCount").textContent = String(course?.units?.length || 0);
  document.querySelector("#managerMaterialsCount").textContent = String(state.workspace.materials.length);
  renderUnitManagerList(course);
  renderAssignUnitSelect(course);
  renderManagerMaterialList();
}

function renderUnitManagerList(course) {
  const list = document.querySelector("#unitManagerList");
  list.innerHTML = "";
  if (!course?.units?.length) {
    list.innerHTML = `<div class="empty">${escapeHtml(t("unitPlannerTitle"))}</div>`;
    return;
  }
  course.units.forEach((unit) => {
    const count = materialsForUnit(unit.id).length;
    const item = document.createElement("div");
    item.className = "unit-manager-item";
    item.innerHTML = `<strong>${escapeHtml(unit.name)}</strong><span>${count} ${escapeHtml(t("materialsTitle"))}</span>`;
    list.append(item);
  });
}

function renderAssignUnitSelect(course) {
  const select = document.querySelector("#assignUnitSelect");
  select.innerHTML = `<option value="">${escapeHtml(t("chooseUnit"))}</option>`;
  (course?.units || []).forEach((unit) => {
    const option = document.createElement("option");
    option.value = unit.id;
    option.textContent = unit.name;
    select.append(option);
  });
}

function renderManagerMaterialList() {
  const list = document.querySelector("#managerMaterialList");
  list.innerHTML = "";
  if (!state.workspace.materials.length) {
    list.innerHTML = `<div class="empty">${escapeHtml(t("noMaterials"))}</div>`;
    return;
  }
  state.workspace.materials.forEach((material) => {
    const row = document.createElement("label");
    row.className = "manager-material-row";
    row.innerHTML = `
      <input type="checkbox" value="${escapeHtml(material.id)}" />
      <span>
        <strong>${escapeHtml(material.title)}</strong>
        <small>${escapeHtml(material.relative_path)}</small>
      </span>
    `;
    list.append(row);
  });
}

function renderLearning() {
  const course = activeCourse();
  document.querySelector("#courseName").textContent = course?.name || t("noCourse");
  document.querySelector("#courseMeta").textContent = course
    ? format(t("courseMeta"), { count: state.workspace.materials.length, parsed: state.workspace.materials.filter((item) => item.text_available).length })
    : t("noCourseMeta");
  document.querySelector("#activeTitle").textContent = course?.name || t("emptyCourseTitle");
  renderUnitTree();
  renderHomeNotes();
  renderNotes("#allNotes", allLearningItems(), false);
}

function renderUnitTree() {
  const tree = document.querySelector("#unitTree");
  tree.innerHTML = "";
  const allButton = document.createElement("button");
  allButton.className = state.noteScope.type === "all" ? "tree-row active" : "tree-row";
  allButton.type = "button";
  allButton.innerHTML = `<strong>${escapeHtml(t("allCourseNotes"))}</strong><span>${allLearningItems().length}</span>`;
  allButton.addEventListener("click", () => selectNoteScope("all"));
  tree.append(allButton);

  const groups = materialGroups();
  groups.forEach((group) => {
    const unitButton = document.createElement("button");
    unitButton.className = state.noteScope.type === "unit" && state.noteScope.id === group.id ? "tree-row active" : "tree-row";
    unitButton.type = "button";
    unitButton.innerHTML = `<strong>${escapeHtml(group.name)}</strong><span>${group.materials.length}</span>`;
    unitButton.addEventListener("click", () => selectNoteScope("unit", group.id));
    tree.append(unitButton);
    group.materials.forEach((material) => {
      const fileButton = document.createElement("button");
      fileButton.className = state.noteScope.type === "material" && state.noteScope.id === material.id ? "tree-row file active" : "tree-row file";
      fileButton.type = "button";
      fileButton.innerHTML = `<strong>${escapeHtml(material.title)}</strong><small>${escapeHtml(material.kind)} · ${escapeHtml(material.text_available ? t("textAvailable") : t("notReadable"))}</small>`;
      fileButton.addEventListener("click", () => selectNoteScope("material", material.id));
      fileButton.addEventListener("dblclick", () => openMaterial(material.id));
      tree.append(fileButton);
    });
  });
}

async function selectNoteScope(type, id = null) {
  state.noteScope = { type, id };
  if (type === "material" && id) {
    state.activeMaterialId = id;
    await loadMaterial(id);
  }
  renderLearning();
}

function renderHomeNotes() {
  const title = document.querySelector("#homeNotesTitle");
  const notes = notesForCurrentScope();
  const scopeTitle = scopeTitleForNotes();
  title.textContent = scopeTitle;
  document.querySelector("#notesCount").textContent = String(notes.length);
  renderNotes("#recentNotes", notes, false, state.noteScope.type !== "all");
}

async function openMaterial(materialId, switchPanel = true) {
  state.activeMaterialId = materialId;
  state.noteScope = { type: "material", id: materialId };
  await loadMaterial(materialId);
  renderLearning();
  if (switchPanel) {
    activatePanel("reader");
  }
}

async function loadMaterial(materialId) {
  state.annotationDraft = emptyAnnotationDraft();
  state.editingAnnotationId = null;
  state.regionMode = false;
  state.lastSelectionKey = "";
  state.textSelectionDrag = null;
  const annotationInput = document.querySelector("#annotationInput");
  if (annotationInput) annotationInput.value = "";
  state.activeNoteId = latestReadingNoteForMaterial(materialId)?.id || null;
  state.activeMaterial = await api(`/api/materials/${encodeURIComponent(materialId)}`);
  renderReader();
}

function renderReader() {
  const material = state.activeMaterial;
  const title = document.querySelector("#readerMaterialTitle");
  const meta = document.querySelector("#readerMaterialMeta");
  const page = document.querySelector("#documentPage");
  if (!material) {
    title.textContent = t("readerTitle");
    meta.textContent = t("readerEmptyMeta");
    page.className = "document-page";
    page.innerHTML = `<p class="quiet">${escapeHtml(t("readerEmptyBody"))}</p>`;
    hydrateReadingNoteInput(null);
    renderAnnotationTools();
    return;
  }
  title.textContent = material.title;
  meta.textContent = `${material.kind} · ${material.status} · ${material.relative_path}`;
  if (canRenderPagedPreview(material)) {
    page.className = "document-page pdf-page";
    renderPagedPreview(material, page);
    hydrateReadingNoteInput(material.id);
    renderAnnotationTools();
    return;
  }
  page.className = "document-page";
  const text = material.text || "";
  if (!text) {
    page.innerHTML = `<p class="quiet">${escapeHtml(t("noExtractedText"))}</p>${renderDiagnostics(material)}`;
    hydrateReadingNoteInput(material.id);
    renderAnnotationTools();
    return;
  }
  page.innerHTML = text.split(/\n{2,}/).slice(0, 22).map((paragraph) => `<p>${escapeHtml(paragraph)}</p>`).join("");
  hydrateReadingNoteInput(material.id);
  renderAnnotationTools();
}

function hydrateReadingNoteInput(materialId) {
  const input = document.querySelector("#noteInput");
  if (!input) return;
  const note = materialId ? latestReadingNoteForMaterial(materialId) : null;
  state.activeNoteId = note?.id || null;
  if (document.activeElement !== input) {
    input.value = note?.body || "";
  }
  setSaveStatus("#noteSaveStatus", t("saveReady"));
  setSaveStatus("#annotationSaveStatus", t("saveReady"));
  updateNoteControls();
  updateAnnotationControls();
}

async function renderPagedPreview(material, page) {
  page.innerHTML = `
    <div class="pdf-preview-head">
      <strong>${escapeHtml(t("pdfPreviewTitle"))}</strong>
      <span>${escapeHtml(t("pdfLazyHint"))}</span>
    </div>
    <div class="pdf-loading">${escapeHtml(t("pdfRendering"))}</div>
  `;
  try {
    const meta = await api(`/api/materials/${encodeURIComponent(material.id)}/pages`);
    if (state.activeMaterial?.id !== material.id) return;
    const pages = Array.from({ length: meta.page_count }, (_item, index) => index + 1);
    page.innerHTML = `
      <div class="pdf-preview-head">
        <strong>${escapeHtml(t("pdfPreviewTitle"))} · ${escapeHtml(String(material.kind).toUpperCase())}</strong>
        <span>${escapeHtml(meta.text_available ? t("textLayerReady") : t("textIndexHint"))}</span>
      </div>
      <div class="pdf-page-list">
        ${pages.map((pageNumber) => `
          <figure class="pdf-sheet" data-page="${pageNumber}">
            <figcaption>${escapeHtml(format(t("pageLabel"), { page: pageNumber }))}</figcaption>
            <div class="pdf-sheet-canvas">
              <img loading="lazy" data-src="${escapeHtml(meta.image_template.replace("{page}", pageNumber))}" alt="${escapeHtml(format(t("pageLabel"), { page: pageNumber }))}" />
              <div class="pdf-text-layer" data-text-src="${escapeHtml(meta.text_template.replace("{page}", pageNumber))}" aria-label="${escapeHtml(format(t("pageLabel"), { page: pageNumber }))}"></div>
              <div class="annotation-layer" aria-hidden="true">${renderPdfAnnotationMarks(material, pageNumber)}</div>
            </div>
          </figure>
        `).join("")}
      </div>
    `;
    setupPagedLazyLoading(page);
    bindPdfRegionSelection(page);
  } catch (error) {
    const fallbackText = safeMaterialTextFallback(material);
    const fallback = fallbackText
      ? `<div class="text-fallback">${fallbackText.split(/\n{2,}/).slice(0, 28).map((paragraph) => `<p>${escapeHtml(paragraph)}</p>`).join("")}</div>`
      : "";
    page.className = "document-page";
    page.innerHTML = `<p class="quiet">${escapeHtml(error.message)}</p>${fallback}${renderDiagnostics(material)}`;
  }
}

function setupPagedLazyLoading(page) {
  const list = page.querySelector(".pdf-page-list");
  const loadSheet = (sheet) => {
    const img = sheet.querySelector("img[data-src]");
    const textLayer = sheet.querySelector(".pdf-text-layer[data-text-src]");
    if (img) loadImage(img);
    if (textLayer) loadTextLayer(textLayer);
  };
  if (!("IntersectionObserver" in window)) {
    Array.from(page.querySelectorAll(".pdf-sheet")).slice(0, 8).forEach(loadSheet);
    return;
  }
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      loadSheet(entry.target);
      observer.unobserve(entry.target);
    });
  }, { root: list, rootMargin: "900px 0px", threshold: 0.01 });
  page.querySelectorAll(".pdf-sheet").forEach((sheet) => observer.observe(sheet));
}

function loadImage(img) {
  if (img.dataset.loaded === "true") return;
  img.src = img.dataset.src;
  img.dataset.loaded = "true";
}

async function loadTextLayer(layer) {
  if (layer.dataset.loaded === "true" || layer.dataset.loading === "true") return;
  layer.dataset.loading = "true";
  try {
    const data = await api(layer.dataset.textSrc);
    const words = data.words || [];
    layer.innerHTML = words.map((word) => `
      <span
        class="pdf-text-word"
        data-text="${escapeHtml(word.text)}"
        data-x="${word.x}"
        data-y="${word.y}"
        data-w="${word.w}"
        data-h="${word.h}"
        style="left:${word.x * 100}%;top:${word.y * 100}%;width:${word.w * 100}%;height:${word.h * 100}%;font-size:${Math.max(7, Math.min(28, word.h * 980))}px"
      >${escapeHtml(word.text)} </span>
    `).join("");
    layer.dataset.loaded = "true";
    layer.dataset.empty = words.length ? "false" : "true";
  } catch (_error) {
    layer.dataset.empty = "true";
  } finally {
    layer.dataset.loading = "false";
  }
}

function bindPdfRegionSelection(page) {
  page.querySelectorAll(".pdf-sheet-canvas").forEach((canvas) => {
    canvas.addEventListener("pointerdown", beginTextSelectionFallback);
    canvas.addEventListener("pointerdown", startRegionSelection);
  });
}

function renderPdfAnnotationMarks(material, pageNumber) {
  return annotationsForMaterial(material.id)
    .filter((annotation) => annotation.page === pageNumber && Array.isArray(annotation.rects))
    .flatMap((annotation) => annotation.rects.map((rect) => `
      <div
        class="annotation-mark comment target-${escapeHtml(annotation.target_type || "text")}"
        data-annotation-id="${escapeHtml(annotation.id)}"
        title="${escapeHtml(annotation.body || annotation.selected_text || "")}"
        style="left:${rect.x * 100}%;top:${rect.y * 100}%;width:${rect.w * 100}%;height:${rect.h * 100}%"
      ></div>
    `))
    .join("");
}

function refreshAnnotationViews() {
  if (state.activeMaterial) {
    renderPdfAnnotationLayers(state.activeMaterial);
  }
  renderAnnotationTools();
}

function renderPdfAnnotationLayers(material) {
  document.querySelectorAll(".pdf-sheet").forEach((sheet) => {
    const layer = sheet.querySelector(".annotation-layer");
    const pageNumber = Number(sheet.dataset.page || 0);
    if (layer && pageNumber) layer.innerHTML = renderPdfAnnotationMarks(material, pageNumber);
  });
}

function renderDiagnostics(material) {
  const diagnostics = material.diagnostics || [];
  if (!diagnostics.length) return "";
  return `<ul class="diagnostics">${diagnostics.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`;
}

function renderAnnotationTools() {
  const selected = document.querySelector("#annotationSelection");
  const button = document.querySelector("#markRegionButton");
  const saveButton = document.querySelector("#saveAnnotationButton");
  const cancelButton = document.querySelector("#cancelAnnotationEditButton");
  if (!selected || !button) return;
  const draft = state.annotationDraft;
  const material = state.activeMaterial;
  button.textContent = state.regionMode ? t("cancelRegion") : t("markRegion");
  button.disabled = !material || !canRenderPagedPreview(material);
  button.classList.toggle("active", state.regionMode);
  if (saveButton) saveButton.textContent = state.editingAnnotationId ? t("saveChanges") : t("saveAnnotation");
  cancelButton?.classList.toggle("hidden", !state.editingAnnotationId);
  selected.innerHTML = draftSummaryHtml(draft);
  renderAssistantSelectionChip();
  updateAnnotationControls();
  renderAnnotations("#annotationList", material ? annotationsForMaterial(material.id) : []);
}

function renderAssistantSelectionChip() {
  const chip = document.querySelector("#assistantSelectionChip");
  if (!chip) return;
  const selectedText = state.annotationDraft?.selected_text || "";
  chip.classList.toggle("hidden", !selectedText);
  if (!selectedText) {
    chip.innerHTML = "";
    return;
  }
  chip.innerHTML = `
    <span>${escapeHtml(t("assistantUsingSelection"))}</span>
    <blockquote>${escapeHtml(selectedText.slice(0, 180))}</blockquote>
    <button class="text-button" type="button" data-clear-assistant-selection>${escapeHtml(t("clearAssistantSelection"))}</button>
  `;
}

function draftSummaryHtml(draft) {
  const editHint = state.editingAnnotationId ? `<strong>${escapeHtml(t("editingAnnotation"))}</strong>` : "";
  if (draft.target_type === "region" && draft.page && draft.rects?.length) {
    return `${editHint}<strong>${escapeHtml(format(t("regionReady"), { page: draft.page }))}</strong>`;
  }
  if (draft.selected_text) {
    return `
      ${editHint}
      <strong>${escapeHtml(t("textSelectionReady"))}</strong>
      <blockquote>${escapeHtml(draft.selected_text.slice(0, 280))}</blockquote>
    `;
  }
  return `${editHint}<span>${escapeHtml(t("noSelection"))}</span>`;
}

function renderAnnotations(selector, annotations) {
  const container = document.querySelector(selector);
  if (!container) return;
  container.innerHTML = "";
  if (!annotations.length) {
    container.innerHTML = `<div class="empty">${escapeHtml(t("noAnnotations"))}</div>`;
    return;
  }
  annotations.forEach((annotation) => {
    const item = document.createElement("div");
    item.className = `note-item source annotation-note ${annotation.style || "comment"}`;
    item.dataset.annotationId = annotation.id;
    const page = annotation.page ? `${escapeHtml(format(t("pageLabel"), { page: annotation.page }))} · ` : "";
    item.innerHTML = `
      <div class="note-source">
        <strong>${escapeHtml(page)}${escapeHtml(annotationTypeLabel(annotation))}</strong>
        <small>${escapeHtml(annotation.target_type || "text")}</small>
      </div>
      ${annotation.selected_text ? `<blockquote>${escapeHtml(annotation.selected_text)}</blockquote>` : ""}
      ${annotation.body ? `<p>${escapeHtml(annotation.body)}</p>` : ""}
      <div class="annotation-actions">
        <button type="button" data-annotation-action="locate">${escapeHtml(t("locateAnnotation"))}</button>
        <button type="button" data-annotation-action="edit">${escapeHtml(t("editAnnotation"))}</button>
        <button type="button" data-annotation-action="delete">${escapeHtml(t("deleteAnnotation"))}</button>
      </div>
      <small>${escapeHtml(new Date(annotation.updated_at || annotation.created_at).toLocaleString())}</small>
    `;
    item.querySelector("[data-annotation-action='locate']")?.addEventListener("click", () => locateAnnotation(annotation.id));
    item.querySelector("[data-annotation-action='edit']")?.addEventListener("click", () => editAnnotation(annotation.id));
    item.querySelector("[data-annotation-action='delete']")?.addEventListener("click", () => deleteAnnotation(annotation.id));
    container.append(item);
  });
}

function queueTextSelectionCapture() {
  window.clearTimeout(state.selectionCaptureTimer);
  state.selectionCaptureTimer = window.setTimeout(captureTextSelection, 90);
}

function captureTextSelection() {
  if (!state.activeMaterial || state.regionMode) return false;
  const selection = window.getSelection();
  const text = selection?.toString().trim() || "";
  if (!text) return false;
  const page = document.querySelector("#documentPage");
  if (!selection.rangeCount || !selectionIntersectsNode(selection, page)) return false;
  const range = selection.getRangeAt(0);
  const sheet = closestElement(range.commonAncestorContainer, ".pdf-sheet") || closestElement(selection.anchorNode, ".pdf-sheet") || closestElement(selection.focusNode, ".pdf-sheet");
  const rectInfo = sheet ? selectionRectsForSheet(selection, sheet) : { page: null, rects: [] };
  const selectedText = (rectInfo.selectedText || text).replace(/\s+/g, " ").trim();
  if (!selectedText) return false;
  return commitTextSelectionDraft({
    page: rectInfo.page,
    rects: rectInfo.rects,
    selectedText
  });
}

function commitTextSelectionDraft({ page, rects, selectedText }) {
  const normalizedText = (selectedText || "").replace(/\s+/g, " ").trim();
  if (!state.activeMaterial || !normalizedText) return false;
  const normalizedRects = Array.isArray(rects) ? rects : [];
  const selectionKey = [state.activeMaterial.id, page || "text", normalizedText, JSON.stringify(normalizedRects)].join("|");
  if (selectionKey === state.lastSelectionKey && !state.editingAnnotationId) return false;
  state.lastSelectionKey = selectionKey;
  state.annotationDraft = {
    ...emptyAnnotationDraft(),
    target_type: "text",
    page,
    rects: normalizedRects,
    selected_text: normalizedText.slice(0, 1200),
    style: "comment"
  };
  state.editingAnnotationId = null;
  const input = document.querySelector("#annotationInput");
  if (input) input.value = "";
  renderAnnotationTools();
  setSaveStatus("#annotationSaveStatus", t("saveReady"));
  return true;
}

function beginTextSelectionFallback(event) {
  if (state.regionMode || !state.activeMaterial || event.button !== 0) return;
  const canvas = event.currentTarget;
  const sheet = canvas.closest(".pdf-sheet");
  const pageNumber = Number(sheet?.dataset.page || 0);
  if (!sheet || !pageNumber) return;
  const drag = {
    materialId: state.activeMaterial.id,
    beforeKey: state.lastSelectionKey,
    page: pageNumber,
    sheet,
    canvas,
    start: normalizedPointer(event, canvas)
  };
  state.textSelectionDrag = drag;
  const cleanup = () => {
    document.removeEventListener("pointerup", finish);
    document.removeEventListener("pointercancel", cancel);
    if (state.textSelectionDrag === drag) state.textSelectionDrag = null;
  };
  const finish = (upEvent) => {
    cleanup();
    finishTextSelectionFallback(upEvent, drag);
  };
  const cancel = () => cleanup();
  document.addEventListener("pointerup", finish);
  document.addEventListener("pointercancel", cancel);
}

function finishTextSelectionFallback(event, drag) {
  if (!drag || state.regionMode || !state.activeMaterial || state.activeMaterial.id !== drag.materialId) return;
  const end = normalizedPointer(event, drag.canvas);
  const canvasRect = drag.canvas.getBoundingClientRect();
  const movedX = Math.abs(end.x - drag.start.x) * canvasRect.width;
  const movedY = Math.abs(end.y - drag.start.y) * canvasRect.height;
  if (Math.max(movedX, movedY) < 6) return;
  window.setTimeout(() => {
    const nativeCaptured = captureTextSelection();
    const fallback = textSelectionFromDrag(drag, end);
    if (!fallback) return;
    const currentText = state.annotationDraft?.selected_text || "";
    const currentTooBroad = currentText && fallback.selectedText.length > 8 && currentText.length > fallback.selectedText.length * 3;
    if (!nativeCaptured && state.lastSelectionKey === drag.beforeKey) {
      commitTextSelectionDraft(fallback);
      return;
    }
    if (currentTooBroad) commitTextSelectionDraft(fallback);
  }, 160);
}

function textSelectionFromDrag(drag, end) {
  if (!drag.sheet?.isConnected) return null;
  const rect = paddedTextDragRect(rectFromPoints(drag.start, end));
  if (!rect) return null;
  const words = wordsForSelection(drag.sheet, [rect]);
  if (!words.length) return null;
  return {
    page: drag.page,
    rects: mergeLineRects(words.map((word) => ({ x: word.x, y: word.y, w: word.w, h: word.h }))).slice(0, 16),
    selectedText: words.map((word) => word.text).join(" ")
  };
}

function paddedTextDragRect(rect) {
  if (rect.w <= 0.002 && rect.h <= 0.002) return null;
  const padded = { ...rect };
  if (padded.h < 0.024) {
    const center = padded.y + padded.h / 2;
    padded.y = clamp01(center - 0.012);
    padded.h = Math.min(0.024, 1 - padded.y);
  }
  if (padded.w < 0.006) {
    const center = padded.x + padded.w / 2;
    padded.x = clamp01(center - 0.003);
    padded.w = Math.min(0.006, 1 - padded.x);
  }
  return padded;
}

function closestElement(node, selector) {
  const element = node?.nodeType === Node.ELEMENT_NODE ? node : node?.parentElement;
  return element?.closest?.(selector) || null;
}

function selectionIntersectsNode(selection, node) {
  if (!node) return false;
  for (let index = 0; index < selection.rangeCount; index += 1) {
    const range = selection.getRangeAt(index);
    try {
      if (range.intersectsNode(node)) return true;
    } catch (_error) {
      if (node.contains(range.commonAncestorContainer)) return true;
    }
  }
  return false;
}

function selectionRectsForSheet(selection, sheet) {
  if (!selection.rangeCount) return { page: null, rects: [] };
  const canvas = sheet.querySelector(".pdf-sheet-canvas");
  if (!canvas) return { page: null, rects: [] };
  const canvasRect = canvas.getBoundingClientRect();
  const rawRects = Array.from(selection.getRangeAt(0).getClientRects())
    .map((rect) => {
      const left = Math.max(rect.left, canvasRect.left);
      const top = Math.max(rect.top, canvasRect.top);
      const right = Math.min(rect.right, canvasRect.right);
      const bottom = Math.min(rect.bottom, canvasRect.bottom);
      if (right <= left || bottom <= top) return null;
      return {
        x: (left - canvasRect.left) / canvasRect.width,
        y: (top - canvasRect.top) / canvasRect.height,
        w: (right - left) / canvasRect.width,
        h: (bottom - top) / canvasRect.height
      };
    })
    .filter(Boolean);
  const selectedWords = wordsForSelection(sheet, rawRects);
  const wordRects = selectedWords.map((word) => ({ x: word.x, y: word.y, w: word.w, h: word.h }));
  const rects = mergeLineRects(wordRects.length ? wordRects : rawRects).slice(0, 16);
  return {
    page: Number(sheet.dataset.page || 0) || null,
    rects,
    selectedText: selectedWords.map((word) => word.text).join(" ")
  };
}

function wordsForSelection(sheet, rects) {
  if (!rects.length) return [];
  const expanded = rects.map((rect) => ({
    x: Math.max(0, rect.x - 0.004),
    y: Math.max(0, rect.y - 0.006),
    w: Math.min(1, rect.w + 0.024),
    h: Math.min(1, rect.h + 0.012)
  }));
  const words = Array.from(sheet.querySelectorAll(".pdf-text-word[data-text]"))
    .map((node, index) => ({
      index,
      text: node.dataset.text || "",
      x: Number(node.dataset.x),
      y: Number(node.dataset.y),
      w: Number(node.dataset.w),
      h: Number(node.dataset.h)
    }))
    .filter((word) => word.text && Number.isFinite(word.x) && Number.isFinite(word.y));
  return words
    .filter((word) => expanded.some((rect) => rectOverlapsWord(rect, word)))
    .sort(readingOrderSort);
}

function rectOverlapsWord(rect, word) {
  const wordCenterX = word.x + word.w / 2;
  const wordCenterY = word.y + word.h / 2;
  if (wordCenterX >= rect.x && wordCenterX <= rect.x + rect.w && wordCenterY >= rect.y && wordCenterY <= rect.y + rect.h) {
    return true;
  }
  const overlapX = Math.max(0, Math.min(rect.x + rect.w, word.x + word.w) - Math.max(rect.x, word.x));
  const overlapY = Math.max(0, Math.min(rect.y + rect.h, word.y + word.h) - Math.max(rect.y, word.y));
  const overlapArea = overlapX * overlapY;
  const wordArea = Math.max(0.000001, word.w * word.h);
  return overlapArea / wordArea > 0.22;
}

function readingOrderSort(a, b) {
  const lineTolerance = Math.max(a.h || 0, b.h || 0, 0.012) * 0.75;
  if (Math.abs(a.y - b.y) > lineTolerance) return a.y - b.y;
  return a.x - b.x || a.index - b.index;
}

function mergeLineRects(rects) {
  const sorted = rects.filter(Boolean).sort(readingOrderSort);
  const lines = [];
  sorted.forEach((rect) => {
    const line = lines.find((item) => Math.abs(item.y - rect.y) <= Math.max(item.h, rect.h, 0.012) * 0.75);
    if (!line) {
      lines.push({ ...rect });
      return;
    }
    const right = Math.max(line.x + line.w, rect.x + rect.w);
    const bottom = Math.max(line.y + line.h, rect.y + rect.h);
    line.x = Math.min(line.x, rect.x);
    line.y = Math.min(line.y, rect.y);
    line.w = right - line.x;
    line.h = bottom - line.y;
  });
  return lines.map((rect) => ({
    x: clamp01(rect.x),
    y: clamp01(rect.y),
    w: Math.max(0, Math.min(1 - clamp01(rect.x), rect.w)),
    h: Math.max(0, Math.min(1 - clamp01(rect.y), rect.h))
  }));
}

function toggleRegionMode() {
  if (!state.activeMaterial || !canRenderPagedPreview(state.activeMaterial)) return;
  state.regionMode = !state.regionMode;
  if (!state.regionMode && state.annotationDraft.target_type === "region") {
    state.annotationDraft = emptyAnnotationDraft();
    document.querySelectorAll(".draft-region").forEach((node) => node.remove());
  }
  document.querySelector("#documentPage")?.classList.toggle("region-mode", state.regionMode);
  renderAnnotationTools();
}

function startRegionSelection(event) {
  if (!state.regionMode || !state.activeMaterial || event.button !== 0) return;
  const canvas = event.currentTarget;
  const sheet = canvas.closest(".pdf-sheet");
  const pageNumber = Number(sheet?.dataset.page || 0);
  if (!pageNumber) return;
  event.preventDefault();
  canvas.setPointerCapture(event.pointerId);
  canvas.querySelectorAll(".draft-region").forEach((node) => node.remove());
  const draft = document.createElement("div");
  draft.className = "draft-region";
  canvas.append(draft);
  const start = normalizedPointer(event, canvas);
  const move = (moveEvent) => {
    const current = normalizedPointer(moveEvent, canvas);
    const rect = rectFromPoints(start, current);
    positionRegionNode(draft, rect);
  };
  const finish = (upEvent) => {
    canvas.removeEventListener("pointermove", move);
    canvas.removeEventListener("pointerup", finish);
    canvas.releasePointerCapture(upEvent.pointerId);
    const rect = rectFromPoints(start, normalizedPointer(upEvent, canvas));
    if (rect.w <= 0.01 || rect.h <= 0.01) {
      draft.remove();
      return;
    }
    positionRegionNode(draft, rect);
    state.annotationDraft = {
      ...emptyAnnotationDraft(),
      target_type: "region",
      page: pageNumber,
      rects: [rect],
      style: "comment"
    };
    state.editingAnnotationId = null;
    state.lastSelectionKey = "";
    const input = document.querySelector("#annotationInput");
    if (input) input.value = "";
    state.regionMode = false;
    document.querySelector("#documentPage")?.classList.remove("region-mode");
    renderAnnotationTools();
    setSaveStatus("#annotationSaveStatus", t("saveReady"));
  };
  canvas.addEventListener("pointermove", move);
  canvas.addEventListener("pointerup", finish);
}

function normalizedPointer(event, node) {
  const rect = node.getBoundingClientRect();
  return {
    x: Math.max(0, Math.min(1, (event.clientX - rect.left) / rect.width)),
    y: Math.max(0, Math.min(1, (event.clientY - rect.top) / rect.height))
  };
}

function rectFromPoints(a, b) {
  const x = Math.min(a.x, b.x);
  const y = Math.min(a.y, b.y);
  return {
    x,
    y,
    w: Math.abs(a.x - b.x),
    h: Math.abs(a.y - b.y)
  };
}

function positionRegionNode(node, rect) {
  node.style.left = `${rect.x * 100}%`;
  node.style.top = `${rect.y * 100}%`;
  node.style.width = `${rect.w * 100}%`;
  node.style.height = `${rect.h * 100}%`;
}

async function saveNote() {
  const body = document.querySelector("#noteInput").value.trim();
  if (!activeCourse()) return;
  if (!body && !state.activeNoteId) {
    setSaveStatus("#noteSaveStatus", t("noteEmpty"), "warn");
    return;
  }
  setSaveStatus("#noteSaveStatus", t("saving"));
  try {
    let result;
    let message = t("noteSaved");
    if (!body && state.activeNoteId) {
      result = await api(`/api/notes/${encodeURIComponent(state.activeNoteId)}`, { method: "DELETE" });
      state.activeNoteId = null;
      message = t("noteDeleted");
    } else {
      result = state.activeNoteId
        ? await api(`/api/notes/${encodeURIComponent(state.activeNoteId)}`, {
            method: "PATCH",
            body: { body, language: state.language }
          })
        : await api("/api/notes", {
            method: "POST",
            body: { material_id: state.activeMaterialId, body, language: state.language }
          });
      state.activeNoteId = result.note.id;
    }
    state.workspace = result.workspace;
    renderLearning();
    updateNoteControls();
    setSaveStatus("#noteSaveStatus", message || t("saved"), "success");
  } catch (error) {
    setSaveStatus("#noteSaveStatus", `${t("saveFailed")} ${error.message}`, "warn");
  }
}

async function saveAssistantExchangeAsNote() {
  const exchange = state.lastAssistantExchange;
  if (!exchange?.answerText || !activeCourse()) return;
  setSaveStatus("#assistantSaveStatus", t("saving"));
  try {
    const result = await api("/api/notes", {
      method: "POST",
      body: {
        material_id: state.activeMaterialId || null,
        body: assistantExchangeNoteBody(exchange),
        language: state.language
      }
    });
    state.workspace = result.workspace;
    renderLearning();
    setSaveStatus("#assistantSaveStatus", t("assistantNoteSaved"), "success");
  } catch (error) {
    setSaveStatus("#assistantSaveStatus", `${t("assistantNoteFailed")} ${error.message}`, "warn");
  }
}

function assistantExchangeNoteBody(exchange) {
  const labels = state.language === "zh"
    ? { title: "学习辅助问答", question: "问题", answer: "回答", sources: "来源" }
    : { title: "Study assistant Q&A", question: "Question", answer: "Answer", sources: "Sources" };
  const sources = (exchange.citations || [])
    .map((citation) => `${citation.source_id ? `[${citation.source_id}] ` : ""}${citation.title || ""} - ${sourceMeta(citation)}`)
    .join("\n");
  return [
    labels.title,
    "",
    `${labels.question}: ${exchange.question || ""}`,
    "",
    `${labels.answer}:`,
    exchange.answerText || "",
    "",
    `${labels.sources}:`,
    sources || "-"
  ].join("\n");
}

function updateNoteControls() {
  const button = document.querySelector("#saveNoteButton");
  if (!button) return;
  const body = document.querySelector("#noteInput")?.value.trim() || "";
  button.disabled = !activeCourse() || (!body && !state.activeNoteId);
}

async function saveAnnotation() {
  const material = state.activeMaterial;
  if (!material) return;
  const body = document.querySelector("#annotationInput").value.trim();
  const draft = { ...state.annotationDraft, style: "comment" };
  if (!body && !draft.selected_text && !draft.rects.length) return;
  if (draft.target_type === "region" && !draft.rects.length) return;
  setSaveStatus("#annotationSaveStatus", t("saving"));
  const payload = {
    material_id: material.id,
    target_type: draft.target_type,
    style: "comment",
    page: draft.page,
    rects: draft.rects,
    selected_text: draft.selected_text,
    body,
    language: state.language
  };
  const wasEditing = Boolean(state.editingAnnotationId);
  try {
    const result = wasEditing
      ? await api(`/api/annotations/${encodeURIComponent(state.editingAnnotationId)}`, { method: "PATCH", body: payload })
      : await api("/api/annotations", { method: "POST", body: payload });
    state.workspace = result.workspace;
    state.activeMaterial = {
      ...material,
      annotations: annotationsForMaterial(material.id)
    };
    document.querySelector("#annotationInput").value = "";
    state.annotationDraft = emptyAnnotationDraft();
    state.editingAnnotationId = null;
    state.lastSelectionKey = "";
    document.querySelectorAll(".draft-region").forEach((node) => node.remove());
    refreshAnnotationViews();
    renderLearning();
    setSaveStatus("#annotationSaveStatus", wasEditing ? t("annotationUpdated") : t("annotationSaved"), "success");
  } catch (error) {
    setSaveStatus("#annotationSaveStatus", `${t("saveFailed")} ${error.message}`, "warn");
  }
}

function updateAnnotationControls() {
  const button = document.querySelector("#saveAnnotationButton");
  if (!button) return;
  const draft = state.annotationDraft;
  const hasSource = Boolean(draft.selected_text || draft.rects?.length || state.editingAnnotationId);
  button.disabled = !state.activeMaterial || !hasSource;
}

function cancelAnnotationEdit() {
  state.annotationDraft = emptyAnnotationDraft();
  state.editingAnnotationId = null;
  state.lastSelectionKey = "";
  document.querySelector("#annotationInput").value = "";
  document.querySelectorAll(".draft-region").forEach((node) => node.remove());
  renderAnnotationTools();
  setSaveStatus("#annotationSaveStatus", t("saveReady"));
}

async function editAnnotation(annotationId) {
  const annotation = annotationById(annotationId);
  if (!annotation) return;
  if (annotation.material_id !== state.activeMaterialId) {
    await openMaterial(annotation.material_id);
  }
  beginAnnotationEdit(annotationById(annotationId) || annotation);
}

function beginAnnotationEdit(annotation) {
  state.editingAnnotationId = annotation.id;
  state.regionMode = false;
  state.annotationDraft = {
    target_type: annotation.target_type || "text",
    style: "comment",
    page: annotation.page || null,
    rects: annotation.rects || [],
    selected_text: annotation.selected_text || ""
  };
  state.lastSelectionKey = "";
  document.querySelector("#annotationInput").value = annotation.body || "";
  document.querySelector("#documentPage")?.classList.remove("region-mode");
  renderAnnotationTools();
  setSaveStatus("#annotationSaveStatus", t("saveReady"));
}

async function deleteAnnotation(annotationId) {
  if (!window.confirm(t("confirmDeleteAnnotation"))) return;
  const result = await api(`/api/annotations/${encodeURIComponent(annotationId)}`, { method: "DELETE" });
  state.workspace = result.workspace;
  if (state.activeMaterial) {
    state.activeMaterial = {
      ...state.activeMaterial,
      annotations: annotationsForMaterial(state.activeMaterial.id)
    };
  }
  if (state.editingAnnotationId === annotationId) cancelAnnotationEdit();
  refreshAnnotationViews();
  renderLearning();
  setManagerStatus(t("annotationDeleted"), "success");
}

async function locateAnnotation(annotationId) {
  const annotation = annotationById(annotationId);
  if (!annotation) return;
  if (annotation.material_id !== state.activeMaterialId) {
    await openMaterial(annotation.material_id);
  } else {
    activatePanel("reader");
  }
  window.setTimeout(() => scrollAnnotationIntoView(annotationId), 120);
}

function scrollAnnotationIntoView(annotationId) {
  const annotation = annotationById(annotationId);
  if (!annotation) return;
  const page = annotation.page ? document.querySelector(`.pdf-sheet[data-page="${annotation.page}"]`) : document.querySelector("#documentPage");
  page?.scrollIntoView({ block: "center", behavior: "smooth" });
  document.querySelectorAll(".annotation-mark.active").forEach((node) => node.classList.remove("active"));
  document.querySelectorAll(`.annotation-mark[data-annotation-id="${CSS.escape(annotationId)}"]`).forEach((node) => {
    node.classList.add("active");
    window.setTimeout(() => node.classList.remove("active"), 1800);
  });
}

async function refreshNotebookLMStatus() {
  const card = document.querySelector("#notebooklmCard");
  if (!card) return;
  card.className = "assistant-card loading";
  card.innerHTML = `<small>${escapeHtml(t("notebooklmStatusTitle"))}</small><p>${escapeHtml(t("notebooklmChecking"))}</p>`;
  try {
    renderNotebookLMStatus(await api("/api/notebooklm/status"));
  } catch (error) {
    card.className = "assistant-card warn";
    card.innerHTML = `<small>${escapeHtml(t("notebooklmStatusTitle"))}</small><p>${escapeHtml(error.message)}</p>`;
  }
}

function renderNotebookLMStatus(status) {
  const card = document.querySelector("#notebooklmCard");
  if (!card) return;
  const notebook = status.notebook || {};
  const sourceCount = Number(notebook.source_count || Object.keys(notebook.sources || {}).length || 0);
  let tone = "";
  let message = t("notebooklmReady");
  if (!status.installed || !status.cli) {
    tone = "warn";
    message = t("notebooklmPackageMissing");
  } else if (!status.authenticated) {
    tone = "warn";
    message = `${t("notebooklmNeedsAuth")} NOTEBOOKLM_HOME=${status.home || ""}`;
  } else if (notebook.notebook_id) {
    message = t("notebooklmSynced").replace("{count}", String(sourceCount));
  }
  const notebookUrl = notebook.notebook_id ? `https://notebooklm.google.com/notebook/${encodeURIComponent(notebook.notebook_id)}` : "";
  card.className = `assistant-card ${tone}`.trim();
  card.innerHTML = `
    <small>${escapeHtml(t("notebooklmStatusTitle"))}</small>
    <p>${escapeHtml(message)}</p>
    ${notebook.title ? `<p><strong>${escapeHtml(notebook.title)}</strong></p>` : ""}
    ${notebookUrl ? `<p><a href="${escapeHtml(notebookUrl)}" target="_blank" rel="noreferrer">${escapeHtml(notebookUrl)}</a></p>` : ""}
  `;
}

async function syncNotebookLM() {
  const card = document.querySelector("#notebooklmCard");
  if (card) {
    card.className = "assistant-card loading";
    card.innerHTML = `<small>${escapeHtml(t("notebooklmStatusTitle"))}</small><p>${escapeHtml(t("notebooklmSyncing"))}</p>`;
  }
  try {
    const result = await api("/api/notebooklm/sync", { method: "POST", body: { wait: false } });
    state.workspace = await api("/api/workspace");
    const uploaded = result.uploaded?.length || 0;
    const skipped = result.skipped?.length || 0;
    const failed = result.failed?.length || 0;
    if (card) {
      card.className = failed ? "assistant-card warn" : "assistant-card";
      card.innerHTML = `
        <small>${escapeHtml(t("notebooklmStatusTitle"))}</small>
        <p>${escapeHtml(format(t("notebooklmSyncDone"), { uploaded, skipped, failed }))}</p>
      `;
    }
  } catch (error) {
    if (card) {
      card.className = "assistant-card warn";
      card.innerHTML = `<small>${escapeHtml(t("notebooklmStatusTitle"))}</small><p>${escapeHtml(error.message)}</p>`;
    }
  }
}

async function askNotebookLM() {
  const input = document.querySelector("#notebooklmQuestion");
  const answerBox = document.querySelector("#notebooklmAnswer");
  const question = String(input?.value || "").trim();
  if (!question || !answerBox) return;
  answerBox.className = "assistant-card loading";
  answerBox.innerHTML = `<small>${escapeHtml(t("notebooklmAnswerTitle"))}</small><p>${escapeHtml(t("notebooklmAsking"))}</p>`;
  try {
    const result = await api("/api/notebooklm/ask", { method: "POST", body: { question } });
    answerBox.className = "assistant-card";
    answerBox.innerHTML = `
      <small>${escapeHtml(t("notebooklmAnswerTitle"))}</small>
      <div class="assistant-answer">${renderAssistantMarkdown(String(result.answer || ""), new Map())}</div>
    `;
  } catch (error) {
    answerBox.className = "assistant-card warn";
    answerBox.innerHTML = `<small>${escapeHtml(t("notebooklmAnswerTitle"))}</small><p>${escapeHtml(t("notebooklmAskFailed"))} ${escapeHtml(error.message)}</p>`;
  }
}

async function askMaterials(action = "ask", questionOverride = null, scopeOverride = null) {
  const questionInput = document.querySelector("#question");
  const question = String(questionOverride ?? questionInput?.value ?? "").trim();
  if (!question) return;
  if (questionOverride !== null && questionInput) questionInput.value = "";
  renderAssistantMessage(t("asking"), "loading");
  const scope = scopeOverride || document.querySelector("input[name='askScope']:checked")?.value || "course";
  try {
    const result = await api("/api/ask-materials", {
      method: "POST",
      body: assistantRequestPayload({ question, scope, action })
    });
    renderAnswer(result, { question, scope, action });
    if (questionOverride === null && questionInput) questionInput.value = "";
  } catch (error) {
    renderAssistantMessage(error.message, "error");
  }
}

async function askLegacyMaterials(action = "ask", questionOverride = null) {
  return askMaterials(action, questionOverride);
}

function assistantQuestionForAction(action) {
  const key = `${action}Prompt`;
  return t(key);
}

function assistantRequestPayload({ question, scope, action }) {
  const provider = state.assistantProvider || state.workspace.settings?.api_provider || "local";
  const preset = API_PROVIDER_PRESETS[provider] || API_PROVIDER_PRESETS.local;
  return {
    question,
    scope,
    action,
    material_id: state.activeMaterialId,
    language: state.language,
    selected_text: state.annotationDraft?.selected_text || "",
    selected_page: state.annotationDraft?.page || null,
    note_body: document.querySelector("#noteInput")?.value.trim() || "",
    annotation_body: document.querySelector("#annotationInput")?.value.trim() || "",
    api_provider: provider,
    api_key: provider === "local" ? "" : state.assistantApiKey,
    api_model: state.assistantModel || state.workspace.settings?.api_model || preset.models[0] || "",
    api_base_url: state.assistantBaseUrl || state.workspace.settings?.api_base_url || preset.baseUrl || "",
    include_notes: false
  };
}

async function testAssistantApi() {
  const provider = state.assistantProvider || state.workspace.settings?.api_provider || "local";
  const preset = API_PROVIDER_PRESETS[provider] || API_PROVIDER_PRESETS.local;
  setApiTestStatus(t("apiTesting"), "active");
  try {
    const result = await api("/api/assistant/test-provider", {
      method: "POST",
      body: {
        language: state.language,
        api_provider: provider,
        api_key: provider === "local" ? "" : state.assistantApiKey,
        api_model: state.assistantModel || preset.models[0] || "",
        api_base_url: state.assistantBaseUrl || preset.baseUrl || ""
      }
    });
    const tone = result.status === "ok" ? "success" : result.status === "config_required" ? "warn" : "error";
    setApiTestStatus(result.answer || assistantStatusLabel(result.status), tone);
  } catch (error) {
    setApiTestStatus(error.message, "error");
  }
}

function renderNotes(selector, notes, compact, filteredByMaterial = false) {
  const container = document.querySelector(selector);
  container.innerHTML = "";
  if (!notes.length) {
    container.innerHTML = `<div class="empty">${escapeHtml(filteredByMaterial ? t("noNotesForMaterial") : t("noNotes"))}</div>`;
    return;
  }
  notes.forEach((note) => {
    const material = materialById(note.material_id);
    const item = document.createElement("div");
    const isAnnotation = note.type === "annotation";
    item.className = isAnnotation ? `note-item source annotation-note ${note.style || "comment"}` : "note-item student";
    const page = isAnnotation && note.page ? `${format(t("pageLabel"), { page: note.page })} · ` : "";
    item.innerHTML = isAnnotation
      ? `
        <div class="note-source">
          <strong>${escapeHtml(material?.title || t("learningNotesTitle"))}</strong>
          <small>${escapeHtml(page)}${escapeHtml(annotationTypeLabel(note))} · ${escapeHtml(material?.relative_path || "")}</small>
        </div>
        ${note.selected_text ? `<blockquote>${escapeHtml(compact ? note.selected_text.slice(0, 180) : note.selected_text)}</blockquote>` : ""}
        ${note.body ? `<p>${escapeHtml(compact ? note.body.slice(0, 180) : note.body)}</p>` : ""}
        <small>${escapeHtml(new Date(note.created_at).toLocaleString())}</small>
      `
      : `
        <div class="note-source">
          <strong>${escapeHtml(material?.title || t("learningNotesTitle"))}</strong>
          <small>${escapeHtml(t("sourceFileLabel"))}: ${escapeHtml(material?.relative_path || "")}</small>
        </div>
        <p>${escapeHtml(compact ? note.body.slice(0, 180) : note.body)}</p>
        <small>${escapeHtml(new Date(note.created_at).toLocaleString())}</small>
      `;
    container.append(item);
  });
}

function notesForCurrentScope() {
  const items = allLearningItems();
  if (state.noteScope.type === "material") {
    return items.filter((note) => note.material_id === state.noteScope.id);
  }
  if (state.noteScope.type === "unit") {
    const ids = new Set(materialsForUnit(state.noteScope.id).map((material) => material.id));
    return items.filter((note) => ids.has(note.material_id));
  }
  return items;
}

function allLearningItems() {
  const notes = (state.workspace.notes || []).filter((item) => item.type !== "assistant_note" && !isAssistantGeneratedNote(item));
  return [...notes, ...(state.workspace.annotations || [])].sort((a, b) => {
    return String(b.created_at || "").localeCompare(String(a.created_at || ""));
  });
}

function scopeTitleForNotes() {
  if (state.noteScope.type === "material") {
    const material = materialById(state.noteScope.id);
    return material ? format(t("materialNotesTitle"), { title: material.title }) : t("allNotesTitle");
  }
  if (state.noteScope.type === "unit") {
    const group = materialGroups().find((item) => item.id === state.noteScope.id);
    return group ? format(t("unitNotesTitle"), { title: group.name }) : t("allNotesTitle");
  }
  return t("allNotesTitle");
}

function materialGroups() {
  const course = activeCourse();
  const units = course?.units || [];
  const groups = units.map((unit) => ({ id: unit.id, name: unit.name, folderName: unit.folder_name, materials: [] }));
  const unassigned = { id: "unassigned", name: t("unassignedUnit"), folderName: "", materials: [] };
  state.workspace.materials.forEach((material) => {
    const firstPart = material.relative_path.split(/[\\/]/)[0];
    const group = groups.find((item) => item.folderName === firstPart);
    (group || unassigned).materials.push(material);
  });
  return [...groups.filter((group) => group.materials.length || group.id === state.noteScope.id), ...(unassigned.materials.length ? [unassigned] : [])];
}

function materialsForUnit(unitId) {
  const group = materialGroups().find((item) => item.id === unitId);
  return group?.materials || [];
}

function renderAnswer(result, request = {}) {
  const citations = result.citations || [];
  const tone = result.status === "ok" ? "" : ["refused", "not_found", "config_required"].includes(result.status) ? "warn" : "error";
  const citationHtml = citations.length ? renderCitationGroups(citations) : "";
  const answerText = extractAssistantAnswerText(result.answer);
  const canSave = Boolean(answerText && activeCourse() && result.status === "ok");
  state.lastAssistantExchange = canSave ? { ...request, answerText, citations } : null;
  const card = document.querySelector("#assistantCard");
  card.className = `assistant-card ${tone}`.trim();
  card.innerHTML = `
    <div class="assistant-result-head">
      <small>${escapeHtml(assistantStatusLabel(result.status))}</small>
      ${canSave ? `<button class="text-button" type="button" data-assistant-save-note>${escapeHtml(t("saveAssistantNote"))}</button>` : ""}
    </div>
    ${result.warning ? `<div class="assistant-warning"><strong>${escapeHtml(t("assistantWarning"))}</strong><span>${escapeHtml(result.warning)}</span></div>` : ""}
    <div class="assistant-answer">${renderAnswerBody(answerText, citations)}</div>
    ${citationHtml}
    <div class="save-status assistant-save-status" id="assistantSaveStatus"></div>
  `;
}

function renderCitationGroups(citations) {
  const course = citations.filter((citation) => citation.source_group !== "web" && citation.source_type !== "web");
  const web = citations.filter((citation) => citation.source_group === "web" || citation.source_type === "web");
  return [
    course.length ? citationGroupHtml(t("courseCitations"), course) : "",
    web.length ? citationGroupHtml(t("webCitations"), web) : ""
  ].join("");
}

function citationGroupHtml(title, citations) {
  return `<details class="citation-group"><summary>${escapeHtml(format(t("citationGroupToggle"), { title, count: citations.length }))}</summary><ol>${citations.map((citation) => `
    <li id="citation-${escapeHtml(citation.source_id || "")}" data-citation-id="${escapeHtml(citation.source_id || "")}">
      <strong>${escapeHtml(citation.source_id ? `[${citation.source_id}] ${citation.title}` : citation.title)}</strong>
      <small>${escapeHtml(sourceMeta(citation))}</small>
      <blockquote>${escapeHtml(citation.quote)}</blockquote>
    </li>
  `).join("")}</ol></details>`;
}

function renderAnswerBody(answer, citations) {
  const sourceMap = new Map(citations.map((citation) => [citation.source_id, citation]));
  return renderAssistantMarkdown(extractAssistantAnswerText(answer), sourceMap);
}

function normalizeAssistantDisplayText(answer) {
  return extractAssistantAnswerText(answer);
}

function extractAssistantAnswerText(value) {
  if (value && typeof value === "object") {
    return extractAssistantAnswerText(value.answer ?? value.content ?? value.message ?? value.text ?? "");
  }
  let text = stripMarkdownFence(String(value || "").trim());
  const parsed = parseAssistantJsonText(text);
  if (parsed && typeof parsed === "object") {
    const nested = parsed.answer ?? parsed.content ?? parsed.message ?? parsed.text;
    if (nested !== undefined) return extractAssistantAnswerText(nested);
  }
  const answerField = extractAnswerFieldFromJsonishText(text);
  if (answerField) text = answerField;
  text = text.replaceAll("\\n", "\n").replaceAll('\\"', '"').replaceAll("\\/", "/");
  return stripMarkdownFence(text);
}

function stripMarkdownFence(text) {
  return String(text || "")
    .replace(/^```(?:json|markdown|md)?\s*/i, "")
    .replace(/\s*```$/i, "")
    .trim();
}

function parseAssistantJsonText(text) {
  const clean = String(text || "").trim();
  const candidates = [clean, firstBalancedJsonText(clean)].filter(Boolean);
  for (const candidate of candidates) {
    try {
      return JSON.parse(candidate);
    } catch (_error) {
      // Try the next candidate or the regex fallback.
    }
  }
  return null;
}

function firstBalancedJsonText(text) {
  const start = String(text || "").indexOf("{");
  if (start < 0) return "";
  let depth = 0;
  let inString = false;
  let escaped = false;
  for (let index = start; index < text.length; index += 1) {
    const char = text[index];
    if (inString) {
      if (escaped) escaped = false;
      else if (char === "\\") escaped = true;
      else if (char === "\"") inString = false;
      continue;
    }
    if (char === "\"") inString = true;
    else if (char === "{") depth += 1;
    else if (char === "}") {
      depth -= 1;
      if (depth === 0) return text.slice(start, index + 1);
    }
  }
  return "";
}

function extractAnswerFieldFromJsonishText(text) {
  const clean = String(text || "");
  if (!clean.trim().startsWith("{") || !clean.includes("\"answer\"")) return "";
  const match = clean.match(/"answer"\s*:\s*"((?:\\.|[^"\\])*)"/s);
  if (!match) return "";
  try {
    return JSON.parse(`"${match[1]}"`);
  } catch (_error) {
    return match[1].replaceAll("\\n", "\n").replaceAll('\\"', '"').replaceAll("\\/", "/");
  }
}

function renderAssistantMarkdown(text, sourceMap) {
  const lines = stripMarkdownFence(text).split(/\n+/);
  const html = [];
  let listType = "";
  const closeList = () => {
    if (listType) {
      html.push(`</${listType}>`);
      listType = "";
    }
  };
  lines.forEach((rawLine) => {
    const line = rawLine.trim();
    if (!line) {
      closeList();
      return;
    }
    const numbered = line.match(/^\d+[.、]\s+(.+)$/);
    const bullet = line.match(/^[-*]\s+(.+)$/);
    if (numbered) {
      if (listType !== "ol") {
        closeList();
        html.push("<ol>");
        listType = "ol";
      }
      html.push(`<li>${renderAssistantInline(numbered[1], sourceMap)}</li>`);
      return;
    }
    if (bullet) {
      if (listType !== "ul") {
        closeList();
        html.push("<ul>");
        listType = "ul";
      }
      html.push(`<li>${renderAssistantInline(bullet[1], sourceMap)}</li>`);
      return;
    }
    closeList();
    html.push(`<p>${renderAssistantInline(line.replace(/^#{1,4}\s+/, ""), sourceMap)}</p>`);
  });
  closeList();
  return html.join("");
}

function renderAssistantInline(text, sourceMap) {
  const parts = String(text || "").split(/(\[(?:C|W)\d+\])/g);
  return parts
    .map((part) => {
      const match = part.match(/^\[((?:C|W)\d+)\]$/);
      if (!match) return renderSimpleMarkdownInline(part);
      const sourceId = match[1];
      const citation = sourceMap.get(sourceId);
      if (!citation) return escapeHtml(part);
      const preview = sourceBadgePreview(citation);
      return `<button class="source-badge" type="button" data-source-id="${escapeHtml(sourceId)}" data-preview="${escapeHtml(preview)}" title="${escapeHtml(preview)}">${escapeHtml(sourceId)}</button>`;
    })
    .join("");
}

function renderSimpleMarkdownInline(text) {
  return escapeHtml(text)
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/__(.+?)__/g, "<strong>$1</strong>")
    .replace(/`([^`]+)`/g, "<code>$1</code>");
}

function sourceBadgePreview(citation) {
  const quote = String(citation.quote || "").slice(0, 220);
  return `${citation.source_id ? `[${citation.source_id}] ` : ""}${citation.title || ""}\n${sourceMeta(citation)}\n${quote}`;
}

function focusCitation(sourceId) {
  if (!sourceId) return;
  const item = document.querySelector(`#citation-${CSS.escape(sourceId)}`);
  if (!item) return;
  const group = item.closest("details");
  if (group) group.open = true;
  item.scrollIntoView({ block: "nearest", behavior: "smooth" });
  item.classList.add("active");
  window.setTimeout(() => item.classList.remove("active"), 1600);
}

function sourceMeta(citation) {
  const path = citation.url || citation.relative_path;
  const parts = [citation.source_id ? `[${citation.source_id}]` : "", sourceTypeLabel(citation.source_type), path];
  const location = citation.locator || (citation.page ? format(t("pageLabel"), { page: citation.page }) : "");
  if (location) parts.push(`${t("sourceLocatorLabel")}: ${location}`);
  return parts.filter(Boolean).join(" · ");
}

function sourceTypeLabel(sourceType) {
  const labels = {
    material: t("sourceTypeMaterial"),
    web: t("sourceTypeWeb"),
    selection: t("sourceTypeSelection"),
    reading_note: t("sourceTypeReadingNote"),
    annotation: t("sourceTypeAnnotation"),
    current_note: t("sourceTypeCurrentNote"),
    current_annotation: t("sourceTypeCurrentAnnotation")
  };
  return labels[sourceType] || t("sourceTypeMaterial");
}

function assistantStatusLabel(status) {
  if (status === "not_found") return t("assistantUnable");
  if (status === "refused") return t("assistantRefused");
  if (status === "config_required") return t("assistantConfigRequired");
  return t("sourceGrounded");
}

function renderAssistantMessage(message, tone = "") {
  const card = document.querySelector("#assistantCard");
  if (!card) return;
  card.className = `assistant-card ${tone}`.trim();
  card.innerHTML = `<small>${escapeHtml(t("askMaterialsTitle"))}</small><p>${escapeHtml(message)}</p>`;
}

function showView(name) {
  document.querySelector("#dashboardView").classList.toggle("hidden", name !== "dashboard");
  document.querySelector("#fileManagerView").classList.toggle("hidden", name !== "manager");
  document.querySelector("#settingsView").classList.toggle("hidden", name !== "settings");
  document.querySelector("#learningView").classList.toggle("hidden", name !== "learning");
  syncSidebarState();
}

function activatePanel(target) {
  tabs.forEach((item) => item.classList.toggle("active", item.dataset.panel === target));
  panels.forEach((panel) => panel.classList.toggle("active", panel.id === target));
  if (target === "home") setSidebarCollapsed(false);
  if (target === "reader" && state.autoHideSidebar) setSidebarCollapsed(true);
}

function setLanguage(language) {
  const normalized = language === "zh" ? "zh" : "en";
  state.language = normalized;
  localStorage.setItem("clw.language", normalized);
  document.documentElement.lang = normalized === "zh" ? "zh-CN" : "en";
  document.title = t("pageTitle");
  const languageSelect = document.querySelector("#languageSelect");
  if (languageSelect) languageSelect.value = normalized;
  document.querySelectorAll("[data-i18n]").forEach((node) => {
    node.textContent = t(node.dataset.i18n);
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((node) => {
    node.setAttribute("placeholder", t(node.dataset.i18nPlaceholder));
  });
  syncSidebarState();
  renderAll();
}

function setSidebarCollapsed(collapsed) {
  state.sidebarCollapsed = Boolean(collapsed);
  localStorage.setItem("clw.sidebarCollapsed", String(state.sidebarCollapsed));
  syncSidebarState();
}

function syncSidebarState() {
  const learningView = document.querySelector("#learningView");
  const button = document.querySelector("#sidebarToggleButton");
  learningView?.classList.toggle("sidebar-collapsed", state.sidebarCollapsed);
  if (!button) return;
  const label = state.sidebarCollapsed ? t("showSidebarTitle") : t("hideSidebarTitle");
  button.setAttribute("aria-label", label);
  button.setAttribute("title", label);
  button.setAttribute("aria-pressed", String(state.sidebarCollapsed));
  button.classList.toggle("active", state.sidebarCollapsed);
  const settingsButton = document.querySelector("#learningSettingsButton");
  settingsButton?.setAttribute("aria-label", t("openSettingsTitle"));
  settingsButton?.setAttribute("title", t("openSettingsTitle"));
}

function setManagerStatus(message, tone = "") {
  const box = document.querySelector("#managerStatus");
  if (!box) return;
  box.className = `status-box ${tone}`;
  box.textContent = message;
}

function setApiTestStatus(message, tone = "") {
  const box = document.querySelector("#apiTestStatus");
  if (!box) return;
  box.className = `status-box ${tone}`;
  box.textContent = message;
}

function activeCourse() {
  return state.workspace.course;
}

function materialById(materialId) {
  return state.workspace.materials.find((item) => item.id === materialId);
}

function annotationsForMaterial(materialId) {
  return (state.workspace.annotations || []).filter((item) => item.material_id === materialId);
}

function annotationById(annotationId) {
  return (state.workspace.annotations || []).find((item) => item.id === annotationId);
}

function latestReadingNoteForMaterial(materialId) {
  return (state.workspace.notes || [])
    .filter((item) => item.type !== "annotation" && item.type !== "assistant_note" && item.material_id === materialId && !isAssistantGeneratedNote(item))
    .sort((a, b) => String(b.updated_at || b.created_at || "").localeCompare(String(a.updated_at || a.created_at || "")))[0];
}

function isAssistantGeneratedNote(note) {
  const body = String(note?.body || "").trimStart();
  return body.startsWith("AI 学习辅助") || body.startsWith("AI Study Assistant");
}

function canRenderPagedPreview(material) {
  return ["pdf", "docx", "pptx", "xlsx"].includes(material?.kind);
}

function emptyAnnotationDraft() {
  return { target_type: "text", style: "comment", page: null, rects: [], selected_text: "" };
}

function annotationTypeLabel(annotation) {
  return annotation?.target_type === "region" || annotation?.target_type === "image" ? t("styleRegion") : t("styleComment");
}

function styleLabel(style) {
  const labels = {
    comment: t("styleComment"),
    highlight: t("styleComment"),
    underline: t("styleComment"),
    strike: t("styleComment")
  };
  return labels[style] || labels.comment;
}

function safeMaterialTextFallback(material) {
  const text = material?.text || "";
  if (!text.trim()) return "";
  const diagnostics = (material.diagnostics || []).join(" ");
  const locators = (material.locators || []).join(" ");
  const looksLikePdfInternals = /\/Type\s*\/Pages|\/Kids\s*\[|endobj|\/MarkInfo|xref table/i.test(text.slice(0, 6000));
  const knownBadFallback = /pdf fallback/i.test(locators) || /fallback PDF text extraction|PDF text extraction failed|Couldn't read xref table/i.test(diagnostics);
  return looksLikePdfInternals || knownBadFallback ? "" : text;
}

function initialLanguage() {
  const saved = localStorage.getItem("clw.language");
  if (saved) return saved;
  return navigator.language && navigator.language.toLowerCase().startsWith("zh") ? "zh" : "en";
}

function initialBooleanSetting(key, fallback) {
  const saved = localStorage.getItem(key);
  if (saved === "true") return true;
  if (saved === "false") return false;
  return fallback;
}

function initialTextSetting(key, fallback) {
  const saved = localStorage.getItem(key);
  return saved === null ? fallback : saved;
}

function clamp01(value) {
  return Math.max(0, Math.min(1, Number(value) || 0));
}

function setSaveStatus(selector, message, tone = "") {
  const node = document.querySelector(selector);
  if (!node) return;
  node.textContent = message;
  node.className = `save-status ${tone}`;
}

function t(key) {
  return translations[state.language]?.[key] || translations.en[key] || key;
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    method: options.method || "GET",
    headers: { "Content-Type": "application/json" },
    body: options.body ? JSON.stringify(options.body) : undefined
  });
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.error || response.statusText);
  return payload;
}

async function apiForm(path, form) {
  const response = await fetch(path, { method: "POST", body: form });
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.error || response.statusText);
  return payload;
}

function format(template, values) {
  return template.replace(/\{(\w+)\}/g, (_match, key) => values[key] ?? "");
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
