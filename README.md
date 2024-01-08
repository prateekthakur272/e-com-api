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