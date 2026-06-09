import io
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                 TableStyle, HRFlowable)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from sqlalchemy import func
from models.income import Income
from models.expense import Expense
from models.category import Category
from extensions import db
from utils.currency import format_kwanza


def generate_pdf_report(user, date_from=None, date_to=None):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()
    PRIMARY_COLOR = colors.HexColor('#6366f1')
    SUCCESS_COLOR = colors.HexColor('#10b981')
    DANGER_COLOR = colors.HexColor('#ef4444')
    LIGHT_BG = colors.HexColor('#f8fafc')
    DARK_TEXT = colors.HexColor('#1e293b')

    style_title = ParagraphStyle('Title', parent=styles['Title'],
                                  fontSize=22, textColor=PRIMARY_COLOR,
                                  spaceAfter=4, alignment=TA_CENTER)
    style_subtitle = ParagraphStyle('Subtitle', parent=styles['Normal'],
                                     fontSize=11, textColor=colors.HexColor('#64748b'),
                                     spaceAfter=2, alignment=TA_CENTER)
    style_section = ParagraphStyle('Section', parent=styles['Heading2'],
                                    fontSize=13, textColor=DARK_TEXT,
                                    spaceBefore=14, spaceAfter=6)
    style_normal = ParagraphStyle('Normal2', parent=styles['Normal'],
                                   fontSize=9, textColor=DARK_TEXT)
    style_right = ParagraphStyle('Right', parent=styles['Normal'],
                                  fontSize=9, alignment=TA_RIGHT)

    # Build queries
    income_query = Income.query.filter_by(user_id=user.id)
    expense_query = Expense.query.filter_by(user_id=user.id)

    if date_from:
        income_query = income_query.filter(Income.date >= date_from)
        expense_query = expense_query.filter(Expense.date >= date_from)
    if date_to:
        income_query = income_query.filter(Income.date <= date_to)
        expense_query = expense_query.filter(Expense.date <= date_to)

    incomes = income_query.order_by(Income.date.desc()).all()
    expenses = expense_query.order_by(Expense.date.desc()).all()

    total_income = sum(float(i.amount) for i in incomes)
    total_expense = sum(float(e.amount) for e in expenses)
    balance = total_income - total_expense

    elements = []

    # Header
    elements.append(Paragraph("💰 Sistema de Gestão de Gastos Pessoais - Angola", style_title))
    elements.append(Paragraph(f"Relatório Financeiro — {user.name}", style_subtitle))

    period_text = "Período: Todo o histórico"
    if date_from and date_to:
        period_text = f"Período: {date_from.strftime('%d/%m/%Y')} a {date_to.strftime('%d/%m/%Y')}"
    elif date_from:
        period_text = f"A partir de: {date_from.strftime('%d/%m/%Y')}"
    elif date_to:
        period_text = f"Até: {date_to.strftime('%d/%m/%Y')}"

    elements.append(Paragraph(period_text, style_subtitle))
    elements.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}", style_subtitle))
    elements.append(Spacer(1, 0.3*cm))
    elements.append(HRFlowable(width="100%", thickness=2, color=PRIMARY_COLOR))
    elements.append(Spacer(1, 0.4*cm))

    # Summary Cards
    elements.append(Paragraph("Resumo Financeiro", style_section))

    balance_color = SUCCESS_COLOR if balance >= 0 else DANGER_COLOR
    summary_data = [
        ['📈 Receitas', '📉 Despesas', '💰 Saldo'],
        [
            Paragraph(f"<font color='#10b981'><b>{format_kwanza(total_income)}</b></font>", styles['Normal']),
            Paragraph(f"<font color='#ef4444'><b>{format_kwanza(total_expense)}</b></font>", styles['Normal']),
            Paragraph(f"<b>{format_kwanza(balance)}</b>", styles['Normal']),
        ]
    ]

    summary_table = Table(summary_data, colWidths=[5.5*cm, 5.5*cm, 5.5*cm])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY_COLOR),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [LIGHT_BG, colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('ROUNDEDCORNERS', [4, 4, 4, 4]),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 0.5*cm))

    # Incomes Table
    elements.append(Paragraph(f"Receitas ({len(incomes)} registros)", style_section))

    if incomes:
        income_data = [['Data', 'Título', 'Categoria', 'Valor']]
        for inc in incomes:
            income_data.append([
                inc.date.strftime('%d/%m/%Y'),
                inc.title[:45] + ('...' if len(inc.title) > 45 else ''),
                inc.category.name if inc.category else 'N/A',
                format_kwanza(inc.amount)
            ])
        income_data.append(['', '', 'TOTAL', format_kwanza(total_income)])

        income_table = Table(income_data, colWidths=[2.8*cm, 7.5*cm, 3.5*cm, 2.7*cm])
        income_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), SUCCESS_COLOR),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, LIGHT_BG]),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#d1fae5')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#e2e8f0')),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ]))
        elements.append(income_table)
    else:
        elements.append(Paragraph("Nenhuma receita encontrada no período.", style_normal))

    elements.append(Spacer(1, 0.5*cm))

    # Expenses Table
    elements.append(Paragraph(f"Despesas ({len(expenses)} registros)", style_section))

    if expenses:
        expense_data = [['Data', 'Título', 'Categoria', 'Valor']]
        for exp in expenses:
            expense_data.append([
                exp.date.strftime('%d/%m/%Y'),
                exp.title[:45] + ('...' if len(exp.title) > 45 else ''),
                exp.category.name if exp.category else 'N/A',
                format_kwanza(exp.amount)
            ])
        expense_data.append(['', '', 'TOTAL', format_kwanza(total_expense)])

        expense_table = Table(expense_data, colWidths=[2.8*cm, 7.5*cm, 3.5*cm, 2.7*cm])
        expense_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), DANGER_COLOR),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, LIGHT_BG]),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#fee2e2')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#e2e8f0')),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ]))
        elements.append(expense_table)
    else:
        elements.append(Paragraph("Nenhuma despesa encontrada no período.", style_normal))

    elements.append(Spacer(1, 0.5*cm))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e2e8f0')))
    elements.append(Spacer(1, 0.3*cm))

    footer_style = ParagraphStyle('Footer', parent=styles['Normal'],
                                   fontSize=8, textColor=colors.HexColor('#94a3b8'),
                                   alignment=TA_CENTER)
    elements.append(Paragraph(
        "Sistema de Gestão de Gastos Pessoais • Angola • Relatório gerado automaticamente",
        footer_style
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer
