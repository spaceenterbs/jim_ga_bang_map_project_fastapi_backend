"""
connections.py 파일은 db 관련된 설정과 연결을 관리 하는 파일.
이 파일에는 db를 사용하기 위한 변수, 함수등을 정의하고
접속할 db의 주소와 사용자, 비밀번호 등을 관리한다.
"""
from beanie import init_beanie, PydanticObjectId
from motor.motor_asyncio import (
    AsyncIOMotorClient,
)  # AsyncIOMotorClient는 비동기로 작동하는 몽고DB 클라이언트이다.
from typing import Any, List, Optional
from pydantic_settings import BaseSettings
from pydantic import BaseModel
from models.users import Host, Client
from models.reservations import Service, Booking


# 데이터베이스를 초기화하는 메서드를 갖고 있다. 환경 변수를 읽어오는 클래스를 정의한다.
class Settings(BaseSettings):
    """
    DB 초기화와 관련된 설정을 다루는 데 사용된다.
    환경 변수를 읽어오며 'initialize_database'메서드를 통해 DB 초기화 작업을 수행한다.
    또한 .env 파일에서 환경 변수를 읽어온다.
    """

    SECRET_KEY: Optional[str] = None
    DATABASE_URL: Optional[str] = "default"

    async def initialize_database(self):  # 데이터베이스를 초기화하는 메서드를 정의한다.
        client = AsyncIOMotorClient(
            self.DATABASE_URL
        )  # AsyncIOMotorClient는 비동기로 작동하는 몽고DB 클라이언트이다.
        await init_beanie(  # db 클라이언트를 설정한다. SQLModel에서 생성한 몽고 엔진 버전과 문서 모델을 인수로 설정한다.
            database=client.get_default_database(),
            document_models=[Host, Client, Service, Booking],
        )

    class Config:  # db URL을 .env 파일에서 읽어온다.
        env_file = ".env"


class Database:  # 초기화 시 모델을 인수로 받는다. db 초기화 중에 사용되는 모델은 Event 또는 User 문서의 모델이다.
    """
    모델을 인수로 받아서 해당 모델과 상호작용하는 여러 메서드를 제공한다.
    save() 메서드는 문서를 인수로 받아서 db에 저장한다.
    find_one() 메서드는 쿼리를 인수로 받아서 일치하는 문서를 반환한다.
    find_all() 메서드는 컬렉션에 있는 모든 문서를 반환한다.
    get() 메서드는 ID를 인수로 받아서 컬렉션에서 일치하는 레코드를 불러온다.
    get_all() 메서드는 인수가 없고 컬렉션에 있는 모든 레코드를 불러온다.
    find() 메서드는 쿼리를 인수로 받아서 일치하는 레코드를 반환한다.
    update() 메서드는 하나의 ID와 pydantic 스키마(모델)를 인수로 받아서, 클라이언트가 보낸 PUT 요청에 의해 변경된 필드를 업데이트한다.
    delete() 메서드는 해당 레코드가 있는지 확인하고 있으면 삭제한다.
    delete_all() 메서드는 컬렉션에 있는 모든 레코드를 삭제한다.
    """

    def __init__(self, model):
        self.model = model

    async def save(
        self, document
    ) -> None:  # 문서를 인수로 받는 save() 메서드를 정의한다. 문서의 인스턴스를 받아서 db 인스턴스에 전달한다.
        await document.create()
        return

    async def find_one(self, query):
        return await self.model.get_or_none(**query)

    async def find_all(self):
        return await self.model.all().to_list()

    async def get(
        self, id: PydanticObjectId
    ) -> bool:  # ID를 인수로 받아 컬렉션에서 일치하는 레코드를 불러온다.
        doc = await self.model.get(id)
        if doc:
            return doc
        return False

    async def get_all(self) -> List[Any]:  # 인수가 없고 컬렉션에 있는 모든 레코드를 불러온다.
        docs = await self.model.find_all().to_list()
        return docs

    async def find(self, query):  # 주어진 쿼리에 해당하는 모든 문서를 반환한다.
        return await self.model.filter(**query).all().to_list()

    async def update(
        self, id: PydanticObjectId, body: BaseModel
    ) -> Any:  # update() 메서드는 하나의 ID와 pydantic 스키마(모델)를 인수로 받는다. 주어진 문서 id와 업데이트할 내용인 body를 인자로 받아 해당 id를 가진 문서의 내용을 업데이트한다.
        """
        update() 메서드는 하나의 ID와 pydantic 스키마(모델)를 인수로 받아서,
        클라이언트가 보낸 PUT 요청에 의해 변경된 필드를 업데이트한다.
        None 값은 제외되며, 변경 쿼리는 beanie의 update() 메서드를 통해 실행된다.
        """
        doc_id = id
        des_body = body.dict()
        des_body = {
            k: v for k, v in des_body.items() if v is not None
        }  # 변경된 요청 바디는 딕셔너리에 저장된 다음 None값을 제외하도록 필터링된다.
        update_query = {
            "$set": {  # $set은 명령이다. 몽고DB에서는 문서의 필드를 업데이트할 때 사용한다.
                field: value for field, value in des_body.items()
            },  # 스키마에는 클라이언트가 보낸 PUT 요청에 의해 변경된 필드가 저장된다.
        }

        doc = await self.get(doc_id)
        if not doc:
            return False  # 해당 id의 문서가 존재하지 않으면 함수는 False 값을 반환하며 종료된다.
        await doc.update(update_query)
        return doc

    # 작업이 완료되면 변경 쿼리에 저장되고 beanie의 update() 메서드를 통해 실행된다.

    async def delete(self, id: PydanticObjectId) -> bool:
        """
        해당 레코드가 있는지 확인하고 있으면 삭제한다.
        """
        doc = await self.get(id)
        if not doc:
            return False
        await doc.delete()
        return True

    async def delete_all(self):
        await self.model.delete_all()
        return True
