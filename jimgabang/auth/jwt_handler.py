import time
from datetime import datetime

from fastapi import HTTPException, status
from jose import jwt, JWTError  # JWT를 인코딩, 디코딩하는 jose 라이브러리
from database.connection import Settings
from models.users import User

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
    algorithm: payload를 ㅏㅅ인 및 암호화하는 알고리즘으로, 기본값인 HS256 알고리즘이 가장 많이 사용된다.
    """
    token = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm="HS256",
    )
    return token


# 앱에 전달된 토큰을 검증하는 함수
async def verify_access_token(token: str) -> dict:
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
                detail="Token expired!",
            )
        user_exist = await User.find_one(User.email == data["user"])
        if not user_exist:  # 토큰에 저장된 사용자가 존재하는지 확인한다.
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token",
            )
        return data  # 토큰이 유효하면 디코딩된 페이로드를 반환한다.
    except JWTError:  # JWT 요청 자체에 오류가 있는지 확인한다.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token",
        )
