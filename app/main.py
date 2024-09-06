from fastapi import FastAPI
from app.api import bot_routes, chat_routes, user_routes
from app.db.database import init_db, drop_all_tables

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    await init_db()
    # await drop_all_tables()

app.include_router(user_routes.router, prefix="/api/users", tags=["users"])
app.include_router(bot_routes.router, prefix="/api/bots", tags=["bots"])
app.include_router(chat_routes.router, prefix="/api/chats", tags=["chats"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888)