from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models.category import Category
from models.user import User
from werkzeug.security import check_password_hash

categories_bp = Blueprint('categories', __name__)


@categories_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user_categories = Category.query.filter_by(user_id=current_user.id, is_default=False).all()

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'update_profile':
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip().lower()

            if not name or len(name) < 2:
                flash('Nome deve ter pelo menos 2 caracteres.', 'danger')
            elif not email or '@' not in email:
                flash('Email inválido.', 'danger')
            elif email != current_user.email and User.query.filter_by(email=email).first():
                flash('Este email já está em uso.', 'danger')
            else:
                current_user.name = name
                current_user.email = email
                db.session.commit()
                flash('Perfil atualizado com sucesso!', 'success')

        elif action == 'change_password':
            current_pwd = request.form.get('current_password', '')
            new_pwd = request.form.get('new_password', '')
            confirm_pwd = request.form.get('confirm_password', '')

            if not current_user.check_password(current_pwd):
                flash('Senha atual incorreta.', 'danger')
            elif len(new_pwd) < 6:
                flash('Nova senha deve ter pelo menos 6 caracteres.', 'danger')
            elif new_pwd != confirm_pwd:
                flash('As senhas não coincidem.', 'danger')
            else:
                current_user.set_password(new_pwd)
                db.session.commit()
                flash('Senha alterada com sucesso!', 'success')

        elif action == 'add_category':
            cat_name = request.form.get('category_name', '').strip()
            if not cat_name:
                flash('Nome da categoria é obrigatório.', 'danger')
            elif Category.query.filter_by(name=cat_name, user_id=current_user.id).first():
                flash('Você já tem uma categoria com este nome.', 'danger')
            else:
                new_cat = Category(name=cat_name, user_id=current_user.id, is_default=False)
                db.session.add(new_cat)
                db.session.commit()
                flash('Categoria criada com sucesso!', 'success')

        return redirect(url_for('categories.profile'))

    return render_template('profile.html', user_categories=user_categories)


@categories_bp.route('/categories/delete/<int:cat_id>', methods=['POST'])
@login_required
def delete_category(cat_id):
    cat = Category.query.filter_by(id=cat_id, user_id=current_user.id, is_default=False).first_or_404()
    db.session.delete(cat)
    db.session.commit()
    flash('Categoria excluída.', 'success')
    return redirect(url_for('categories.profile'))
