# awesome-sophnet-skills

Curated collection of Sophnet skills — ready-to-install plugins for [OpenClaw](https://github.com/openclaw/openclaw) agents.

## Quick Start

```bash
# List all available skills
pnpm openclaw agent --local -m "list sophnet skills"

# Install a specific skill
pnpm openclaw agent --local -m "install sophnet-stock"
```

Or use the **sophnet-skill-installer** skill to browse, compare versions, and batch-install.

## Skills

### Feishu (飞书) — Document Collaboration Suite

飞书全家桶：覆盖文档、表格、多维表格、知识库、云空间、权限管理六大场景。

| Skill | Description |
|-------|-------------|
| [**feishu-bitable**](skills/feishu-bitable/) | 多维表格 CRUD — 表格/记录/字段/视图的增删改查，支持 `/base/` 和 `/wiki/` URL |
| [**feishu-doc**](skills/feishu-doc/) | 云文档内容读写 — 读取、替换全文、追加内容、块级操作，支持 Markdown 写入 |
| [**feishu-drive**](skills/feishu-drive/) | 云空间文件管理 — 移动/删除/复制文件、列出文件夹、创建文件夹、获取元信息 |
| [**feishu-perm**](skills/feishu-perm/) | 权限与分享管理 — 添加/移除协作者、查看权限列表（默认禁用，需手动启用） |
| [**feishu-sheets**](skills/feishu-sheets/) | 电子表格操作 — 工作表管理、A1 记法单元格范围读写、追加行数据（类 Excel） |
| [**feishu-wiki**](skills/feishu-wiki/) | 知识库导航 — 列出知识空间/节点、创建/移动/重命名节点、解析 `/wiki/` URL 路由 |

<details>
<summary><strong>飞书 Skills 配置说明</strong></summary>

使用飞书 skills 前，需在 OpenClaw 配置中完成以下设置：

**1. 启用飞书插件**

```json
{
  "plugins": {
    "entries": {
      "feishu": { "enabled": true }
    }
  }
}
```

**2. 配置飞书 Channel**

```json
{
  "channels": {
    "feishu": {
      "enabled": true,
      "dmPolicy": "pairing",
      "accounts": {
        "main": {
          "enabled": true,
          "appId": "<your-app-id>",
          "appSecret": "<your-app-secret>",
          "botName": "<your-bot-name>",
          "domain": "feishu"
        }
      }
    }
  }
}
```

**3. 启用权限管理工具（可选）**

```json
{ "channels": { "feishu": { "tools": { "perm": true } } } }
```

**4. 获取凭据**

| 字段 | 说明 | 获取方式 |
|------|------|----------|
| `appId` | 应用凭证 App ID | [飞书开放平台](https://open.feishu.cn) → 应用管理 → 凭证与基础信息 |
| `appSecret` | 应用凭证 App Secret | 同上 |
| `botName` | 机器人名称 | 创建应用时自定义 |

> `domain` 保持 `"feishu"`；Lark 国际版改为 `"lark"`。

</details>

### Sophnet — AI-Powered Tools

| Skill | Description |
|-------|-------------|
| [**sophnet-dailynews**](skills/sophnet-dailynews/) | 每日新闻摘要 — 多层级新闻源抓取、过滤去重、生成 Markdown 报告，含缓存防重复 |
| [**sophnet-stock**](skills/sophnet-stock/) | 股票与加密货币分析 (v6.2) — 8 维度评分、投资组合、自选股提醒、股息分析、Hot Scanner、Rumor Scanner |
| [**sophnet-docx**](skills/sophnet-docx/) | Word 文档处理 — 创建、读取、编辑 `.docx` 文件，支持样式/表格/批注/修订 |
| [**sophnet-pdf**](skills/sophnet-pdf/) | PDF 文档处理 — 创建、编辑、合并、拆分、水印、文本提取、格式转换 |
| [**sophnet-pptx**](skills/sophnet-pptx/) | PowerPoint 演示文稿 — 创建、编辑 `.pptx` 文件 |
| [**sophnet-xlsx**](skills/sophnet-xlsx/) | Excel 表格处理 — 创建、读取、编辑 `.xlsx` 文件 |

### Sophnet — Image & Vision

| Skill | Description |
|-------|-------------|
| [**sophnet-face-search**](skills/sophnet-face-search/) | 人脸检测与相似度搜索 — 通过 Sophnet API 在多张图片中查找相似面孔 |
| [**sophnet-image-edit**](skills/sophnet-image-edit/) | 图像编辑 — 图生图、多图合成、风格迁移等 Sophnet 图像编辑能力 |
| [**sophnet-image-generate**](skills/sophnet-image-generate/) | 文生图 — 基于 Z-Image-Turbo/Qwen-Image 等模型的文本到图像生成 |
| [**sophnet-image-ocr**](skills/sophnet-image-ocr/) | OCR 文字识别 — 从图片中提取文字和表格，支持本地文件和 URL |

### Infrastructure

| Skill | Description |
|-------|-------------|
| [**sophnet-skill-installer**](skills/sophnet-skill-installer/) | 技能安装器 — 浏览、对比版本、批量安装本仓库中的 skills |
| [**sophnet-sophon-key**](skills/sophnet-sophon-key/) | API Key 管理 — 自动读取或引导配置 `SOPH_API_KEY` |

## Repository Structure

```
skills/
├── feishu-bitable/        # 飞书多维表格
├── feishu-doc/            # 飞书云文档
├── feishu-drive/          # 飞书云空间
├── feishu-perm/           # 飞书权限管理
├── feishu-sheets/         # 飞书电子表格
├── feishu-wiki/           # 飞书知识库
├── sophnet-dailynews/     # 每日新闻
├── sophnet-docx/          # Word 文档
├── sophnet-face-search/   # 人脸搜索
├── sophnet-image-edit/    # 图像编辑
├── sophnet-image-generate/# 文生图
├── sophnet-image-ocr/     # OCR 识别
├── sophnet-pdf/           # PDF 处理
├── sophnet-pptx/          # PPT 演示
├── sophnet-skill-installer/# 技能安装器
├── sophnet-sophon-key/    # API Key 管理
├── sophnet-stock/         # 股票分析
└── sophnet-xlsx/          # Excel 表格
```

Each skill directory contains:
- `SKILL.md` — Skill definition, trigger rules, and usage documentation
- Source code, scripts, and configuration files specific to the skill

## Contributing

1. Fork this repository
2. Create your skill directory under `skills/`
3. Include a `SKILL.md` with proper frontmatter (`name`, `description`, `metadata`)
4. Submit a pull request

## License

MIT
