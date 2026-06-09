from flask import Flask
from extensions import db, login_manager
from config import config
from utils.currency import kwanza_filter, date_filter


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    login_manager.login_message_category = 'info'

    # Register Jinja filters for currency and date formatting
    app.jinja_env.filters['kwanza'] = kwanza_filter
    app.jinja_env.filters['format_date'] = date_filter

    with app.app_context():
        # Import models to register them with SQLAlchemy
        from models.user import User       # noqa: F401
        from models.category import Category  # noqa: F401
        from models.income import Income   # noqa: F401
        from models.expense import Expense # noqa: F401

        db.create_all()
        _seed_default_categories()

        # Register Blueprints
        from routes.auth import auth_bp
        from routes.dashboard import dashboard_bp
        from routes.income import income_bp
        from routes.expense import expense_bp
        from routes.reports import reports_bp
        from routes.categories import categories_bp

        app.register_blueprint(auth_bp)
        app.register_blueprint(dashboard_bp)
        app.register_blueprint(income_bp)
        app.register_blueprint(expense_bp)
        app.register_blueprint(reports_bp)
        app.register_blueprint(categories_bp)

    return app


def _seed_default_categories():
    """Seed default Angolan income and expense categories."""
    from models.category import Category
    
    # Angolan income categories
    income_categories = [
        'Salário',
        'Negócio',
        'Freelance',
        'Comissão',
        'Bónus',
        'Investimentos',
        'Outros'
    ]
    
    # Angolan expense categories
    expense_categories = [
        'Alimentação',
        'Táxi',
        'Transporte',
        'Combustível',
        'ENDE',
        'EPAL',
        'Internet',
        'Unitel',
        'Africell',
        'Movicel',
        'Educação',
        'Saúde',
        'Habitação',
        'Renda',
        'Impostos',
        'Outros'
    ]
    
    # Create income categories
    for name in income_categories:
        if not Category.query.filter_by(name=name, is_default=True).first():
            cat = Category(name=name, is_default=True)
            db.session.add(cat)
    
    # Create expense categories
    for name in expense_categories:
        if not Category.query.filter_by(name=name, is_default=True).first():
            cat = Category(name=name, is_default=True)
            db.session.add(cat)
    
    db.session.commit()


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
