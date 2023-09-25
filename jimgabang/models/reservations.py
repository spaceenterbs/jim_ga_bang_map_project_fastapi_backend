# 이벤트 처리용 모델을 정의
from pydantic import BaseModel
from beanie import Document
from datetime import date
from typing import Optional, List
from beanie import PydanticObjectId


class ServiceBookingRelation(Document):
    service_id: PydanticObjectId
    booking_id: PydanticObjectId


# models 폴더의 모델 파일을 변경하여 몽고DB 문서를 사용할 수 있도록 한다.
class Service(Document):
    # id: int
    # creator_id: PydanticObjectId
    creator: Optional[str]  # 해당 서비스를 소유한 사용자만 처리할 수 있도록 한다.
    serviceName: str
    category: str
    address: str
    latitude: float
    longitude: float
    serviceTime: str
    serviceDate: List[str]
    availableBag: int
    totalAvailableBag: int
    # bookings: List[Booking]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "seviceName": "카페 짐가방",
                    "category": "카페",
                    "address": "서울특별시 강남구 역삼동 123-45",
                    "latitude": 37.123456,
                    "longitude": 37.123456,
                    "serviceTime": "09:00 ~ 18:00",
                    "serviceDate": "2021-09-01, 2021-09-02, 2021-09-03, 2021-09-04, 2021-09-05",
                    "availableBag": 5,
                    "totalAvailableBag": 5,
                }
            ]
        }
    }

    class Settings:  # Beanie ORM을 사용하여 MongoDB에 저장할 때 사용할 설정을 정의
        name = "services"  # Event 모델을 사용하여 MongoDB에 저장할 때 사용할 컬렉션 이름을 정의. 기본값은 모델 이름의 소문자 복수형이다. 사용자 컬렉션을 사용하려면 이 값을 설정해야 한다.


class Booking(Document):
    # id: int
    # creator_id: PydanticObjectId
    creator: Optional[str]  # 해당 이벤트를 소유한 사용자만 처리할 수 있도록 한다.
    bookingDate: List[date]
    bookingBag: int
    confirm: bool = False
    # services: List[PydanticObjectId]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "bookingDate": "2021-09-01, 2021-09-02, 2021-09-03, 2021-09-04, 2021-09-05",
                    "bookingBag": 5,
                    "confirm": False,
                },
            ]
        }
    }

    class Settings:  # Beanie ORM을 사용하여 MongoDB에 저장할 때 사용할 설정을 정의
        name = "bookings"  # Event 모델을 사용하여 MongoDB에 저장할 때 사용할 컬렉션 이름을 정의. 기본값은 모델 이름의 소문자 복수형이다. 사용자 컬렉션을 사용하려면 이 값을 설정해야 한다.


class ServiceUpdate(BaseModel):
    seviceName: Optional[str]
    category: Optional[str]
    address: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    serviceTime: Optional[str]
    serviceDate: Optional[List[date]]
    availableBag: Optional[int]
    totalAvailableBag: Optional[int]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "seviceName": "카페 짐가방",
                    "category": "카페",
                    "address": "서울특별시 강남구 역삼동 123-45",
                    "latitude": 37.123456,
                    "longitude": 37.123456,
                    "serviceTime": "09:00 ~ 18:00",
                    "serviceDate": "2021-09-01, 2021-09-02, 2021-09-03, 2021-09-04, 2021-09-05",
                    "availableBag": 5,
                    "totalAvailableBag": 5,
                }
            ]
        }
    }


class BookingUpdate(BaseModel):
    bookingDate: Optional[List[date]]
    bookingBag: Optional[int]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "bookingDate": "2021-09-01, 2021-09-02, 2021-09-03, 2021-09-04, 2021-09-05",
                    "bookingBag": 5,
                }
            ]
        }
    }


class BookingConfirmUpdate(BaseModel):
    confirm: Optional[bool]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "confirm": False,
                }
            ]
        }
    }
