from app import db
from app import create_app
from app.models.user import User
from app.models.article import Article
from app.models.paragraph import Paragraph
from app.models.unfamiliar_word import UnfamiliarWord
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
    article1 = Article(user_id=1, title="Shark bites teenager's leg in attack at North Carolina beach", word_count=71, author="Jasmine Baehr", url="https://www.foxnews.com/us/shark-bites-teenagers-leg-attack-north-carolina-beach")
    article2 = Article(user_id=2, title="Russia has seen two major terror attacks in just three months. Here’s what we know",  word_count=150, author="Kathleen Magramo and Jerome Taylor", url="https://edition.cnn.com/2024/06/24/europe/russia-dagestan-attacks-explainer-intl-hnk/index.html")
    db.session.add(article1)
    db.session.add(article2)
    db.session.commit()

    paragraph1 = Paragraph(article_id=1, text="Marine ecologist Mike Heithaus joins ‘America Reports’ to discuss three injured in two separate shark attacks off of Florida’s panhandle.")
    paragraph2 = Paragraph(article_id=1, text='A teen is recovering from injuries to his right leg after a shark attack at a North Carolina beach on Sunday afternoon. ')
    paragraph3 = Paragraph(article_id=1, text="North Topsail Beach Police Chief William Younginer told Fox News Digital that he raced to the scene in Onslow County, where 14-year-old Blayne Brown had been bitten.")
    paragraph4 = Paragraph(article_id=2, text="Russia is reeling from another major terror attack, with at least 19 people killed and 25 injured in what appeared to be coordinated shootings at various places of worship in Russia’s southernmost Dagestan republic.")
    paragraph5 = Paragraph(article_id=2, text="The attack is the second in the last three months after more than 130 people were killed at a concert hall near Moscow in a terrorist attack claimed by ISIS-K in March, and challenges President Vladimir Putin’s self-declared reputation as a leader able to guarantee order across the vast, turbulent country.")
    paragraph6 = Paragraph(article_id=2, text="The uptick in violence comes as long-simmering ethnic tensions resurface, compounded both by drives to fill Russia’s military ranks as Putin’s war against Ukraine grinds on – and by the ongoing conflict in the Middle East.")
    db.session.add(paragraph1)
    db.session.add(paragraph2)
    db.session.add(paragraph3)
    db.session.add(paragraph4)
    db.session.add(paragraph5)
    db.session.add(paragraph6)
    db.session.commit()

def seed_unfamiliar_words():
    unfamiliar_word1 = UnfamiliarWord(user_id=1, word='military', article_id=1, paragraph_id=1)
    unfamiliar_word2 = UnfamiliarWord(user_id=2, word='ambulance', article_id=2, paragraph_id=3)
    db.session.add(unfamiliar_word1)
    db.session.add(unfamiliar_word2)
    db.session.commit()

def seed_all():
    seed_users()
    seed_articles()
    seed_unfamiliar_words()

if __name__ == "__main__":
    app = create_app()
    app.app_context().push()
    seed_all()
    print("Database seeded!")