from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime
from extensions import db
from models.expense import Expense
from models.category import Category

expense_bp = Blueprint('expense', __name__)


def get_user_categories(user_id):
    defaults = Category.query.filter_by(is_default=True).all()
    customs = Category.query.filter_by(user_id=user_id, is_default=False).all()
    return defaults + customs


@expense_bp.route('/expenses')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    category_id = request.args.get('category_id', type=int)
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')

    query = Expense.query.filter_by(user_id=current_user.id)

    if search:
        query = query.filter(Expense.title.ilike(f'%{search}%'))
    if category_id:
        query = query.filter_by(category_id=category_id)
    if date_from:
        try:
            query = query.filter(Expense.date >= datetime.strptime(date_from, '%Y-%m-%d').date())
        except ValueError:
            pass
    if date_to:
        try:
            query = query.filter(Expense.date <= datetime.strptime(date_to, '%Y-%m-%d').date())
        except ValueError:
            pass

    expenses = query.order_by(Expense.date.desc()).paginate(page=page, per_page=10, error_out=False)
    categories = get_user_categories(current_user.id)

    return render_template('expenses.html',
                           expenses=expenses,
                           categories=categories,
                           search=search,
                           category_id=category_id,
                           date_from=date_from,
                           date_to=date_to)


@expense_bp.route('/expenses/add', methods=['GET', 'POST'])
@login_required
def add():
    categories = get_user_categories(current_user.id)

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        amount = request.form.get('amount', '')
        category_id = request.form.get('category_id', type=int)
        date_str = request.form.get('date', '')
        description = request.form.get('description', '').strip()

        errors = []
        if not title:
            errors.append('Título é obrigatório.')
        if not amount or float(amount) <= 0:
            errors.append('Valor deve ser maior que zero.')
        if not category_id:
            errors.append('Categoria é obrigatória.')
        if not date_str:
            errors.append('Data é obrigatória.')

        if errors:
            for e in errors:
                flash(e, 'danger')
            return render_template('expenses.html', categories=categories, mode='add')

        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Data inválida.', 'danger')
            return render_template('expenses.html', categories=categories, mode='add')

        expense = Expense(
            user_id=current_user.id,
            title=title,
            amount=float(amount),
            category_id=category_id,
            date=date,
            description=description
        )
        db.session.add(expense)
        db.session.commit()
        flash('Despesa adicionada com sucesso!', 'success')
        return redirect(url_for('expense.index'))

    return render_template('expenses.html', categories=categories, mode='add')


@expense_bp.route('/expenses/edit/<int:expense_id>', methods=['GET', 'POST'])
@login_required
def edit(expense_id):
    expense = Expense.query.filter_by(id=expense_id, user_id=current_user.id).first_or_404()
    categories = get_user_categories(current_user.id)

    if request.method == 'POST':
        expense.title = request.form.get('title', '').strip()
        expense.amount = float(request.form.get('amount', 0))
        expense.category_id = request.form.get('category_id', type=int)
        expense.description = request.form.get('description', '').strip()
        try:
            expense.date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
        except (ValueError, TypeError):
            flash('Data inválida.', 'danger')
            return render_template('expenses.html', expense=expense, categories=categories, mode='edit')

        db.session.commit()
        flash('Despesa atualizada com sucesso!', 'success')
        return redirect(url_for('expense.index'))

    return render_template('expenses.html', expense=expense, categories=categories, mode='edit')


@expense_bp.route('/expenses/delete/<int:expense_id>', methods=['POST'])
@login_required
def delete(expense_id):
    expense = Expense.query.filter_by(id=expense_id, user_id=current_user.id).first_or_404()
    db.session.delete(expense)
    db.session.commit()
    flash('Despesa excluída com sucesso.', 'success')
    return redirect(url_for('expense.index'))
