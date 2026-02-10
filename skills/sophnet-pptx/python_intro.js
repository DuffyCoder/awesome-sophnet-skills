const pptxgen = require("pptxgenjs");

// 创建演示文稿
let pres = new pptxgen();
pres.layout = 'LAYOUT_16x9';
pres.author = 'OpenClaw Assistant';
pres.title = 'Python编程语言介绍';

// Python 主题配色
const PYTHON_BLUE = "306998";
const PYTHON_YELLOW = "FFDC42";
const PYTHON_BLUE_LIGHT = "3776AB";
const WHITE = "FFFFFF";
const DARK_TEXT = "363636";

// ===== 第1页：标题页 =====
let titleSlide = pres.addSlide();

// 背景色 - 使用 Python 的深蓝色
titleSlide.background = { color: PYTHON_BLUE };

// 添加装饰性形状 - 左上角黄色几何图形
titleSlide.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 3, h: 0.15,
  fill: { color: PYTHON_YELLOW }
});

// 右下角装饰
titleSlide.addShape(pres.shapes.OVAL, {
  x: 8, y: 4.2, w: 2.5, h: 2.5,
  fill: { color: PYTHON_BLUE_LIGHT },
  transparency: 70
});

// 主标题
titleSlide.addText("Python编程语言", {
  x: 1, y: 1.5, w: 8, h: 1.5,
  fontSize: 60,
  bold: true,
  color: WHITE,
  fontFace: "Arial",
  align: "center",
  valign: "middle"
});

// 副标题
titleSlide.addText("简洁强大 · 易学易用", {
  x: 1, y: 3.2, w: 8, h: 0.8,
  fontSize: 28,
  color: PYTHON_YELLOW,
  fontFace: "Arial",
  align: "center",
  valign: "middle"
});

// 底部装饰线
titleSlide.addShape(pres.shapes.RECTANGLE, {
  x: 3.5, y: 4.5, w: 3, h: 0.08,
  fill: { color: PYTHON_YELLOW }
});

// ===== 第2页：内容页 =====
let contentSlide = pres.addSlide();

// 背景白色
contentSlide.background = { color: WHITE };

// 顶部装饰条
contentSlide.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.15,
  fill: { color: PYTHON_BLUE }
});

// 页面标题
contentSlide.addText("为什么选择 Python？", {
  x: 0.8, y: 0.6, w: 8.4, h: 0.8,
  fontSize: 40,
  bold: true,
  color: PYTHON_BLUE,
  fontFace: "Arial",
  margin: 0
});

// 左侧内容区域
const leftX = 0.8;
const rightX = 5.2;

// 特点1：简洁易学
contentSlide.addShape(pres.shapes.RECTANGLE, {
  x: leftX, y: 1.7, w: 0.12, h: 2.5,
  fill: { color: PYTHON_YELLOW }
});

contentSlide.addText([
  { text: "简洁易学", options: { fontSize: 24, bold: true, color: PYTHON_BLUE, breakLine: true } },
  { text: "语法清晰，接近自然语言，", options: { fontSize: 16, color: DARK_TEXT, breakLine: true } },
  { text: "初学者也能快速上手", options: { fontSize: 16, color: DARK_TEXT } }
], {
  x: leftX + 0.25, y: 1.7, w: 3.8, h: 2.5,
  valign: "middle"
});

// 特点2：功能强大
contentSlide.addShape(pres.shapes.RECTANGLE, {
  x: rightX, y: 1.7, w: 0.12, h: 2.5,
  fill: { color: PYTHON_BLUE }
});

contentSlide.addText([
  { text: "功能强大", options: { fontSize: 24, bold: true, color: PYTHON_BLUE, breakLine: true } },
  { text: "丰富的标准库和第三方库，", options: { fontSize: 16, color: DARK_TEXT, breakLine: true } },
  { text: "支持 Web、AI、数据分析等领域", options: { fontSize: 16, color: DARK_TEXT } }
], {
  x: rightX + 0.25, y: 1.7, w: 3.8, h: 2.5,
  valign: "middle"
});

// 应用领域标题
contentSlide.addText("应用领域", {
  x: 0.8, y: 4.5, w: 8.4, h: 0.6,
  fontSize: 28,
  bold: true,
  color: PYTHON_BLUE,
  fontFace: "Arial",
  margin: 0
});

// 应用领域列表
contentSlide.addText([
  { text: "Web 开发", options: { fontSize: 18, color: DARK_TEXT, breakLine: true, bullet: true, indentLevel: 0 } },
  { text: "人工智能与机器学习", options: { fontSize: 18, color: DARK_TEXT, breakLine: true, bullet: true, indentLevel: 0 } },
  { text: "数据分析与可视化", options: { fontSize: 18, color: DARK_TEXT, breakLine: true, bullet: true, indentLevel: 0 } },
  { text: "自动化脚本与运维", options: { fontSize: 18, color: DARK_TEXT, bullet: true, indentLevel: 0 } }
], {
  x: 0.8, y: 5.2, w: 8.4, h: 1.5,
  paraSpaceAfter: 8
});

// 底部装饰
contentSlide.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 5.475, w: 10, h: 0.15,
  fill: { color: PYTHON_YELLOW }
});

// 保存文件
pres.writeFile({ fileName: "/tmp/python_introduction.pptx" })
  .then(fileName => {
    console.log("Presentation created: " + fileName);
  })
  .catch(err => {
    console.error("Error creating presentation:", err);
  });