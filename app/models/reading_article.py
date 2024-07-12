from datetime import datetime
from ..extensions import db
from urllib.parse import urlparse
from flask_sqlalchemy import SQLAlchemy

class ReadingArticle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    word_count = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    unfamiliar_words = db.relationship('UnfamiliarWord', backref='reading_article', lazy=True)
    
    def brief(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'article_id': self.article_id,
            'title': self.title,
            'word_count': self.word_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        
    def json(self):
        info = self.brief()
        info['paragraphs'] = {p.id: p.text for p in self.article.paragraphs}
        info['unfamiliar_words'] = [lw.word for lw in list(set(self.unfamiliar_words))]
        return info
