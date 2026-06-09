from extensions import db
from datetime import datetime
from decimal import Decimal


class Income(db.Model):
    __tablename__ = 'incomes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    description = db.Column(db.Text, nullable=True)
    date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Income {self.title} Kz{self.amount}>'

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'amount': float(self.amount),  # JSON serialization requires float
            'description': self.description,
            'date': self.date.strftime('%d/%m/%Y'),  # Angolan date format
            'category': self.category.name if self.category else 'N/A',
            'category_id': self.category_id,
        }
