# E-com API
## Overview

The FastAPI E-commerce API is a robust and scalable solution designed to power modern e-commerce applications. Built using the FastAPI framework, it leverages the speed of asynchronous programming and the simplicity of Python to provide a seamless and efficient development experience.

## Features

- **FastAPI Framework:** Utilizes the FastAPI framework for building modern, fast, and high-performance APIs with Python.
- **Secure Authentication:** Implements secure user authentication using JWT and advanced encryption.
- **RESTful Endpoints:** Provides a set of RESTful endpoints for ecom operations.
- **Error Handling:** Includes comprehensive error handling to ensure smooth user experiences and easy debugging.

## Getting Started

### Prerequisites

- Python 3.7 or later
- Install dependencies:

```bash
git clone https://github.com/yourusername/derm-detect.git
cd derm-detect
pipenv install
```

### Run API
```bash
uvicorn main:app --reload
or
python main.py
```

## Documentation
To view api documentation click on [Documentation](http://127.0.0.1:8000/docs) after starting the server


## Endpoints

### Register
Create user account to use application
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/register' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "your_username",
  "email": "your_email@gmail.com",
  "password": "your_password"
}'
```

### Login
Login user with jwt token
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/user/me' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer your_jwt_token' \
  -d ''
```

### Get JWT Token
Make a post request using a form to get JWT
```bash
curl -X 'POST' \
  'http://localhost:8000/token' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'grant_type=&username=username&password=password&scope=&client_id=&client_secret='
```

### Upload Profile
Upload a profile picture for a user
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/upload/profile' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer your_jwt_token' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@image.png;type=image/png'
```

### Update Buisness
Update your buisness/store detais
```bash
curl -X 'PUT' \
  'http://localhost:8000/buisness/me' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer your_jwt_token' \
  -H 'Content-Type: application/json' \
  -d '{
  "buisness_name": "name",
  "city": "city",
  "region": "region",
  "buisness_description": "description"
}'
```

### Get Products
```bash
curl -X 'GET' \
  'http://localhost:8000/products' \
  -H 'accept: application/json'
```

### Get Product By Id
```bash
curl -X 'GET' \
  'http://localhost:8000/products/[id]' \
  -H 'accept: application/json'
```

### Add Products
```bash
curl -X 'POST' \
  'http://localhost:8000/products' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer your_jwt_token' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "Google Pixel 7",
  "category": "Mobile Phones",
  "original_price": 450000,
  "new_price": 370000,
  "offer_expiration_date": "2024-08-11"
}'
```

### Update Product
```bash
curl -X 'PUT' \
  'http://localhost:8000/products/5' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwidXNlcm5hbWUiOiJwcmF0ZWVrdGhha3VyIn0.DNllDuG7NQNNzA2CGfVtPopdVBpJwKtjo5O9Jx5pAho' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "Google Pixel 7",
  "category": "Mobile Phone",
  "original_price": 45000,
  "new_price": 38000,
  "offer_expiration_date": "2024-05-11"
}'
```

### Delete Product
```bash
curl -X 'DELETE' \
  'http://localhost:8000/products/6' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer your_jwt_token'
```

### Upload Product Picture
```bash
curl -X 'POST' \
  'http://localhost:8000/upload/product/4' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer your_jwt_token' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@product-photo.png;type=image/png'
```