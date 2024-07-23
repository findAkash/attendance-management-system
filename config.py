import os
from dotenv import load_dotenv

print("Current working directory:", os.getcwd())
# Load .env file
load_dotenv()

class Config:
    SECRET_FOR_JWT = os.getenv('SECRET_FOR_JWT', 'JWT123')
    SECRET_FOR_QR = os.getenv('SECRET_FOR_QR', 'QR123')
    ENDPOINT = os.getenv('ENDPOINT', 'http://localhost:8000')
    QR_REFRESH_INTERVAL = os.getenv('QR_REFRESH_INTERVAL', 100)
    DATABASE_URL = os.getenv('DATABASE_URL', 'mongodb+srv://findakash:text1234567890@cluster0.grpw3tv.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
