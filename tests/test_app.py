import pytest
from flask import json
from app.models.user import User
from app.models.article import Article
from app.models.paragraph import Paragraph
from app.models.looking_word import LookingWord

def test_register_user(client):
    response = client.post('/auth/register', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    assert response.status_code == 201
    assert response.json['message'] == 'User registered successfully'

def test_login_user(client):
    client.post('/auth/register', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    response = client.post('/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    assert response.status_code == 200
    assert 'access_token' in response.json

def test_create_article(client):
    client.post('/auth/register', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    login_response = client.post('/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    token = login_response.json['access_token']
    
    response = client.post('/articles/create', json={
        'title': 'Test Article',
        'paragraphs': ['Paragraph 1', 'Paragraph 2']
    }, headers={'Authorization': f'Bearer {token}'})
    
    assert response.status_code == 201
    assert response.json['message'] == 'Article created successfully'
    assert 'id' in response.json['data']

def test_get_article(client):
    client.post('/auth/register', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    login_response = client.post('/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    token = login_response.json['access_token']
    
    create_response = client.post('/articles/create', json={
        'title': 'Test Article',
        'paragraphs': ['Paragraph 1', 'Paragraph 2']
    }, headers={'Authorization': f'Bearer {token}'})
    article_id = create_response.json['data']['id']
    
    response = client.get(f'/articles/{article_id}', headers={'Authorization': f'Bearer {token}'})
    
    assert response.status_code == 200
    assert response.json['data']['id'] == article_id
    assert response.json['data']['title'] == 'Test Article'

def test_get_user_articles(client):
    client.post('/auth/register', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    login_response = client.post('/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    token = login_response.json['access_token']
    
    create_response = client.post('/articles/create', json={
        'title': 'Test Article',
        'paragraphs': ['Paragraph 1', 'Paragraph 2']
    }, headers={'Authorization': f'Bearer {token}'})
    article_id = create_response.json['data']['id']
    
    response = client.get(f'/articles/list', headers={'Authorization': f'Bearer {token}'})
    
    assert response.status_code == 200
    assert response.json['data'][0]['id'] == article_id
    assert response.json['data'][0]['title'] == 'Test Article'


def test_add_looking_word(client):
    client.post('/auth/register', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    login_response = client.post('/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    token = login_response.json['access_token']
    
    create_response = client.post('/articles/create', json={
        'title': 'Test Article',
        'paragraphs': ['Paragraph 1', 'Paragraph 2']
    }, headers={'Authorization': f'Bearer {token}'})
    article_id = create_response.json['data']['id']
    # print(f'article id: {article_id}')
    
    response = client.post('/looking_word/add', json={
        'word': 'test',
        'article_id': article_id,
        'paragraph_id': 1
    }, headers={'Authorization': f'Bearer {token}'})
    print(response.json)
    
    assert response.status_code == 201
    assert response.json['message'] == 'Word added to history successfully'
    assert response.json['data']['article_id'] == article_id

def test_get_looking_word(client):
    client.post('/auth/register', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    login_response = client.post('/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    token = login_response.json['access_token']
    
    create_response = client.post('/articles/create', json={
        'title': 'Test Article',
        'paragraphs': ['Paragraph 1', 'Paragraph 2']
    }, headers={'Authorization': f'Bearer {token}'})
    article_id = create_response.json['data']['id']
    
    client.post('/looking_word/add', json={
        'word': 'test',
        'article_id': article_id,
        'paragraph_id': 1
    }, headers={'Authorization': f'Bearer {token}'})
    
    response = client.get('/looking_word/get', headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == 200
    assert len(response.json['data']) > 0
    assert response.json['data'][0]['word'] == 'test'
    assert 'article_id' in response.json['data'][0]
    assert 'paragraph_id' in response.json['data'][0]
    assert 'created_at' in response.json['data'][0]
