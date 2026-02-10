#!/usr/bin/env python3
"""Enhance the Image-Edit tutorial PDF with richer content."""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Create output PDF
output_path = "/Data/shutong.shan/clawd/media/outbound/Image-Edit_教程_增强版.pdf"
doc = SimpleDocTemplate(
    output_path,
    pagesize=A4,
    rightMargin=2*cm,
    leftMargin=2*cm,
    topMargin=2*cm,
    bottomMargin=2*cm
)

# Define styles
styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    'Title',
    parent=styles['Title'],
    fontSize=24,
    textColor=colors.darkblue,
    spaceAfter=1*cm,
    alignment=TA_CENTER,
    fontName='Helvetica-Bold'
)

subtitle_style = ParagraphStyle(
    'Subtitle',
    parent=styles['Heading2'],
    fontSize=16,
    textColor=colors.darkgray,
    spaceAfter=0.8*cm,
    alignment=TA_CENTER,
    fontName='Helvetica'
)

heading1_style = ParagraphStyle(
    'Heading1',
    parent=styles['Heading1'],
    fontSize=18,
    textColor=colors.darkblue,
    spaceAfter=0.5*cm,
    spaceBefore=0.5*cm,
    fontName='Helvetica-Bold'
)

heading2_style = ParagraphStyle(
    'Heading2',
    parent=styles['Heading2'],
    fontSize=14,
    textColor=colors.darkgreen,
    spaceAfter=0.3*cm,
    spaceBefore=0.4*cm,
    fontName='Helvetica-Bold'
)

heading3_style = ParagraphStyle(
    'Heading3',
    parent=styles['Heading3'],
    fontSize=12,
    textColor=colors.purple,
    spaceAfter=0.2*cm,
    spaceBefore=0.2*cm,
    fontName='Helvetica-Bold'
)

body_style = ParagraphStyle(
    'Body',
    parent=styles['Normal'],
    fontSize=11,
    spaceAfter=0.3*cm,
    alignment=TA_JUSTIFY,
    fontName='Helvetica',
    leading=16
)

code_style = ParagraphStyle(
    'Code',
    parent=styles['Code'],
    fontSize=10,
    textColor=colors.darkblue,
    fontName='Courier',
    leftIndent=1*cm,
    spaceAfter=0.3*cm
)

note_style = ParagraphStyle(
    'Note',
    parent=styles['Normal'],
    fontSize=10,
    textColor=colors.darkred,
    leftIndent=0.5*cm,
    rightIndent=0.5*cm,
    spaceAfter=0.3*cm,
    fontName='Helvetica-Oblique'
)

# Build content
story = []

# Title page
story.append(Paragraph("Image-Edit 教程", title_style))
story.append(Paragraph("完整的图像编辑技能指南", subtitle_style))
story.append(Spacer(1, 2*cm))

story.append(Paragraph(
    "Image-Edit 是一个强大的图像编辑技能，通过 Sophnet API 实现智能图像处理。本教程将帮助你快速掌握 Image-Edit 的使用方法，包括基础操作、高级技巧和最佳实践。",
    body_style
))

story.append(PageBreak())

# Table of Contents
story.append(Paragraph("目录", heading1_style))
toc_items = [
    ("1. 简介", 3),
    ("2. 快速开始", 4),
    ("3. 基础操作", 5),
    ("4. 高级编辑功能", 6),
    ("5. 最佳实践", 7),
    ("6. 常见问题", 8),
    ("7. 示例代码", 9),
]

toc_data = [['章节', '页码']]
toc_data.extend(toc_items)

toc_table = Table(toc_data, colWidths=[12*cm, 3*cm])
toc_table.setStyle(TableStyle([
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
    ('FONTSIZE', (0, 1), (-1, -1), 11),
    ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightblue]),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('LEFTPADDING', (0, 0), (-1, -1), 12),
    ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ('TOPPADDING', (0, 0), (-1, -1), 8),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
]))

story.append(toc_table)
story.append(PageBreak())

# Chapter 1: Introduction
story.append(Paragraph("1. 简介", heading1_style))
story.append(Paragraph("1.1 什么是 Image-Edit?", heading2_style))
story.append(Paragraph(
    "Image-Edit 是基于 Sophnet API 的图像编辑技能，支持多种图像处理操作，包括图像到图像的转换、风格迁移、区域编辑、多图像合成等功能。它使用先进的深度学习模型来实现高质量的图像编辑效果。",
    body_style
))

story.append(Paragraph("1.2 核心功能", heading2_style))
story.append(Paragraph(
    "<b>•</b> 图像风格转换 - 将一张图片的风格应用到另一张图片上<br/>"
    "<b>•</b> 区域编辑 - 精确编辑图片的特定区域<br/>"
    "<b>•</b> 多图像合成 - 将多张图片组合成一幅作品<br/>"
    "<b>•</b> 图像增强 - 改善图片质量，提高清晰度和色彩<br/>"
    "<b>•</b> 背景替换 - 更换或移除图片背景<br/>"
    "<b>•</b> 对象移除/添加 - 智能删除或添加图片中的元素",
    body_style
))

story.append(Paragraph("1.3 系统要求", heading2_style))
story.append(Paragraph(
    "<b>•</b> Python 3.7 或更高版本<br/>"
    "<b>•</b> Sophnet API 密钥（通过 sophnet-sophon-key 技能配置）<br/>"
    "<b>•</b> 稳定的网络连接（调用远程 API 需要）",
    body_style
))

story.append(PageBreak())

# Chapter 2: Quick Start
story.append(Paragraph("2. 快速开始", heading1_style))
story.append(Paragraph("2.1 安装依赖", heading2_style))
story.append(Paragraph(
    "首先确保已安装 sophnet-skill-installer 技能，然后使用以下命令安装 Image-Edit 相关技能：",
    body_style
))
story.append(Paragraph(
    "clawhub install sophnet-image-edit",
    code_style
))
story.append(Paragraph(
    "这将自动安装所有必要的依赖和配置文件。",
    body_style
))

story.append(Paragraph("2.2 配置 API 密钥", heading2_style))
story.append(Paragraph(
    "在使用 Image-Edit 之前，需要配置 Sophnet API 密钥：",
    body_style
))
story.append(Paragraph(
    "1. 确保已设置 SOPH_API_KEY 环境变量<br/>"
    "2. 或者在 Moltbot 配置文件中添加 API 密钥配置<br/>"
    "3. sophnet-sophon-key 技能会自动检测并引导你完成配置",
    body_style
))

story.append(Paragraph("2.3 基本使用流程", heading2_style))
story.append(Paragraph(
    "Image-Edit 的基本使用流程如下：",
    body_style
))
story.append(Paragraph(
    "1. <b>输入图片</b> - 准备需要编辑的原始图片（支持本地文件或 URL）<br/>"
    "2. <b>编辑指令</b> - 提供清晰的编辑指令或提示词<br/>"
    "3. <b>处理图像</b> - 调用 Image-Edit API 进行处理<br/>"
    "4. <b>获取结果</b> - 接收并保存编辑后的图片<br/>"
    "5. <b>迭代优化</b> - 如有需要，根据结果调整参数重新处理",
    body_style
))

story.append(PageBreak())

# Chapter 3: Basic Operations
story.append(Paragraph("3. 基础操作", heading1_style))
story.append(Paragraph("3.1 单张图片编辑", heading2_style))
story.append(Paragraph(
    "最简单的用法是对单张图片进行编辑。提供一张图片和编辑描述：",
    body_style
))
story.append(Paragraph(
    "示例：将一张照片转换为油画风格",
    body_style
))
story.append(Paragraph(
    "<b>输入图片：</b>  portrait.jpg<br/>"
    "<b>编辑指令：</b> 将这张照片转换为梵高风格的油画<br/>"
    "<b>处理结果：</b> 获得 oil_painting_style.jpg",
    body_style
))

story.append(Paragraph("3.2 区域编辑", heading2_style))
story.append(Paragraph(
    "区域编辑允许你精确控制图片的特定部分进行修改：",
    body_style
))
story.append(Paragraph(
    "<b>示例场景：</b><br/>"
    "• 修改人物发色<br/>"
    "• 更换衣服颜色<br/>"
    "• 调整背景亮度<br/>"
    "• 移除或添加特定对象",
    body_style
))
story.append(Paragraph(
    "提示：提供精确的区域描述可以大大提高编辑准确性。",
    note_style
))

story.append(Paragraph("3.3 图片风格迁移", heading3_style))
story.append(Paragraph(
    "使用一张图片的风格来处理另一张图片：",
    body_style
))
story.append(Paragraph(
    "<b>参考图片：</b> 梵高《星空》<br/>"
    "<b>目标图片：</b> 你的城市照片<br/>"
    "<b>效果：</b> 城市照片呈现出《星空》的笔触和色彩风格",
    body_style
))

story.append(PageBreak())

# Chapter 4: Advanced Features
story.append(Paragraph("4. 高级编辑功能", heading1_style))
story.append(Paragraph("4.1 多图像编辑", heading2_style))
story.append(Paragraph(
    "Image-Edit 支持同时处理多张图片，适用于复杂的合成任务：",
    body_style
))
story.append(Paragraph(
    "<b>典型应用：</b><br/>"
    "• 换脸技术<br/>"
    "• 服装试穿<br/>"
    "• 场景合成<br/>"
    "• 多人图像组合",
    body_style
))

story.append(Paragraph("4.2 批量处理", heading2_style))
story.append(Paragraph(
    "对于需要处理大量相似图片的场景，可以使用批量处理功能：",
    body_style
))
story.append(Paragraph(
    "• 统一风格转换<br/>"
    "• 批量背景移除<br/>"
    "• 批量质量增强<br/>"
    "• 批量水印添加",
    body_style
))

story.append(Paragraph("4.3 高级控制参数", heading2_style))
story.append(Paragraph(
    "Image-Edit 支持多种高级参数来控制编辑效果：",
    body_style
))

advanced_params = [
    ['参数', '说明', '示例值'],
    ['strength', '编辑强度', '0.1-1.0'],
    ['steps', '处理步数', '20-50'],
    ['guidance_scale', '提示词引导强度', '7.5-15.0'],
    ['seed', '随机种子（复现结果）', '42'],
    ['negative_prompt', '负面提示词', 'blur, low quality'],
]

params_table = Table(advanced_params, colWidths=[4*cm, 5*cm, 6*cm])
params_table.setStyle(TableStyle([
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 11),
    ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
    ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ('TOPPADDING', (0, 0), (-1, -1), 6),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
]))

story.append(params_table)

story.append(PageBreak())

# Chapter 5: Best Practices
story.append(Paragraph("5. 最佳实践", heading1_style))
story.append(Paragraph("5.1 提示词编写技巧", heading2_style))
story.append(Paragraph(
    "良好的提示词是获得理想效果的关键。以下是一些实用技巧：",
    body_style
))

tips = [
    ("明确具体", "避免模糊的描述，使用具体的形容词和名词"),
    ("使用正向语言", "描述你想要的效果，而不是你不想要的"),
    ("参考风格", "提及知名艺术家或艺术风格可以提高准确性"),
    ("控制长度", "提示词不宜过长或过短，通常50-200字效果最佳"),
    ("迭代优化", "根据结果调整提示词，逐步接近理想效果"),
]

for i, (tip, desc) in enumerate(tips, 1):
    story.append(Paragraph(f"5.1.{i} {tip}", heading3_style))
    story.append(Paragraph(desc, body_style))

story.append(Paragraph("5.2 图片质量要求", heading2_style))
story.append(Paragraph(
    "为了获得最佳的编辑效果，输入图片应满足以下要求：",
    body_style
))
story.append(Paragraph(
    "<b>•</b> <b>分辨率：</b> 建议 512x512 或更高<br/>"
    "<b>•</b> <b>格式：</b> 支持 JPEG、PNG、WebP 等常见格式<br/>"
    "<b>•</b> <b>文件大小：</b> 建议不超过 10MB<br/>"
    "<b>•</b> <b>清晰度：</b> 避免过度模糊或压缩的图片<br/>"
    "<b>•</b> <b>对比度：</b> 适当的对比度有助于理解图片内容",
    body_style
))

story.append(Paragraph("5.3 性能优化", heading2_style))
story.append(Paragraph(
    "优化处理效率的建议：",
    body_style
))
story.append(Paragraph(
    "<b>•</b> 批量处理时使用合理的并发数<br/>"
    "<b>•</b> 适当调整 steps 参数以平衡质量和速度<br/>"
    "<b>•</b> 缓存常用的参考图片<br/>"
    "<b>•</b> 使用相同 seed 以便复现和调试",
    body_style
))

story.append(PageBreak())

# Chapter 6: FAQ
story.append(Paragraph("6. 常见问题", heading1_style))

faqs = [
    (
        "Q: 为什么我的编辑效果不理想？",
        "A: 尝试改进提示词的描述性，使用更具体的形容词和艺术风格参考。同时检查输入图片的清晰度和质量。"
    ),
    (
        "Q: 处理速度很慢怎么办？",
        "A: 可以减少 steps 参数值，或降低图片分辨率。对于大批量处理，考虑使用队列系统。"
    ),
    (
        "Q: 如何保持图片的某些部分不变？",
        "A: 使用区域编辑功能，明确指定需要编辑的区域，其他部分将保持不变。"
    ),
    (
        "Q: 可以撤销编辑操作吗？",
        "A: 编辑完成后无法撤销，建议在重要操作前保存原始图片的备份。"
    ),
    (
        "Q: 支持哪些图片格式？",
        "A: 支持 JPEG、PNG、WebP、GIF 等常见格式，推荐使用 PNG 以获得最佳质量。"
    ),
    (
        "Q: API 调用失败怎么办？",
        "A: 检查网络连接和 API 密钥配置，查看错误信息并根据错误类型采取相应措施。"
    ),
]

for i, (q, a) in enumerate(faqs, 1):
    story.append(Paragraph(f"6.{i} {q}", heading2_style))
    story.append(Paragraph(a, body_style))
    story.append(Spacer(1, 0.3*cm))

story.append(PageBreak())

# Chapter 7: Example Code
story.append(Paragraph("7. 示例代码", heading1_style))
story.append(Paragraph("7.1 基础编辑示例", heading2_style))
story.append(Paragraph(
    "以下是一个简单的 Python 示例，展示如何使用 Image-Edit 进行基础编辑：",
    body_style
))

example1 = '''
# 导入 Image-Edit 技能
from skills import image_edit

# 准备输入图片
input_image = "portrait.jpg"

# 编辑指令
prompt = "将这张照片转换为梵高风格的油画，使用鲜艳的色彩和厚重的笔触"

# 调用 Image-Edit
result = image_edit.edit(
    image_path=input_image,
    prompt=prompt,
    strength=0.8,
    steps=30
)

# 保存结果
result.save("oil_painting_portrait.jpg")
print("编辑完成！")
'''
story.append(Paragraph(example1, code_style))

story.append(Paragraph("7.2 风格迁移示例", heading2_style))
style_example = '''
# 风格迁移：应用艺术风格到照片
result = image_edit.style_transfer(
    source_image="city_photo.jpg",
    reference_image="starry_night.jpg",
    prompt="将城市照片转换为梵高《星空》的艺术风格",
    strength=0.7,
    guidance_scale=10.0
)

result.save("starry_night_city.jpg")
'''
story.append(Paragraph(style_example, code_style))

story.append(Paragraph("7.3 区域编辑示例", heading2_style))
region_example = '''
# 区域编辑：修改人物发色
result = image_edit.edit_region(
    image_path="portrait.jpg",
    region="人物的头发",
    prompt="将头发颜色改为栗棕色，保持自然的发丝质感",
    strength=0.6
)

result.save("new_hair_color.jpg")
'''
story.append(Paragraph(region_example, code_style))

story.append(Spacer(1, 1*cm))
story.append(Paragraph("7.4 批量处理示例", heading2_style))
batch_example = '''
# 批量处理：统一风格转换
import os

input_dir = "photos/"
output_dir = "stylized/"
os.makedirs(output_dir, exist_ok=True)

for filename in os.listdir(input_dir):
    if filename.endswith(('.jpg', '.png')):
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, f"stylized_{filename}")
        
        result = image_edit.edit(
            image_path=input_path,
            prompt="转换为油画风格，使用印象派技法",
            strength=0.8,
            steps=25
        )
        
        result.save(output_path)
        print(f"已处理: {filename}")
'''
story.append(Paragraph(batch_example, code_style))

story.append(PageBreak())

# Appendix and Conclusion
story.append(Paragraph("附录", heading1_style))
story.append(Paragraph("A. 相关技能", heading2_style))
story.append(Paragraph(
    "<b>•</b> sophnet-image-generate - 从文本生成图像<br/>"
    "<b>•</b> sophnet-image-ocr - 从图像中提取文字<br/>"
    "<b>•</b> sophnet-smart-image-loader - 智能图像加载器<br/>"
    "<b>•</b> sophnet-sophon-key - Sophnet API 密钥管理",
    body_style
))

story.append(Paragraph("B. 参考资料", heading2_style))
story.append(Paragraph(
    "<b>•</b> Sophnet API 文档<br/>"
    "<b>•</b> Image-Edit GitHub 仓库<br/>"
    "<b>•</b> OpenClaw 技能中心 (clawhub.com)",
    body_style
))

story.append(Spacer(1, 1*cm))
story.append(Paragraph("结语", heading1_style))
story.append(Paragraph(
    "本教程涵盖了 Image-Edit 技能的核心功能和最佳实践。通过掌握这些知识和技巧，你可以充分发挥 Image-Edit 的强大功能，创造出令人惊艳的图像作品。",
    body_style
))
story.append(Paragraph(
    "如有任何问题或建议，欢迎通过社区反馈渠道与我们联系。祝你在图像编辑的旅程中取得丰硕成果！",
    body_style
))
story.append(Spacer(1, 0.5*cm))
story.append(Paragraph(
    "© 2026 Image-Edit 教程 | 基于 OpenClaw 技能系统",
    note_style
))

# Build the PDF
print("正在构建增强版 PDF...")
doc.build(story)
print(f"✓ 增强版 PDF 已创建: {output_path}")