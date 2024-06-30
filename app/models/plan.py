from datetime import datetime
from ..extensions import db
from urllib.parse import urlparse
from flask_sqlalchemy import SQLAlchemy

class Plan(db.Model):
    id = db.Column(db.String(100), nullable=False, primary_key=True)
    product_id = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    interval_unit = db.Column(db.String(50), nullable=False)
    interval_count = db.Column(db.Integer, nullable=False)
    value = db.Column(db.String(50), nullable=False)
    currency = db.Column(db.String(50), nullable=False)
    subscriptions = db.relationship('Subscription', backref='plan', lazy=True)

    def info(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'name': self.name,
            'description': self.description,
            'interval_unit': self.interval_unit,
            'interval_count': self.interval_count,
            'value': self.value,
            'currency': self.currency
        }

    def free():
        return {
            'id': 'free',
            'product_id': None,
            'name': 'Free Plan',
            'description': 'Limited Access to English Reader',
            'interval_unit': None,
            'interval_count': None,
            'value': None,
            'currency': None
        }