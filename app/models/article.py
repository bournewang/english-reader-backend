from datetime import datetime
from ..extensions import db

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    word_count = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    paragraphs = db.relationship('Paragraph', backref='article', lazy=True)
    looking_words = db.relationship('LookingWord', backref='article', lazy=True)
