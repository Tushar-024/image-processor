class Config:
    SECRET_KEY = "your_secret_key"
    MONGO_URI = "mongodb://localhost:27017/your_db"
    MONGO_DB_NAME = "your_db"
    CELERY_BROKER_URL = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND = "redis://localhost:6379/0"
