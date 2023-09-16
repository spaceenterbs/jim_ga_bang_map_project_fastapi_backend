# 이벤트 처리용 모델을 정의
from pydantic import BaseModel
from beanie import Document
from typing import Optional, List


# models 폴더의 모델 파일을 변경하여 몽고DB 문서를 사용할 수 있도록 한다.
class Event(Document):
    # id: int
    creator: Optional[str]  # 해당 이벤트를 소유한 사용자만 처리할 수 있도록 한다.
    title: str
    image: str
    description: str
    tags: List[str]
    location: str

    # model_config = {
    #     "json_schema_extra": {
    class Config:
        schema_extra = {
            "example": {
                "title": "FastAPI Book Launch",
                "image": "https://linktomyimage.com/image.png",
                "description": "We will be discussing the contents of the FastAPI book in this event. Ensure to come with your own copy to win gifts!",
                "tags": ["python", "fastapi", "book", "launch"],
                "location": "Google Meet",
            }
        }

    class Settings:  # Beanie ORM을 사용하여 MongoDB에 저장할 때 사용할 설정을 정의
        name = "events"  # Event 모델을 사용하여 MongoDB에 저장할 때 사용할 컬렉션 이름을 정의. 기본값은 모델 이름의 소문자 복수형이다. 사용자 컬렉션을 사용하려면 이 값을 설정해야 한다.


class EventUpdate(BaseModel):
    title: Optional[str]
    image: Optional[str]
    description: Optional[str]
    tags: Optional[List[str]]
    location: Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "title": "FastAPI Book Launch",
                "image": "https://linktomyimage.com/image.png",
                "description": "We will be discussing the contents of the FastAPI book in this event. Ensure to come with your own copy to win gifts!",
                "tags": ["python", "fastapi", "book", "launch"],
                "location": "Google Meet",
            }
        }
