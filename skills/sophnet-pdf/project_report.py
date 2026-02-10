#!/usr/bin/env python3
"""
项目进度报告 PDF 生成器
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from datetime import datetime

# 创建 PDF 文档
output_file = "/tmp/project_progress_report.pdf"
doc = SimpleDocTemplate(
    output_file,
    pagesize=letter,
    rightMargin=0.75*inch,
    leftMargin=0.75*inch,
    topMargin=0.75*inch,
    bottomMargin=0.75*inch
)

# 获取样式并创建自定义样式
styles = getSampleStyleSheet()

# 标题样式
title_style = ParagraphStyle(
    'CustomTitle',
    parent=styles['Heading1'],
    fontSize=24,
    textColor=colors.HexColor('#2C3E50'),
    spaceAfter=30,
    alignment=TA_CENTER,
    fontName='Helvetica-Bold'
)

# 日期样式
date_style = ParagraphStyle(
    'Date',
    parent=styles['Normal'],
    fontSize=12,
    textColor=colors.HexColor('#666666'),
    alignment=TA_CENTER,
    spaceAfter=40
)

# 标题样式
heading_style = ParagraphStyle(
    'Heading',
    parent=styles['Heading2'],
    fontSize=18,
    textColor=colors.HexColor('#2C3E50'),
    spaceBefore=20,
    spaceAfter=10,
    fontName='Helvetica-Bold'
)

# 内容样式
body_style = ParagraphStyle(
    'Body',
    parent=styles['Normal'],
    fontSize=12,
    textColor=colors.HexColor('#333333'),
    spaceAfter=12,
    leading=18
)

# 构建文档内容
story = []

# 标题
title = Paragraph("项目进度报告", title_style)
story.append(title)

# 日期
current_date = datetime.now().strftime("%Y年%m月%d日")
date = Paragraph(f"报告日期：{current_date}", date_style)
story.append(date)

# 进度项目
heading = Paragraph("当前进度", heading_style)
story.append(heading)

# 进度项目数据
progress_items = [
    ["项目阶段", "完成状态", "进度说明"],
    ["需求分析与设计", "已完成", "已完成所有需求文档编写，通过了技术评审会议，设计方案已确认。"],
    ["核心功能开发", "进行中", "主要模块开发进度达到75%，API接口已完成80%，预计本周完成。"],
    ["测试与优化", "待开始", "已制定详细测试计划，准备在开发完成后启动单元测试和集成测试。"]
]

# 创建表格
table = Table(progress_items, colWidths=[2.5*inch, 2*inch, 3.5*inch])
table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498DB')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 12),
    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F7F9F9')]),
    ('FONTSIZE', (0, 1), (-1, -1), 11),
    ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
    ('TOPPADDING', (0, 0), (-1, -1), 12),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ('LEFTPADDING', (0, 0), (-1, -1), 10),
    ('RIGHTPADDING', (0, 0), (-1, -1), 10),
]))

story.append(table)

# 添加一些间距
story.append(Spacer(1, 20))

# 总结段落
summary_title = Paragraph("总体评估", heading_style)
story.append(summary_title)

summary_text = Paragraph(
    "项目整体进展顺利，按计划推进。团队协作良好，关键里程碑按时完成。下阶段将重点关注测试和优化工作，确保项目按时交付。",
    body_style
)
story.append(summary_text)

# 生成 PDF
print(f"Creating PDF: {output_file}")
doc.build(story)
print(f"PDF created successfully!")