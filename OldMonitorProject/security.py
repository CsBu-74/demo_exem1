
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

# Простые логин и пароль без хеширования
VALID_USERNAME = "user"
VALID_PASSWORD = "password"

security_check = HTTPBasic()

def authorize(credentials: HTTPBasicCredentials = Depends(security_check)):
    if credentials.username != VALID_USERNAME or credentials.password != VALID_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

