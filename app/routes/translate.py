# app/routes/translate.py

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import requests

translate_bp = Blueprint('translate', __name__)

@translate_bp.route('/text', methods=['POST'])
def translate_text():
    data = request.json
    text = data.get('text')
    target_lang = data.get('target_lang', 'zh-CN')

    if not text:
        return jsonify({'error': 'Text is required'}), 400

    # Create a cache key
    cache_key = f'{text}-{target_lang}'
    
    # Check if the translation is already in the cache
    cached_translation = current_app.cache.get(cache_key)
    if cached_translation:
        print("hit cache ")
        return jsonify({'data': cached_translation, 'success': True})

    subscription_key = current_app.config['TRANSLATE_API_KEY']
    location = current_app.config['TRANSLATE_LOCATION']
    endpoint = 'https://api.cognitive.microsofttranslator.com/translate?api-version=3.0'
    url = f'{endpoint}&to={target_lang}'

    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key,
        'Ocp-Apim-Subscription-Region': location,
        'Content-type': 'application/json'
    }

    body = [{'Text': text}]

    try:
        response = requests.post(url, headers=headers, json=body)
        response.raise_for_status()
        translation = response.json()[0]['translations'][0]['text']
        
        # Store the translation in the cache
        current_app.cache.set(cache_key, translation)
        
        return jsonify({'data': translation, 'success': True})
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500
