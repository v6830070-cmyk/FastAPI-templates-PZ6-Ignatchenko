from fastapi import APIRouter, Request, Form, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from model import Todo, User, TaskCreate, TodoResponse
from typing import List

html_router = APIRouter(tags=["HTML Страницы"], include_in_schema=False)
task_router = APIRouter(tags=["Задачи (API)"])

templates = Jinja2Templates(directory="templates")

users_db = {}
todo_list = []

# ==========================================
# БЛОК API ДЛЯ SWAGGER
# ==========================================

@task_router.get("/api/tasks", response_model=List[TodoResponse])
async def get_all_todos():
    result = []
    for todo in todo_list:
        # Ищем пользователя в базе
        user = users_db.get(todo.user_email)
        # Если нашли - берем имя, если удалили - пишем "Неизвестно"
        user_name = user.name if user else "Неизвестно (пользователь удален)"
        
        # Формируем красивый ответ
        result.append(TodoResponse(
            id=todo.id,
            item=todo.item,
            user_name=user_name,
            user_email=todo.user_email
        ))
    return result

@task_router.post("/api/tasks")
async def api_add_todo(task: TaskCreate):
    user = users_db.get(task.user_email)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь с таким email не найден!")
    
    if user.name != task.user_name:
        raise HTTPException(status_code=400, detail="Имя пользователя не совпадает с указанным email!")
    
    new_id = len(todo_list) + 1
    todo_list.append(Todo(id=new_id, user_email=task.user_email, item=task.item))
    return {"message": "Задача успешно добавлена", "task": task}

@task_router.put("/api/tasks/{id}")
async def api_update_todo(id: int, task: TaskCreate):
    todo = next((t for t in todo_list if t.id == id), None)
    if not todo:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    user = users_db.get(task.user_email)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь с таким email не найден!")
    
    if user.name != task.user_name:
        raise HTTPException(status_code=400, detail="Имя пользователя не совпадает с указанным email!")

    todo.item = task.item
    todo.user_email = task.user_email
    return {"message": "Задача обновлена", "task": task}

@task_router.delete("/api/tasks/{id}")
async def api_delete_todo(id: int):
    global todo_list
    todo_list = [t for t in todo_list if t.id != id]
    return {"message": "Задача удалена"}

# ==========================================
# БЛОК HTML СТРАНИЦ (Без изменений)
# ==========================================

@html_router.get("/todo")
async def get_todos_page(request: Request):
    return templates.TemplateResponse(
        request=request, name="todo.html", 
        context={"todos": todo_list, "users": list(users_db.values())}
    )

@html_router.get("/user/add")
async def add_user_page(request: Request):
    return templates.TemplateResponse(request=request, name="add_user.html", context={})

@html_router.post("/user/add")
async def add_user(name: str = Form(...), email: str = Form(...)):
    if email in users_db:
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует!")
    users_db[email] = User(name=name, email=email)
    return RedirectResponse(url="/todo", status_code=303)

@html_router.get("/user/edit/{email}")
async def edit_user_page(request: Request, email: str):
    user = users_db.get(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return templates.TemplateResponse(request=request, name="user_edit.html", context={"user": user})

@html_router.post("/user/edit/{old_email}")
async def update_user(old_email: str, name: str = Form(...), email: str = Form(...)):
    users_db[email] = User(name=name, email=email)
    if old_email != email:
        users_db.pop(old_email, None)
        for t in todo_list:
            if t.user_email == old_email:
                t.user_email = email
    return RedirectResponse(url="/todo", status_code=303)

@html_router.get("/user/delete")
async def delete_user_page(request: Request):
    return templates.TemplateResponse(request=request, name="delete_user.html", context={"users": list(users_db.values())})

@html_router.post("/user/delete/{email}")
async def delete_user(email: str):
    if email in users_db:
        del users_db[email]
    return RedirectResponse(url="/todo", status_code=303)

@html_router.get("/todo/add")
async def add_todo_page(request: Request):
    return templates.TemplateResponse(request=request, name="add_todo.html", context={"users": list(users_db.values())})

@html_router.post("/todo/add")
async def add_todo(item: str = Form(...), user_email: str = Form(...)):
    if user_email not in users_db:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    new_id = len(todo_list) + 1
    todo_list.append(Todo(id=new_id, user_email=user_email, item=item))
    return RedirectResponse(url="/todo", status_code=303)

@html_router.get("/todo/edit/{id}")
async def edit_todo_page(request: Request, id: int):
    todo = next((t for t in todo_list if t.id == id), None)
    if not todo:
        raise HTTPException(status_code=404, detail="Task not found")
    return templates.TemplateResponse(request=request, name="edit.html", context={"todo": todo, "users": list(users_db.values())})

@html_router.post("/todo/edit/{id}")
async def update_todo(id: int, item: str = Form(...), user_email: str = Form(...)):
    todo = next((t for t in todo_list if t.id == id), None)
    if todo:
        todo.item = item
        todo.user_email = user_email
    return RedirectResponse(url="/todo", status_code=303)

@html_router.get("/todo/delete/{id}")
async def delete_todo(id: int):
    global todo_list
    todo_list = [t for t in todo_list if t.id != id]
    return RedirectResponse(url="/todo", status_code=303)

@html_router.get("/todo/{id}")
async def view_todo_page(request: Request, id: int):
    todo = next((t for t in todo_list if t.id == id), None)
    if not todo:
        raise HTTPException(status_code=404, detail="Task not found")
    return templates.TemplateResponse(request=request, name="view.html", context={"todo": todo, "users": list(users_db.values())})