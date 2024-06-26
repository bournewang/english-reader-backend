from ..extensions import db

class Paragraph(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    looking_words = db.relationship('LookingWord', backref='paragraph', lazy=True)
