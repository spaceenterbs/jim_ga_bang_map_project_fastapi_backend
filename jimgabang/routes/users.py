# 사용자 등록 및 로그인 처리를 위한 라우팅
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import (
    OAuth2PasswordRequestForm,
)  # 인증 정보(사용자명과 패스워드)를 추출하기 위해 로그인 라우트에 주입될 것
from auth.jwt_handler import create_access_token
from database.connection import Database

from auth.hash_password import HashPassword

from models.users import Server, Client, TokenResponse  # UserSignIn

server_router = APIRouter(  # swagger에서 보여지는 태그 이름을 설정한다.
    tags=["Server"],
)
client_router = APIRouter(
    tags=["client"],
)

server_database = Database(Server)
client_database = Database(Client)
hash_password = HashPassword()

# users = {}  # 사용자 데이터를 관리하기 위한 목적. 데이터를 딕셔너리에 추가하고 검색하기 위해 사용된다.


@server_router.post("/server/signup")
async def sign_new_server(server: Server) -> dict:
    """
    해당 이메일의 사용자가 존재하는지 확인하고 없으면 db에 등록한다.
    """
    server_exist = await Server.find_one(Server.email == server.email)
    if server_exist:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Server with email provided exists already",
        )
    # 패스워드를 해싱해서 db에 저장하도록 routes/servers.py의 사용자 등록 라우트를 수정한다.
    """ 이렇게 하면 사용자 등록 라우트가 사용자를 등록할 때 패스워드를 해싱한 후 저장한다. """
    hashed_password = hash_password.create_hash(server.password)
    server.password = hashed_password
    await server_database.save(server)
    return {
        "message": "Server created successfully.",
    }


@client_router.post("/client/signup")
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
    """ 이렇게 하면 사용자 등록 라우트가 사용자를 등록할 때 패스워드를 해싱한 후 저장한다. """
    hashed_password = hash_password.create_hash(client.password)
    client.password = hashed_password
    await client_database.save(client)
    return {
        "message": "Client created successfully.",
    }


# 등록 라우트에서는 애플리케이션에 내장된 데이터베이스를 사용한다.
# 이 라우트는 사용자를 등록하기 전 데이터베이스에 같은 이메일이 존재하는지 확인한다.


@server_router.post("/server/signin", response_model=TokenResponse)
async def sign_server_in(
    server: OAuth2PasswordRequestForm = Depends(),
) -> dict:
    # OAuth2PasswordRequestForm 클래스를 sign_server_in() 라우트 함수에 주입하여 해당 함수가 OAuth2 사양을 엄격하게 따르도록 한다.
    # 함수 내에서는 패스워드, 반환된 접속 토큰, 토큰 유형을 검증한다.
    """
    해당 사용자가 존재하는지 확인한다.
    여기 쓰인 간단한 사용자 인증은 추후 수정할 예정이다.
    """
    server_exist = await Server.find_one(Server.email == server.servername)
    if not server_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Server with email does not exist.",
        )

    if hash_password.verify_hash(
        server.password, server_exist.password
    ):  # 사용자가 입력한 원본 비밀번호와, db에 저장돼있는 해시된 비밀번호를 비교한다.
        access_token = create_access_token(server_exist.email)
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
    여기 쓰인 간단한 사용자 인증은 추후 수정할 예정이다.
    """
    client_exist = await Client.find_one(Client.email == client.clientname)
    if not client_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client with email does not exist.",
        )

    if hash_password.verify_hash(
        client.password, client_exist.password
    ):  # 사용자가 입력한 원본 비밀번호와, db에 저장돼있는 해시된 비밀번호를 비교한다.
        access_token = create_access_token(client_exist.email)
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
