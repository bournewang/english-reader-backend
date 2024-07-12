from datetime import datetime
from ..extensions import db

class UnfamiliarWord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    word = db.Column(db.String(100), nullable=False)
    reading_article_id = db.Column(db.Integer, db.ForeignKey('reading_article.id'), nullable=False)
    paragraph_id = db.Column(db.Integer, db.ForeignKey('paragraph.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
