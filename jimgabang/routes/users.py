# 사용자 등록 및 로그인 처리를 위한 라우팅
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import (
    OAuth2PasswordRequestForm,
)  # 인증 정보(사용자명과 패스워드)를 추출하기 위해 로그인 라우트에 주입될 것
from auth.jwt_handler import (
    create_access_token,
    create_refresh_token,
    verify_host_refresh_token,
    verify_client_refresh_token,
)
from database.connections import Database
from jose import JWTError  # JWT를 인코딩, 디코딩하는 jose 라이브러리
from auth.hash_password import HashPassword
from auth.authenticate import authenticate_client, authenticate_host
from models.users import (
    Host,
    Client,
    TokenResponse,
    HostUpdate,
    ClientUpdate,
)

# from bson import ObjectId

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
async def sign_new_host_up(
    current_user: Host,  # 라우트 함수가 호출될 때 전달되는 인자인 'current_user'는 'Host' 타입으로 정의되어 있고 'Host' 데이터 모델 형식에 맞는 데이터를 전달해야 함을 의미한다.
) -> dict:
    """
    Host 등록 라우트\n
    해당 이메일의 Host가 존재하는지 확인하고 없으면 DB에 등록한다.
    """
    host_exist = await Host.find_one(
        Host.email
        == current_user.email,  # 전달받은 'current_user' 객체의 'email' 필드 값과 일치하는 'Host' 객체(문서 내)의 email 필드 값을 찾는다.
    )
    if host_exist:  # 이미 존재하는 이메일이라면 409 상태 코드를 반환한다.
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Host with the email provided already exists",
        )

    hashed_password = hash_password.create_hash(current_user.password)  # 패스워드를 해싱한 후 저장
    current_user.password = hashed_password  # 사용자 등록 라우트가 사용자를 등록할 때 패스워드를 해싱한 후 저장

    result = await host_database.save(current_user)  # 데이터베이스에 host를 저장한다.

    return {
        "message": "Host created successfully.",
        "host": result.dict(
            exclude={"password"},
        ),  # dict() 메서드를 사용하여 Host 모델의 모든 필드를 딕셔너리로 변환한다. exclude 매개변수를 사용하여 password 필드를 제외한다. or include "email", "host_name",
        # 여기서는 password 필드를 제외하기 위해 response_model을 인자로 받지 않는다.
    }


@host_router.post("/signin", response_model=TokenResponse)
async def sign_host_in(
    host: OAuth2PasswordRequestForm = Depends(),
) -> dict:
    # OAuth2PasswordRequestForm 클래스를 sign_host_in() 라우트 함수에 주입하여 해당 함수가 OAuth2 사양을 엄격하게 따르도록 한다.
    # 함수 내에서는 패스워드, 반환된 접속 토큰, 토큰 유형을 검증한다.
    """
    해당 email을 사용하는 Host가 존재하는지 확인하고\n
    로그인하면 access와 refresh 토큰, 그리고 토큰 유형을 반환한다.
    """
    host_exist = await Host.find_one(
        Host.email == host.username,
    )  # Host 객체의 email 필드가 host.username과 일치하는 문서를 찾는다.
    if not host_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Host with email does not exist.",
        )

    if hash_password.verify_hash(
        host.password, host_exist.password
    ):  # 사용자가 입력한 원본 비밀번호와, DB에 저장돼있는 해시된 비밀번호를 비교한다.
        access_token = create_access_token(host_exist.email)
        refresh_token = create_refresh_token(host_exist.email)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer ",
        }
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid details passed for Host signin",
    )


@host_router.post("/refresh-token", response_model=TokenResponse)
async def refresh_host_access_token(
    host: OAuth2PasswordRequestForm = Depends(),
) -> dict:
    """
    refresh 토큰으로 access 토큰을 갱신한다.
    1. 호스트는 서버에 로그인 요청(signin시)을 보내고, 서버는 응답으로 access, refresh 토큰, 그리고 토큰 유형을 반환한다.
    2. 호스트는 이후의 요청에 대해 받은 access_token을 Authorization header에 담아서 보낸다.
    3. 만약 서버가 401 Unauthorized 응답(access_token 만료)을 반환하면, 호스트는 refresh_token을 사용하여 새로운 access_token을 요청한다.
    4. 서버는 refresh token을 검증하고, 유효한 경우 새로운 access_token과 refresh_token을 반환한다.
    """
    host_exist = await Host.find_one(
        Host.email == host.username,
    )

    if not host_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Host with the email does not exist.",
        )

    try:
        # refresh 토큰을 검증한다.
        decoded_refresh_token = verify_host_refresh_token(  # decoded_refresh_token은 코루틴을 반환하는 비동기 함수이다. async def로 정의된 함수는 호출될 때 즉시 코루틴 객체를 반환한다. await 키워드를 사용하면 코루틴 객체가 실행되고 결과를 반환한다.
            host.password
        )  # host.password는 host.refresh_token이 대입된 값이다.

        if (await decoded_refresh_token)["user"] == host.username:
            # refresh 토큰이 유효하다면 새로운 access 토큰을 발급한다.
            access_token = create_access_token(host_exist.email)

            # 새로운 refresh 토큰도 발급한다.
            new_refresh_token = create_refresh_token(host_exist.email)

            return {
                "access_token": access_token,
                "refresh_token": new_refresh_token,
                "token_type": "Bearer ",
            }

    except (
        JWTError
    ) as jwt_error:  # verify_host_refresh_token() 함수를 호출하는 곳에서 발생한 예외를 처리한다.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid JWTError host token",
        ) from jwt_error

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid host email passed",
    )


@host_router.get("/", response_model=Host)
async def get_host(current_user: Host = Depends(authenticate_host)) -> Host:
    """
    생성 목적: Host 정보를 가져온다.
    """

    # host_id = current_user.id
    # host = await Host.find_one(Host.id == host_id)

    host_exist = await Host.find_one(
        Host.email == current_user.email,
    )  # Host 객체의 email 필드가 host.email과 일치하는 문서를 찾는다.

    if not host_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Host with the given access_token(email) not found",
        )
    return host_exist


@host_router.put("/", response_model=Host)
async def update_host(
    body: HostUpdate,
    current_user: Host = Depends(authenticate_host),
) -> Host:
    """
    현재 호스트 정보를 업데이트한다.
    """

    # current_user 객체에서 호스트 ID를 가져온다.
    host_id = current_user.id

    # 비밀번호를 수정한 경우에만 비밀번호 해싱을 적용한다.
    if body.password:
        hashed_password = hash_password.create_hash(body.password)
        body.password = hashed_password

    # host_id를 사용하여 호스트 정보를 업데이트한다.
    updated_host = await host_database.update(host_id, body)

    if not updated_host:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Host update has been made",
        )
    return updated_host


@host_router.delete("/")
async def delete_host(current_user: Host = Depends(authenticate_host)):
    """
    생성 목적: 현재 Host 정보를 삭제합니다.
    """

    # current_user 객체에서 호스트 ID 가져온다
    host_id = current_user.id

    await host_database.delete(host_id)

    return {
        "message": "Host deleted successfully.",
    }


"""
=======================================================================================
"""


@client_router.post("/signup")
async def sign_new_client_up(
    current_user: Client,
) -> dict:
    """
    Client 등록 라우트\n
    해당 이메일의 Client가 존재하는지 확인하고 없으면 DB에 등록한다.
    """
    client_exist = await Client.find_one(Client.email == current_user.email)
    if client_exist:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Client with the email provided already exists",
        )
    """
    사용자 등록 라우트가 사용자를 등록할 때 패스워드를 해싱한 후 저장
    """
    hashed_password = hash_password.create_hash(current_user.password)
    current_user.password = hashed_password
    result = await client_database.save(current_user)

    return {
        "message": "Client created successfully.",
        "client": result.dict(
            exclude={"password"},  # password 필드를 제외한다.
        ),
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
    client_exist = await Client.find_one(
        Client.email == client.username,
    )
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
            "token_type": "Bearer ",
        }
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid details passed for Client signin",
    )


@client_router.post("/refresh-token", response_model=TokenResponse)
async def refresh_client_access_token(
    client: OAuth2PasswordRequestForm = Depends(),
) -> dict:
    """
    refresh 토큰으로 access 토큰을 갱신한다.
    1. 호스트는 서버에 로그인 요청(signin시)을 보내고, 서버는 응답으로 access, refresh 토큰, 그리고 토큰 유형을 반환한다.
    2. 호스트는 이후의 요청에 대해 받은 access_token을 Authorization header에 담아서 보낸다.
    3. 만약 서버가 401 Unauthorized 응답(access_token 만료)을 반환하면, 호스트는 refresh_token을 사용하여 새로운 access_token을 요청한다.
    4. 서버는 refresh token을 검증하고, 유효한 경우 새로운 access_token과 refresh_token을 반환한다.
    """
    client_exist = await Client.find_one(
        Client.email == client.username,
    )

    if not client_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client with email does not exist.",
        )

    try:
        # refresh 토큰을 검증한다.
        decoded_refresh_token = verify_client_refresh_token(
            client.password
        )  # client.password는 client.refresh_token이 대입된 값이다.

        if (await decoded_refresh_token)["user"] == client.username:
            # refresh 토큰이 유효하다면 새로운 access 토큰을 발급한다.
            access_token = create_access_token(client_exist.email)

            # 새로운 refresh 토큰도 발급한다.
            new_refresh_token = create_refresh_token(client_exist.email)

            return {
                "access_token": access_token,
                "refresh_token": new_refresh_token,
                "token_type": "Bearer ",
            }
    except (
        JWTError
    ) as jwt_error:  # verify_host_refresh_token() 함수를 호출하는 곳에서 발생한 예외를 처리한다.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid JWTError client token",
        ) from jwt_error

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid client email passed",
    )


@client_router.get("/", response_model=Client)
async def get_client(current_user: Client = Depends(authenticate_client)) -> Client:
    """
    생성 목적: Client 정보를 가져온다.
    """

    # client_id = current_user.id
    # client = await Client.find_one(Client.id == client_id)

    client_exist = await Client.find_one(
        Client.email == current_user.email,
    )  # Client 객체의 email 필드가 client.email과 일치하는 문서를 찾는다.

    if not client_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client with teh given access_token(email) not found",
        )
    return client_exist


@client_router.put("/", response_model=Client)
async def update_client(
    body: ClientUpdate,
    current_user: Client = Depends(authenticate_client),
) -> Client:
    """
    현재 호스트 정보를 업데이트한다.
    """

    # current_user 객체에서 호스트 ID를 가져온다.
    client_id = current_user.id

    # 비밀번호를 수정한 경우에만 비밀번호 해싱을 적용한다.
    if body.password:
        hashed_password = hash_password.create_hash(body.password)
        body.password = hashed_password

    # client_id를 사용하여 호스트 정보를 업데이트한다.
    updated_client = await client_database.update(client_id, body)

    if not updated_client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Client update has been made",
        )
    return updated_client


@client_router.delete("/")
async def delete_client(current_user: Client = Depends(authenticate_client)):
    """
    생성 목적: 현재 Client 정보를 삭제한다.
    """

    # current_user 객체에서 호스트 ID 가져온다
    client_id = current_user.id

    await client_database.delete(client_id)

    return {
        "message": "Client deleted successfully.",
    }


"""
===================================================================================================
"""

# @host_router.get("/{host_id}", response_model=Host)
# async def get_host(
#     host_id: PydanticObjectId, current_user: Host = Depends(authenticate_host)
# ) -> Host:
#     """
#     생성 목적: 호스트 정보를 id로 가져온다.
#     """
#     if current_user.id != host_id:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Forbidden: You can only get your own account",
#         )
#     host = await Host.find_one(Host.id == host_id)
#     if not host:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Host not found",
#         )
#     return host

# @host_router.put("/{host_id}", response_model=Host)
# async def update_host(
#     host_id: PydanticObjectId,
#     body: HostUpdate,
#     current_user: Host = Depends(authenticate_host),
# ) -> Host:
#     """
#     현재 호스트 정보를 업데이트한다.
#     """
#     host = await Host.get(host_id)

#     """
#     업데이트되는 사용자 정보의 password 필드가 비어 있지 않다면, 새로운 비밀번호를 해싱하고 업데이트하기 전에 해싱된 비밀번호를 해당 필드에 할당합니다. 이렇게 하면 비밀번호가 변경될 때 새로운 해시값이 저장되며, 기존 비밀번호는 해싱되어 저장됩니다.
#     """
#     # 비밀번호를 수정한 경우에만 비밀번호 해싱을 적용한다.
#     if body.password:
#         hashed_password = hash_password.create_hash(body.password)
#         body.password = hashed_password

#     # current_user 객체에서 호스트 ID를 가져온다.
#     host_id = current_user.id
#     if host_id != host.id:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Forbidden: You can only update your own account",
#         )
#     # host_id를 사용하여 호스트 정보를 업데이트한다.
#     updated_host = await host_database.update(host_id, body)

#     if not updated_host:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="No Host update has been made",
#         )
#     return updated_host

# @host_router.delete("/{host_id}")
# async def delete_host(
#     host_id: PydanticObjectId,
#     current_user: Host = Depends(authenticate_host),
# ):
#     """
#     생성 목적: 현재 호스트 정보를 삭제합니다.
#     """
#     if host_id != current_user.id:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Forbidden: You can only delete your own account",
#         )
#     host = await Host.get(host_id)
#     if not host:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Host account not found",
#         )
#     await host_database.delete(current_user.id)
#     return {
#         "message": "Host deleted successfully.",
#     }

"""
-----------------------------------------------------------------------
"""

# @client_router.get("/{client_id}", response_model=Client)
# async def get_client(
#     client_id: PydanticObjectId,
#     current_user: Client = Depends(authenticate_client),
# ) -> Client:
#     """
#     생성 목적: 클라이언트 정보를 id로 가져옵니다.
#     """
#     if current_user.id != client_id:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Forbidden: You can only get your own account",
#         )
#     client = await Client.find_one(Client.id == client_id)
#     if not client:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Client not found",
#         )
#     return client

# @client_router.put("/{client_id}", response_model=Client)
# async def update_client(
#     client_id: PydanticObjectId,
#     body: ClientUpdate,
#     current_user: Client = Depends(authenticate_client),
# ) -> Client:
#     """
#     생성 목적: 현재 클라이언트 정보를 수정합니다.
#     """
#     client = await Client.get(client_id)

#     # 비밀번호를 수정한 경우에만 비밀번호 해싱을 적용한다.
#     if body.password:
#         hashed_password = hash_password.create_hash(body.password)
#         body.password = hashed_password

#     # current_user 객체에서 클라이언트 ID를 가져온다.
#     client_id = current_user.id
#     if client_id != client.id:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Forbidden: You can only update your own account",
#         )
#     # client_id를 사용하여 클라이언트 정보를 업데이트한다.
#     updated_client = await client_database.update(client_id, body)

#     if not updated_client:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="No Client update has been made",
#         )
#     return updated_client

# @host_router.get("/get-all", response_model=list[Host])
# async def get_all_hosts():
#     """
#     생성 목적: 모든 호스트 정보를 가져옵니다.
#     """
#     hosts = await host_database.get_all()
#     return hosts

# @host_router.delete("/delete-all")
# async def delete_all_hosts():
#     """
#     모든 호스트 정보를 삭제합니다.
#     """
#     await host_database.delete_all()
#     return {"message": "All hosts deleted successfully."}


# @client_router.get("/get-all", response_model=list[Client])
# async def get_all_clients():
#     """
#     생성 목적: 모든 클라이언트 정보를 가져옵니다.
#     """
#     clients = await client_database.get_all()
#     return clients


# @client_router.delete("/delete-all")
# async def delete_all_clients():
#     """
#     모든 클라이언트 정보를 삭제합니다.
#     """
#     await client_database.delete_all()
#     return {"message": "All clients deleted successfully."}

# @client_router.delete("/{client_id}")
# async def delete_client(
#     client_id: PydanticObjectId,  # 삭제할 Client 계정의 ID를 받는다.
#     current_user: Client = Depends(authenticate_client),
# ):
#     """
#     생성 목적: 현재 호스트 정보를 삭제합니다.
#     """
#     if client_id != current_user.id:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Forbidden: You can only delete your own account",
#         )

#     client = await Client.get(client_id)
#     if not client:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Client account not found",
#         )

#     await client_database.delete(current_user.id)
#     return {
#         "message": "Client deleted successfully.",
#     }
