from fastapi import FastAPI, HTTPException, status, Depends
from tortoise.contrib.fastapi import register_tortoise
import uvicorn
import models
from fastapi.responses import HTMLResponse
from fastapi.requests import Request
from datetime import datetime
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
    buisness = await models.BuisnessPydantic.from_tortoise_orm(buisness)
    logo = buisness.logo
    logo_url = f'{BASE_URL}static/images/{logo}'
    buisness = buisness.model_dump(exclude=['logo',])
    user = await models.UserPydanticOut.from_tortoise_orm(user)
    return {
        'status': 'ok',
        'data': {
            'user': user,
            'buisness': {
                **buisness,
                'logo_url':logo_url,
            },
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

@app.put('/buisness/me')
async def update_buisness_details(data:models.BuisnessPydanticIn, user:models.UserPydantic = Depends(get_current_user)):
    buisness = await models.Buisness.get(owner=user)
    data = data.model_dump(exclude_unset=True)
    buisness = buisness.update_from_dict(data=data)
    await buisness.save()
    return {'status':'ok',}


@app.get('/products')
async def get_all_products():
    query = models.Product.all()
    print(query)
    response = await models.ProductPydantic.from_queryset(query)
    return {'status':'ok', 'data': response}

@app.get('/products/{id}')
async def get_product_by_id(id:int):
    product = await models.Product.get(id=id)
    buisness = await product.buisness
    owner = await buisness.owner
    response = await models.ProductPydantic.from_tortoise_orm(product)
    return {'status':'ok', 'data':
        {
            'product': response,
            'buisness':{
                'name':buisness.buisness_name,
                'city':buisness.city,
                'region':buisness.region,
                'description':buisness.buisness_description,
                'logo':buisness.logo,
            },
            'owner':{
                'id':owner.id,
                'email':owner.email,
                'join_date':owner.join_date.strftime('%b %d %Y'),
                
            }
        }
    }


@app.post('/products')
async def add_product(product: models.ProductPydanticIn, user: models.UserPydantic = Depends(get_current_user)):
    product = product.model_dump(exclude_unset=True)
    if product['original_price'] > 0:
        product['percentage_discount'] = ((product['original_price']-product['new_price'])/product['original_price'])*100
        product_obj = await models.Product.create(**product, buisness = user)
        product_obj = await models.ProductPydantic.from_tortoise_orm(product_obj)
        return {'status' : 'ok', 'data' : product_obj}
    else:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = 'original price should be more than zero')
    

@app.put('/products/{id}')
async def update_product(id:int, data:models.ProductPydanticIn, user:models.UserPydantic = Depends(get_current_user)):
    product = await models.Product.get(id=id)
    buisness = await product.buisness
    owner = await buisness.owner
    
    data = data.model_dump(exclude_unset=True)
    data['date_published'] = datetime.utcnow()
    print(data)
    
    if user == owner:
        if data['original_price'] > 0:
            data['percentage_discount'] = ((data['original_price']-data['new_price'])/data['original_price'])*100
            product = product.update_from_dict(data=data)
            await product.save()
            response = await models.ProductPydantic.from_tortoise_orm(product)
            return {'status':'ok', 'data':response}
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='original price should be more than zero')
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Not Authorised', headers={
            'WWW-Authenticate':'Bearer'
        })        
    
    
@app.delete('/products/{id}')
async def delete_product(id:int, user:models.UserPydantic = Depends(get_current_user)):
    product = await models.Product.get(id=id)
    buisness = await product.buisness
    owner = await buisness.owner
    if user == owner:
        await product.delete()
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail= 'Not authorised',headers={
            'WWW-Authenticate':'Bearer'
        })
    return {'status':'ok'}
    

@app.post('/upload/product/{id}')
async def upload_product_picture(id: int, file:UploadFile = File(...), user:models.UserPydantic = Depends(get_current_user)):
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