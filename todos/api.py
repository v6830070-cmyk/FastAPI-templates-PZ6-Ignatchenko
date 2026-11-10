from fastapi import FastAPI, HTTPException
from todo import task_router, html_router, users_db
from model import User
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse
import uvicorn

# Отключаем стандартную документацию (docs_url=None), чтобы сделать свою
app = FastAPI(title="Todo App — Игнатченко Владислав", docs_url=None)

# Корень из методички
@app.get("/")
async def welcome() -> dict:
    return {"message": "Hello World! Это приложение создал [Игнатченко Владислав]"}

# ==========================================
# БЛОК: КЛИЕНТ (API)
# ==========================================
@app.get("/api/users", tags=["Клиент (API)"])
async def get_users():
    return {"users": list(users_db.values())}

@app.post("/api/users", tags=["Клиент (API)"])
async def create_user(user: User):
    if user.email in users_db:
        raise HTTPException(status_code=409, detail="Пользователь с таким email уже существует!")
    users_db[user.email] = user
    return {"message": "Пользователь создан", "user": user}

@app.delete("/api/users/{email}", tags=["Клиент (API)"])
async def api_delete_user(email: str):
    if email in users_db:
        del users_db[email]
        return {"message": f"Пользователь {email} удален"}
    raise HTTPException(status_code=404, detail="User not found")

# ==========================================
# КАСТОМНАЯ СТРАНИЦА SWAGGER (С кнопкой назад)
# ==========================================
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    # Генерируем стандартный HTML Swagger
    swagger_html = get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI"
    )
    
    # Достаем HTML-код как строку
    html_content = swagger_html.body.decode("utf-8")
    
    # Создаем нашу кнопку (фиксируем в правом верхнем углу)
    custom_button = """
    <div style="position: fixed; top: 15px; right: 15px; z-index: 9999;">
        <a href="/todo" style="background-color: #0d6efd; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-family: sans-serif; font-weight: bold; box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: 0.3s;" onmouseover="this.style.backgroundColor='#0b5ed7'" onmouseout="this.style.backgroundColor='#0d6efd'">
            ← Вернуться к задачам
        </a>
    </div>
    """
    
    # Вставляем кнопку сразу после открывающего тега <body>
    html_content = html_content.replace("<body>", f"<body>\n{custom_button}")
    
    return HTMLResponse(content=html_content)

# Подключаем роутеры
app.include_router(task_router)
app.include_router(html_router)

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)