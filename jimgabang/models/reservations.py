# 이벤트 처리용 모델을 정의
from pydantic import BaseModel
from beanie import Document
from typing import Optional, List


# models 폴더의 모델 파일을 변경하여 몽고DB 문서를 사용할 수 있도록 한다.
class Opening(Document):
    # id: int
    creator: Optional[str]  # 해당 서비스를 소유한 사용자만 처리할 수 있도록 한다.
    seviceName: str
    category: str
    address: str
    latitude: float
    longitude: float
    openingTime: str
    openingDate: List[str]
    availableBag: int
    totalAvailableBag: int

    class Config:
        schema_extra = {
            "example": {
                "seviceName": "카페 짐가방",
                "category": "카페",
                "address": "서울특별시 강남구 역삼동 123-45",
                "latitude": 37.123456,
                "longitude": 37.123456,
                "openingTime": "09:00 ~ 18:00",
                "openingDate": "2021-09-01, 2021-09-02, 2021-09-03, 2021-09-04, 2021-09-05",
                "availableBag": 5,
                "totalAvailableBag": 5,
            }
        }

    class Settings:  # Beanie ORM을 사용하여 MongoDB에 저장할 때 사용할 설정을 정의
        name = "openings"  # Event 모델을 사용하여 MongoDB에 저장할 때 사용할 컬렉션 이름을 정의. 기본값은 모델 이름의 소문자 복수형이다. 사용자 컬렉션을 사용하려면 이 값을 설정해야 한다.


class Booking(Document):
    # id: int
    creator: Optional[str]  # 해당 이벤트를 소유한 사용자만 처리할 수 있도록 한다.
    bookDate: List[str]
    bookingBag: int
    confirm: bool

    class Config:
        schema_extra = {
            "example": {
                "bookDate": "2021-09-01, 2021-09-02, 2021-09-03, 2021-09-04, 2021-09-05",
                "bookingBag": 5,
                "confirm": False,
            }
        }

    class Settings:  # Beanie ORM을 사용하여 MongoDB에 저장할 때 사용할 설정을 정의
        name = "bookings"  # Event 모델을 사용하여 MongoDB에 저장할 때 사용할 컬렉션 이름을 정의. 기본값은 모델 이름의 소문자 복수형이다. 사용자 컬렉션을 사용하려면 이 값을 설정해야 한다.


class OpeningUpdate(BaseModel):
    seviceName: Optional[str]
    category: Optional[str]
    address: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    openingTime: Optional[str]
    openingDate: Optional[List[str]]
    availableBag: Optional[int]
    totalAvailableBag: Optional[int]

    class Config:
        schema_extra = {
            "example": {
                "seviceName": "카페 짐가방",
                "category": "카페",
                "address": "서울특별시 강남구 역삼동 123-45",
                "latitude": 37.123456,
                "longitude": 37.123456,
                "openingTime": "09:00 ~ 18:00",
                "openingDate": "2021-09-01, 2021-09-02, 2021-09-03, 2021-09-04, 2021-09-05",
                "availableBag": 5,
                "totalAvailableBag": 5,
            }
        }


class BookingUpdate(BaseModel):
    bookDate: Optional[List[str]]
    bookingBag: Optional[int]
    confirm: Optional[bool]

    class Config:
        schema_extra = {
            "example": {
                "bookDate": "2021-09-01, 2021-09-02, 2021-09-03, 2021-09-04, 2021-09-05",
                "bookingBag": 5,
                "confirm": False,
            }
        }
