from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.looking_word import LookingWord
from ..extensions import db

looking_word_bp = Blueprint('looking_word', __name__)

@looking_word_bp.route('/add', methods=['POST'])
@jwt_required()
def add_looking_word():
    data = request.get_json()
    current_user_id = get_jwt_identity()
    new_looking_word = LookingWord(
        user_id=current_user_id,
        word=data['word'],
        article_id=data['article_id'],
        paragraph_id=data['paragraph_id']
    )
    # print(vars(new_looking_word))
    db.session.add(new_looking_word)
    db.session.commit()
    return jsonify({
            'success':True, 
            'message': 'Word added to history successfully', 
            "data": {
                'id': new_looking_word.id,
                'article_id': new_looking_word.article_id,
                'paragraph_id': new_looking_word.paragraph_id,
            }
        }), 201

@looking_word_bp.route('/get', methods=['GET'])
@jwt_required()
def get_looking_word():
    current_user_id = get_jwt_identity()
    looking_words = LookingWord.query.filter_by(user_id=current_user_id).order_by(LookingWord.created_at.desc()).all()

    word_list = [{
        'word': lw.word,
        'article_id': lw.article_id,
        'article_title': lw.article.title,
        'paragraph_id': lw.paragraph_id,
        'paragraph_text': lw.paragraph.text,
        'created_at': lw.created_at
    } for lw in looking_words]

    return jsonify({"success": True, "data": word_list}), 200

# add a api filter by article id
@looking_word_bp.route('/get/by_article/<int:article_id>', methods=['GET'])
@jwt_required()
def get_looking_word_by_article_id(article_id):
    current_user_id = get_jwt_identity()
    looking_words = LookingWord.query.filter_by(user_id=current_user_id, article_id=article_id).all()

    word_list = [{
        'word': lw.word,
        'article_id': lw.article_id,
        'paragraph_id': lw.paragraph_id,
        'created_at': lw.created_at
    } for lw in looking_words]

    return jsonify({"success": True, "data": word_list}), 200