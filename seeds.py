from app import db
from app import create_app
from app.models.user import User
from app.models.article import Article
from app.models.paragraph import Paragraph
from app.models.looking_word import LookingWord
from flask_bcrypt import Bcrypt

# Initialize the Bcrypt object
bcrypt = Bcrypt()

def seed_users():
    user1 = User(email='hello@reader.com', password_hash=bcrypt.generate_password_hash('123456').decode('utf-8'))
    user2 = User(email='wang@reader.com', password_hash=bcrypt.generate_password_hash('123456').decode('utf-8'))
    db.session.add(user1)
    db.session.add(user2)
    db.session.commit()

def seed_articles():
    article1 = Article(user_id=1, title='Article 1', word_count=100)
    article2 = Article(user_id=2, title='Article 2', word_count=150)
    db.session.add(article1)
    db.session.add(article2)
    db.session.commit()

    paragraph1 = Paragraph(article_id=1, text='The Israeli military has said its forces violated protocol by strapping a wounded Palestinian man to the front of their vehicle during a raid in the West Bank city of Jenin.')
    paragraph2 = Paragraph(article_id=1, text='The Israel Defense Forces confirmed the incident after it was captured on video and shared on social media. An IDF statement said the man was wounded in an exchange of fire during the raid, in which he was a suspect.')
    paragraph3 = Paragraph(article_id=2, text="The injured man's family said that when they asked for an ambulance, the army took him, strapped him to the bonnet of their jeep and drove off.")
    db.session.add(paragraph1)
    db.session.add(paragraph2)
    db.session.add(paragraph3)
    db.session.commit()

def seed_looking_words():
    looking_word1 = LookingWord(user_id=1, word='military', article_id=1, paragraph_id=1)
    looking_word2 = LookingWord(user_id=2, word='ambulance', article_id=2, paragraph_id=3)
    db.session.add(looking_word1)
    db.session.add(looking_word2)
    db.session.commit()

def seed_all():
    seed_users()
    seed_articles()
    seed_looking_words()

if __name__ == "__main__":
    app = create_app()
    app.app_context().push()
    seed_all()
    print("Database seeded!")