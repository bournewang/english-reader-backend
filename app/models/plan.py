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
    subscriptions = db.relationship('Subscription', backref='article', lazy=True)
