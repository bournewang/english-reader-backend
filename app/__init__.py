from flask import Flask
from .extensions import db, migrate, jwt, bcrypt
from .routes import auth_bp, articles_bp, unfamiliar_word_bp, stats_bp, order_bp, paypal_bp
from .helpers import check_if_token_is_revoked

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(articles_bp, url_prefix='/articles')
    app.register_blueprint(unfamiliar_word_bp, url_prefix='/unfamiliar_word')
    app.register_blueprint(stats_bp, url_prefix='/stats')
    app.register_blueprint(order_bp, url_prefix='/order')
    app.register_blueprint(paypal_bp, url_prefix='/paypal')

    return app

@jwt.token_in_blocklist_loader
def is_token_revoked(jwt_header, jwt_payload):
    return check_if_token_is_revoked(jwt_header, jwt_payload)
