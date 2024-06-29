from datetime import datetime
from app.extensions import db

class Subscription(db.Model):
    id = db.Column(db.String(100), nullable=False, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    plan_id = db.Column(db.String(100), db.ForeignKey('plan.id'), nullable=False)
    plan_name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='PENDING')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def info(self):        
        return {
            'id': self.id,
            'user_id': self.user_id,
            'plan_id': self.plan_id,
            'plan_name': self.plan_name,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }