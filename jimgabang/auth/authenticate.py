from fastapi import (
    Depends,
    HTTPException,
    status,
)  # Depends = oauth2_scheme을 의존 라이브러리 함수에 주입한다.
from fastapi.security import (
    OAuth2PasswordBearer,
)  # OAuth2PasswordBearer = 보안 로직이 존재한다는 것을 앱에 알려준다.
from auth.jwt_handler import (
    verify_access_token,
)  # 앞서 정의한 토큰 생성 및 검증 함수로, 토큰의 유효성을 확인한다.

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/signin")  # OAuth2를 위한 토큰 URL 정의


async def authenticate(
    token: str = Depends(oauth2_scheme),  # 토큰을 인수로 받는다.
) -> str:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sign in for access",
        )

    decoded_token = verify_access_token(
        token
    )  # 토큰이 유효하면 토큰을 디코딩한 후 페이로드의 사용자 필드를 반환한다.
    return decoded_token["user"]
