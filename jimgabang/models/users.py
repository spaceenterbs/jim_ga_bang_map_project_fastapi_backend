# 사용자 처리용 모델을 정의
from typing import Optional, List
from beanie import Document, Link
from pydantic import BaseModel, EmailStr


class Host(Document):
    email: EmailStr
    password: str
    hostName: str
    image: str

    class Settings:  # Beanie ORM을 사용하여 MongoDB에 저장할 때 사용할 설정을 정의
        name = "hosts"  # User 모델을 사용하여 MongoDB에 저장할 때 사용할 컬렉션 이름을 정의. 기본값은 모델 이름의 소문자 복수형이다. 사용자 컬렉션을 사용하려면 이 값을 설정해야 한다.

    class Config:
        schema_extra = {
            "example": {
                "email": "jimgabang@gmail.com",
                "password": "jim",
                "hostName": "gabang",
                "image": "https://linktomyimage.com/image.png",
            }
        }


class Client(Document):
    email: EmailStr
    password: str
    clientName: str

    class Settings:  # Beanie ORM을 사용하여 MongoDB에 저장할 때 사용할 설정을 정의
        name = "clients"  # User 모델을 사용하여 MongoDB에 저장할 때 사용할 컬렉션 이름을 정의. 기본값은 모델 이름의 소문자 복수형이다. 사용자 컬렉션을 사용하려면 이 값을 설정해야 한다.

    class Config:
        schema_extra = {
            "example": {
                "email": "jimgabang@gmail.com",
                "password": "jim",
                "clientName": "gabang",
            }
        }


class TokenResponse(BaseModel):
    access_token: str
    token_type: str

    class Config:
        schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImZh",
                "token_type": "bearer ",
            }
        }
