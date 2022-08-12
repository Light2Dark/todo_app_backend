from typing import List
from app.models import Person, ToDo
from firebase_admin import db
import json

DB: List[Person] = [
    Person(id=1, name="Adam", age=23),
    Person(id=2, name="Eve", age=10),
    Person(id=3, name="Ola", age=65)
]

db_todos: List[ToDo] = [
    
]
    
    
# TODO: ADD try-catch methods for all this db-server functions

def pushTodoInDBServer(userID: str, todo: ToDo):
    ref = db.reference(f"/{userID}")
    ref.push().set({
        "id": todo.id,
        "item": todo.item
    })
    
    
def getTodosInDBServer(userID: str):
    ref = db.reference(f"/{userID}") # reference to user ID block in DB
    return ref.get() # get the database to the contents of the file


def editTodoInDBServer(userID: str, todo_id: int, todo: ToDo):
    ref = db.reference(f"/{userID}")
    db_user_todos = ref.get() # getting all todos of this user
    
    for key, value in db_user_todos.items(): # iterating through each todo of the user
        if (value["id"] == todo_id): # found the matching to-do of the user that we want to edit
            ref.child(key).update({ # update the whole todo because update replaces the entire dict when I test
                "id": todo_id,
                "item": todo.item
            })
      
      
def deleteTodoInDBServer(userID: str, todo_id: int):
    ref = db.reference(f"/{userID}")      
    db_user_todos = ref.get()
    
    for key, value in db_user_todos.items():
        if (value["id"] == todo_id):
            ref.child(key).delete()

# def setTodosInDBServer(userID: str):
#     ref = db.reference("/1") # reference to root of the datbase as /, can also be child value
#     with open("app/test.json", "r") as f:
#         file_contents = json.load(f)
#     ref.set(file_contents) # set the database to the contents of the file