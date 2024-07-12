from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.reading_article import ReadingArticle
from ..models.paragraph import Paragraph
from ..models.user import User
from ..extensions import db
import time

reading_articles_bp = Blueprint('reading_articles', __name__)

@reading_articles_bp.route('/create', methods=['POST'])
@jwt_required()
def create_reading_article():
    data = request.get_json()
    user_id = get_jwt_identity()
    article_id = data.get('article_id')
    # paragraphs = data.get('paragraphs')
    article = Article.query.get(article_id)
    if not article:
        return jsonify(
            success=False,
            message='Article does not exist.'
        )

    try:
        new_reading_article = ReadingArticle(
            user_id     =user_id, 
            article_id  =article_id,
            title       =article.title,
            word_count  = article.word_count,
        )
        db.session.add(new_reading_article)
        db.session.commit()  # Commit to get the reading_article ID

        response = {
            'success': True,
            'message': 'ReadingArticle created successfully',
            'data': new_reading_article.json()
        }
        return jsonify(response), 201

    except Exception as e:
        db.session.rollback()
        response = {
            'success': False,
            'message': str(e),
            'data': {}
        }
        return jsonify(response), 500

@reading_articles_bp.route('/list', methods=['GET'])
@jwt_required()
def get_user_reading_articles():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    reading_articles = ReadingArticle.query.filter_by(user_id=user_id).order_by(ReadingArticle.id.desc()).all()

    # reading_articles = reading_articles.all()
    reading_articles_list = [reading_article.brief() for reading_article in reading_articles]

    return jsonify({'success': True, 'data': reading_articles_list})


@reading_articles_bp.route('/<int:reading_article_id>', methods=['GET'])
@jwt_required()
def get_reading_article(reading_article_id):
    reading_article = ReadingArticle.query.get_or_404(reading_article_id)

    return jsonify({'success': True, 'data': reading_article.json()}), 200
