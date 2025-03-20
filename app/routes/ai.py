from flask import Blueprint, request, jsonify, session
from openai import OpenAI
import os
from typing import List, Dict
import uuid
import markdown

ai_bp = Blueprint('ai', __name__)
client = OpenAI(api_key=os.getenv('DASHSCOPE_API_KEY'), base_url=os.getenv('DASHSCOPE_API_URL'))

# In-memory storage for articles (for demonstration purposes)
# In production, consider using a database or other persistent storage
articles = {}

def generate_chat_messages(article: str, messages: List[Dict]) -> List[Dict]:
    # Initial system message defines the AI's role and context
    chat_messages = [
        {
            "role": "system",
            "content": """You are an expert English teacher. Your role is to:
1. Review student responses for grammar and vocabulary
2. Provide gentle corrections when needed
4. Ask engaging follow-up questions without asking my choice like in a quiz, untile I give you the instruction. 
    for example, you shouldn't ask me "Would you like to discuss any specific parts of the article further?", 
    instead, you should ask questions about the article content.
5. Keep the discussion focused on the article content.
6. Your answer should be brief, for too much words will make the user feel bored.
"""
        },
        {
            "role": "system",
            "content": f"Article context:\n{article}"
        }
    ]
    
    # Add conversation history
    chat_messages.extend(messages)
    
    return chat_messages

@ai_bp.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        chat_type = data.get('type', 'chat')
        messages = data.get('messages', [])

        if chat_type == 'initialize':
            if not data or 'article' not in data:
                return jsonify({'error': 'Article content is required'}), 400
            article = data['article']
            session_id = str(uuid.uuid4())
            articles[session_id] = article
            # For initialization, add a specific prompt to start the discussion
            messages = [
                {
                    "role": "user",
                    "content": "Please start a discussion about this article with an engaging question."
                }
            ]
        else:
            session_id = data.get('session_id')
            if not session_id or session_id not in articles:
                return jsonify({'error': 'Invalid session ID'}), 400
            article = articles[session_id]

        # Generate messages array for API call
        chat_messages = generate_chat_messages(article, messages)

        # Call DashScope API with the structured messages
        completion = client.chat.completions.create(
            model="qwen-omni-turbo",
            messages=chat_messages,
            stream=True,
            temperature=0.7,
            max_tokens=500
        )

        # Handle streaming response
        ai_response = ""
        try:
            for chunk in completion:
                if hasattr(chunk, 'choices') and chunk.choices:
                    if hasattr(chunk.choices[0], 'delta'):
                        if chunk.choices[0].delta.content:
                            ai_response += chunk.choices[0].delta.content
                    elif hasattr(chunk.choices[0], 'message'):
                        if chunk.choices[0].message.content:
                            ai_response += chunk.choices[0].message.content

            if not ai_response:
                raise Exception('No response from AI')
            
            # Convert markdown to HTML
            # html_response = markdown.markdown(
            #     ai_response,
            #     extensions=['extra', 'nl2br', 'sane_lists']
            # )

            response_data = {
                # 'message': html_response,
                # 'raw': ai_response  # Optional: include raw markdown
                'message': ai_response,
            }
            if chat_type == 'initialize':
                response_data['session_id'] = session_id

            return jsonify(response_data)

        except Exception as e:
            print(f"Streaming error: {str(e)}")
            return jsonify({'error': 'Failed to process streaming response'}), 500

    except Exception as e:
        print(f"Chat error: {str(e)}")
        return jsonify({'error': 'Failed to process chat request'}), 500

# Optional: Add rate limiting
from functools import wraps
from time import time
from flask import session

def rate_limit(limit: int, window: int):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            now = time()
            rate_key = f'rate_limit_{f.__name__}'
            window_key = f'rate_window_{f.__name__}'
            
            if rate_key not in session:
                session[rate_key] = 0
                session[window_key] = now

            window_start = session[window_key]
            if now - window_start > window:
                session[rate_key] = 0
                session[window_key] = now
            
            if session[rate_key] >= limit:
                return jsonify({'error': 'Rate limit exceeded'}), 429

            session[rate_key] = session[rate_key] + 1
            return f(*args, **kwargs)
        return wrapped
    return decorator

# Example usage of rate limiting (optional)
# @ai.route('/chat', methods=['POST'])
# @rate_limit(limit=10, window=60)  # 10 requests per minute
# def chat():
#     ...