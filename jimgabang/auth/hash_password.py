"""
패스워드를 암호화하는 함수가 포함된다. 이 함수는 계정을 등록할 때 또는 로그인 시 패스워드를 비교할 때 사용된다.
"""
from passlib.context import (
    CryptContext,
)  # passlib 라이브러리는 패스워드를 해싱하는 bcrypt 알고리즘을 제공한다. # pip install passlib[bcrypt]

pwd_context = CryptContext(
    schemes=["bcrypt"], deprecated="auto"
)  # bcrypt는 암호화 알고리즘이다. 저장된 pwd_context 변수를 사용해 해싱에 필요한 함수들을 호출한다.


class HashPassword:
    def create_hash(self, password: str) -> str:
        """
        문자열을 해싱한 값을 반환한다.
        """
        return pwd_context.hash(password)

    def verify_hash(self, plain_password: str, hashed_password: str) -> bool:
        """
        일반 텍스트 패스워드와 해싱한 패스워드를 인수로 받아 두 값이 일치하는지 비교한다.
        일치 여부에 따라 boolean값을 반환한다.
        """
        return pwd_context.verify(plain_password, hashed_password)
