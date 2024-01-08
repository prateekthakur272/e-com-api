from dotenv import dotenv_values

config_creds = dotenv_values('.env')


EMAIL = config_creds['EMAIL']
PASSWORD = config_creds['PASSWORD']
SECRET = config_creds['SECRET']


BASE_URL = 'localhost:8000/'