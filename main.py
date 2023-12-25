from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
import uvicorn
from tortoise import models

app = FastAPI()


@app.get('/')
def index():
    return {'message': 'Ecom Api'}

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