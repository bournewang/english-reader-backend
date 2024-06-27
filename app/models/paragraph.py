from ..extensions import db

class Paragraph(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    unfamiliar_words = db.relationship('UnfamiliarWord', backref='paragraph', lazy=True)
