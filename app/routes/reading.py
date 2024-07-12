from flask import Flask, request, Blueprint, jsonify
from bs4 import BeautifulSoup
from ..article_helper import fetch_and_save_article
from ..models.reading_article import ReadingArticle
from ..models.article import Article
from ..extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import requests

reading_bp = Blueprint('reading', __name__)

# Register route
@reading_bp.route('/', methods=['GET'])
def fetch_reading_article():
    url = request.args.get('url')
    # if article with url exists, return the article
    article = Article.query.filter_by(url=url).first()
    if article:
        return jsonify({'data': article.json()}), 200

    user_id = None
    try:
        article = fetch_and_save_article(url, user_id)
    except requests.RequestException as e:
        return jsonify({"message": str(e)}), 500

    return jsonify({'data': article.json()}), 200
    # reading_article = ReadingArticle(
    #     user_id=user_id,
    #     article_id=article.id,
    #     created_at=datetime.utcnow()
    # )
    # db.session.add(reading_article)
    # db.session.commit()
    # return jsonify(reading_article.json()), 200