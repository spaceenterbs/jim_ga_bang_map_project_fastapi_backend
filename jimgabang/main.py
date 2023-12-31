"""
app 객체는 FastAPI의 핵심 객체이다. app 객체를 통해 FastAPI의 설정을 할 수 있다.
main.py는 FastAPI 프로젝트의 전체적인 환경을 설정하는 파일이다.
"""

# 라우트를 등록하고 앱을 실행한다. 라이브러리와 사용자 라우트 정의를 임포트한다.
# import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# from fastapi.responses import RedirectResponse
from database.connections import Settings

from routes.users import host_router, client_router
from routes.reservations import service_router, booking_router

import uvicorn


# logging.basicConfig(level=logging.DEBUG)

settings = Settings()

app = FastAPI()  # debug=True)


# 출처 등록

# origins 배열을 등록하고
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://jimgabang.store",  # 도메인 이름 및 포트 번호를 기반으로 출처를 확인하므로 경로(path)인 "/"는 안 적어줘도 된다.
    "http://www.jimgabang.store",
    "https://jimgabang.store",
    "https://www.jimgabang.store",
]  # ["*"] 어떤 출처(origin)에서 들어오는 요청을 허용할지 설정한다.

# add_middleware() 메서드를 사용해 미들웨어를 등록한다.
# 미들웨어는 각 요청과 응답 사이에서 작동하는 컴포넌트로, 여러 가지 기능(로그 생성, 오류 처리 등)을 수행할 수 있다.
app.add_middleware(
    CORSMiddleware,  # 추가하려는 미들웨어의 종류. 여기서는 CORS 관련 미들웨어를 사용한다.
    allow_origins=origins,  # 어떤 출처의 요청을 허용할지 결정한다. 위에서 정의한 origins 리스트를 사용한다.
    allow_credentials=True,  # 자격 증명(예: 쿠키나 HTTP Authentication 데이터)을 포함한 요청도 허용할지 결정한다.
    allow_methods=["*"],  # 어떤 HTTP 메서드(GET, POST 등)를 허용할지 결정한다.
    allow_headers=["*"],  # 어떤 HTTP 헤더를 허용할지 결정한다.
)

# 라우트 등록
app.include_router(
    host_router,
    prefix="/api/host",
)
app.include_router(
    client_router,
    prefix="/api/client",
)
app.include_router(
    service_router,
    prefix="/api/service",
)
app.include_router(
    booking_router,
    prefix="/api/booking",
)


# 앱 실행 시 몽고DB를 초기화하도록 만든다.
@app.on_event("startup")
async def init_db():
    await settings.initialize_database()


@app.get("/")
def home():
    return "안녕하세요 짐가방입니다."


# uvicorn.run() 메서드를 사용해 8000번 포트에서 앱을 실행하도록 설정한다.
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",  # 모든 네트워크 인터페이스에서 수신 대기하므로, 같은 네트워크에 있는 다른 컴퓨터나 토커 컨테이너 등에서도 접근할 수 있다. 따라서 Docker 컨테이너 내부에서 앱을 실행하고 외부(호스트 시스템이나 다른 컨테이너)에서 접근하려면, host를 localhost 또는 127.0.0.1 대신에 0.0.0.0으로 설정해야 한다. # "127.0.0.1"
        port=8000,
        reload=True,
    )
