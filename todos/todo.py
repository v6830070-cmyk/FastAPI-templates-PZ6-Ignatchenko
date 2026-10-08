from fastapi import APIRouter, Path, HTTPException, status, Request
from fastapi.templating import Jinja2Templates
from model import Todo, TodoItem, TodoItems

todo_router = APIRouter()
todo_list = []
templates = Jinja2Templates(directory="templates/")

@todo_router.post("/todo")
async def add_todo(request: Request):
    form_data = await request.form()
    item = form_data.get("item")
    if item:
        todo = Todo(id=len(todo_list) + 1, item=item)
        todo_list.append(todo)
    return templates.TemplateResponse(
        request=request,
        name="todo.html",
        context={"todos": todo_list}
    )

@todo_router.get("/todo")
async def retrieve_todos(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="todo.html",
        context={"todos": todo_list}
    )

@todo_router.get("/todo/{todo_id}")
async def get_single_todo(request: Request, todo_id: int = Path(..., title="The ID of the todo to retrieve.")):
    for todo in todo_list:
        if todo.id == todo_id:
            return templates.TemplateResponse(
                request=request,
                name="todo.html",
                context={"todo": todo}
            )
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Todo with supplied ID doesn't exist"
    )

@todo_router.put("/todo/{todo_id}")
async def update_todo(todo_data: TodoItem, todo_id: int = Path(..., title="The ID of the todo to be updated.")):
    for todo in todo_list:
        if todo.id == todo_id:
            todo.item = todo_data.item
            return {"message": "Todo updated successfully. (Выполнил: [Игнатченко Владислав])"}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Todo with supplied ID doesn't exist"
    )

@todo_router.delete("/todo/{todo_id}")
async def delete_single_todo(todo_id: int):
    for index in range(len(todo_list)):
        todo = todo_list[index]
        if todo.id == todo_id:
            todo_list.pop(index)
            return {"message": "Todo deleted successfully. (Выполнил: [Игнатченко Владислав])"}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Todo with supplied ID doesn't exist"
    )

@todo_router.delete("/todo")
async def delete_all_todo():
    todo_list.clear()
    return {"message": "Todos deleted successfully. (Выполнил: [Игнатченко Владислав])"}