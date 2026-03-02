# Image Style Dimensions

图片生成的风格维度系统。通过 Palette × Rendering × Mood 三个维度组合，精确控制生成图片的视觉风格。

## Palette (色调)

通过 `--palette` 参数指定。控制整体色彩方向。

| Palette | 描述 | 色彩特征 | 适用场景 |
|---------|------|----------|----------|
| `warm` | 暖色系 | 金黄、琥珀橙、赤陶红、蜜糖色 | 美食、旅游、生活方式、故事类内容 |
| `elegant` | 优雅系 | 香槟金、象牙白、灰粉、柔灰 | 品牌宣传、高端产品、商务内容 |
| `cool` | 冷色系 | 海洋蓝、薄荷绿、银灰、冰白 | 科技、健康、清爽场景 |
| `dark` | 深色系 | 深海军蓝、炭灰、深青、暗酒红 | 高端感、夜景、戏剧性场景 |
| `earth` | 大地色 | 橄榄绿、陶土棕、砂岩、森林色调 | 自然、户外、有机产品、环保主题 |
| `vivid` | 高饱和 | 饱和三原色、强对比、鲜艳点缀 | 促销、节日、活力场景、吸睛封面 |
| `pastel` | 马卡龙 | 柔粉、婴儿蓝、薰衣草、薄荷 | 少女风、甜品、母婴、轻柔氛围 |
| `mono` | 单色调 | 单一色相的深浅变化 | 极简设计、艺术感、品牌一致性 |
| `retro` | 复古色 | 芥末黄、焦橙、牛油果绿、褪色青 | 怀旧主题、文艺风、咖啡/书店场景 |

## Rendering (渲染风格)

通过 `--rendering` 参数指定。控制画面的视觉表现手法。

| Rendering | 描述 | 视觉特征 | 适用场景 |
|-----------|------|----------|----------|
| `flat-vector` | 扁平矢量 | 干净几何形状、纯色填充、无渐变纹理、极简线条 | 信息图、LOGO、图标风格、小红书卡片 |
| `hand-drawn` | 手绘风 | 可见素描线条、有机不规则感、纸笔质感、略带随性 | 攻略图、笔记风、教程类、有温度的内容 |
| `painterly` | 绘画风 | 可见笔触、丰富纹理、柔和边缘、油画/水彩感 | 风景、美食、艺术氛围、公众号封面 |
| `digital` | 数字精修 | 平滑渐变、精致细节、现代精炼感 | 产品展示、商业配图、专业感 |
| `pixel` | 像素风 | 复古 8-bit 美学、方块造型、有限色板 | 游戏主题、怀旧内容、趣味封面 |
| `chalk` | 粉笔风 | 彩色粉笔在深色背景上、手写字体感、教育美学 | 知识科普、黑板风教程、教育类内容 |

## Mood (情绪)

通过 `--mood` 参数指定。控制画面的整体强度和感受。

| Mood | 描述 | 视觉特征 |
|------|------|----------|
| `subtle` | 克制柔和 | 低对比度、柔和色调、大面积留白、安静沉稳的构图 |
| `balanced` | 均衡适中 | 中等对比度、和谐构图、专业且亲和的感觉 |
| `bold` | 强烈冲击 | 高对比度、饱和色彩、动态构图、强视觉冲击力 |

## Style Presets (风格预设)

通过 `--style-preset` 参数指定。快捷方式，自动设置 palette + rendering + mood 组合。
单独指定的 `--palette`/`--rendering`/`--mood` 会覆盖预设中的对应值。

| Preset | Palette | Rendering | Mood | 适用场景 |
|--------|---------|-----------|------|----------|
| `blueprint` | dark | chalk | bold | 技术解析、流程图、工程感 |
| `notion` | mono | hand-drawn | subtle | 知识卡片、极简笔记、Notion 风 |
| `watercolor` | pastel | painterly | subtle | 文艺风景、温柔氛围 |
| `pop-art` | vivid | flat-vector | bold | 促销、潮流、高能量 |
| `vintage` | retro | hand-drawn | balanced | 文艺怀旧、咖啡/书店 |
| `corporate` | cool | flat-vector | balanced | 企业宣传、行业报告 |
| `cozy` | warm | painterly | subtle | 美食、居家、温暖故事 |
| `kawaii` | pastel | flat-vector | balanced | 少女风、萌系、小红书 cute 风 |
| `morandi` | earth | hand-drawn | subtle | 高级感、莫兰迪色、生活美学 |

## 平台推荐默认组合

各平台推荐的默认风格维度组合，agent 可根据内容和平台自动选择。

### 微信公众号

| 图片用途 | 推荐 Palette | 推荐 Rendering | 推荐 Mood | 推荐 Preset |
|----------|-------------|----------------|-----------|-------------|
| 头图封面 | warm / elegant | painterly / digital | balanced | cozy / — |
| 方形预览 | 同头图 | 同头图 | 同头图 | 同头图 |
| 文内配图 | warm / earth | painterly / digital | balanced / subtle | cozy / morandi |
| 数据/流程图 | cool / mono | flat-vector | balanced | corporate / notion |

### 小红书

| 图片用途 | 推荐 Palette | 推荐 Rendering | 推荐 Mood | 推荐 Preset |
|----------|-------------|----------------|-----------|-------------|
| 封面（种草） | vivid / pastel | flat-vector | bold | pop-art / kawaii |
| 封面（攻略） | warm / earth | hand-drawn | balanced | vintage / morandi |
| 文内配图 | pastel / warm | painterly / hand-drawn | balanced | cozy / watercolor |
| 信息图 | mono / cool | flat-vector / hand-drawn | balanced | notion / corporate |

### 搜狐号

| 图片用途 | 推荐 Palette | 推荐 Rendering | 推荐 Mood | 推荐 Preset |
|----------|-------------|----------------|-----------|-------------|
| 封面 | cool / elegant | digital | balanced | corporate |
| 文内配图 | earth / warm | digital / painterly | balanced | — |
| 数据图 | cool / mono | flat-vector | balanced | corporate / notion |

### 百家号

| 图片用途 | 推荐 Palette | 推荐 Rendering | 推荐 Mood | 推荐 Preset |
|----------|-------------|----------------|-----------|-------------|
| 三图封面 | warm / vivid | digital / painterly | balanced / bold | — |
| 文内配图 | warm / earth | digital / painterly | balanced | cozy |
| 信息图 | cool / mono | flat-vector | balanced | corporate / notion |

## 构图原则

所有图片生成需遵守的构图规则（源自最佳实践）：

- **留白 40-60%**：画面需要有呼吸感，避免信息过满
- **视觉锚点**：主要元素居中或偏左放置
- **人物处理**：使用简化剪影或卡通形象，不使用写实人像
- **文字标题**：使用用户给定的标题文字，不自行编造
- **小尺寸可辨**：方形预览图（200×200）的主体必须居中，在缩小后仍可辨识
