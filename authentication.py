from passlib.context import CryptContext


password_context = CryptContext(schemes=['bcrypt'], deprecated = 'auto')

def get_hashed_password(raw_password:str):
    return password_context.hash(raw_password)