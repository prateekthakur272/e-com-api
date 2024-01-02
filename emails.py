# from fastapi import (BackgroundTasks, UploadFile, File, Form, Depends, HTTPException, status)
from dotenv import dotenv_values

from models import User
import jwt
from email.mime.text import MIMEText
from smtplib import SMTP_SSL


config_creds = dotenv_values('.env')

EMAIL = config_creds['EMAIL']
PASSWORD = config_creds['PASSWORD']
SECRET = config_creds['SECRET']
    
    
async def send_email(instance: User):
    
    token_data = {
        'id' : instance.id,
        'username' : instance.username,
    }
    token = jwt.encode(payload=token_data, key=SECRET, algorithm='HS256')
    
    template = f"""
    <!DOCTYPE html>
    <html>
        <head></head>
        <body>
            <div style = "display: flex; align-items: center; justify-content: center; flex-direction: column">
                <h3>Account Verification</h3>
                <br>
                <p>Thanks for choosing E-com API, please click on the button to verify your account</p>
                <br>
                <a style = "margin-top: 1rem; padding: 1rem; border-radius: 0.5rem; font-size: 1rem; text-decoraton: none; background: #0275d8; color: white;" href="http://localhost:8000/verification?token={token}">Verify Account</a>
                <br>
                <p>Please ignore if already verified, or you did not registered</p>
            </div>
        </body>
    </html>
    """
    
    message = MIMEText(template, 'html')
    message['Subject'] = 'Ecom API Account Verification'
    message['To'] = instance.email
    message['From'] = EMAIL
    
    with SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL, PASSWORD)
        smtp.send_message(message)