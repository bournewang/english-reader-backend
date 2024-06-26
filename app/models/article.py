from datetime import datetime
from ..extensions import db
from urllib.parse import urlparse
from flask_sqlalchemy import SQLAlchemy

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    word_count = db.Column(db.Integer, nullable=False)
    author = db.Column(db.String(100), nullable=True)
    url = db.Column(db.String(500), nullable=True, index=True)
    site = db.Column(db.String(100), nullable=True, index=True)
    site_name = db.Column(db.String(100), nullable=True)
    site_icon = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    paragraphs = db.relationship('Paragraph', backref='article', lazy=True)
    unfamiliar_words = db.relationship('LookingWord', backref='article', lazy=True)

    @staticmethod
    def extract_site(url):
        parsed_url = urlparse(url)
        return parsed_url.netloc

    @staticmethod
    def before_insert(mapper, connection, target):
        if target.url:
            target.site = Article.extract_site(target.url)

    def brief(self):
        return {
            'id': self.id,
            'title': self.title,
            'word_count': self.word_count,
            'author': self.author,
            'url': self.url,
            'site': self.site,
            'site_name': self.site_name,
            'site_icon': self.site_icon,        
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    def json(self):
        info = self.brief()
        info['paragraphs'] = {p.id: p.text for p in self.paragraphs}
        info['unfamiliar_words'] = [lw.word for lw in list(set(self.unfamiliar_words))]
        return info

from sqlalchemy import event
event.listen(Article, 'before_insert', Article.before_insert)
event.listen(Article, 'before_update', Article.before_insert)