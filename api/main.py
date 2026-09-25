# -*- coding: utf-8 -*-
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import users, tasks, reminders

# Создаем приложение FastAPI
app = FastAPI(
    title="Garden Helper API",
    description="Асинхронный API для управления огородом",
    version="1.0.0"
)

# Настройка CORS (Cross-Origin Resource Sharing)
# Это позволяет боту (или фронтенду) делать запросы к API с другого домена/порта
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене укажи конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(users.router)
app.include_router(tasks.router)
app.include_router(reminders.router)

@app.get("/")
async def root():
    """Простой эндпоинт для проверки работоспособности API"""
    return {
        "message": "Garden Helper API is running",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }

# Точка входа для запуска через uvicorn
if __name__ == "__main__":
    import uvicorn
    # reload=True автоматически перезагружает сервер при изменении кода (удобно при разработке)
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
