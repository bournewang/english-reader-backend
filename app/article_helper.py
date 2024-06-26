from .models.article import Article

def article_json(article):
    return {
        'id': article.id,
        'user_id': article.user_id,
        'title': article.title,
        'word_count': article.word_count,
        'created_at': article.created_at,
        'paragraphs': {p.id: p.text for p in article.paragraphs},
        'looking_words': [lw.word for lw in list(set(article.looking_words))]
    }