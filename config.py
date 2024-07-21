import os
from dotenv import load_dotenv

print("Current working directory:", os.getcwd())
# Load .env file
load_dotenv()

class Config:
    SECRET_FOR_JWT = os.getenv('SECRET_FOR_JWT', 'JWT123')
    SECRET_FOR_QR = os.getenv('SECRET_FOR_QR', 'QR123')
    ENDPOINT = os.getenv('ENDPOINT', 'http://localhost:7000')

# Debug prints to check if values are being loaded
print("SECRET_FOR_JWT:", Config.SECRET_FOR_JWT)
print("SECRET_FOR_QR:", Config.SECRET_FOR_QR)
print("ENDPOINT:", Config.ENDPOINT)
