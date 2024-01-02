from fastapi import FastAPI, HTTPException, status
from tortoise.contrib.fastapi import register_tortoise
import uvicorn
import models
from authentication import get_hashed_password, verify_token
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


app = FastAPI()

# signals
@post_save(models.User)
async def create_buisness(sender :"Type[models.User]", instance: models.User, created:bool, using_db: "Optional[BaseDBAsyncClient]", update_fields: List[str]) -> None:
    if created:
        try:
            buisness = await models.Buisness.create(
                buisness_name = '{instance.username}',
                owner = instance,
            )
            await models.BuisnessPydantic.from_tortoise_orm(buisness)
            await send_email(instance=instance)
            #send mail
        except IntegrityError:
            pass
        
@app.get('/')
def index():
    return {'message': 'Ecom Api'}

@app.post('/register')
async def register_user(user: models.UserPydanticIn):
    user_info = user.model_dump(exclude_unset=True)
    user_info['password'] = get_hashed_password(user_info['password'])
    user = await models.User.create(**user_info)
    user_response = await models.UserPydantic.from_tortoise_orm(user)
    return {'status':'ok', 'message':f'user created with username: {user_response.username} and email: {user_response.email}, please verify your email by clicking the link in a email sent by us.'}


templates = Jinja2Templates('templates')

@app.get('/verification', response_class=HTMLResponse)
async def verification(request:Request, token:str):
    user = await verify_token(token)
    if (user and not user.is_verified):
        user.is_verified = True
        await user.save()
        return templates.TemplateResponse('verification.html', {'request':request, 'username':user.username})
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid or expired token', headers={
            'WWW-Authenticate':'Bearer'
        })


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