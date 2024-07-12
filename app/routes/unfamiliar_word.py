from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.unfamiliar_word import UnfamiliarWord
from ..models.user import User
from ..models.reading_article import ReadingArticle
from ..extensions import db

unfamiliar_word_bp = Blueprint('unfamiliar_word', __name__)

@unfamiliar_word_bp.route('/add', methods=['POST'])
@jwt_required()
def add_unfamiliar_word():
    data = request.get_json()
    current_user_id = get_jwt_identity()

    # Check if the word already exists for the user in the specified reading_article
    existing_word = UnfamiliarWord.query.filter_by(
        user_id=current_user_id,
        word=data['word'],
        reading_article_id=data['reading_article_id']
    ).first()

    if existing_word:
        word = existing_word   
    else:
        new_unfamiliar_word = UnfamiliarWord(
            user_id=current_user_id,
            word=data['word'],
            reading_article_id=data['reading_article_id'],
            paragraph_id=data['paragraph_id']
        )
        # print(vars(new_unfamiliar_word))
        db.session.add(new_unfamiliar_word)
        db.session.commit()

        word = new_unfamiliar_word     

    reading_article = word.reading_article
    return jsonify({
            'success':True, 
            'message': 'Word added to history successfully', 
            "data": {
                'id': word.id,
                'reading_article_id': word.reading_article_id,
                'paragraph_id': word.paragraph_id,
                'reading_article': {
                    'id': reading_article.id,
                    'title': reading_article.title,
                    'unfamiliar_words': [lw.word for lw in list(set(reading_article.unfamiliar_words))]
                }
            }
        }), 200

@unfamiliar_word_bp.route('/delete', methods=['DELETE'])
@jwt_required()
def delete_unfamiliar_word():
    data = request.get_json()
    current_user_id = get_jwt_identity()
    word = data.get('word')
    reading_article_id = data.get('reading_article_id')
    paragraph_id = data.get('paragraph_id')

    try:
        looking_word = UnfamiliarWord.query.filter_by(
            user_id=current_user_id,
            word=word,
            reading_article_id=reading_article_id,
            # paragraph_id=paragraph_id
        ).first()

        if looking_word:
            db.session.delete(looking_word)
            db.session.commit()
            reading_article = ReadingArticle.query.get(reading_article_id)
            return jsonify({
                    'success':True, 
                    'message': 'Word added to history successfully', 
                    "data": {
                        'id': None,
                        'reading_article_id': reading_article_id,
                        'paragraph_id': paragraph_id,
                        'reading_article': {
                            'id': reading_article.id,
                            'title': reading_article.title,
                            'unfamiliar_words': [lw.word for lw in list(set(reading_article.unfamiliar_words))]
                        }
                    }
                }), 200
        else:
            return jsonify({'success': False, 'message': 'Word not found'}), 404

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@unfamiliar_word_bp.route('/get', methods=['GET'])
@jwt_required()
def get_unfamiliar_word():
    user_id = get_jwt_identity()
    # unfamiliar_words = UnfamiliarWord.query.filter_by(user_id=user_id).order_by(UnfamiliarWord.created_at.desc()).all()
    user = User.query.get(user_id)
    # make reading_articles order by id desc
    unfamiliar_words = UnfamiliarWord.query.filter_by(user_id=user_id).order_by(UnfamiliarWord.id.desc())
    if not user.premium:
        unfamiliar_words = unfamiliar_words.limit(30)

    unfamiliar_words = unfamiliar_words.all()

    word_list = [{
        'word': lw.word,
        'reading_article_id': lw.reading_article_id,
        'reading_article_title': lw.reading_article.title,
        'paragraph_id': lw.paragraph_id,
        'paragraph_text': lw.paragraph.text,
        'created_at': lw.created_at
    } for lw in unfamiliar_words]

    return jsonify({"success": True, "data": word_list}), 200

# add a api filter by reading_article id
@unfamiliar_word_bp.route('/get/by_reading_article/<int:reading_article_id>', methods=['GET'])
@jwt_required()
def get_unfamiliar_word_by_reading_article_id(reading_article_id):
    current_user_id = get_jwt_identity()
    unfamiliar_words = UnfamiliarWord.query.filter_by(user_id=current_user_id, reading_article_id=reading_article_id).all()

    word_list = [{
        'word': lw.word,
        'reading_article_id': lw.reading_article_id,
        'paragraph_id': lw.paragraph_id,
        'created_at': lw.created_at
    } for lw in unfamiliar_words]

    return jsonify({"success": True, "data": word_list}), 200