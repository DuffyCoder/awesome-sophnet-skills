const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const {
  FaGithub,
  FaCodeBranch,
  FaCode,
  FaShieldAlt,
  FaUsers,
  FaCloud,
  FaArrowRight,
  FaCheckCircle,
  FaTerminal,
  FaEye,
  FaStar,
  FaExchangeAlt,
  FaDatabase,
  FaLock,
  FaLightbulb
} = require("react-icons/fa");

// GitHub-inspired color palette
const colors = {
  primary: "24292F",    // GitHub dark
  secondary: "1F6FEB",  // GitHub blue
  accent: "238636",     // GitHub green
  light: "F6F8FA",      // Light background
  white: "FFFFFF",
  gray: "6E7781",
  border: "D0D7DE"
};

// Render icon to base64 PNG
async function iconToBase64Png(IconComponent, color, size = 256) {
  const svg = ReactDOMServer.renderToStaticMarkup(
    React.createElement(IconComponent, { color, size: String(size) })
  );
  const pngBuffer = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + pngBuffer.toString("base64");
}

// Create presentation
let pres = new pptxgen();
pres.layout = 'LAYOUT_16x9';
pres.author = 'Clawd Assistant';
pres.title = 'Introduction to GitHub';

// Pre-generate icons for reuse
const icons = {};
async function loadIcons() {
  icons.github = await iconToBase64Png(FaGithub, "#FFFFFF", 512);
  icons.code = await iconToBase64Png(FaCode, colors.secondary, 256);
  icons.branch = await iconToBase64Png(FaCodeBranch, colors.secondary, 256);
  icons.shield = await iconToBase64Png(FaShieldAlt, colors.secondary, 256);
  icons.users = await iconToBase64Png(FaUsers, colors.secondary, 256);
  icons.cloud = await iconToBase64Png(FaCloud, colors.secondary, 256);
  icons.arrow = await iconToBase64Png(FaArrowRight, colors.gray, 128);
  icons.check = await iconToBase64Png(FaCheckCircle, colors.accent, 256);
  icons.terminal = await iconToBase64Png(FaTerminal, colors.gray, 256);
  icons.eye = await iconToBase64Png(FaEye, colors.secondary, 256);
  icons.star = await iconToBase64Png(FaStar, colors.gray, 256);
  icons.exchange = await iconToBase64Png(FaExchangeAlt, colors.gray, 256);
  icons.database = await iconToBase64Png(FaDatabase, colors.secondary, 256);
  icons.lock = await iconToBase64Png(FaLock, colors.accent, 256);
  icons.lightbulb = await iconToBase64Png(FaLightbulb, colors.secondary, 256);
}

// Slide 1: Title
function addTitleSlide() {
  let slide = pres.addSlide();
  slide.background = { color: colors.primary };

  // GitHub logo/icon
  slide.addImage({
    data: icons.github,
    x: 4.5, y: 1.5, w: 1.0, h: 1.0
  });

  slide.addText("Introduction to", {
    x: 0, y: 2.8, w: 10, h: 0.6,
    fontSize: 28, color: colors.gray, align: "center", fontFace: "Calibri"
  });

  slide.addText("GitHub", {
    x: 0, y: 3.5, w: 10, h: 1.2,
    fontSize: 72, color: colors.white, bold: true, align: "center",
    fontFace: "Calibri", margin: 0
  });

  slide.addText("The world's leading platform for software development & collaboration", {
    x: 1.5, y: 4.9, w: 7, h: 0.5,
    fontSize: 16, color: colors.gray, align: "center", fontFace: "Calibri"
  });
}

// Slide 2: What is GitHub?
function addWhatIsSlide() {
  let slide = pres.addSlide();
  slide.background = { color: colors.white };

  slide.addText("What is GitHub?", {
    x: 0.5, y: 0.5, w: 9, h: 0.7,
    fontSize: 40, color: colors.primary, bold: true, fontFace: "Calibri", margin: 0
  });

  // Subtle divider line
  slide.addShape(pres.shapes.LINE, {
    x: 0.5, y: 1.2, w: 9, h: 0,
    line: { color: colors.secondary, width: 3 }
  });

  // Main content
  slide.addText([
    { text: "GitHub is a cloud-based platform that hosts Git repositories and provides tools for", options: { breakLine: true } },
    { text: "software development collaboration. It's where developers write, review, and ship code together." }
  ], {
    x: 0.5, y: 1.5, w: 9, h: 1.5,
    fontSize: 18, color: "333333", align: "left", fontFace: "Calibri"
  });

  // Key points with icons
  const keyPoints = [
    { icon: icons.cloud, text: "Hosts 100M+ repositories", y: 3.1 },
    { icon: icons.users, text: "100M+ developers worldwide", y: 3.8 },
    { icon: icons.code, text: "Powerful version control (Git)", y: 4.5 }
  ];

  keyPoints.forEach((point, i) => {
    slide.addImage({
      data: point.icon,
      x: 0.5, y: point.y, w: 0.5, h: 0.5
    });
    slide.addText(point.text, {
      x: 1.2, y: point.y, w: 8.3, h: 0.5,
      fontSize: 16, color: "333333", align: "left", valign: "middle", fontFace: "Calibri"
    });
  });

  // Bottom accent
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 5.2, w: 10, h: 0.425,
    fill: { color: colors.secondary }
  });
}

// Slide 3: Key Features
function addFeaturesSlide() {
  let slide = pres.addSlide();
  slide.background = { color: colors.light };

  slide.addText("Key Features", {
    x: 0.5, y: 0.5, w: 9, h: 0.7,
    fontSize: 40, color: colors.primary, bold: true, fontFace: "Calibri", margin: 0
  });

  slide.addShape(pres.shapes.LINE, {
    x: 0.5, y: 1.2, w: 9, h: 0,
    line: { color: colors.secondary, width: 3 }
  });

  // Feature cards
  const features = [
    { icon: icons.branch, title: "Version Control", desc: "Track changes, revert mistakes, collaborate seamlessly" },
    { icon: icons.users, title: "Collaboration", desc: "Pull requests, code reviews, team discussions" },
    { icon: icons.shield, title: "Security", desc: "Vulnerability scanning, dependency checks, secure secrets" },
    { icon: icons.eye, title: "Code Review", desc: "Inline comments, approval workflows, quality checks" },
    { icon: icons.star, title: "Open Source", desc: "Discover and contribute to millions of projects" },
    { icon: icons.terminal, title: "CI/CD", desc: "Automated testing, builds, and deployments via GitHub Actions" }
  ];

  features.forEach((feature, i) => {
    const row = Math.floor(i / 2);
    const col = i % 2;
    const x = 0.5 + col * 4.75;
    const y = 1.5 + row * 1.6;

    // Card background
    slide.addShape(pres.shapes.RECTANGLE, {
      x, y, w: 4.6, h: 1.5,
      fill: { color: colors.white },
      shadow: { type: "outer", blur: 8, offset: 2, color: "000000", opacity: 0.08 }
    });

    // Icon
    slide.addImage({
      data: feature.icon,
      x: x + 0.15, y: y + 0.15, w: 0.4, h: 0.4
    });

    // Title
    slide.addText(feature.title, {
      x: x + 0.65, y: y + 0.15, w: 3.8, h: 0.4,
      fontSize: 14, color: colors.primary, bold: true, fontFace: "Calibri", margin: 0
    });

    // Description
    slide.addText(feature.desc, {
      x: x + 0.15, y: y + 0.6, w: 4.3, h: 0.75,
      fontSize: 11, color: "555555", fontFace: "Calibri"
    });
  });

  // Bottom accent
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 5.2, w: 10, h: 0.425,
    fill: { color: colors.secondary }
  });
}

// Slide 4: How GitHub Works
function addHowItWorksSlide() {
  let slide = pres.addSlide();
  slide.background = { color: colors.white };

  slide.addText("How GitHub Works", {
    x: 0.5, y: 0.5, w: 9, h: 0.7,
    fontSize: 40, color: colors.primary, bold: true, fontFace: "Calibri", margin: 0
  });

  slide.addShape(pres.shapes.LINE, {
    x: 0.5, y: 1.2, w: 9, h: 0,
    line: { color: colors.secondary, width: 3 }
  });

  // Workflow steps
  const steps = [
    { text: "Write Code", x: 0.8 },
    { text: "Commit", x: 2.8 },
    { text: "Push", x: 4.5 },
    { text: "Review", x: 6.2 },
    { text: "Merge", x: 8.0 }
  ];

  steps.forEach((step, i) => {
    // Circle
    slide.addShape(pres.shapes.OVAL, {
      x: step.x, y: 2.0, w: 0.7, h: 0.7,
      fill: { color: i === 0 ? colors.secondary : colors.white },
      line: { color: colors.secondary, width: 2 }
    });

    // Step number
    slide.addText(String(i + 1), {
      x: step.x, y: 2.0, w: 0.7, h: 0.7,
      fontSize: 20, color: i === 0 ? colors.white : colors.secondary,
      bold: true, align: "center", valign: "middle", fontFace: "Calibri", margin: 0
    });

    // Label
    slide.addText(step.text, {
      x: step.x, y: 2.8, w: 0.7, h: 0.4,
      fontSize: 11, color: colors.primary, bold: true, align: "center",
      fontFace: "Calibri", margin: 0
    });

    // Arrow (except last)
    if (i < steps.length - 1) {
      slide.addImage({
        data: icons.arrow,
        x: step.x + 0.85, y: 2.1, w: 0.3, h: 0.5
      });
    }
  });

  // Description boxes
  const descriptions = [
    { text: "Develop locally on your machine", x: 0.5, y: 3.5 },
    { text: "Save snapshots with meaningful messages", x: 2.5, y: 3.5 },
    { text: "Upload changes to GitHub repository", x: 4.2, y: 3.5 },
    { text: "Team reviews and provides feedback", x: 5.9, y: 3.5 },
    { text: "Approved changes join the main branch", x: 7.7, y: 3.5 }
  ];

  descriptions.forEach((desc, i) => {
    slide.addText(desc.text, {
      x: desc.x, y: desc.y, w: 1.5, h: 0.8,
      fontSize: 10, color: "555555", align: "center", fontFace: "Calibri"
    });
  });

  // Branch visualization
  slide.addText("Branch & Pull Request Flow:", {
    x: 0.5, y: 4.5, w: 4, h: 0.4,
    fontSize: 14, color: colors.primary, bold: true, fontFace: "Calibri", margin: 0
  });

  // Simple branch diagram
  slide.addShape(pres.shapes.LINE, { x: 0.5, y: 5.0, w: 2, h: 0, line: { color: colors.accent, width: 3 } });
  slide.addText("Main", { x: 0.5, y: 5.1, w: 0.6, h: 0.2, fontSize: 9, color: colors.accent, fontFace: "Calibri", margin: 0 });

  slide.addShape(pres.shapes.LINE, { x: 2.5, y: 5.0, w: 1, h: 0, line: { color: colors.secondary, width: 3 } });
  slide.addText("Feature", { x: 2.5, y: 5.1, w: 0.8, h: 0.2, fontSize: 9, color: colors.secondary, fontFace: "Calibri", margin: 0 });

  slide.addImage({ data: icons.arrow, x: 3.55, y: 4.85, w: 0.2, h: 0.3 });

  slide.addShape(pres.shapes.LINE, { x: 3.8, y: 5.0, w: 2, h: 0, line: { color: colors.accent, width: 3 } });
  slide.addText("Main (merged)", { x: 3.8, y: 5.1, w: 1.2, h: 0.2, fontSize: 9, color: colors.accent, fontFace: "Calibri", margin: 0 });

  // Bottom accent
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 5.2, w: 10, h: 0.425,
    fill: { color: colors.secondary }
  });
}

// Slide 5: Why Developers Love GitHub
function addWhyLoveSlide() {
  let slide = pres.addSlide();
  slide.background = { color: colors.light };

  slide.addText("Why Developers Love GitHub", {
    x: 0.5, y: 0.5, w: 9, h: 0.7,
    fontSize: 40, color: colors.primary, bold: true, fontFace: "Calibri", margin: 0
  });

  slide.addShape(pres.shapes.LINE, {
    x: 0.5, y: 1.2, w: 9, h: 0,
    line: { color: colors.secondary, width: 3 }
  });

  // Benefits in two columns
  const benefits = [
    { icon: icons.check, text: "Never lose work with version history" },
    { icon: icons.check, text: "Collaborate in real-time with teams" },
    { icon: icons.check, text: "Showcase your portfolio to employers" },
    { icon: icons.check, text: "Learn from open-source projects" },
    { icon: icons.check, text: "Automate workflows with GitHub Actions" },
    { icon: icons.check, text: "Access powerful code review tools" },
    { icon: icons.check, text: "Join a global developer community" },
    { icon: icons.check, text: "Free for public repositories" }
  ];

  benefits.forEach((benefit, i) => {
    const col = i < 4 ? 0 : 1;
    const row = i % 4;
    const x = 0.5 + col * 4.8;
    const y = 1.6 + row * 0.8;

    slide.addImage({
      data: benefit.icon,
      x, y, w: 0.35, h: 0.35
    });

    slide.addText(benefit.text, {
      x: x + 0.45, y, w: 4.3, h: 0.5,
      fontSize: 14, color: "333333", valign: "middle", fontFace: "Calibri"
    });
  });

  // Bottom accent
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 5.2, w: 10, h: 0.425,
    fill: { color: colors.secondary }
  });
}

// Slide 6: Getting Started
function addGettingStartedSlide() {
  let slide = pres.addSlide();
  slide.background = { color: colors.white };

  slide.addText("Getting Started", {
    x: 0.5, y: 0.5, w: 9, h: 0.7,
    fontSize: 40, color: colors.primary, bold: true, fontFace: "Calibri", margin: 0
  });

  slide.addShape(pres.shapes.LINE, {
    x: 0.5, y: 1.2, w: 9, h: 0,
    line: { color: colors.secondary, width: 3 }
  });

  // Steps with numbers
  const steps = [
    { num: 1, title: "Create an Account", desc: "Sign up for free at github.com" },
    { num: 2, title: "Install Git", desc: "Download git from git-scm.com" },
    { num: 3, title: "Create a Repository", desc: "Start your first project repo" },
    { num: 4, title: "Clone & Code", desc: "Download repo to your machine" }
  ];

  steps.forEach((step, i) => {
    const y = 1.6 + i * 1.0;

    // Step number circle
    slide.addShape(pres.shapes.OVAL, {
      x: 0.5, y, w: 0.6, h: 0.6,
      fill: { color: colors.secondary }
    });

    slide.addText(String(step.num), {
      x: 0.5, y, w: 0.6, h: 0.6,
      fontSize: 24, color: colors.white, bold: true,
      align: "center", valign: "middle", fontFace: "Calibri", margin: 0
    });

    // Title
    slide.addText(step.title, {
      x: 1.3, y, w: 8.2, h: 0.4,
      fontSize: 18, color: colors.primary, bold: true, fontFace: "Calibri", margin: 0
    });

    // Description
    slide.addText(step.desc, {
      x: 1.3, y: y + 0.4, w: 8.2, h: 0.5,
      fontSize: 14, color: "555555", fontFace: "Calibri", margin: 0
    });
  });

  // Quick tip box
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 5.6, w: 9, h: 0.6,
    fill: { color: colors.light },
    line: { color: colors.secondary, width: 1 }
  });

  slide.addImage({
    data: icons.lightbulb,
    x: 0.6, y: 5.65, w: 0.5, h: 0.5
  });

  slide.addText("Pro Tip: Start with a simple 'Hello World' project to practice the basic Git workflow!",
    { x: 1.2, y: 5.65, w: 8.2, h: 0.5, fontSize: 12, color: "333333", valign: "middle", fontFace: "Calibri" });
}

// Slide 7: GitHub Growth Stats
function addStatsSlide() {
  let slide = pres.addSlide();
  slide.background = { color: colors.white };

  slide.addText("GitHub in Numbers", {
    x: 0.5, y: 0.5, w: 9, h: 0.7,
    fontSize: 40, color: colors.primary, bold: true, fontFace: "Calibri", margin: 0
  });

  slide.addShape(pres.shapes.LINE, {
    x: 0.5, y: 1.2, w: 9, h: 0,
    line: { color: colors.secondary, width: 3 }
  });

  // Big stats
  const stats = [
    { num: "100M+", label: "Developers", icon: icons.users },
    { num: "370M+", label: "Repositories", icon: icons.database },
    { num: "90%", label: "Fortune 100", icon: icons.star }
  ];

  stats.forEach((stat, i) => {
    const x = 0.5 + i * 3.2;
    const y = 1.8;

    // Stat box
    slide.addShape(pres.shapes.RECTANGLE, {
      x, y, w: 3, h: 1.8,
      fill: { color: colors.light },
      shadow: { type: "outer", blur: 6, offset: 2, color: "000000", opacity: 0.1 }
    });

    // Icon
    slide.addImage({
      data: stat.icon,
      x: x + 1.2, y: y + 0.1, w: 0.5, h: 0.5
    });

    // Number
    slide.addText(stat.num, {
      x, y: y + 0.6, w: 3, h: 0.7,
      fontSize: 36, color: colors.secondary, bold: true,
      align: "center", fontFace: "Calibri", margin: 0
    });

    // Label
    slide.addText(stat.label, {
      x, y: y + 1.3, w: 3, h: 0.4,
      fontSize: 14, color: "555555", align: "center", fontFace: "Calibri", margin: 0
    });
  });

  // Growth description
  slide.addText([
    { text: "GitHub has grown from a small startup in 2008 to the world's largest development platform.", options: { breakLine: true } },
    { text: "Acquired by Microsoft in 2018, it continues to shape how software is built globally." }
  ], {
    x: 0.5, y: 3.8, w: 9, h: 1.0,
    fontSize: 14, color: "555555", align: "center", fontFace: "Calibri"
  });

  // Bottom accent
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 5.2, w: 10, h: 0.425,
    fill: { color: colors.secondary }
  });
}

// Slide 8: Summary
function addSummarySlide() {
  let slide = pres.addSlide();
  slide.background = { color: colors.primary };

  slide.addImage({
    data: icons.github,
    x: 4.5, y: 0.8, w: 1.0, h: 1.0
  });

  slide.addText("Start Building with GitHub", {
    x: 0, y: 2.0, w: 10, h: 0.8,
    fontSize: 42, color: colors.white, bold: true, align: "center", fontFace: "Calibri", margin: 0
  });

  slide.addText("Join millions of developers shaping the future of software", {
    x: 0, y: 2.9, w: 10, h: 0.5,
    fontSize: 18, color: colors.gray, align: "center", fontFace: "Calibri"
  });

  // Key takeaways
  const takeaways = [
    "Version control that never loses your work",
    "Collaborate with teams anywhere in the world",
    "Showcase your skills with a public portfolio",
    "Learn from and contribute to open source"
  ];

  takeaways.forEach((item, i) => {
    slide.addImage({
      data: icons.check,
      x: 3.0, y: 3.6 + i * 0.4, w: 0.3, h: 0.3
    });

    slide.addText(item, {
      x: 3.5, y: 3.6 + i * 0.4, w: 6.5, h: 0.4,
      fontSize: 14, color: colors.light, valign: "middle", fontFace: "Calibri"
    });
  });

  // Visit GitHub
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 3.0, y: 5.3, w: 4.0, h: 0.5,
    fill: { color: colors.accent }
  });

  slide.addText("Visit github.com", {
    x: 3.0, y: 5.3, w: 4.0, h: 0.5,
    fontSize: 16, color: colors.white, bold: true,
    align: "center", valign: "middle", fontFace: "Calibri", margin: 0
  });
}

// Build presentation
async function buildPresentation() {
  await loadIcons();

  addTitleSlide();
  addWhatIsSlide();
  addFeaturesSlide();
  addHowItWorksSlide();
  addWhyLoveSlide();
  addGettingStartedSlide();
  addStatsSlide();
  addSummarySlide();

  await pres.writeFile({ fileName: "/Data/shutong.shan/clawd/github-intro.pptx" });
  console.log("Presentation created: github-intro.pptx");
}

buildPresentation().catch(console.error);