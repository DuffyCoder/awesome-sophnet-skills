const pptxgen = require("pptxgenjs");

// Create presentation
let pres = new pptxgen();
pres.layout = 'LAYOUT_16x9';
pres.author = 'OpenClaw';
pres.title = 'Rust 编程语言';

// ==================== SLIDE 1: Title Page ====================
let slide1 = pres.addSlide();
slide1.background = { color: "B85042" }; // Terracotta background

// Title
slide1.addText("Rust 编程语言", {
  x: 1, y: 2.2, w: 8, h: 1.2,
  fontSize: 54, fontFace: "Arial", bold: true,
  color: "FFFFFF", align: "center", valign: "middle"
});

// Subtitle
slide1.addText("安全、并发、高效的系统编程语言", {
  x: 1, y: 3.6, w: 8, h: 0.6,
  fontSize: 24, fontFace: "Arial",
  color: "E7E8D1", align: "center", valign: "middle"
});

// Decorative accent line
slide1.addShape(pres.shapes.RECTANGLE, {
  x: 4, y: 4.4, w: 2, h: 0.08,
  fill: { color: "F5F5F5" }
});

// Footer text
slide1.addText("Empowering everyone to build reliable and efficient software", {
  x: 1, y: 4.8, w: 8, h: 0.4,
  fontSize: 14, fontFace: "Arial",
  color: "F5F5F5", align: "center", valign: "middle", italic: true
});

// ==================== SLIDE 2: Content Page ====================
let slide2 = pres.addSlide();
slide2.background = { color: "F5F5F5" }; // Light cream background

// Section title background
slide2.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 0.5, w: 9, h: 0.7,
  fill: { color: "B85042" }
});

// Section title
slide2.addText("核心优势", {
  x: 0.5, y: 0.5, w: 9, h: 0.7,
  fontSize: 32, fontFace: "Arial", bold: true,
  color: "FFFFFF", align: "center", valign: "middle", margin: 0
});

// Feature items with bullets
slide2.addText([
  { text: "🛡️ 内存安全", options: { bullet: true, breakLine: true, fontSize: 18, bold: true, color: "B85042" } },
  { text: "    编译时检查，杜绝空指针、数据竞争等内存问题", options: { breakLine: true, fontSize: 14, color: "4A5568" } },
  { text: "", options: { breakLine: true } },
  
  { text: "⚡ 零成本抽象", options: { bullet: true, breakLine: true, fontSize: 18, bold: true, color: "B85042" } },
  { text: "    高级语言特性 + 底层性能，无需垃圾回收", options: { breakLine: true, fontSize: 14, color: "4A5568" } },
  { text: "", options: { breakLine: true } },
  
  { text: "🚀 高性能", options: { bullet: true, breakLine: true, fontSize: 18, bold: true, color: "B85042" } },
  { text: "    运行速度媲美 C/C++，内存占用低", options: { breakLine: true, fontSize: 14, color: "4A5568" } },
  { text: "", options: { breakLine: true } },
  
  { text: "📦 优秀的工具链", options: { bullet: true, breakLine: true, fontSize: 18, bold: true, color: "B85042" } },
  { text: "    Cargo 包管理器、Rust Analyzer、丰富的生态系统", options: { breakLine: true, fontSize: 14, color: "4A5568" } }
], {
  x: 1, y: 1.5, w: 8, h: 3.5,
  fontFace: "Arial", paraSpaceAfter: 12
});

// Info box at bottom
slide2.addShape(pres.shapes.RECTANGLE, {
  x: 1, y: 5.2, w: 8, h: 0.6,
  fill: { color: "FFFFFF" },
  line: { color: "B85042", width: 1 }
});

slide2.addText("开始学习: https://www.rust-lang.org/learn", {
  x: 1, y: 5.2, w: 8, h: 0.6,
  fontSize: 14, fontFace: "Arial", bold: true,
  color: "B85042", align: "center", valign: "middle", margin: 0
});

// Save presentation
pres.writeFile({ fileName: "/tmp/rust_programming.pptx" });
console.log("Presentation created: /tmp/rust_programming.pptx");
