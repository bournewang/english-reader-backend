# from fastapi import APIRouter, HTTPException
from flask import Blueprint, request, jsonify
import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional
from datetime import datetime
from urllib.parse import urlparse

extract_bp = Blueprint('extract', __name__)

def extract_meta_content(soup: BeautifulSoup, name: str = None, property: str = None) -> str:
    if name:
        meta = soup.find('meta', attrs={'name': name})
    if property:
        meta = soup.find('meta', attrs={'property': property})
    return meta.get('content') if meta else None

def collect_article_info(soup: BeautifulSoup, url: str) -> dict:
    meta_tags = {
        'author': ['author', 'article:author', 'og:author'],
        'site_name': ['og:site_name', 'application-name', 'twitter:site'],
        'title': ['og:title', 'twitter:title']
    }

    # Extract author
    author = None
    for tag in meta_tags['author']:
        author = extract_meta_content(soup, name=tag) or extract_meta_content(soup, property=tag)
        if author:
            break

    # Extract site name
    site_name = None
    for tag in meta_tags['site_name']:
        site_name = extract_meta_content(soup, property=tag)
        if site_name:
            break

    domain = urlparse(url).netloc
    return {
        'url': url,
        'title': soup.title.string if soup.title else '',
        'author': author or 'Unknown Author',
        'site_name': site_name or domain,
        'site_icon': f'https://{domain}/favicon.ico'
    }

@extract_bp.route('/', methods=['GET'])
def extract_article():
    try:
        url = request.args.get('url')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400

        # Fetch URL content
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find main content
        content = None
        for selector in ['article', 'main', '.content', '#content']:
            content = soup.select_one(selector)
            if content:
                break
        
        if not content:
            # Fallback to largest text block
            paragraphs = soup.find_all('p')
            if paragraphs:
                content = max(paragraphs, key=lambda p: len(p.get_text()))
            else:
                return jsonify({'error': 'Could not find article content'}), 400

        # Extract paragraphs and images
        paragraphs = {}
        word_count = 0
        
        for i, element in enumerate(content.find_all(['p', 'img']), 1):
            if element.name == 'p':
                text = element.get_text().strip()
                if text:
                    paragraphs[str(i)] = {
                        'type': 'text',
                        'content': text
                    }
                    word_count += len([w for w in text.split() if w])
            elif element.name == 'img':
                src = element.get('src')
                alt = element.get('alt', '')
                
                # Skip placeholder images
                if (src and 
                    not src.endswith(('.ico', '.svg')) and
                    not any(x in src.lower() for x in ['placeholder', 'grey', 'gray', 'blank']) and
                    not src.startswith('/') and
                    len(src) > 10):
                    
                    # Try to find image description from various sources
                    description = None
                    
                    # Check for figure caption
                    figure_parent = element.find_parent('figure')
                    if figure_parent:
                        figcaption = figure_parent.find('figcaption')
                        if figcaption:
                            description = figcaption.get_text().strip()
                    
                    # Check for aria-label
                    if not description:
                        description = element.get('aria-label')
                    
                    # Check for alt text
                    if not description:
                        description = alt
                    
                    # Check for title attribute
                    if not description:
                        description = element.get('title')
                    
                    paragraphs[str(i)] = {
                        'type': 'image',
                        'content': src,
                        'alt': alt,
                        'description': description
                    }

        if not paragraphs:
            return jsonify({'error': 'No paragraphs found in the article'}), 400

        # Collect article info
        info = collect_article_info(soup, url)

        article = {
            **info,
            'paragraphs': paragraphs,
            'word_count': word_count,
            'created_at': datetime.utcnow().isoformat(),
            'unfamiliar_words': []
        }

        return jsonify(article)

    except requests.RequestException as e:
        return jsonify({'error': f'Failed to fetch URL: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500
