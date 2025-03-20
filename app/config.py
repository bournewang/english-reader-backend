import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

username = os.getenv('DB_USERNAME')
password = os.getenv('DB_PASSWORD')
hostname = os.getenv('DB_HOST', 'localhost')
database_name = os.getenv('DB_NAME')

class Config:
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
    SQLALCHEMY_DATABASE_URI = f'mysql+mysqldb://{username}:{password}@{hostname}/{database_name}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'your_jwt_secret_key'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=2)

    # Cache configuration
    CACHE_TYPE =        os.getenv("CACHE_TYPE") # RedisCache
    CACHE_REDIS_HOST =  os.getenv("CACHE_REDIS_HOST") #'localhost'
    CACHE_REDIS_PORT =  os.getenv("CACHE_REDIS_PORT") # 6379
    CACHE_REDIS_DB =    os.getenv("CACHE_REDIS_DB") # 0
    CACHE_REDIS_URL =   os.getenv("CACHE_REDIS_URL") #'redis://localhost:6379/0'

    TRANSLATE_API_KEY = os.getenv("TRANSLATE_API_KEY")
    TRANSLATE_LOCATION =os.getenv("TRANSLATE_LOCATION")

    DASHSCOPE_API_URL = os.getenv("DASHSCOPE_API_URL")
    DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
