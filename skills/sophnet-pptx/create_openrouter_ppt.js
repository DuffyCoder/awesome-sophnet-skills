const pptxgen = require("pptxgenjs");

// Create presentation
let pres = new pptxgen();
pres.layout = 'LAYOUT_16x9';
pres.author = 'OpenClaw';
pres.title = 'OpenRouter 介绍';

// ==================== SLIDE 1: Title Page ====================
let slide1 = pres.addSlide();
slide1.background = { color: "065A82" }; // Deep blue background

// Title
slide1.addText("OpenRouter 介绍", {
  x: 1, y: 2.2, w: 8, h: 1.2,
  fontSize: 54, fontFace: "Arial", bold: true,
  color: "FFFFFF", align: "center", valign: "middle"
});

// Subtitle
slide1.addText("统一的多模型 AI API 网关", {
  x: 1, y: 3.6, w: 8, h: 0.6,
  fontSize: 24, fontFace: "Arial",
  color: "E0F2F1", align: "center", valign: "middle"
});

// Decorative accent line
slide1.addShape(pres.shapes.RECTANGLE, {
  x: 4, y: 4.4, w: 2, h: 0.08,
  fill: { color: "1C7293" }
});

// Footer text
slide1.addText("Powering the Next Generation of AI Applications", {
  x: 1, y: 4.8, w: 8, h: 0.4,
  fontSize: 14, fontFace: "Arial",
  color: "B0E3D6", align: "center", valign: "middle", italic: true
});

// ==================== SLIDE 2: Content Page ====================
let slide2 = pres.addSlide();
slide2.background = { color: "F0F9FA" }; // Light background

// Section title background
slide2.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 0.5, w: 9, h: 0.7,
  fill: { color: "1C7293" }
});

// Section title
slide2.addText("核心特性", {
  x: 0.5, y: 0.5, w: 9, h: 0.7,
  fontSize: 32, fontFace: "Arial", bold: true,
  color: "FFFFFF", align: "center", valign: "middle", margin: 0
});

// Feature items with bullets
slide2.addText([
  { text: "🔗 统一 API 接口", options: { bullet: true, breakLine: true, fontSize: 18, bold: true, color: "065A82" } },
  { text: "    一次集成，接入多个 AI 模型（GPT-4、Claude、Llama 等）", options: { breakLine: true, fontSize: 14, color: "4A5568" } },
  { text: "", options: { breakLine: true } },
  
  { text: "⚡ 智能路由", options: { bullet: true, breakLine: true, fontSize: 18, bold: true, color: "065A82" } },
  { text: "    根据需求和成本自动选择最优模型", options: { breakLine: true, fontSize: 14, color: "4A5568" } },
  { text: "", options: { breakLine: true } },
  
  { text: "💰 透明定价", options: { bullet: true, breakLine: true, fontSize: 18, bold: true, color: "065A82" } },
  { text: "    按实际使用量计费，无隐藏费用", options: { breakLine: true, fontSize: 14, color: "4A5568" } },
  { text: "", options: { breakLine: true } },
  
  { text: "🌐 开发者友好", options: { bullet: true, breakLine: true, fontSize: 18, bold: true, color: "065A82" } },
  { text: "    完整的文档、SDK 和社区支持", options: { breakLine: true, fontSize: 14, color: "4A5568" } }
], {
  x: 1, y: 1.5, w: 8, h: 3.5,
  fontFace: "Arial", paraSpaceAfter: 12
});

// Info box at bottom
slide2.addShape(pres.shapes.RECTANGLE, {
  x: 1, y: 5.2, w: 8, h: 0.6,
  fill: { color: "FFFFFF" },
  line: { color: "1C7293", width: 1 }
});

slide2.addText("了解更多: https://openrouter.ai", {
  x: 1, y: 5.2, w: 8, h: 0.6,
  fontSize: 14, fontFace: "Arial", bold: true,
  color: "065A82", align: "center", valign: "middle", margin: 0
});

// Save presentation
pres.writeFile({ fileName: "/tmp/openrouter_introduction.pptx" });
console.log("Presentation created: /tmp/openrouter_introduction.pptx");
