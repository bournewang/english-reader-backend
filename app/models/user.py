from datetime import datetime
from ..extensions import db, bcrypt

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    membership = db.Column(db.Enum('FREE', 'PREMIUM', 'VIP', name='membership_types'), default='FREE')
    status = db.Column(db.Enum('ACTIVE', 'INACTIVE', 'BANNED', name='status_types'), default='ACTIVE')
    # history = db.relationship('History', backref='user', lazy=True)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def verify_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
