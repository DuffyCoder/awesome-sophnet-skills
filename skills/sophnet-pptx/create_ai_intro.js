const PptxGenJS = require('pptxgenjs');

// 创建演示文稿
const pptx = new PptxGenJS();

// 设置页面大小（16:9）
pptx.layout = 'LAYOUT_16x9';

// 颜色主题 - 科技感
const colors = {
  primary: '0F4C81',      // 深蓝色
  secondary: 'E8F4F8',    // 浅蓝色背景
  accent: 'FF6B35',       // 橙色强调
  dark: '1A1A2E',         // 深色
  light: 'FFFFFF'         // 白色
};

// ============ 幻灯片 1: 标题页 ============
const slide1 = pptx.addSlide();

// 深蓝色背景
slide1.background = { color: colors.primary };

// 主标题
slide1.addText('人工智能', {
  x: 0.5, y: 2.5, w: 9, h: 1.5,
  fontSize: 54,
  bold: true,
  color: 'FFFFFF',
  fontFace: 'Microsoft YaHei',
  align: 'center',
  valign: 'middle'
});

// 副标题
slide1.addText('Artificial Intelligence', {
  x: 0.5, y: 3.8, w: 9, h: 0.8,
  fontSize: 24,
  bold: false,
  color: colors.secondary,
  fontFace: 'Arial',
  align: 'center',
  valign: 'middle'
});

// 日期
const today = new Date();
const dateStr = today.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' });
slide1.addText(dateStr, {
  x: 0.5, y: 4.8, w: 9, h: 0.5,
  fontSize: 14,
  color: colors.secondary,
  fontFace: 'Microsoft YaHei',
  align: 'center'
});

// ============ 幻灯片 2: 内容页 ============
const slide2 = pptx.addSlide();

// 浅色背景
slide2.background = { color: colors.light };

// 标题区域 - 深色背景
slide2.addShape('rect', {
  x: 0, y: 0, w: 10, h: 1.2,
  fill: { color: colors.dark }
});

// 标题文字
slide2.addText('什么是人工智能？', {
  x: 0.5, y: 0.2, w: 9, h: 0.8,
  fontSize: 32,
  bold: true,
  color: 'FFFFFF',
  fontFace: 'Microsoft YaHei'
});

// 内容区域 - 分为三个要点
const contentItems = [
  {
    title: '定义',
    text: '人工智能是计算机科学的一个分支，致力于创建能够模拟人类智能的系统',
    icon: '🎯'
  },
  {
    title: '核心能力',
    text: '学习、推理、问题解决、感知、语言理解等智能行为',
    icon: '⚡'
  },
  {
    title: '应用领域',
    text: '图像识别、自然语言处理、自动驾驶、医疗诊断、智能推荐等',
    icon: '🚀'
  }
];

let yPos = 1.6;
contentItems.forEach((item, index) => {
  // 内容卡片背景
  slide2.addShape('rect', {
    x: 0.5, y: yPos, w: 9, h: 1.1,
    fill: { color: colors.secondary },
    line: { color: colors.primary, width: 2 }
  });

  // 图标
  slide2.addText(item.icon, {
    x: 0.7, y: yPos + 0.15, w: 0.7, h: 0.8,
    fontSize: 40,
    align: 'center',
    valign: 'middle'
  });

  // 标题
  slide2.addText(item.title, {
    x: 1.6, y: yPos + 0.1, w: 7.5, h: 0.35,
    fontSize: 18,
    bold: true,
    color: colors.primary,
    fontFace: 'Microsoft YaHei'
  });

  // 内容文本
  slide2.addText(item.text, {
    x: 1.6, y: yPos + 0.5, w: 7.5, h: 0.5,
    fontSize: 14,
    color: '333333',
    fontFace: 'Microsoft YaHei'
  });

  yPos += 1.3;
});

// 保存文件
const outputPath = '/tmp/AI_Introduction.pptx';
pptx.writeFile({ fileName: outputPath });

console.log('PPT已创建: ' + outputPath);