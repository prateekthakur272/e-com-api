from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
import uvicorn
import models
from authentication import get_hashed_password

# imports for signals
from tortoise.signals import post_save
from typing import List, Optional, Type
from tortoise import BaseDBAsyncClient
from tortoise.exceptions import IntegrityError

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