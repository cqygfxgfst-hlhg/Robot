from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.jobs import router as jobs_router

app = FastAPI()

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 允许前端域名
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有请求头
)

app.include_router(jobs_router)

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}