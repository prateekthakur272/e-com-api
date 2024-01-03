# from fastapi import (BackgroundTasks, UploadFile, File, Form, Depends, HTTPException, status)
from dotenv import dotenv_values
from models import User
import jwt
from email.mime.text import MIMEText
from smtplib import SMTP_SSL

from jinja2 import Environment, FileSystemLoader


config_creds = dotenv_values('.env')

EMAIL = config_creds['EMAIL']
PASSWORD = config_creds['PASSWORD']
SECRET = config_creds['SECRET']
    

def render_template(path:str, data:dict):
    env = Environment(loader= FileSystemLoader('templates/'))
    template = env.get_template(path)
    return template.render(data)
    
    
    
async def send_email(instance: User):
    
    token_data = {
        'id' : instance.id,
        'username' : instance.username,
    }
    token = jwt.encode(payload=token_data, key=SECRET, algorithm='HS256')
    
    template = render_template('verification.html', {'token':token})
    
    message = MIMEText(template, 'html')
    message['Subject'] = 'Ecom API Account Verification'
    message['To'] = instance.email
    message['From'] = EMAIL
    
    with SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL, PASSWORD)
        smtp.send_message(message)