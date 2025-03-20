# app/routes/translate.py
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import requests
import os
from openai import OpenAI
import json
import httpx

translate_bp = Blueprint('translate', __name__)

@translate_bp.route('/array', methods=['POST'])
def translate_array():
    data = request.json
    text = data.get('array')
    target_lang = data.get('target_lang', 'zh-CN')
    # combine the array into a string
    text = ' | '.join(text)

    client = OpenAI(
        # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
        api_key=os.getenv("DASHSCOPE_API_KEY"),  # 如何获取API Key：https://help.aliyun.com/zh/model-studio/developer-reference/get-api-key
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        http_client=httpx.Client(verify=False)
    )

    completion = client.chat.completions.create(
        model="deepseek-v3",  # 此处以 deepseek-r1 为例，可按需更换模型名称。
        messages=[
            {'role': 'user', 'content': '将下列内容翻译成中文，保留里面的|：' + text},
        ]
    )

    translation = completion.choices[0].message.content
    # split the string back into an array, and remove the space at head and tail
    return translation.split('|')
    # return translation

@translate_bp.route('/text', methods=['POST'])
def translate_text():
    data = request.json
    text = data.get('text')
    target_lang = data.get('target_lang', 'zh-CN')

    client = OpenAI(
        # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
        api_key=os.getenv("DASHSCOPE_API_KEY"),  # 如何获取API Key：https://help.aliyun.com/zh/model-studio/developer-reference/get-api-key
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        http_client=httpx.Client(verify=False)
    )

    completion = client.chat.completions.create(
        # model='qwen-plus',
        model="deepseek-v3",  # 此处以 deepseek-r1 为例，可按需更换模型名称。
        messages=[
            {'role': 'user', 'content': 'translate into Chinese: ' + text},
        ]
    )

    # In translate_array function
    translation = completion.choices[0].message.content.strip()
    return jsonify({'data': translation, 'success': True})

def translate_text_azure():
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
