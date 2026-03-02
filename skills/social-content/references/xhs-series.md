# 小红书多图系列生成指南

当小红书笔记需要生成多张配图（6-9 张图的多图笔记）时，参照本指南的风格、布局和工作流。

---

## 10 种视觉风格

每种风格定义了配色、装饰元素和整体视觉方向。通过 `--style-preset` 或 `--palette`+`--rendering`+`--mood` 组合实现。

| 风格 | 描述 | 脚本参数映射 | 适用内容 |
|------|------|-------------|----------|
| `cute` | 甜美可爱，经典小红书少女风 | `--style-preset kawaii` | 美妆、穿搭、甜品、少女心 |
| `fresh` | 清新自然，干净透亮 | `--palette cool --rendering flat-vector --mood balanced` | 健康、有机、户外、清爽场景 |
| `warm` | 温暖舒适，有亲和力 | `--style-preset cozy` | 生活分享、美食、家居、情感 |
| `bold` | 高冲击力，抢眼夺目 | `--style-preset pop-art` | 重要提醒、避坑、对比测评 |
| `minimal` | 极简精致，高级感 | `--palette mono --rendering flat-vector --mood subtle` | 商务、效率工具、高端产品 |
| `retro` | 复古怀旧，文艺潮流 | `--style-preset vintage` | 咖啡店、古着、胶片风、怀旧 |
| `pop` | 活力四射，视觉跳跃 | `--palette vivid --rendering flat-vector --mood bold` | 派对、旅行、网红打卡 |
| `notion` | 极简手绘线条，知识感 | `--style-preset notion` | 干货、SaaS、生产力、知识卡片 |
| `chalkboard` | 彩色粉笔黑板风 | `--style-preset blueprint` | 教程、学习笔记、科普 |
| `study-notes` | 手写笔记风，蓝笔+红批注 | `--palette earth --rendering hand-drawn --mood balanced` | 学习攻略、知识总结、手帐 |

## 8 种信息布局

布局控制每张图片内的信息结构。通过 `--layout` 参数指定（仅 `--type guide` 有效），或在 prompt 中描述。

| 布局 | 描述 | 信息密度 | 适用场景 |
|------|------|----------|----------|
| `sparse` | 极简布局，1-2 个要点，最大视觉冲击 | 低 | 封面、ending、金句、单品展示 |
| `balanced` | 标准布局，3-4 个要点，信息与美感均衡 | 中 | 常规内容页、产品介绍、体验分享 |
| `dense` | 高密度，5-8 个要点，知识卡片风格 | 高 | 干货总结、攻略清单、对比评测 |
| `list` | 列表/排名式，4-7 项纵向排列 | 中高 | TOP N、推荐清单、步骤列表 |
| `comparison` | 双栏对比，并排展示两个选项 | 中 | A vs B、优缺点、前后对比 |
| `flow` | 流程/时间线，3-6 步有方向性连接 | 中 | 步骤教程、行程路线、使用流程 |
| `mindmap` | 中心辐射，4-8 个分支 | 中高 | 知识框架、思维导图、体系梳理 |
| `quadrant` | 四象限/环形分区 | 中 | 分类对比、矩阵分析 |

## Style × Layout 兼容矩阵

推荐组合用 ++ 表示，可用组合用 + 表示。

| | sparse | balanced | dense | list | comparison | flow | mindmap | quadrant |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| cute | ++ | ++ | + | ++ | + | + | + | + |
| fresh | ++ | ++ | + | + | + | ++ | + | + |
| warm | ++ | ++ | + | + | ++ | + | + | + |
| bold | ++ | + | + | ++ | ++ | + | + | ++ |
| minimal | ++ | ++ | ++ | + | + | + | + | + |
| retro | ++ | ++ | + | ++ | + | + | + | + |
| pop | ++ | ++ | + | ++ | ++ | + | + | + |
| notion | ++ | ++ | ++ | ++ | ++ | ++ | ++ | ++ |
| chalkboard | ++ | ++ | ++ | ++ | + | ++ | ++ | + |
| study-notes | — | + | ++ | ++ | + | + | ++ | + |

---

## 3 种大纲策略

多图笔记的内容编排策略，决定了每张图片的角色和叙事线。

### Strategy A: 故事驱动型

| 要素 | 说明 |
|------|------|
| **理念** | 以个人经历为主线，情感共鸣优先 |
| **特征** | 从痛点出发，展示前后变化，强真实感 |
| **适用** | 体验分享、种草测评、个人成长、旅行日记 |
| **推荐风格** | warm, cute, fresh |
| **推荐图数** | 4-6 张 |

典型结构：
```
P1 (封面)：Hook + 视觉冲击 → sparse
P2：痛点/问题 → balanced
P3：发现/转折 → balanced
P4：体验/细节 → balanced/dense
P5：效果/成果 → balanced
P6 (ending)：CTA + 总结 → sparse
```

### Strategy B: 信息密集型

| 要素 | 说明 |
|------|------|
| **理念** | 价值优先，高效传递信息 |
| **特征** | 结构清晰、要点明确、专业可信 |
| **适用** | 教程、对比评测、产品推荐、知识清单 |
| **推荐风格** | notion, minimal, chalkboard |
| **推荐图数** | 3-5 张 |

典型结构：
```
P1 (封面)：核心结论 + Hook → sparse
P2：信息卡片/核心数据 → dense/list
P3：优缺点/对比 → comparison/list
P4：推荐建议 → balanced
P5 (ending)：总结 + CTA → sparse
```

### Strategy C: 视觉优先型

| 要素 | 说明 |
|------|------|
| **理念** | 视觉冲击为核心，文字极简 |
| **特征** | 大图为主、氛围感强、即时吸引力 |
| **适用** | 高颜值产品、旅行风景、生活美学、mood 类 |
| **推荐风格** | bold, pop, retro |
| **推荐图数** | 3-4 张 |

典型结构：
```
P1 (封面)：Hero image + 大字标题 → sparse
P2：细节/特写 → sparse/balanced
P3：场景/生活方式 → sparse
P4 (ending)：CTA → sparse
```

---

## 多图系列工作流

### 生成步骤

1. **分析内容**：根据文案内容判断适用的大纲策略（A/B/C）
2. **确认方案**：向用户展示推荐的策略、风格和图片数量，确认后执行
3. **制定大纲**：按选定策略为每张图写出内容大纲（角色 + 要点 + 布局）
4. **生成封面（P1）**：首先生成第 1 张图，作为视觉锚点
5. **生成后续图片**：后续每张图在 prompt 中描述与 P1 一致的视觉元素，保持风格统一
6. **展示结果**：按 SKILL.md Workflow 2 步骤 6 的格式展示每张图片

### 视觉一致性保持

多图系列中最重要的是风格统一。具体方法：

1. **所有图片使用相同的 `--style-preset` 或 `--palette`+`--rendering`+`--mood` 组合**
2. **在后续图片的 prompt 中引用 P1 的视觉特征**：
   - 提及 P1 使用的配色方案
   - 提及 P1 的装饰元素风格（如圆角卡片、手绘线条等）
   - 提及 P1 的背景处理方式
3. **保持统一的排版元素**：字体风格、标题位置、边距比例

### Prompt 模板

**封面（P1）：**
```
--type xiaohongshu --style-preset [preset] --prompt "[场景描述], cover image for a Xiaohongshu post, eye-catching title area at [top/center], [风格关键词]"
```

**内容页（P2-Pn）：**
```
--type xiaohongshu --style-preset [preset] --prompt "[内容描述], matching the visual style of the cover: [P1 的颜色/装饰/背景特征], [布局描述]"
```

**Ending（最后一张）：**
```
--type xiaohongshu --style-preset [preset] --prompt "call-to-action ending card, [品牌/互动引导], matching the visual style of the cover: [P1 特征], clean and minimal"
```

### 自动风格推荐

根据内容信号自动推荐风格和策略：

| 内容信号关键词 | 推荐风格 | 推荐策略 | 推荐布局 |
|--------------|----------|----------|----------|
| 美妆、穿搭、少女、粉色 | cute | A | sparse/balanced |
| 健康、自然、清爽、有机 | fresh | A/B | balanced/flow |
| 生活、故事、情感、温暖 | warm | A | balanced |
| 警告、避坑、重要、必看 | bold | B | list/comparison |
| 专业、商务、简约、高级 | minimal | B | sparse/balanced |
| 复古、文艺、胶片、怀旧 | retro | C | balanced |
| 有趣、惊艳、打卡、网红 | pop | C | sparse/list |
| 知识、干货、效率、工具 | notion | B | dense/list |
| 教程、学习、科普、课程 | chalkboard | B | balanced/dense |
| 笔记、手写、总结、手帐 | study-notes | B | dense/list/mindmap |
