# 사용자 등록 및 로그인 처리를 위한 라우팅
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import (
    OAuth2PasswordRequestForm,
)  # 인증 정보(사용자명과 패스워드)를 추출하기 위해 로그인 라우트에 주입될 것
from auth.jwt_handler import create_access_token, create_refresh_token
from database.connections import Database

from auth.hash_password import HashPassword
from auth.authenticate import authenticate_client, authenticate_host
from models.users import Host, Client, TokenResponse, HostUpdate, ClientUpdate
from beanie import PydanticObjectId


host_router = APIRouter(  # swagger에서 보여지는 태그 이름을 설정한다.
    tags=["Host"],
)
client_router = APIRouter(
    tags=["Client"],
)

host_database = Database(Host)
client_database = Database(Client)

hash_password = HashPassword()


@host_router.post("/signup")
async def sign_new_host_up(host: Host) -> dict:
    """
    해당 이메일의 사용자가 존재하는지 확인하고 없으면 db에 등록한다.
    등록 라우트에서는 애플리케이션에 내장된 데이터베이스를 사용한다.
    이 라우트는 사용자를 등록하기 전 데이터베이스에 같은 이메일이 존재하는지 확인한다.
    """
    host_exist = await Host.find_one(
        Host.email == host.email
    )  # Host 객체의 email 필드가 host.email과 일치하는 문서를 찾는다.
    if host_exist:  # 이미 존재하는 이메일이라면 409 상태 코드를 반환한다.
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Host with email provided exists already",
        )

    """
    사용자 등록 라우트가 사용자를 등록할 때 패스워드를 해싱한 후 저장
    """
    hashed_password = hash_password.create_hash(host.password)
    host.password = hashed_password
    await host_database.save(host)  # 데이터베이스에 host를 저장한다.
    return {
        "message": "Host created successfully.",
    }


@host_router.post("/signin", response_model=TokenResponse)
async def sign_host_in(
    host: OAuth2PasswordRequestForm = Depends(),
) -> dict:
    # OAuth2PasswordRequestForm 클래스를 sign_host_in() 라우트 함수에 주입하여 해당 함수가 OAuth2 사양을 엄격하게 따르도록 한다.
    # 함수 내에서는 패스워드, 반환된 접속 토큰, 토큰 유형을 검증한다.
    """
    해당 사용자가 존재하는지 확인한다.
    """
    host_exist = await Host.find_one(
        Host.email == host.username
    )  # Host 객체의 email 필드가 host.username과 일치하는 문서를 찾는다.
    if not host_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Host with email does not exist.",
        )

    if hash_password.verify_hash(
        host.password, host_exist.password
    ):  # 사용자가 입력한 원본 비밀번호와, db에 저장돼있는 해시된 비밀번호를 비교한다.
        access_token = create_access_token(host_exist.email)
        refresh_token = create_refresh_token(host_exist.email)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
        }
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid details passed",
    )


@client_router.post("/signup")
async def sign_new_client_up(client: Client) -> dict:
    """
    해당 이메일의 사용자가 존재하는지 확인하고 없으면 db에 등록한다.
    """
    client_exist = await Client.find_one(Client.email == client.email)
    if client_exist:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Client with email provided exists already",
        )
    """
    사용자 등록 라우트가 사용자를 등록할 때 패스워드를 해싱한 후 저장
    """
    hashed_password = hash_password.create_hash(client.password)
    client.password = hashed_password
    await client_database.save(client)
    return {
        "message": "Client created successfully.",
    }


@client_router.post("/signin", response_model=TokenResponse)
async def sign_client_in(
    client: OAuth2PasswordRequestForm = Depends(),
) -> dict:
    # OAuth2PasswordRequestForm 클래스를 sign_client_in() 라우트 함수에 주입하여 해당 함수가 OAuth2 사양을 엄격하게 따르도록 한다.
    # 함수 내에서는 패스워드, 반환된 접속 토큰, 토큰 유형을 검증한다.
    """
    해당 사용자가 존재하는지 확인한다.
    """
    client_exist = await Client.find_one(Client.email == client.username)
    if not client_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client with email does not exist.",
        )

    if hash_password.verify_hash(
        client.password, client_exist.password
    ):  # 사용자가 입력한 원본 비밀번호와, db에 저장돼있는 해시된 비밀번호를 비교한다.
        access_token = create_access_token(client_exist.email)
        refresh_token = create_refresh_token(client_exist.email)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
        }
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid details passed",
    )


@host_router.get("/get/{host_id}", response_model=Host)
async def get_host(host_id: PydanticObjectId):  # id: str -> id: PydanticObjectId
    """
    생성 목적: 호스트 정보를 id로 가져옵니다.
    """
    host = await Host.find_one(Host.id == host_id)
    if not host:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Host not found",
        )
    return host


@client_router.get("/get/{client_id}", response_model=Client)
async def get_client(client_id: PydanticObjectId):
    """
    생성 목적: 클라이언트 정보를 id로 가져옵니다.
    """
    client = await Client.find_one(Client.id == client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found",
        )
    return client


@host_router.get("/get-all", response_model=list[Host])
async def get_all_hosts():
    """
    생성 목적: 모든 호스트 정보를 가져옵니다.
    """
    hosts = await host_database.find_all()
    return hosts


@client_router.get("/get-all", response_model=list[Client])
async def get_all_clients():
    """
    생성 목적: 모든 클라이언트 정보를 가져옵니다.
    """
    clients = await client_database.find_all()
    return clients


"""
=======================================================================================
"""


@host_router.put("/{host_id}", response_model=Host)
async def update_host(
    host_id: PydanticObjectId,
    body: HostUpdate,
    current_user: Host = Depends(authenticate_host),
) -> Host:
    """
    현재 호스트 정보를 업데이트한다.
    """
    host = await Host.get(host_id)

    # 비밀번호를 수정한 경우에만 비밀번호 해싱을 적용한다.
    if body.password:
        hashed_password = hash_password.create_hash(body.password)
        body.password = hashed_password

    # current_user 객체에서 호스트 ID를 가져온다.
    host_id = current_user.id
    if host_id != host.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You can only update your own account",
        )
    # host_id를 사용하여 호스트 정보를 업데이트한다.
    updated_host = await host_database.update(host_id, body)

    if not updated_host:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Host update has been made",
        )
    return updated_host


"""
업데이트되는 사용자 정보의 password 필드가 비어 있지 않다면, 새로운 비밀번호를 해싱하고 업데이트하기 전에 해싱된 비밀번호를 해당 필드에 할당합니다. 이렇게 하면 비밀번호가 변경될 때 새로운 해시값이 저장되며, 기존 비밀번호는 해싱되어 저장됩니다.
"""


@client_router.put("/{client_id}", response_model=Client)
async def update_client(
    client_id: PydanticObjectId,
    body: ClientUpdate,
    current_user: Client = Depends(authenticate_client),
) -> Client:
    """
    생성 목적: 현재 클라이언트 정보를 수정합니다.
    """
    client = await Client.get(client_id)

    # 비밀번호를 수정한 경우에만 비밀번호 해싱을 적용한다.
    if body.password:
        hashed_password = hash_password.create_hash(body.password)
        body.password = hashed_password

    # current_user 객체에서 클라이언트 ID를 가져온다.
    client_id = current_user.id
    if client_id != client.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You can only update your own account",
        )
    # client_id를 사용하여 클라이언트 정보를 업데이트한다.
    updated_client = await client_database.update(current_user.id, body)

    if not updated_client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Client update has been made",
        )
    return updated_client


"""
===================================================================================================
"""


@host_router.delete("/{host_id}")
async def delete_host(
    host_id: PydanticObjectId,
    current_host: Host = Depends(authenticate_host),
):
    """
    생성 목적: 현재 호스트 정보를 삭제합니다.
    """
    if host_id != current_host.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You can only delete your own account",
        )
    host = await Host.get(host_id)
    if not host:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Host account not found",
        )
    await host_database.delete(current_host.id)
    return {
        "message": "Host deleted successfully.",
    }


@client_router.delete("/{client_id}")
async def delete_client(
    client_id: PydanticObjectId,  # 삭제할 Client 계정의 ID를 받는다.
    current_client: Client = Depends(authenticate_client),
):
    """
    생성 목적: 현재 호스트 정보를 삭제합니다.
    """
    # 1. 클라이언트가 요청한 Client ID와 현재 인증된 클라이언트 ID를 비교한다.
    if client_id != current_client.id:
        raise HTTPException(
            status_code=403,
            detail="Forbidden: You can only delete your own account",
        )

    # 2. Client 계정을 삭제하기 전에 존재하는지 확인한다.
    client = await Client.get(client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client account not found",
        )

    # 3. Client 계정을 삭제한다.
    await client.delete()

    return {
        "message": "Client deleted successfully.",
    }


"""
===================================================================================================
"""


@host_router.delete("/delete-all")
async def delete_all_hosts():
    """
    모든 호스트 정보를 삭제합니다.
    """
    await host_database.delete_all()
    return {"message": "All hosts deleted successfully."}


@client_router.delete("/delete-all")
async def delete_all_clients():
    """
    모든 클라이언트 정보를 삭제합니다.
    """
    await client_database.delete_all()
    return {"message": "All clients deleted successfully."}
