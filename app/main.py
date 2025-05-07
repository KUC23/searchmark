from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import searchmarks

app = FastAPI(
    title="상표 검색 API",
    description="상표 데이터를 검색할 수 있는 API입니다.",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(searchmarks.router)

@app.get("/")
async def root():
    return {"message": "상표 검색 API에 오신 것을 환영합니다."} 