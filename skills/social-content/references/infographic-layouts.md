# 攻略图 / 信息图 布局与风格指南

`--type guide` 生成的攻略图和信息图的布局与风格选择指南。

---

## 布局 (Layout)

通过 `--layout` 参数指定，控制信息的空间排列方式。

| 布局 | 描述 | 适用内容 |
|------|------|----------|
| `bento-grid` | 大小不一的模块化网格，每块承载独立信息 | 多主题概览、产品合集、旅行攻略 |
| `list` | 编号/图标纵向列表 | TOP N 排名、推荐清单、步骤列表 |
| `comparison` | 双栏或分屏对比 | A vs B、优缺点、前后对比 |
| `flow` | 有方向性的连接步骤/阶段 | 流程教程、行程路线、时间线 |
| `mindmap` | 中心辐射外延分支 | 知识框架、思维导图、分类体系 |
| `hub-spoke` | 中心元素周围环绕相关项 | 核心概念+关联、产品生态 |
| `funnel` | 宽到窄的漏斗层级 | 转化流程、筛选逻辑 |
| `dense-modules` | 紧密排列的信息模块，高密度 | 高密度攻略、数据丰富的指南 |

### 布局详细说明

**bento-grid (便当盒网格)**
- 2×2 到 3×3 的不规则网格
- 每个格子大小可不同，视觉丰富
- 一个大格子放主图/主信息，小格子放辅助要点
- 适合展示 4-9 个不同维度的信息

**list (列表式)**
- 纵向排列，每项包含图标/编号 + 标题 + 简述
- 清晰的视觉层次，由上而下阅读
- 适合有明确顺序或排名的内容

**comparison (对比式)**
- 画面纵向或横向一分为二
- 左右/上下对应展示对比项
- 中间可加 VS 标识或分隔线
- 颜色对比增强差异感

**flow (流程式)**
- 步骤之间用箭头、虚线或路径连接
- 可水平、垂直或蜿蜒排列
- 每步包含图标 + 简要描述
- 时间线变体：带日期/阶段标记

**mindmap (思维导图)**
- 中心放核心主题，四周辐射分支
- 分支可继续细分子节点
- 用颜色区分不同分支类别
- 连接线用曲线更有机感

**hub-spoke (辐射式)**
- 中心一个大元素（品牌/核心概念）
- 周围等距分布 4-8 个关联元素
- 连接线从中心向外辐射
- 适合展示"围绕核心"的关系

**funnel (漏斗式)**
- 最上层最宽，逐层变窄
- 每层标注数据/比例/阶段名
- 颜色由浅到深或由冷到暖
- 适合展示转化/筛选/递进

**dense-modules (密集模块)**
- 每个模块自成一体，紧密排列
- 模块间用细线或小间距分隔
- 高信息密度，适合一图涵盖大量信息
- 类似杂志版面或旅行攻略大图

---

## 风格 (Style)

攻略图/信息图推荐使用以下风格，通过 `--style-preset` 或维度组合实现。

| 风格 | 描述 | 脚本参数 | 适用场景 |
|------|------|----------|----------|
| `craft-handmade` | 手绘纸艺感，温暖亲切 | `--palette warm --rendering hand-drawn --mood balanced` | 旅行攻略、美食指南、生活清单 |
| `kawaii` | 日系可爱，马卡龙色 | `--style-preset kawaii` | 少女风攻略、甜品推荐 |
| `chalkboard` | 黑板粉笔风，教育感 | `--style-preset blueprint` | 知识科普、教程、学习攻略 |
| `corporate-memphis` | 扁平矢量，企业风 | `--style-preset corporate` | 行业报告、商业分析 |
| `bold-graphic` | 漫画式粗线条，视觉冲击 | `--palette vivid --rendering flat-vector --mood bold` | 避坑指南、重要提醒 |
| `morandi-journal` | 莫兰迪手绘日记风 | `--style-preset morandi` | 高级感攻略、生活美学 |
| `retro-pop-grid` | 1970s 复古波普网格 | `--style-preset vintage` 并 `--mood bold` | 潮流指南、文化盘点 |
| `notion-clean` | Notion 风极简线条 | `--style-preset notion` | 效率工具、SaaS 对比、知识卡 |

---

## 推荐组合

根据内容类型推荐 Layout × Style 组合。

| 内容类型 | 推荐布局 | 推荐风格 | 说明 |
|----------|----------|----------|------|
| 旅行攻略 | bento-grid / flow | craft-handmade | 景点+路线+美食模块化展示 |
| 美食清单 | list / bento-grid | craft-handmade / kawaii | 按排名或分类展示 |
| 产品对比 | comparison | corporate-memphis / notion-clean | 双栏清晰对比 |
| 步骤教程 | flow | chalkboard / notion-clean | 流程步骤清晰可循 |
| 知识科普 | mindmap / dense-modules | chalkboard / notion-clean | 知识体系化展示 |
| 避坑指南 | list | bold-graphic | 重要提醒高辨识度 |
| 行程路线 | flow | craft-handmade | 按时间线展示路线 |
| 产品合集/盘点 | bento-grid / list | morandi-journal / kawaii | 多产品概览 |
| 高密度攻略大图 | dense-modules | morandi-journal / retro-pop-grid | 一图涵盖所有信息 |
| 分类对比矩阵 | hub-spoke / mindmap | corporate-memphis | 多维度分类展示 |

---

## 关键词快捷匹配

当用户输入包含以下关键词时，自动推荐对应的布局和风格。

| 关键词 | 自动布局 | 推荐风格 |
|--------|----------|----------|
| 攻略 / guide | bento-grid | craft-handmade |
| 排名 / TOP / 推荐 | list | morandi-journal |
| 对比 / VS / 哪个好 | comparison | corporate-memphis |
| 教程 / 步骤 / 怎么做 | flow | chalkboard |
| 知识 / 科普 / 框架 | mindmap | notion-clean |
| 避坑 / 注意 / 千万别 | list | bold-graphic |
| 路线 / 行程 / 几天几晚 | flow | craft-handmade |
| 清单 / 必买 / 必吃 | list | kawaii |
| 高密度 / 全攻略 / 大图 | dense-modules | morandi-journal |
