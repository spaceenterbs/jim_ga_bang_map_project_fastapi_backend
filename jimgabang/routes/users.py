# 사용자 등록 및 로그인 처리를 위한 라우팅
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import (
    OAuth2PasswordRequestForm,
)  # 인증 정보(사용자명과 패스워드)를 추출하기 위해 로그인 라우트에 주입될 것
from auth.jwt_handler import create_access_token
from database.connections import Database

from auth.hash_password import HashPassword
from auth.authenticate import authenticate, authenticate
from models.users import Host, Client, TokenResponse, HostUpdate, ClientUpdate

host_router = APIRouter(  # swagger에서 보여지는 태그 이름을 설정한다.
    tags=["Host"],
)
client_router = APIRouter(
    tags=["Client"],
)

host_database = Database(Host)
client_database = Database(Client)

hash_password = HashPassword()

# users = {}  # 사용자 데이터를 관리하기 위한 목적. 데이터를 딕셔너리에 추가하고 검색하기 위해 사용된다.


@host_router.post("/signup")
async def sign_new_host(host: Host) -> dict:
    """
    해당 이메일의 사용자가 존재하는지 확인하고 없으면 db에 등록한다.
    등록 라우트에서는 애플리케이션에 내장된 데이터베이스를 사용한다.
    이 라우트는 사용자를 등록하기 전 데이터베이스에 같은 이메일이 존재하는지 확인한다.
    """
    host_exist = await Host.find_one(Host.email == host.email)
    if host_exist:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Host with email provided exists already",
        )
    # 패스워드를 해싱해서 db에 저장하도록 routes/hosts.py의 사용자 등록 라우트를 수정한다.
    """
    이렇게 하면 사용자 등록 라우트가 사용자를 등록할 때 패스워드를 해싱한 후 저장한다.
    """
    hashed_password = hash_password.create_hash(host.password)
    host.password = hashed_password
    await host_database.save(host)
    return {
        "message": "Host created successfully.",
    }


@client_router.post("/signup")
async def sign_new_client(client: Client) -> dict:
    """
    해당 이메일의 사용자가 존재하는지 확인하고 없으면 db에 등록한다.
    """
    client_exist = await Client.find_one(Client.email == client.email)
    if client_exist:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Client with email provided exists already",
        )
    # 패스워드를 해싱해서 db에 저장하도록 routes/clients.py의 사용자 등록 라우트를 수정한다.
    """
    이렇게 하면 사용자 등록 라우트가 사용자를 등록할 때 패스워드를 해싱한 후 저장한다.
    """
    hashed_password = hash_password.create_hash(client.password)
    client.password = hashed_password
    await client_database.save(client)
    return {
        "message": "Client created successfully.",
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
    host_exist = await Host.find_one(Host.email == host.username)
    if not host_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Host with email does not exist.",
        )

    if hash_password.verify_hash(
        host.password, host_exist.password
    ):  # 사용자가 입력한 원본 비밀번호와, db에 저장돼있는 해시된 비밀번호를 비교한다.
        access_token = create_access_token("host", host_exist.email)
        return {
            "access_token": access_token,
            "token_type": "Bearer",
        }
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid details passed",
    )


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
        access_token = create_access_token("client", client_exist.email)
        return {
            "access_token": access_token,
            "token_type": "Bearer",
        }
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid details passed",
    )


# 이 라우트는 로그인하려는 사용자가 데이터베이스에 존재하는지를 먼저 확인하고, 없으면 예외를 발생시킨다.
# 사용자가 존재하면 패스워드가 일치하는지 확인해서 성공 또는 실패 메시지를 반환한다.
# 이후 애플리케이션 내장 데이터베이스를 돕립된 데이터베이스로 옮기는 과정을 다룰 때 암호화를 사용한 패스워드 저장 방식을 다룬다.


@host_router.put("/update", response_model=Host)
async def update_host(
    host_update: HostUpdate,
    current_user: Host = Depends(authenticate),
):
    """
    현재 호스트 정보를 업데이트합니다.
    """
    if host_update.password:
        hashed_password = hash_password.create_hash(host_update.password)
        host_update.password = hashed_password

    updated_host = await host_database.update(current_user.id, host_update.dict())
    if not updated_host:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Host update has been made",
        )
    return updated_host
    # updated_host = await host_database.update(current_user.id, host_update.dict())
    # if not updated_host:
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND,
    #         detail="No Host update has been made",
    #     )
    # return updated_host


"""
업데이트되는 사용자 정보의 password 필드가 비어 있지 않다면, 새로운 비밀번호를 해싱하고 업데이트하기 전에 해싱된 비밀번호를 해당 필드에 할당합니다. 이렇게 하면 비밀번호가 변경될 때 새로운 해시값이 저장되며, 기존 비밀번호는 해싱되어 저장됩니다.
"""


@client_router.put("/update", response_model=Client)
async def update_client(
    client_update: ClientUpdate, current_user: Client = Depends(authenticate)
):
    """
    생성 목적: 현재 클라이언트 정보를 수정합니다.
    \n

    """
    if client_update.password:
        hashed_password = hash_password.create_hash(client_update.password)
        client_update.password = hashed_password

    updated_client = await client_database.update(current_user.id, client_update.dict())
    if not updated_client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Client update has been made",
        )
    return updated_client
    # updated_client = await client_database.update(current_user.id, client_update.dict())
    # if not updated_client:
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND,
    #         detail="No Client update has been made",
    #     )
    # return updated_client


@host_router.delete("/delete")
async def delete_host(current_host: Host = Depends(authenticate)):
    """
    생성 목적: 현재 호스트 정보를 삭제합니다.
    \n

    """
    await host_database.delete(current_host.id)
    return {"message": "Host deleted successfully."}


@client_router.delete("/delete")
async def delete_client(current_client: Client = Depends(authenticate)):
    """
    생성 목적: 현재 클라이언트 정보를 삭제합니다.
    \n

    """
    await client_database.delete(current_client.id)
    return {"message": "Client deleted successfully."}


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


@host_router.get("/get/{host_id}", response_model=Host)
async def get_host(host_id: int):
    """
    생성 목적: 호스트 정보를 id로 가져옵니다.
    """
    host = await host_database.find_one(Host.id == host_id)
    if not host:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Host not found",
        )
    return host


@client_router.get("/get/{client_id}", response_model=Client)
async def get_client(client_id: int):
    """
    생성 목적: 클라이언트 정보를 id로 가져옵니다.
    """
    client = await client_database.find_one(Client.id == client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found",
        )
    return client


# @client_router.delete("/delete-all")
# async def delete_all_clients():
#     """
#     모든 클라이언트 정보를 삭제합니다.
#     """
#     await client_database.delete_all()
#     return {"message": "All clients deleted successfully."}
