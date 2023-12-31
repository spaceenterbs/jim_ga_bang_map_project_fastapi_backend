# 사용자 처리용 모델을 정의
from typing import Optional
from beanie import Document
from pydantic import BaseModel, EmailStr


class Host(Document):
    email: EmailStr
    password: str
    host_name: str

    class Settings:  # Beanie ORM을 사용하여 MongoDB에 저장할 때 사용할 설정을 정의
        name = "hosts"  # User 모델을 사용하여 MongoDB에 저장할 때 사용할 컬렉션 이름을 정의. 기본값은 모델 이름의 소문자 복수형이다. 사용자 컬렉션을 사용하려면 이 값을 설정해야 한다.

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "host@gmail.com",
                    "password": "1234",
                    "host_name": "host",
                }
            ]
        }
    }


class Client(Document):
    email: EmailStr
    password: str
    client_name: str

    class Settings:  # Beanie ORM을 사용하여 MongoDB에 저장할 때 사용할 설정을 정의
        name = "clients"  # User 모델을 사용하여 MongoDB에 저장할 때 사용할 컬렉션 이름을 정의. 기본값은 모델 이름의 소문자 복수형이다. 사용자 컬렉션을 사용하려면 이 값을 설정해야 한다.

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "client@gmail.com",
                    "password": "1234",
                    "client_name": "client",
                }
            ]
        }
    }


class HostUpdate(BaseModel):
    password: Optional[str]
    host_name: Optional[str]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "password": "12345",
                    "host_name": "host1",
                }
            ]
        }
    }


class ClientUpdate(BaseModel):
    password: Optional[str]
    client_name: Optional[str]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "password": "12345",
                    "client_name": "client1",
                }
            ]
        }
    }


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImZh",
                    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImZh",
                    "token_type": "Bearer ",
                }
            ]
        }
    }


# class HostResponse(BaseModel):
#     message: str
#     host: Host
