from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.article import Article
from ..models.unfamiliar_word import UnfamiliarWord
from ..extensions import db
from datetime import datetime, timedelta
import time

stats_bp = Blueprint('stats', __name__)

# define an api to make statictics about how many articles/vocabulary read daily/weekly/monthly etc.
# for example {dailyArticles: 3, dailyVocabulary: 2000, weeklyArticles: 15, weeklyVocabulary: 10000, monthlyArticles: 100, monthlyVocabulary: 100000}

@stats_bp.route('/get', methods=['GET'])
@jwt_required()
def statistics():
    user_id = get_jwt_identity()
    now = datetime.utcnow()
    start_of_today = datetime(now.year, now.month, now.day)
    start_of_yesterday = start_of_today - timedelta(days=1)
    start_of_week = start_of_today - timedelta(days=now.weekday())
    start_of_last_week = start_of_week - timedelta(weeks=1)
    start_of_month = datetime(now.year, now.month, 1)
    start_of_last_month = (start_of_month - timedelta(days=1)).replace(day=1)
    
    def count_articles_words_and_wordcount(start, end):
        articles = Article.query.filter(Article.user_id == user_id, Article.created_at >= start, Article.created_at < end).all()
        articles_count = len(articles)
        word_count = sum(article.word_count for article in articles)
        words_count = UnfamiliarWord.query.filter(UnfamiliarWord.user_id == user_id, UnfamiliarWord.created_at >= start, UnfamiliarWord.created_at < end).count()
        return articles_count, word_count, words_count
    
    # Current period counts
    today_articles, today_word_count, today_words = count_articles_words_and_wordcount(start_of_today, now)
    week_articles, week_word_count, week_words = count_articles_words_and_wordcount(start_of_week, now)
    month_articles, month_word_count, month_words = count_articles_words_and_wordcount(start_of_month, now)
    total_articles = Article.query.filter_by(user_id=user_id).count()
    total_word_count = db.session.query(db.func.sum(Article.word_count)).filter_by(user_id=user_id).scalar() or 0
    total_words = UnfamiliarWord.query.filter_by(user_id=user_id).count()
    
    # Previous period counts
    yesterday_articles, yesterday_word_count, yesterday_words = count_articles_words_and_wordcount(start_of_yesterday, start_of_today)
    last_week_articles, last_week_word_count, last_week_words = count_articles_words_and_wordcount(start_of_last_week, start_of_week)
    last_month_articles, last_month_word_count, last_month_words = count_articles_words_and_wordcount(start_of_last_month, start_of_month)
    
    def percentage_change(current, previous):
        previous += 10
        if previous == 0:
            return None
        return ((current - previous) / previous) * 100
    
    stats = {
        'today_articles': today_articles,
        'today_word_count': today_word_count,
        'today_words': today_words,
        'week_articles': week_articles,
        'week_word_count': week_word_count,
        'week_words': week_words,
        'month_articles': month_articles,
        'month_word_count': month_word_count,
        'month_words': month_words,
        'total_articles': total_articles,
        'total_word_count': total_word_count,
        'total_words': total_words,
        'today_articles_change': percentage_change(today_articles, yesterday_articles),
        'today_word_count_change': percentage_change(today_word_count, yesterday_word_count),
        'today_words_change': percentage_change(today_words, yesterday_words),
        'week_articles_change': percentage_change(week_articles, last_week_articles),
        'week_word_count_change': percentage_change(week_word_count, last_week_word_count),
        'week_words_change': percentage_change(week_words, last_week_words),
        'month_articles_change': percentage_change(month_articles, last_month_articles),
        'month_word_count_change': percentage_change(month_word_count, last_month_word_count),
        'month_words_change': percentage_change(month_words, last_month_words),
    }
    
    return jsonify({'success': True, 'message': 'get stats successfully', 'data': stats}), 201