from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.article import Article
from ..models.paragraph import Paragraph
from ..extensions import db
import time

articles_bp = Blueprint('articles', __name__)

@articles_bp.route('/create', methods=['POST'])
@jwt_required()
def create_article():
    data = request.get_json()
    user_id = get_jwt_identity()
    paragraphs = data.get('paragraphs')

    try:
        paragraphs = [p for p in paragraphs if p and p.strip()]
        word_count = sum(len(paragraph.split()) for paragraph in paragraphs)

        new_article = Article(
            user_id=user_id, 
            title=data.get('title'),
            word_count=word_count,
            author=data.get('author'),
            url=data.get('url'),
            site_name=data.get('site_name'),
            site_icon=data.get('site_icon')
        )
        db.session.add(new_article)
        db.session.commit()  # Commit to get the article ID

        paragraph_objects = []
        for text in paragraphs:
            new_paragraph = Paragraph(article_id=new_article.id, text=text)
            paragraph_objects.append(new_paragraph)
            db.session.add(new_paragraph)

        db.session.flush()  # Ensure all paragraphs are added and IDs generated
        db.session.commit()  # Commit all changes

        # paragraph_mapping = {p.id: p.text for p in paragraph_objects}

        response = {
            'success': True,
            'message': 'Article created successfully',
            'data': new_article.json()
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

@articles_bp.route('/list', methods=['GET'])
@jwt_required()
def get_user_articles():
    user_id = get_jwt_identity()
    # make articles order by id desc
    articles = Article.query.filter_by(user_id=user_id).order_by(Article.id.desc()).all()
    articles_list = [article.brief() for article in articles]

    return jsonify({'success': True, 'data': articles_list})


@articles_bp.route('/<int:article_id>', methods=['GET'])
@jwt_required()
def get_article(article_id):
    article = Article.query.get_or_404(article_id)

    return jsonify({'success': True, 'data': article.json()}), 200
