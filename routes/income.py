from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from extensions import db
from models.income import Income
from models.category import Category

income_bp = Blueprint('income', __name__)


def get_user_categories(user_id):
    defaults = Category.query.filter_by(is_default=True).all()
    customs = Category.query.filter_by(user_id=user_id, is_default=False).all()
    return defaults + customs


@income_bp.route('/incomes')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    category_id = request.args.get('category_id', type=int)
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')

    query = Income.query.filter_by(user_id=current_user.id)

    if search:
        query = query.filter(Income.title.ilike(f'%{search}%'))
    if category_id:
        query = query.filter_by(category_id=category_id)
    if date_from:
        try:
            query = query.filter(Income.date >= datetime.strptime(date_from, '%Y-%m-%d').date())
        except ValueError:
            pass
    if date_to:
        try:
            query = query.filter(Income.date <= datetime.strptime(date_to, '%Y-%m-%d').date())
        except ValueError:
            pass

    incomes = query.order_by(Income.date.desc()).paginate(page=page, per_page=10, error_out=False)
    categories = get_user_categories(current_user.id)

    return render_template('incomes.html',
                           incomes=incomes,
                           categories=categories,
                           search=search,
                           category_id=category_id,
                           date_from=date_from,
                           date_to=date_to)


@income_bp.route('/incomes/add', methods=['GET', 'POST'])
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
            return render_template('incomes.html', categories=categories, mode='add')

        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Data inválida.', 'danger')
            return render_template('incomes.html', categories=categories, mode='add')

        income = Income(
            user_id=current_user.id,
            title=title,
            amount=float(amount),
            category_id=category_id,
            date=date,
            description=description
        )
        db.session.add(income)
        db.session.commit()
        flash('Receita adicionada com sucesso!', 'success')
        return redirect(url_for('income.index'))

    return render_template('incomes.html', categories=categories, mode='add')


@income_bp.route('/incomes/edit/<int:income_id>', methods=['GET', 'POST'])
@login_required
def edit(income_id):
    income = Income.query.filter_by(id=income_id, user_id=current_user.id).first_or_404()
    categories = get_user_categories(current_user.id)

    if request.method == 'POST':
        income.title = request.form.get('title', '').strip()
        income.amount = float(request.form.get('amount', 0))
        income.category_id = request.form.get('category_id', type=int)
        income.description = request.form.get('description', '').strip()
        try:
            income.date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
        except (ValueError, TypeError):
            flash('Data inválida.', 'danger')
            return render_template('incomes.html', income=income, categories=categories, mode='edit')

        db.session.commit()
        flash('Receita atualizada com sucesso!', 'success')
        return redirect(url_for('income.index'))

    return render_template('incomes.html', income=income, categories=categories, mode='edit')


@income_bp.route('/incomes/delete/<int:income_id>', methods=['POST'])
@login_required
def delete(income_id):
    income = Income.query.filter_by(id=income_id, user_id=current_user.id).first_or_404()
    db.session.delete(income)
    db.session.commit()
    flash('Receita excluída com sucesso.', 'success')
    return redirect(url_for('income.index'))
