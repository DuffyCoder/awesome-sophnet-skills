const pptxgen = require("pptxgenjs");

// Create presentation
let pres = new pptxgen();
pres.layout = 'LAYOUT_16x9';
pres.author = 'OpenClaw';
pres.title = 'GitHub介绍';

// Color palette (GitHub-inspired)
const colors = {
  dark: "24292F",
  blue: "58A6FF",
  green: "238636",
  light: "F6F8FA",
  text: "24292F",
  lightText: "F0F6FC"
};

// ===== SLIDE 1: Title Page =====
let slide1 = pres.addSlide();
slide1.background = { color: colors.dark };

// GitHub icon (octocat)
slide1.addText("🐙", { x: 4.25, y: 1.2, w: 1.5, h: 1.5, fontSize: 80, align: "center", valign: "middle" });

// Title
slide1.addText("GitHub", {
  x: 0.5, y: 2.8, w: 9, h: 1,
  fontSize: 60, bold: true,
  color: colors.lightText,
  align: "center", valign: "middle",
  fontFace: "Arial"
});

// Subtitle
slide1.addText("全球最大的代码托管平台", {
  x: 0.5, y: 3.8, w: 9, h: 0.6,
  fontSize: 24,
  color: colors.blue,
  align: "center", valign: "middle",
  fontFace: "Arial"
});

// Decorative line
slide1.addShape(pres.shapes.RECTANGLE, {
  x: 3.5, y: 4.5, w: 3, h: 0.05,
  fill: { color: colors.green }
});

// Footer
slide1.addText("Build and ship software · Collaborate with millions of developers", {
  x: 0.5, y: 4.8, w: 9, h: 0.5,
  fontSize: 14,
  color: "8B949E",
  align: "center", valign: "middle"
});

// ===== SLIDE 2: Content Page =====
let slide2 = pres.addSlide();
slide2.background = { color: colors.light };

// Header
slide2.addText("什么是GitHub?", {
  x: 0.5, y: 0.3, w: 9, h: 0.6,
  fontSize: 36, bold: true,
  color: colors.text,
  fontFace: "Arial"
});

// Accent line
slide2.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 0.9, w: 0.1, h: 0.05,
  fill: { color: colors.green }
});

// Content blocks
const contentItems = [
  {
    icon: "💻",
    title: "代码托管",
    desc: "基于Git的分布式版本控制系统"
  },
  {
    icon: "🤝",
    title: "协作开发",
    desc: "团队协作、代码审查、合并请求"
  },
  {
    icon: "🔧",
    title: "项目管理",
    desc: "Issue跟踪、Wiki文档、项目看板"
  },
  {
    icon: "🚀",
    title: "持续集成",
    desc: "GitHub Actions自动化部署与测试"
  }
];

// Create 2x2 grid of content blocks
const blockWidth = 4.5;
const blockHeight = 1.8;
const startX = 0.5;
const startY = 1.2;
const gap = 0.2;

contentItems.forEach((item, index) => {
  const col = index % 2;
  const row = Math.floor(index / 2);
  const x = startX + col * (blockWidth + gap);
  const y = startY + row * (blockHeight + gap);

  // Background card with shadow
  slide2.addShape(pres.shapes.RECTANGLE, {
    x: x, y: y, w: blockWidth, h: blockHeight,
    fill: { color: "FFFFFF" },
    shadow: {
      type: "outer",
      color: "000000",
      blur: 4,
      offset: 1,
      angle: 135,
      opacity: 0.08
    }
  });

  // Accent bar on left
  slide2.addShape(pres.shapes.RECTANGLE, {
    x: x, y: y, w: 0.08, h: blockHeight,
    fill: { color: colors.blue }
  });

  // Icon
  slide2.addText(item.icon, {
    x: x + 0.3, y: y + 0.3, w: 0.5, h: 0.5,
    fontSize: 28
  });

  // Title
  slide2.addText(item.title, {
    x: x + 1, y: y + 0.25, w: 3.3, h: 0.4,
    fontSize: 18, bold: true,
    color: colors.text,
    margin: 0
  });

  // Description
  slide2.addText(item.desc, {
    x: x + 1, y: y + 0.65, w: 3.3, h: 1,
    fontSize: 14,
    color: "57606A",
    margin: 0
  });
});

// Footer
slide2.addText("全球超过100万开发者使用GitHub构建软件", {
  x: 0.5, y: 5.1, w: 9, h: 0.4,
  fontSize: 12,
  color: "8B949E",
  align: "center",
  italic: true
});

// Save presentation
pres.writeFile({ fileName: "/tmp/github-intro.pptx" });