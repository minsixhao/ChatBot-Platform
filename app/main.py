from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import bot_routes, chat_routes, user_routes, haiguitang_routes, prompt_routes
from app.db.database import init_db, drop_all_tables
from app.core.exceptions import AppException, app_exception_handler
import logging

logging.basicConfig(level=logging.DEBUG)

app = FastAPI()

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中，应该指定允许的源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加异常处理器
app.add_exception_handler(AppException, app_exception_handler)

@app.on_event("startup")
async def startup_event():
    await init_db()
    # await drop_all_tables()

app.include_router(user_routes.router, prefix="/api/users", tags=["users"])
app.include_router(bot_routes.router, prefix="/api/bots", tags=["bots"])
app.include_router(chat_routes.router, prefix="/api/chats", tags=["chats"])
app.include_router(haiguitang_routes.router, prefix="/api", tags=["haiguitang"])
app.include_router(prompt_routes.router, prefix="/api/prompt", tags=["prompt"])

@app.get("/api/chats/test")
async def test_chat_route():
    return {"message": "Chat route is working"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888)