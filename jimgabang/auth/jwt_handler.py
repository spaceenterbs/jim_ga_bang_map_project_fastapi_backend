import time
from datetime import datetime

from fastapi import HTTPException, status
from jose import jwt, JWTError  # JWT를 인코딩, 디코딩하는 jose 라이브러리
from database.connections import Settings
from models.users import Host, Client

# SECRET_KEY 변수를 추출할 수 있도록 Settings 클래스의 인스턴스를 만들고 토큰 생성용 함수를 정의한다.
settings = Settings()


def create_access_token(user: str) -> str:  # 토큰 생성함수는 문자열 하나를 받아서 payload 딕셔너리에 전달한다.
    # payload 딕셔너리는 사용자명과 만료 시간을 포함하여 JWT가 디코딩될 때 반환된다.
    payload = {
        "user": user,
        "expires": time.time() + 3600,  # 토큰의 만료 시간을 1시간으로 설정한다.
    }

    """
    encode() 메서드는
    payload: 값이 저장된 딕셔너리로, 인코딩할 대상.
    key: 페이로드를 사인하기 위한 키.
    algorithm: payload를 사인 및 암호화하는 알고리즘으로, 기본값인 HS256 알고리즘이 가장 많이 사용된다.
    """
    token = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm="HS256",
    )
    return token


# 앱에 전달된 토큰을 검증하는 함수
async def verify_host_access_token(token: str) -> dict:
    try:
        # 함수가 토큰을 문자열로 받아 try 블록 내에서 여러 가지 확인 작업을 거친다.
        data = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        expire = data.get("expires")

        if expire is None:  # 토큰의 만료 시간이 존재하는지 확인한다.
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No access token supplied",
            )
        if datetime.utcnow() > datetime.utcfromtimestamp(
            expire
        ):  # 토큰의 만료 시간이 지났는지 확인한다.
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Refresh token expired",
            )
        user_exist = await Host.find_one(Host.email == data["user"])
        if not user_exist:  # 토큰에 저장된 사용자가 존재하는지 확인한다.
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid access token",
            )
        return data  # 토큰이 유효하면 디코딩된 페이로드를 반환한다.
    except JWTError as exec:  # JWT 요청 자체에 오류가 있는지 확인한다.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JWTError refresh token",
        ) from exec


# 앱에 전달된 토큰을 검증하는 함수
async def verify_client_access_token(token: str) -> dict:
    try:
        # 함수가 토큰을 문자열로 받아 try 블록 내에서 여러 가지 확인 작업을 거친다.
        data = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        expire = data.get("expires")

        if expire is None:  # 토큰의 만료 시간이 존재하는지 확인한다.
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No access token supplied",
            )
        if datetime.utcnow() > datetime.utcfromtimestamp(
            expire
        ):  # 토큰의 만료 시간이 지났는지 확인한다.
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Refresh token expired",
            )
        user_exist = await Client.find_one(Client.email == data["user"])
        if not user_exist:  # 토큰에 저장된 사용자가 존재하는지 확인한다.
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid access token",
            )
        return data  # 토큰이 유효하면 디코딩된 페이로드를 반환한다.
    except JWTError as exec:  # JWT 요청 자체에 오류가 있는지 확인한다.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JWTError refresh token",
        ) from exec


"""
=====================================================================================
"""


def create_refresh_token(
    # user_type: str,
    user: str,
) -> str:
    """
    사용자 이름을 받아서 새로운 Refresh 토큰을 생성한다. 이 토큰은 더 오랜 기간 동안 유효하다.
    """
    payload = {
        # "user_type": user_type,
        "user": user,
        "expires": time.time() + 3600 * 24 * 7,  # 토큰의 만료 시간을 7일로 설정한다.
    }
    token = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm="HS256",
    )
    return token


# 앱에 전달된 refresh 토큰을 검증하는 함수
async def verify_host_refresh_token(token: str) -> dict:
    try:
        # 함수가 토큰을 문자열로 받아 try 블록 내에서 여러 가지 확인 작업을 거친다.
        data = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        expire = data.get("expires")

        if expire is None:  # 토큰의 만료 시간이 존재하는지 확인한다.
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No refresh token supplied",
            )
        if datetime.utcnow() > datetime.utcfromtimestamp(
            expire
        ):  # 토큰의 만료 시간이 지났는지 확인한다.
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Refresh token expired!",
            )
        user_exist = await Host.find_one(Host.email == data["user"])
        if not user_exist:  # 토큰에 저장된 사용자가 존재하는지 확인한다.
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid refresh token",
            )
        return data  # 토큰이 유효하면 디코딩된 페이로드를 반환한다.
    except JWTError as exec:  # JWT 요청 자체에 오류가 있는지 확인한다.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JWTError refresh token",
        ) from exec


async def verify_client_refresh_token(token: str) -> dict:
    try:
        # 함수가 토큰을 문자열로 받아 try 블록 내에서 여러 가지 확인 작업을 거친다.
        data = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        expire = data.get("expires")

        if expire is None:  # 토큰의 만료 시간이 존재하는지 확인한다.
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No refresh token supplied",
            )
        if datetime.utcnow() > datetime.utcfromtimestamp(
            expire
        ):  # 토큰의 만료 시간이 지났는지 확인한다.
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Refresh token expired!",
            )
        user_exist = await Client.find_one(Client.email == data["user"])
        if not user_exist:  # 토큰에 저장된 사용자가 존재하는지 확인한다.
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid refresh token",
            )
        return data  # 토큰이 유효하면 디코딩된 페이로드를 반환한다.
    except JWTError as exec:  # JWT 요청 자체에 오류가 있는지 확인한다.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JWTError refresh token",
        ) from exec


# def create_access_token(
#     user_type: str,
#     user: str,
# ) -> str:  # 토큰 생성함수는 문자열 하나를 받아서 payload 딕셔너리에 전달한다.
#     # payload 딕셔너리는 사용자명과 만료 시간을 포함하여 JWT가 디코딩될 때 반환된다.
#     payload = {
#         "user_type": user_type,
#         "user": user,
#         "expires": time.time() + 3600 * 24,  # 토큰의 만료 시간을 1일으로 설정한다.
#     }

#     """
#     encode() 메서드는
#     payload: 값이 저장된 딕셔너리로, 인코딩할 대상.
#     key: 페이로드를 사인하기 위한 키.
#     algorithm: payload를 사인 및 암호화하는 알고리즘으로, 기본값인 HS256 알고리즘이 가장 많이 사용된다.
#     """
#     token = jwt.encode(
#         payload,
#         settings.SECRET_KEY,
#         algorithm="HS256",
#     )
#     return token


# async def verify_access_token(token: str) -> dict:
#     """
#     앱에 전달된 토큰을 검증하는 함수
#     """
#     try:
#         # 함수가 토큰을 문자열로 받아 try 블록 내에서 여러 가지 확인 작업을 거친다.
#         data = jwt.decode(
#             token,
#             settings.SECRET_KEY,
#             algorithms=["HS256"],
#         )
#         expire = data.get("expires")

#         if expire is None:  # 토큰의 만료 시간이 존재하는지 확인한다.
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="No access token supplied",
#             )
#         if datetime.utcnow() > datetime.utcfromtimestamp(
#             expire
#         ):  # 토큰의 만료 시간이 지났는지 확인한다.
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="Token expired!",
#             )

#         user_type = data.get("user_type")  # , "")  # user_type 필드가 없으면 빈 문자열로 초기화

#         if user_type == "host":
#             host_exist = await Host.find_one(Host.email == data["user"])

#             if not host_exist:
#                 raise HTTPException(
#                     status_code=status.HTTP_400_BAD_REQUEST,
#                     detail="Invalid host token",
#                 )

#             return data

#         elif user_type == "client":
#             client_exist = await Client.find_one(Client.email == data["user"])

#             if not client_exist:
#                 raise HTTPException(
#                     status_code=status.HTTP_400_BAD_REQUEST,
#                     detail="Invalid client token",
#                 )

#             return data

#         else:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Invalid exception token",
#             )

#     except JWTError as exc:
#         # 예외 발생 시 로그를 출력한다.
#         # print(f"JWTERROR: {exc}")
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Invalid JWTError token",
#         ) from exc

# async def verify_refresh_token(refresh_token: str) -> str:
#     """
#     Refresh 토큰 검증 및 엑세스 토큰 재발급:
#     클라이언트가 엑세스 토큰을 사용하다가 만료되면, Refresh 토큰을 사용하여 새로운 엑세스 토큰을 발급한다.
#     """
#     try:
#         data = jwt.decode(
#             refresh_token,
#             settings.SECRET_KEY,
#             algorithms=["HS256"],
#         )
#         expire = data.get("expires")

#         if expire is None:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="No refresh token supplied",
#             )
#         if datetime.utcnow() > datetime.utcfromtimestamp(expire):
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="Refresh token expired!",
#             )

#         user_type = data.get("user_type")

#         if user_type == "host":
#             host_exist = await Host.find_one(Host.email == data["user"])

#             if not host_exist:
#                 raise HTTPException(
#                     status_code=status.HTTP_400_BAD_REQUEST,
#                     detail="Invalid host refresh token",
#                 )

#             access_token = create_access_token(
#                 "host", host_exist.email
#             )  # user_type과 user 값을 전달합니다.
#             return access_token

#         elif user_type == "client":
#             client_exist = await Client.find_one(Client.email == data["user"])

#             if not client_exist:
#                 raise HTTPException(
#                     status_code=status.HTTP_400_BAD_REQUEST,
#                     detail="Invalid client refresh token",
#                 )

#             access_token = create_access_token(
#                 "client", client_exist.email
#             )  # user_type과 user 값을 전달합니다.
#             return access_token

#         else:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Invalid exception refresh token",
#             )

#     except (
#         JWTError
#     ) as exc:  # as exc로 HTTPException이 JWTError를 원인으로 갖게 되며, 디버깅 및 로깅 등의 목적으로 예외 정보를 더 자세하게 추적할 수 있다.
#         print(f"JWTERROR: {exc}")
#         raise HTTPException(  # 예외를 다시 발생시킬 때 보다 명시적인 방식으로 다시 발생시키도록 권장
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Invalid JWTError refresh token",
#         ) from exc
