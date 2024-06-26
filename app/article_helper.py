from .models.article import Article

def article_json(article):
    return {
        'id': article.id,
        'user_id': article.user_id,
        'title': article.title,
        'word_count': article.word_count,
        'author': article.author,
        'url': article.url,
        'site': article.site,
        'site_name': article.site_name,
        'site_icon': article.site_icon,        
        'created_at': article.created_at,
        'paragraphs': {p.id: p.text for p in article.paragraphs},
        'unfamiliar_words': [lw.word for lw in list(set(article.unfamiliar_words))]
    }