const pptxgen = require("pptxgenjs");

// 创建演示文稿
let pres = new pptxgen();
pres.layout = 'LAYOUT_16x9';
pres.author = 'OpenClaw Assistant';
pres.title = 'Rust编程语言';

// Rust 主题配色
const RUST_ORANGE = "CE422B";
const RUST_DARK = "2C3E50";
const RUST_GREY = "8D8D8D";
const WHITE = "FFFFFF";
const DARK_TEXT = "2D2D2D";

// ===== 第1页：标题页 =====
let titleSlide = pres.addSlide();

// 背景色 - 深色背景
titleSlide.background = { color: RUST_DARK };

// 添加装饰性形状 - 顶部橙色条纹
titleSlide.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.2,
  fill: { color: RUST_ORANGE }
});

// 对角装饰矩形
titleSlide.addShape(pres.shapes.RECTANGLE, {
  x: 7, y: 1, w: 3, h: 4.5,
  fill: { color: RUST_ORANGE },
  transparency: 15
});

// 主标题
titleSlide.addText("Rust编程语言", {
  x: 0.8, y: 1.5, w: 8, h: 1.5,
  fontSize: 64,
  bold: true,
  color: WHITE,
  fontFace: "Arial",
  align: "left",
  valign: "middle"
});

// 副标题
titleSlide.addText("安全 · 高效 · 现代", {
  x: 0.8, y: 3.2, w: 8, h: 0.8,
  fontSize: 28,
  color: RUST_ORANGE,
  fontFace: "Arial",
  align: "left",
  valign: "middle"
});

// 底部装饰条
titleSlide.addShape(pres.shapes.RECTANGLE, {
  x: 0.8, y: 5.0, w: 2, h: 0.1,
  fill: { color: RUST_ORANGE }
});

// ===== 第2页：内容页 =====
let contentSlide = pres.addSlide();

// 背景白色
contentSlide.background = { color: WHITE };

// 顶部装饰条
contentSlide.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.15,
  fill: { color: RUST_DARK }
});

// 页面标题
contentSlide.addText("为什么选择 Rust？", {
  x: 0.8, y: 0.6, w: 8.4, h: 0.8,
  fontSize: 40,
  bold: true,
  color: RUST_DARK,
  fontFace: "Arial",
  margin: 0
});

// 左侧内容区域
const leftX = 0.8;
const rightX = 5.2;

// 特点1：内存安全
contentSlide.addShape(pres.shapes.RECTANGLE, {
  x: leftX, y: 1.7, w: 0.15, h: 2.4,
  fill: { color: RUST_ORANGE }
});

contentSlide.addText([
  { text: "内存安全", options: { fontSize: 24, bold: true, color: RUST_DARK, breakLine: true } },
  { text: "编译时保证内存安全，", options: { fontSize: 16, color: DARK_TEXT, breakLine: true } },
  { text: "无需垃圾回收机制", options: { fontSize: 16, color: DARK_TEXT } }
], {
  x: leftX + 0.3, y: 1.7, w: 3.7, h: 2.4,
  valign: "middle"
});

// 特点2：高性能
contentSlide.addShape(pres.shapes.RECTANGLE, {
  x: rightX, y: 1.7, w: 0.15, h: 2.4,
  fill: { color: RUST_DARK }
});

contentSlide.addText([
  { text: "高性能", options: { fontSize: 24, bold: true, color: RUST_DARK, breakLine: true } },
  { text: "零成本抽象，", options: { fontSize: 16, color: DARK_TEXT, breakLine: true } },
  { text: "性能媲美 C/C++", options: { fontSize: 16, color: DARK_TEXT } }
], {
  x: rightX + 0.3, y: 1.7, w: 3.7, h: 2.4,
  valign: "middle"
});

// 应用领域标题
contentSlide.addText("应用领域", {
  x: 0.8, y: 4.3, w: 8.4, h: 0.6,
  fontSize: 28,
  bold: true,
  color: RUST_DARK,
  fontFace: "Arial",
  margin: 0
});

// 应用领域列表
contentSlide.addText([
  { text: "系统级编程", options: { fontSize: 18, color: DARK_TEXT, breakLine: true, bullet: true, indentLevel: 0 } },
  { text: "WebAssembly", options: { fontSize: 18, color: DARK_TEXT, breakLine: true, bullet: true, indentLevel: 0 } },
  { text: "命令行工具", options: { fontSize: 18, color: DARK_TEXT, breakLine: true, bullet: true, indentLevel: 0 } },
  { text: "区块链与加密货币", options: { fontSize: 18, color: DARK_TEXT, bullet: true, indentLevel: 0 } }
], {
  x: 0.8, y: 5.0, w: 8.4, h: 1.5,
  paraSpaceAfter: 8
});

// 底部装饰条
contentSlide.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 5.475, w: 10, h: 0.15,
  fill: { color: RUST_ORANGE }
});

// 保存文件
pres.writeFile({ fileName: "/tmp/rust_introduction.pptx" })
  .then(fileName => {
    console.log("Presentation created: " + fileName);
  })
  .catch(err => {
    console.error("Error creating presentation:", err);
  });