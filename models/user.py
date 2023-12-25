from tortoise import Model, fields
from pydantic import BaseModel
from datetime import datetime
from tortoise.contrib.pydantic import creator

class User(Model):
    id = fields.IntField(pk=True, index=True)
    username = fields.CharField(max_length=20, null = False, unique = True)
    email = fields.CharField(max_length=200, null = False, unique = True,)
    password = fields.CharField(max_length=100, null = False)
    is_verified = fields.BooleanField(default = False)
    join_date = fields.DatetimeField(default = datetime.utcnow)
    
    
    
class Buisness(Model):
    id = fields.IntField(pk=True, index=True)
    buisness_name = fields.CharField(max_length=20, null = False, unique = True)
    city = fields.CharField(max_length=100, null = False, default = 'Unspecified')
    region = fields.CharField(max_length=100, null = False, default = "Unspecified")
    buisness_description = fields.TextField(null = True)
    logo = fields.CharField(max_length=200, null = False, default = 'default_logo.png')
    owner = fields.ForeignKeyField('user.User', related_name='buisness')
    


UserPydantic = creator.pydantic_model_creator(User, name='User', exclude=('is_verified',))
UserPydanticIn = PydanticIn = creator.pydantic_model_creator(User, name='UserIn', exclude_readonly=True)
UserPydanticOut = PydanticOut = creator.pydantic_model_creator(User, name='UserOut', exclude=('password',))


BuisnessPydantic = creator.pydantic_model_creator(Buisness, name='Buisness')
BuisnessPydanticIn = creator.pydantic_model_creator(Buisness, name='BuisnessIn', exclude_readonly=True)
