"""
FastAPI 앱에서 인증을 처리하기 위한 모듈.
OAuth2를 사용한 토큰 기반 인증을 구현하고 있다.
"""
from fastapi import (
    Depends,
    HTTPException,
    status,
    Query,
    Header,
)  # Depends = oauth2_scheme을 의존 라이브러리 함수에 주입한다.
from fastapi.security import (
    OAuth2PasswordBearer,
)  # OAuth2PasswordBearer = 보안 로직이 존재한다는 것을 앱에 알려준다.
from auth.jwt_handler import (
    verify_access_token,
    verify_refresh_token,
)  # 앞서 정의한 토큰 생성 및 검증 함수로, 토큰의 유효성을 확인한다. # refresh token을 검증하는 함수 추가

from typing import Union
from typing import Optional


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/user/signin",
)  # OAuth2를 위한 access 토큰을 얻기 위한 엔드포인트 URL 정의

refresh_oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/user/refresh",
)  # OAuth2를 위한 refresh 토큰을 얻기 위한 엔드포인트 URL 정의


# host_oauth2_scheme = OAuth2PasswordBearer(
#     tokenUrl="/host/signin"
# )  # OAuth2를 위한 토큰을 얻기 위한 엔드포인트 URL 정의
# # OAuth2PasswordBearer = 객체 OAuth2를 사용하는 보안 인증 방식에 대한 설정을 정의하는 객체.
# client_oauth2_scheme = OAuth2PasswordBearer(
#     tokenUrl="/client/signin"
# )  # OAuth2를 위한 토큰을 얻기 위한 엔드포인트 URL 정의
# # OAuth2PasswordBearer = 객체 OAuth2를 사용하는 보안 인증 방식에 대한 설정을 정의하는 객체.


async def authenticate(
    access_token: str = Depends(oauth2_scheme),
    refresh_token: Optional[str] = Depends(refresh_oauth2_scheme),
    user_type: Optional[str] = Header(
        None, title="User Type", description="User type (host or client)"
    ),
) -> Union[int, str, None]:
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sign in for access",
        )

    decoded_access_token = None
    user_id_key = None

    if user_type == "host":
        user_id_key = "host_id"
    elif user_type == "client":
        user_id_key = "client_id"
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid user type for access",
        )

    try:
        decoded_access_token = await verify_access_token(access_token)
    except HTTPException as exc:
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid access token",
            ) from exc

    if not decoded_access_token:
        # 엑세스 토큰이 만료된 경우 리프레시 토큰을 사용하여 새로운 엑세스 토큰을 발급
        try:
            access_token = await verify_refresh_token(refresh_token)
            decoded_access_token = await verify_access_token(access_token)
        except HTTPException as exc:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid refresh token",
            ) from exc

    user_id = decoded_access_token.get(user_id_key)

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Invalid {user_type} token",
        )

    return user_id


# async def authenticate(
#     access_token: str = Depends(host_oauth2_scheme),
#     refresh_token: str = Depends(host_oauth2_scheme),
# ) -> str:
#     if not access_token:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Sign in for access",
#         )

#     decoded_token = await verify_access_token(access_token)
#     user_type = decoded_token.get("user_type")

#     if user_type == "host":
#         host_id = decoded_token.get("host_id")
#         if not host_id:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="Invalid host token",
#             )

#         # 호스트가 엑세스 토큰을 사용하다가 만료된 경우 리프레시 토큰을 사용하여 새로운 엑세스 토큰 발급
#         if refresh_token:
#             try:
#                 access_token = await verify_refresh_token(refresh_token)
#                 return access_token
#             except HTTPException as exc:
#                 raise HTTPException(
#                     status_code=status.HTTP_403_FORBIDDEN,
#                     detail="Invalid refresh token",
#                 ) from exc

#         return host_id

#     else:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Invalid user type",
#         )


# async def authenticate(
#     access_token: str = Depends(client_oauth2_scheme),
#     refresh_token: str = Depends(client_oauth2_scheme),
# ) -> int:
#     if not access_token:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Sign in for access",
#         )

#     decoded_token = await verify_access_token(access_token)
#     user_type = decoded_token.get("user_type")

#     if user_type == "client":
#         client_id = decoded_token.get("client_id")
#         if not client_id:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="Invalid client token",
#             )

#         # 클라이언트가 엑세스 토큰을 사용하다가 만료된 경우 리프레시 토큰을 사용하여 새로운 엑세스 토큰 발급
#         if refresh_token:
#             try:
#                 access_token = await verify_refresh_token(refresh_token)
#                 return access_token
#             except HTTPException as exc:
#                 raise HTTPException(
#                     status_code=status.HTTP_403_FORBIDDEN,
#                     detail="Invalid refresh token",
#                 ) from exc

#         return client_id

#     else:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Invalid user type",
#         )


"""""" """""" """""" """""" """""" """""" """"""
"""""" """""" """""" """""" """""" """""" """"""


# async def authenticate(
#     access_token: str = Depends(oauth2_scheme),  # 토큰을 인수로 받는다.
# ) -> Union[str, int]:
#     """
#     Depends 기능을 사용하여 인증을 처리한다.
#     함수는 access_token이라는 매개변수를 받고. 이 매개변수는 oauth2_scheme을 통해 주입된다.
#     """
#     if not access_token:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Sign in for access",
#         )

#     decoded_token = await verify_access_token(  # auth.jwt_handler 모듈의 verify_access_token 함수를 호출하여 토큰의 유효성을 검증한다.
#         access_token
#     )  # 토큰을 디코딩한 후 페이로드의 사용자 필드를 반환한다.

#     # host나 client를 사용자로 인식하여 처리하는 로직
#     user_type = decoded_token.get("user_type")  # 토큰에서 사용자 유형을 추출
#     # user_type = (await decoded_token)[
#     #     "user_type"
#     # ]  # 디코딩된 토큰에서 user_type 필드를 추출하여 사용자의 유형을 확인한다. 사용자가 host인 경우 host_id를 반환하고, client인 경우 client_id를 반환한다.
#     """
#     두 줄로 표시한 코드는 아래의 코드와 동일하다.
#     user_type = await decoded_token  # decoded_token을 코루틴으로 실행하여 결과를 얻음
#     user_type = user_type["user_type"]  # 결과를 사용
#     """

#     if user_type == "host":
#         # 호스트 관련 처리
#         host_id = decoded_token.get("host_id")
#         if not host_id:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="Invalid host token",
#             )
#         return host_id

#     elif user_type == "client":
#         # 클라이언트 관련 처리
#         client_id = decoded_token.get("client_id")
#         if not client_id:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="Invalid client token",
#             )
#         return client_id

#     else:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Invalid user type",
#         )
