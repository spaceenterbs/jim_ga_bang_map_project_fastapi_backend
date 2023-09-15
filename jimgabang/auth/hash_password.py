from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"], deprecated="auto"
)  # bcrypt는 암호화 알고리즘이다. 이 변수를 사용해 해싱에 필요한 함수들을 호출한다.


class HashPassword:
    def create_hash(self, password: str) -> str:
        # 문자열을 해싱한 값을 반환한다.
        return pwd_context.hash(password)

    def verify_hash(self, plain_password: str, hashed_password: str) -> bool:
        # 일반 텍스트 패스워드와 해싱한 패스워드를 인수로 받아 두 값이 일치하는지 비교한다. 일치 여부에 따라 boolean값을 반환한다.
        return pwd_context.verify(plain_password, hashed_password)
