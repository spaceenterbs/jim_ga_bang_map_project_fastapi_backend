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

"""
Beanie ORM과 MongoDB를 사용하여 데이터베이스 연결 및 CRUD(Create, Read, Update, Delete) 작업을 처리하는 클래스와 함수들을 정의
"""


class Settings(BaseSettings):
    """
    DB 연결 설정과 관련된 정보를 저장한다.
    'initialize_database'메서드를 통해 DB 초기화 작업을 수행한다.
    또한 .env 파일에서 환경 변수를 읽어온다.
    """

    SECRET_KEY: Optional[str] = None
    DATABASE_URL: Optional[str] = "default"  # 기본값을 설정한다.

    async def initialize_database(self):
        """
        비동기 방식으로 DB 연결을 초기화하는 메서드를 정의한다.
        """
        client = (
            AsyncIOMotorClient(  # AsyncIOMotorClient 객체는 MongoDB와 비동기로 통신하기 위한 클라이언트다.
                self.DATABASE_URL
            )
        )
        """
        init_beanie는 Beanie ORM 라이브러리에서 제공하는 함수이다.
        MongoDB의 연결을 초기화하고 사용할 문서 모델들을 설정한다. 이 함수는 비동기 방식으로 동작하므로 호출 시에는 await 키워드를 사용해야 한다.
        """
        await init_beanie(
            database=client.get_default_database(),
            document_models=[Host, Client, Service, Booking],
        )
        """
        init_beanie 함수는 두 가지 인자를 받는다.
        1. database: MongoDB 클라이언트(AsyncIOMotorClient)의 get_default_database() 메서드를 통해 기본 데이터베이스를 얻어온다. 이 데이터베이스가 Beanie와 연결될 대상이다.
        2. document_models: Beanie에서 사용할 Pydantic 기반의 문서 모델들(Host, Client, Service, Booking)을 리스트 형태로 전달한다. 이 모델들은 MongoDB의 컬렉션과 매핑되며, 각각의 모델은 해당 컬렉션의 문서와 매핑된다.
        """

    class Config:  # db URL을 .env 파일에서 읽어온다.
        env_file = ".env"


class Database:
    """
    모델을 인자로 받아서 해당 모델과 상호작용하는 여러 메서드(CRUD 작업)를 제공한다.
    """

    def __init__(self, model):
        self.model = model

    async def save(self, document) -> None:
        """
        save() 메서드는 Beanie 문서를 인자로 받아서 db에 저장한다.
        create() 메서드는 Beanie에서 제공하는 메서드로, 문서 객체를 db에 저장하는 역할을 한다.
        """
        await document.create()
        return

    # async def find(self, query):
    #     """
    #     find() 메서드는 쿼리를 인자로 받아서 일치하는 모든 레코드를 반환한다.
    #     """
    #     return await self.model.filter(**query).all().to_list()

    # async def find_one(self, query):
    #     """
    #     find_one() 메서드는 쿼리를 인자로 받아서 일치하는 첫 번째 문서를 반환한다.
    #     일치하는 문서가 없으면 None을 반환한다.
    #     """
    #     return await self.model.get_or_none(**query)

    async def get(
        self, id: PydanticObjectId  # ID를 인자로 받아 컬렉션에서 일치하는 레코드를 불러온다.
    ) -> Any:
        """
        get() 메서드는 ID를 인자로 받아서 컬렉션에서 일치하는 레코드를 반환한다.
        찾지 못하면 False를 반환한다.
        """
        doc = await self.model.get(id)
        if doc:
            return doc
        return False

    async def get_all(self) -> List[Any]:
        """
        get_all() 메서드는 인자가 없고 컬렉션에 있는 모든 레코드를 리스트 형태로 반환한다.
        """
        docs = await self.model.find_all().to_list()
        return docs

    # async def find_all(self):
    #     """
    #     find_all() 메서드는 컬렉션에 있는 모든 문서를 리스트 형태로 반환한다.
    #     """
    #     return await self.model.all().to_list()

    async def update(self, id: PydanticObjectId, body: BaseModel) -> Any:
        """
        update() 메서드는 하나의 ID와 pydantic 스키마(모델)를 인자로 받아서,
        클라이언트가 보낸 PUT 요청에 의해 변경된 필드를 업데이트한다.
        None 값은 제외되며, 변경 쿼리는 beanie의 update() 메서드를 통해 실행된다.
        """
        doc_id = id
        des_body = body.model_dump()
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
        delete() 메서드는 해당 레코드가 있는지 확인하고 있으면 삭제한다.
        """
        doc = await self.get(id)
        if not doc:
            return False
        await doc.delete()
        return True

    async def delete_all(self):
        """
        delete_all() 메서드는 컬렉션에 있는 모든 레코드를 삭제한다.
        """
        all_documents = await self.model.all().to_list()
        for doc in all_documents:
            await doc.delete()

        return True
