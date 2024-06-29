from datetime import datetime
from app.extensions import db

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subscription_id = db.Column(db.String(100), nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    plan_id = db.Column(db.String(100), nullable=False)
    plan_name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='PENDING')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    @classmethod
    def find_by_subscription_id(cls, subscription_id):
        return cls.query.filter_by(subscription_id=subscription_id).first()

    def info(self):        
        return {
            'subscription_id': self.subscription_id,
            'user_id': self.user_id,
            'plan_id': self.plan_id,
            'plan_name': self.plan_name,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def __repr__(self):
        return f'<Subscription {self.subscription_id}>'
