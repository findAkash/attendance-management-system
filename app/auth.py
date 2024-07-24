import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from config import Config

load_dotenv()

SECRET_KEY = Config.SECRET_FOR_JWT
print(SECRET_KEY)
ALGORITHM = 'HS256'

def create_jwt_token(data: dict, expires_delta: timedelta = timedelta(hours=1)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_jwt_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {'success': True, 'data': payload}
    except jwt.ExpiredSignatureError as e:
        print(e)
        return {'success': False, 'data': None}
    except jwt.InvalidTokenError as e:
        print(e)
        return {'success': False, 'data': None}
    