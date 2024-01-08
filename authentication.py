from passlib.context import CryptContext
import jwt
from models import User
from fastapi.exceptions import HTTPException
from fastapi import status
from config import SECRET


password_context = CryptContext(schemes=['bcrypt'], deprecated = 'auto')

def get_hashed_password(raw_password:str):
    return password_context.hash(raw_password)


def verify_password(plain_password:str, hashed_password:str) -> bool :
    return password_context.verify(plain_password, hashed_password)

async def verify_token(token:str)-> User:
    try:
        payload = jwt.decode(token, SECRET, algorithms=['HS256'])
        user = await User.get(id = payload.get('id'))
        return user
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token', headers={
            'WWW-Authenticate':'Bearer'
        })

async def authenticate_user(username:str, password:str):
    user = await User.get(username = username)
    if user and verify_password(password, user.password):
        return user
    return False

async def token_generator(username:str, password:str):
    user = await authenticate_user(username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='invalid username of password',
            headers={'WWW-Authenticate':'Bearer'}
        )
    token_data = {
        'id':user.id,
        'username':user.username
    }
    token =  jwt.encode(token_data, SECRET, algorithm='HS256')
    return token