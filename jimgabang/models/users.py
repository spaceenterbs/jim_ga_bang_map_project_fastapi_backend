# 사용자 처리용 모델을 정의
from typing import Optional, List
from beanie import Document, Link
from pydantic import BaseModel, EmailStr
from models.events import Event


class Server(Document):
    email: EmailStr
    password: str
    servername: str
    image: str
    # opening: Optional[List[Opening]]
    # events: Optional[
    #     List[Event]
    # ]  # 선택적 필드인 Optional은 필요에 따라 값을 포함하거나 생략할 수 있다. None이 될 수 있다. # = None  # 기본값을 정해줘야 한다.

    class Settings:  # Beanie ORM을 사용하여 MongoDB에 저장할 때 사용할 설정을 정의
        name = "servers"  # User 모델을 사용하여 MongoDB에 저장할 때 사용할 컬렉션 이름을 정의. 기본값은 모델 이름의 소문자 복수형이다. 사용자 컬렉션을 사용하려면 이 값을 설정해야 한다.

    class Config:
        schema_extra = {
            "example": {
                "email": "jimgabang@gmail.com",
                "password": "jim",
                "serverName": "gabang",
                "image": "https://linktomyimage.com/image.png",
                # "events": [],
            }
        }


class Client(Document):
    email: EmailStr
    password: str
    clientname: str
    # booking: Optional[List[Booking]]
    # events: Optional[
    #     List[Event]
    # ]  # 선택적 필드인 Optional은 필요에 따라 값을 포함하거나 생략할 수 있다. None이 될 수 있다. # = None  # 기본값을 정해줘야 한다.

    class Settings:  # Beanie ORM을 사용하여 MongoDB에 저장할 때 사용할 설정을 정의
        name = "clients"  # User 모델을 사용하여 MongoDB에 저장할 때 사용할 컬렉션 이름을 정의. 기본값은 모델 이름의 소문자 복수형이다. 사용자 컬렉션을 사용하려면 이 값을 설정해야 한다.

    class Config:
        schema_extra = {
            "example": {
                "email": "jimgabang@gmail.com",
                "password": "jim",
                "clientName": "gabang",
                # "events": [],
            }
        }


class TokenResponse(BaseModel):
    access_token: str
    token_type: str

    # class Config:
    #     schema_extra = {
    #         "example": {
    #             "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImZh",
    #             "token_type": "bearer ",
    #         }
    #     }


# class UserSignIn(Document):  # "로그인 라우트 변경"과 함께 더 이상 사용되지 않게 된다.
#     email: EmailStr
#     password: str

#     class Config:
#         schema_extra = {
#             "example": {
#                 "email": "fastapi@packt.com",
#                 "password": "strong!!!",
#                 "events": [],
#             }
#         }
