# 이벤트 처리용 모델을 정의
from pydantic import BaseModel, EmailStr
from beanie import Document

# from datetime import date
from typing import Optional, List
from beanie import PydanticObjectId


# models 폴더의 모델 파일을 변경하여 몽고DB 문서를 사용할 수 있도록 한다.
class Service(Document):
    creator: Optional[EmailStr] = None  # 해당 서비스를 소유한 사용자만 처리할 수 있도록 한다.
    service_name: str
    category: str
    address: str
    latitude: float
    longitude: float
    service_time: str
    service_date: List[str]
    available_bag: int
    total_available_bag: int
    bookings: Optional[List[PydanticObjectId]] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "creator": "host@gmail.com",
                    "service_name": "카페 짐가방",
                    "category": "카페",
                    "address": "서울특별시 강남구 역삼동 123-45",
                    "latitude": 37.123456,
                    "longitude": 37.123456,
                    "service_time": "09:00 ~ 18:00",
                    "service_date": [
                        "2023-10-13",
                        "2023-10-14",
                        "2023-10-15",
                    ],
                    "available_bag": 5,
                    "total_available_bag": 5,
                    "bookings": [],
                }
            ]
        }
    }

    class Settings:  # Beanie ORM을 사용하여 MongoDB에 저장할 때 사용할 설정을 정의
        name = "services"  # Event 모델을 사용하여 MongoDB에 저장할 때 사용할 컬렉션 이름을 정의. 기본값은 모델 이름의 소문자 복수형이다. 사용자 컬렉션을 사용하려면 이 값을 설정해야 한다.


class ServiceUpdate(BaseModel):
    service_name: Optional[str]
    category: Optional[str]
    address: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    service_time: Optional[str]
    service_date: Optional[List[str]]
    available_bag: Optional[int]
    total_available_bag: Optional[int]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "service_name": "카페 짐가방",
                    "category": "카페",
                    "address": "서울특별시 강남구 역삼동 123-45",
                    "latitude": 37.123456,
                    "longitude": 37.123456,
                    "service_time": "09:00 ~ 18:00",
                    "service_date": [
                        "2023-10-13",
                        "2023-10-14",
                        "2023-10-15",
                        "2023-10-16",
                        "2023-10-17",
                    ],
                    "available_bag": 55,
                    "total_available_bag": 55,
                }
            ]
        }
    }


class Booking(Document):
    creator: Optional[EmailStr] = None  # 해당 이벤트를 소유한 사용자만 처리할 수 있도록 한다.
    booking_date: List[str]
    booking_bag: int
    confirm: Optional[str] = "pending"  # confirm: Optional[bool] = False
    service: PydanticObjectId  # 서비스와 연결된다.

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "creator": "client@gmail.com",
                    "booking_date": [
                        "2023-10-13",
                        "2023-10-14",
                    ],
                    "booking_bag": 5,
                    "confirm": "pending",
                    "service": "612c1c1c3e6a7f5f5a7f5f5a",
                },
            ]
        }
    }

    class Settings:  # Beanie ORM을 사용하여 MongoDB에 저장할 때 사용할 설정을 정의
        name = "bookings"  # Event 모델을 사용하여 MongoDB에 저장할 때 사용할 컬렉션 이름을 정의. 기본값은 모델 이름의 소문자 복수형이다. 사용자 컬렉션을 사용하려면 이 값을 설정해야 한다.


class BookingUpdate(BaseModel):
    booking_date: Optional[List[str]]
    booking_bag: Optional[int]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "booking_date": [
                        "2023-10-13",
                        "2023-10-14",
                        "2023-10-15",
                        "2023-10-16",
                    ],
                    "booking_bag": 10,
                }
            ]
        }
    }


class BookingConfirmUpdate(BaseModel):
    confirm: Optional[str]  # confirm: Optional[bool]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "confirm": "cancelled",  # "confirm": "confirmed",
                }
            ]
        }
    }
