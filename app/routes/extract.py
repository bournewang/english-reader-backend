# from fastapi import APIRouter, HTTPException
from flask import Blueprint, request, jsonify
import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional
from datetime import datetime
from urllib.parse import urlparse
import urllib.parse

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
    print("title: ",soup.title.string)
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

        print(article)

        return jsonify(article)

    except requests.RequestException as e:
        return jsonify({'error': f'Failed to fetch URL: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@extract_bp.route('/image', methods=['GET'])
def search_image():
    try:
        keyword = request.args.get('keyword')
        if not keyword:
            return jsonify({'error': 'Keyword is required'}), 400

        encoded_keyword = urllib.parse.quote(keyword)
        url = f'https://unsplash.com/napi/search/photos?page=1&per_page=20&query={encoded_keyword}&xp=free-semantic-perf%3Acontrol'
        
        headers = {
            'authority': 'unsplash.com',
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'en-US',
            'client-geo-region': 'global',
            'dnt': '1',
            'priority': 'u=1, i',
            'referer': f'https://unsplash.com/s/photos/{encoded_keyword}',
            'sec-ch-ua': '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
            'cookie': 'require_cookie_consent=false; xp-free-semantic-perf=control; xp-video-affiliates=experiment; xp-no-ads-in-wp-search=experiment; _sp_ses.0295=*; azk=38d68723-1b93-41de-b95f-4f4a55f15abe; azk-ss=true; _dd_s=aid=yu5142p4mv&logs=1&id=617f02a7-868e-4b68-a4f9-7a8f2b1a9888&created=1741783152144&expire=1741784086055; _sp_id.0295=9135bd59-269f-4aad-80b5-e72083feb925.1741783152.1.1741783186..46333548-dc7a-4877-aaff-154e8f97176b..d33a3eaf-1fdd-45bf-b5de-fdb8c81f7089.1741783152255.22'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if data and 'results' in data and len(data['results']) > 0:
            return jsonify({'url': data['results'][0]['urls']['thumb']})
        
        return jsonify({'error': 'No images found'}), 404

    except requests.RequestException as e:
        return jsonify({'error': f'Failed to fetch image: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500
