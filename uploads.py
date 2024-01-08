import secrets
from fastapi import HTTPException, UploadFile, status
from PIL import Image

async def save_image(file:UploadFile, file_path:str, size:tuple,):
    parts = file.filename.lower().split('.')
    allowed_extensions = ['jpg','png','jpeg','img']
    extension = parts[1]
    if extension not in allowed_extensions:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail= f'file type {extension} not allowed')
    
    token_name = f'{secrets.token_hex(12)}.{extension}'
    file_path = file_path+token_name
    content = await file.read()
    await file.close()
    
    with open(file_path,'wb') as new_file:
        new_file.write(content)
    
    img = Image.open(file_path)
    img = img.resize(size=size)
    img.save(file_path)
    img.close()
    
    return token_name
    
    