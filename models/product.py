from tortoise import Model, fields
from pydantic import BaseModel
from datetime import datetime
from tortoise.contrib.pydantic import creator


class Product(Model):
    id = fields.IntField(pk=True, index = True, )
    name = fields.CharField(max_length=100, null = False, index = True)
    category = fields.CharField(max_length=30, index = True)
    origional_price = fields.DecimalField(max_digits=12, decimal_places=2)
    new_price = fields.DecimalField(max_digits=12, decimal_places=2)
    percentage_discount = fields.IntField()
    offer_expiration_date = fields.DateField(default=datetime.utcnow)
    product_image = fields.CharField(max_length=200, null = False, default = 'default_product_img.png')
    buisness = fields.ForeignKeyField('user.Buisness', related_name='products')
    
    

ProductPydantic = creator.pydantic_model_creator(Product, name='Product')
ProductPydanticIn = creator.pydantic_model_creator(Product, name='ProductIn',exclude=('percentage_discount','id',))