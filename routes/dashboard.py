from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func, extract
from datetime import datetime, date
from models.income import Income
from models.expense import Expense
from models.category import Category
from extensions import db

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard')
@login_required
def index():
    """
    Dashboard principal com indicadores angolanos:
    - Saldo Disponível
    - Receitas do Mês
    - Despesas do Mês
    - Total de Transações
    - Taxa de Poupança
    """
    from sqlalchemy import and_
    
    # Calculate current month totals
    now = datetime.now()
    current_month_start = date(now.year, now.month, 1)
    if now.month == 12:
        current_month_end = date(now.year + 1, 1, 1)
    else:
        current_month_end = date(now.year, now.month + 1, 1)
    
    # Monthly values
    monthly_income = db.session.query(func.sum(Income.amount)).filter(
        Income.user_id == current_user.id,
        Income.date >= current_month_start,
        Income.date < current_month_end
    ).scalar() or 0
    
    monthly_expense = db.session.query(func.sum(Expense.amount)).filter(
        Expense.user_id == current_user.id,
        Expense.date >= current_month_start,
        Expense.date < current_month_end
    ).scalar() or 0
    
    # All-time totals
    total_income = db.session.query(func.sum(Income.amount)).filter_by(user_id=current_user.id).scalar() or 0
    total_expense = db.session.query(func.sum(Expense.amount)).filter_by(user_id=current_user.id).scalar() or 0
    balance = float(total_income) - float(total_expense)
    
    # Calculate savings rate (% of income saved this month)
    monthly_income_float = float(monthly_income)
    monthly_savings = monthly_income_float - float(monthly_expense)
    savings_rate = ((monthly_savings / monthly_income_float) * 100) if monthly_income_float > 0 else 0
    
    # Transaction counts
    income_count = Income.query.filter_by(user_id=current_user.id).count()
    expense_count = Expense.query.filter_by(user_id=current_user.id).count()
    total_transactions = income_count + expense_count

    # Recent transactions (last 8)
    recent_incomes = Income.query.filter_by(user_id=current_user.id).order_by(Income.date.desc()).limit(5).all()
    recent_expenses = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.date.desc()).limit(5).all()

    # Merge and sort recent transactions
    recent_transactions = []
    for i in recent_incomes:
        recent_transactions.append({
            'type': 'income', 'title': i.title,
            'amount': float(i.amount), 'date': i.date,
            'category': i.category.name if i.category else 'N/A'
        })
    for e in recent_expenses:
        recent_transactions.append({
            'type': 'expense', 'title': e.title,
            'amount': float(e.amount), 'date': e.date,
            'category': e.category.name if e.category else 'N/A'
        })
    recent_transactions.sort(key=lambda x: x['date'], reverse=True)
    recent_transactions = recent_transactions[:8]

    return render_template('dashboard.html',
                           balance=balance,
                           total_income=float(total_income),
                           total_expense=float(total_expense),
                           monthly_income=float(monthly_income),
                           monthly_expense=float(monthly_expense),
                           monthly_savings=monthly_savings,
                           savings_rate=savings_rate,
                           total_transactions=total_transactions,
                           recent_transactions=recent_transactions)


@dashboard_bp.route('/api/chart/expenses-by-category')
@login_required
def expenses_by_category():
    results = db.session.query(
        Category.name, func.sum(Expense.amount)
    ).join(Expense, Expense.category_id == Category.id)\
     .filter(Expense.user_id == current_user.id)\
     .group_by(Category.name).all()

    labels = [r[0] for r in results]
    data = [float(r[1]) for r in results]
    colors = ['#6366f1', '#f59e0b', '#10b981', '#ef4444',
              '#3b82f6', '#8b5cf6', '#ec4899', '#14b8a6']

    return jsonify({'labels': labels, 'data': data, 'colors': colors[:len(labels)]})


@dashboard_bp.route('/api/chart/monthly-summary')
@login_required
def monthly_summary():
    current_year = datetime.now().year
    months = list(range(1, 13))
    month_names = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
                   'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']

    income_by_month = db.session.query(
        extract('month', Income.date).label('month'),
        func.sum(Income.amount).label('total')
    ).filter(
        Income.user_id == current_user.id,
        extract('year', Income.date) == current_year
    ).group_by(extract('month', Income.date)).all()

    expense_by_month = db.session.query(
        extract('month', Expense.date).label('month'),
        func.sum(Expense.amount).label('total')
    ).filter(
        Expense.user_id == current_user.id,
        extract('year', Expense.date) == current_year
    ).group_by(extract('month', Expense.date)).all()

    income_map = {int(r.month): float(r.total) for r in income_by_month}
    expense_map = {int(r.month): float(r.total) for r in expense_by_month}

    income_data = [income_map.get(m, 0) for m in months]
    expense_data = [expense_map.get(m, 0) for m in months]

    return jsonify({
        'labels': month_names,
        'income': income_data,
        'expense': expense_data,
        'year': current_year
    })
