from datetime import datetime
from ..extensions import db, bcrypt

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # membership = db.Column(db.Enum('FREE', 'PREMIUM', 'VIP', name='membership_types'), default='FREE')
    premium = db.Column(db.Boolean, default=False)
    expires_at = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.Enum('ACTIVE', 'INACTIVE', 'BANNED', name='status_types'), default='ACTIVE')
    # history = db.relationship('History', backref='user', lazy=True)
    # subscriptions = db.relationship('Subscription', backref='user', lazy=True)
    locale = db.Column(db.String(10), default='')
    country = db.Column(db.String(32), default='') 
    subscriptions = db.relationship('Subscription', backref='user', lazy=True)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def verify_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def info(self):
        return {
            'id': self.id,
            'email': self.email,
            'created_at': self.created_at,
            'premium': self.premium,
            'expires_at': self.expires_at,
            'locale': self.locale,
            'country': self.country,
            'status': self.status
        }
