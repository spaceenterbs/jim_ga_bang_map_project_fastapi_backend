"""
FastAPI 앱에서 인증을 처리하기 위한 모듈.
OAuth2를 사용한 토큰 기반 인증을 구현하고 있다.
"""
from fastapi import (
    Depends,
    HTTPException,
    status,
)  # Depends = oauth2_scheme을 의존 라이브러리 함수에 주입한다.

from models.users import Host, Client

from fastapi.security import (
    OAuth2PasswordBearer,
)  # OAuth2PasswordBearer = 보안 로직이 존재한다는 것을 앱에 알려준다.
from auth.jwt_handler import (
    create_access_token,
    verify_host_access_token,
    verify_client_access_token,
    verify_host_refresh_token,
    verify_client_refresh_token,
)  # 앞서 정의한 토큰 생성 및 검증 함수로, 토큰의 유효성을 확인한다. # refresh token을 검증하는 함수 추가


oauth2_scheme_host = OAuth2PasswordBearer(  # OAuth2PasswordBearer = 객체 OAuth2를 사용하는 보안 인증 방식에 대한 설정을 정의하는 객체.
    tokenUrl="host/access",
)  # OAuth2를 위한 access 토큰을 얻기 위한 엔드포인트 URL 정의

oauth2_scheme_client = OAuth2PasswordBearer(  # OAuth2PasswordBearer = 객체 OAuth2를 사용하는 보안 인증 방식에 대한 설정을 정의하는 객체.
    tokenUrl="client/access",
)  # OAuth2를 위한 access 토큰을 얻기 위한 엔드포인트 URL 정의


async def authenticate_host(
    access_token: str = Depends(oauth2_scheme_host),
) -> str:
    """
    Depends 기능을 사용하여 인증을 처리한다.
    함수는 access_token이라는 매개변수를 받고. 이 매개변수는 oauth2_scheme_host을 통해 주입된다.
    """
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sign in to access",
        )

    decoded_access_token = await verify_host_access_token(access_token)
    user_name = decoded_access_token["user"]

    # # 여기서 refresh_token을 사용하여 새로운 access_token이 유효한지 확인한다.
    # if not refresh_token:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Refresh token is missing",
    #     )

    # decoded_refresh_token = await verify_host_refresh_token(refresh_token)

    # # Refresh 토큰이 유효한지 확인
    # if decoded_access_token["user"] != decoded_refresh_token["user"]:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Mismatched access and refresh tokens",
    #     )

    # 사용자 정보를 조회하여 반환
    user = await Host.find_one(Host.email == user_name)
    return user


"""""" """""" """""" """""" """""" """""" """"""


async def authenticate_client(
    access_token: str = Depends(oauth2_scheme_client),
) -> str:
    """
    Depends 기능을 사용하여 인증을 처리한다.
    함수는 access_token이라는 매개변수를 받고. 이 매개변수는 oauth2_scheme_client을 통해 주입된다.
    """
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sign in to access",
        )

    decoded_access_token = await verify_client_access_token(access_token)
    user_name = decoded_access_token["user"]

    # # 여기서 refresh_token을 사용하여 새로운 access_token이 유효한지 확인한다.
    # if not refresh_token:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Refresh token is missing",
    #     )

    # decoded_refresh_token = await verify_client_refresh_token(refresh_token)

    # # Refresh 토큰이 유효한지 확인
    # if decoded_access_token["user"] != decoded_refresh_token["user"]:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Mismatched access and refresh tokens",
    #     )

    user = await Client.find_one(Client.email == user_name)
    return user
