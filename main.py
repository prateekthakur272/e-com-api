from fastapi import FastAPI, HTTPException, status, Depends
from tortoise.contrib.fastapi import register_tortoise
import uvicorn
import models
from fastapi.responses import HTMLResponse
from fastapi.requests import Request
# imports for signals
from tortoise.signals import post_save
from typing import List, Optional, Type
from tortoise import BaseDBAsyncClient
from tortoise.exceptions import IntegrityError
# templates
from fastapi.templating import Jinja2Templates
# email
from emails import *
# authentication
from authentication import * 
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from config import SECRET, BASE_URL
# files upload
from fastapi import File, UploadFile
import secrets
from fastapi.staticfiles import StaticFiles
from PIL import Image
from uploads import save_image


app = FastAPI()
templates = Jinja2Templates('templates')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')
app.mount('/static', StaticFiles(directory='static'), name='static')

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET, algorithms=['HS256'])
        user = await User.get(id=payload.get('id'))
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token', headers={
            'WWW-Authenticate':'Bearer'
        })
    return user


# signals
@post_save(models.User)
async def create_buisness(sender :"Type[models.User]", instance: models.User, created:bool, using_db: "Optional[BaseDBAsyncClient]", update_fields: List[str]) -> None:
    if created:
        try:
            buisness = await models.Buisness.create(
                buisness_name = instance.username,
                owner = instance,
            )
            await models.BuisnessPydantic.from_tortoise_orm(buisness)
            await send_email(instance=instance)
            #send mail
        except IntegrityError:
            pass

# routes    
@app.get('/')
def root():
    return {'message': 'Ecom Api'}

@app.post('/user/me')
async def login(user: models.UserPydanticIn = Depends(get_current_user)):
    buisness = await models.Buisness.get(owner=user)
    return {
        'status': 'ok',
        'data': {
            'username':user.username,
            'email':user.email,
            'verified':user.is_verified,
            'join_date': user.join_date.strftime('%b %d %Y')
        }
    }

@app.post('/register')
async def register_user(user: models.UserPydanticIn):
    user_info = user.model_dump(exclude_unset=True)
    user_info['password'] = get_hashed_password(user_info['password'])
    user = await models.User.create(**user_info)
    user_response = await models.UserPydantic.from_tortoise_orm(user)
    return {'status':'ok', 'message':f'user created with username: {user_response.username} and email: {user_response.email}, please verify your email by clicking the link in a email sent by us.'}



@app.get('/verification', response_class=HTMLResponse)
async def verification(request:Request, token:str):
    user = await verify_token(token)
    if (user and not user.is_verified):
        user.is_verified = True
        await user.save()
        return templates.TemplateResponse('verified.html', {'request':request, 'username':user.username})
    return templates.TemplateResponse('invalid_token.html', {'request': request}, status_code=status.HTTP_401_UNAUTHORIZED)

@app.post('/token')
async def generate_token(request_form: OAuth2PasswordRequestForm = Depends()):
    token = await token_generator(request_form.username, request_form.password)
    return {'access_token': token, 'token_type': 'bearer'}


@app.post('/upload/profile')
async def upload_profile(file: UploadFile = File(...), user: models.UserPydantic = Depends(get_current_user)):
    parts = file.filename.lower().split('.')
    allowed_extensions = ['jpg','png','jpeg','img']
    file_path = 'static/images/'
    extension = parts[1]
    if extension not in allowed_extensions:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail= f'file type {extension} not allowed')
    
    token_name = f'{secrets.token_hex(12)}.{extension}'
    file_name = file_path+token_name
    content = await file.read()
    
    with open(file_name,'wb') as new_file:
        new_file.write(content)
    
    img = Image.open(file_name)
    img = img.resize(size=(200, 200))
    img.save(file_name)
    img.close()
    file.close()
    
    buisness = await models.Buisness.get(owner = user)
    owner = await buisness.owner
    if owner == user:
        buisness.logo = token_name
        await buisness.save()
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Not Authorised', headers={
            'WWW-Authenticate':'Bearer'
        })
    
    img_url = BASE_URL+file_name
    return {'status':'ok','img_url':img_url}

@app.post('/upload/product/{id}')
async def upload_product(id: int, file:UploadFile = File(...), user:models.UserPydantic = Depends(get_current_user)):
    file_path = 'static/images/'
    
    product = await models.Product.get(id=id)
    buisness = await product.buisness
    owner = await buisness.owner
    
    if owner == user:
        file_name = await save_image(file=file, file_path=file_path, size=(400,400))
        product.product_image = file_name
        await product.save()
        img_url = BASE_URL+file_path+file_name
        return {'status':'ok','img_url':img_url}
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Not Authorised', headers={
            'WWW-Authenticate':'Bearer'
        })
    
    
# tortoise orm
register_tortoise(
    app=app,
    db_url='sqlite://db.sqlite3',
    modules={
        'models':['models'],
    },
    generate_schemas=True,
    add_exception_handlers=True
)


if __name__ == '__main__':
    uvicorn.run('main:app',reload=True)