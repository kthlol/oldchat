from fastapi import FastAPI
from dotenv import load_dotenv
from app.routers import chat

load_dotenv()  # 加载 backend/.env 环境变量

app = FastAPI(title="AI Voice Chat Demo")

# 挂载 WebSocket 路由
app.include_router(chat.router)
