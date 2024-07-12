from .models.reading_article import ReadingArticle
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from .models import Article, Paragraph
from .extensions import db

def fetch_and_save_article(url, user_id):
    # Step 1: Fetch the article content
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch the article. Status code: {response.status_code}")
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract the main article content using your custom logic
    article_content = fetch_main_article_element(soup)
    if not article_content:
        raise Exception("No suitable content found")
    
    # Extract metadata (title, author, etc.)
    title = soup.title.string if soup.title else 'Untitled'
    author = soup.find(attrs={"name": "author"})['content'] if soup.find(attrs={"name": "author"}) else None
    word_count = len(article_content.get_text().split())
    
    # Additional metadata (you might need to extract or set these)
    site = url.split('/')[2]
    site_name = site.split('.')[1] if len(site.split('.')) > 2 else site.split('.')[0]
    site_icon = f"https://{site}/favicon.ico"
    
    # Step 2: Create and save the Article object
    article = Article(
        user_id=user_id,
        title=title,
        word_count=word_count,
        author=author,
        url=url,
        site=site,
        site_name=site_name,
        site_icon=site_icon,
        created_at=datetime.utcnow()
    )
    db.session.add(article)
    db.session.commit()
    
    # Step 3: Split the article content into paragraphs
    paragraphs = article_content.find_all('p')
    
    # Step 4: Create and save Paragraph objects
    for paragraph in paragraphs:
        text = paragraph.get_text()
        word_count = len(text.split())
        if word_count > 0:  # Only save paragraphs with content
            para = Paragraph(
                article_id=article.id,
                text=text,
                word_count=word_count
            )
            db.session.add(para)
    
    db.session.commit()

    return article

def fetch_main_article_element(soup):
    # Your logic to find the main article element
    common_tags = ['article', 'main', 'section']
    for tag in common_tags:
        elements = soup.find_all(tag)
        if elements:
            return elements[0]

    common_classes = ['content', 'main', 'article', 'post']
    for class_name in common_classes:
        elements = soup.find_all(class_=class_name)
        if elements:
            return elements[0]

    common_ids = ['content', 'main', 'article', 'post']
    for id_name in common_ids:
        element = soup.find(id=id_name)
        if element:
            return element

    all_elements = soup.find_all(True)
    largest_element = None
    max_text_length = 0
    for element in all_elements:
        if element.name not in common_tags and element.get_text(strip=True):
            text_length = len(element.get_text(strip=True))
            if text_length > max_text_length:
                max_text_length = text_length
                largest_element = element

    return largest_element    