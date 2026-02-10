const {
  Document,
  Packer,
  Paragraph,
  TextRun,
  HeadingLevel,
  AlignmentType,
  LevelFormat,
} = require("docx");
const fs = require("fs");

// 创建 Word 文档
const doc = new Document({
  // 设置样式 - 使用 Arial 字体
  styles: {
    default: {
      document: {
        run: { font: "Arial", size: 24 }, // 12pt 默认
      },
    },
    paragraphStyles: [
      {
        id: "Heading1",
        name: "Heading 1",
        basedOn: "Normal",
        next: "Normal",
        quickFormat: true,
        run: { size: 32, bold: true, font: "Arial" }, // 16pt 标题
        paragraph: { spacing: { before: 240, after: 240 }, outlineLevel: 0 },
      },
    ],
  },
  // 设置编号配置 - 用于列表
  numbering: {
    config: [
      {
        reference: "bullets",
        levels: [
          {
            level: 0,
            format: LevelFormat.BULLET,
            text: "•",
            alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 720, hanging: 360 } } },
          },
        ],
      },
    ],
  },
  sections: [
    {
      properties: {
        // 设置页面大小为 US Letter
        page: {
          size: {
            width: 12240, // 8.5 英寸 (DXA)
            height: 15840, // 11 英寸 (DXA)
          },
          margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }, // 1 英寸边距
        },
      },
      children: [
        // 标题
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          alignment: AlignmentType.CENTER,
          children: [
            new TextRun({
              text: "AI 技术简报",
              bold: true,
              size: 40, // 20pt
              color: "2C3E50",
            }),
          ],
        }),

        // 摘要段落
        new Paragraph({
          spacing: { before: 400, after: 400 },
          children: [
            new TextRun({
              text: "人工智能（AI）技术近年来取得了突破性进展，深刻改变了各行各业。从机器学习到深度学习，从自然语言处理到计算机视觉，AI 正以前所未有的速度推动技术革新。本简报旨在概述当前 AI 技术的核心要点，为读者提供快速了解这一领域的窗口。",
              size: 24, // 12pt
            }),
          ],
        }),

        // 要点列表标题
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [
            new TextRun({
              text: "核心技术要点",
              bold: true,
              size: 32,
              color: "2C3E50",
            }),
          ],
        }),

        // 要点 1
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          spacing: { before: 200, after: 200 },
          children: [
            new TextRun({
              text: "机器学习与深度学习：通过大量数据训练模型，使计算机能够自主学习和改进，广泛应用于图像识别、语音识别等领域。",
              size: 24,
            }),
          ],
        }),

        // 要点 2
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          spacing: { before: 200, after: 200 },
          children: [
            new TextRun({
              text: "自然语言处理（NLP）：使计算机能够理解和生成人类语言，推动了聊天机器人、机器翻译、文本摘要等应用的发展。",
              size: 24,
            }),
          ],
        }),

        // 要点 3
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          spacing: { before: 200, after: 200 },
          children: [
            new TextRun({
              text: "大语言模型：如 GPT 系列、Claude 等，展示了强大的文本生成和理解能力，正在重新定义人机交互的方式。",
              size: 24,
            }),
          ],
        }),

        // 日期
        new Paragraph({
          spacing: { before: 800 },
          alignment: AlignmentType.RIGHT,
          children: [
            new TextRun({
              text: "发布日期：2025年2月",
              size: 20,
              italics: true,
              color: "666666",
            }),
          ],
        }),
      ],
    },
  ],
});

// 保存文档
const outputPath = "/tmp/ai_technology_brief.docx";
Packer.toBuffer(doc).then((buffer) => {
  fs.writeFileSync(outputPath, buffer);
  console.log("Document created: " + outputPath);
}).catch((err) => {
  console.error("Error creating document:", err);
});