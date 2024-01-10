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
    

UserPydantic = creator.pydantic_model_creator(User, name='User', exclude=('is_verified',))
UserPydanticIn = PydanticIn = creator.pydantic_model_creator(User, name='UserIn', exclude_readonly=True, exclude=('is_verified','join_date'))
UserPydanticOut = PydanticOut = creator.pydantic_model_creator(User, name='UserOut', exclude=('password',))
    
    
    
class Buisness(Model):
    id = fields.IntField(pk=True, index=True)
    buisness_name = fields.CharField(max_length=100, null = False, unique = True)
    city = fields.CharField(max_length=100, null = False, default = 'Unspecified')
    region = fields.CharField(max_length=100, null = False, default = "Unspecified")
    buisness_description = fields.TextField(null = True)
    logo = fields.CharField(max_length=200, null = False, default = 'default_logo.png')
    owner = fields.ForeignKeyField('models.User', related_name='buisness')
    

BuisnessPydantic = creator.pydantic_model_creator(Buisness, name='Buisness')
BuisnessPydanticIn = creator.pydantic_model_creator(Buisness, name='BuisnessIn', exclude_readonly=True)



class Product(Model):
    id = fields.IntField(pk=True, index = True, )
    name = fields.CharField(max_length=100, null = False, index = True)
    category = fields.CharField(max_length=30, index = True)
    original_price = fields.DecimalField(max_digits=12, decimal_places=2)
    new_price = fields.DecimalField(max_digits=12, decimal_places=2)
    percentage_discount = fields.IntField()
    offer_expiration_date = fields.DateField(default=datetime.utcnow)
    product_image = fields.CharField(max_length=200, null = False, default = 'default_product_img.png')
    buisness = fields.ForeignKeyField('models.Buisness', related_name='products')
    

ProductPydantic = creator.pydantic_model_creator(Product, name='Product')
ProductPydanticIn = creator.pydantic_model_creator(Product, name='ProductIn',exclude=('percentage_discount','id',))