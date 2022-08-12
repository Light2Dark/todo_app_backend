from typing import Union
from fastapi import FastAPI, Response, status, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from app.models import ToDo
import firebase_admin
import pyrebase
import json
from firebase_admin import credentials, auth, db
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from dotenv import load_dotenv
import os

from app.database import db_todos
from app.database import getTodosInDBServer, pushTodoInDBServer, editTodoInDBServer, deleteTodoInDBServer

app = FastAPI()

origins = [
    # "http://localhost:3000",
    # "localhost:3000",
    # "http://localhost"
    "https://smolwaffle-todo.netlify.app",
    "smolwaffle-todo.netlify.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/", tags=["root"]) 
async def read_root() -> dict:
    return {"message": "Welcome to a new React-Python app, this is the backend"}

# if no user, store todo's in local db_todos
# if got user, store in firebase db

# GETTING TO-DOS
@app.get("/todo", tags=["todos"])
async def get_todos(req: Request) -> dict:
    user_id = req.headers.get("user_id")
    if user_id == "false":
        return db_todos
    
    # if there is user, return todo's from db
    return getTodosInDBServer(user_id) 

# CREATING A TO-DO
@app.post("/todo", tags=["todos"], status_code=status.HTTP_201_CREATED)
async def add_todo(item: ToDo, request: Request, response: Response):
    try:
        todo = ToDo(id=item.id, item=item.item)
    except Exception:
        return {
            "error": "ToDo added does not meet the format of a ToDo"
        }
    
    # Frontend code will handle duplicates
    # try:
    #     for db_todo in db_todos:
    #         if db_todo.item == todo.item or todo.id == db_todo.id:
    #             raise Exception
    # except Exception:
    #     response.status_code=status.HTTP_400_BAD_REQUEST
    #     return {
    #         "message": "ToDo already exists"
    #     }
        
    user_id = request.headers.get("user_id")
    if user_id == "false": # a false will be sent in the http req if user is not logged in, cant use False, because read as string
        db_todos.append(todo)
    else:
        return pushTodoInDBServer(user_id, todo)
    
    return {
        "message": "ToDo added successfully",
        "todo_id": todo.id
    } 
    
# UPDATING A TO-DO, will receive the id of the to-do
@app.put("/todo/{id}", tags=["todos"])
async def update_todo(id: int, body: ToDo, request: Request) -> ToDo:
    user_id = request.headers.get("user_id")
    if user_id == "false": # not logged in
        for todo in db_todos:
            if todo.id == id:                      # found the to-do to edit, the id is the arg passed in the url endpoint
                db_todos[id-1].item = body.item    # due to db_todos being an array, we start from 0
                return {"message": "ToDo updated successfully"}
    else:
        return editTodoInDBServer(userID=user_id, todo_id=id, todo=body)
    
    return {
        "message": f"ToDo with {id} id not found"
    }
   
# DELETING A TO-DO
@app.delete("/todo/{id}", tags=["todos"])
async def delete_todo(id:int, request: Request) -> dict:
    user_id = request.headers.get("user_id")
    if user_id == "false": # not logged in
        for todo in db_todos:
            if todo.id == id:
                db_todos.remove(todo)               # delete the todo which matches the id, not based on id because issues with array index
                return {"message": "ToDo deleted successfully"}
    else:
        return deleteTodoInDBServer(user_id, todo_id=id)
               
    return {
        "message": f"ToDo with {id} id not found"
    }
    
    
# FIREBASE
cred = credentials.Certificate("to-do_service_account_keys.json") # cr8 credentials
load_dotenv()
firebase = firebase_admin.initialize_app(cred, {
    "databaseURL": os.environ["FIREBASE_DB_URL"]
}) # initialize a firebase_admin app
pb = pyrebase.initialize_app(json.load(open("firebase_config.json"))) # initialize a Firebase/Pyrebase app based on config downloaded

# signup endpoint
@app.post("/signup", include_in_schema=False) # not including in schema because it's should not be a public endpoint + security (won't be in docs)
async def signup(request: Request):
    req = await request.json()
    email = req["email"]
    password = req["password"]
    
    # basic validation
    if email is None or password is None:
        return HTTPException(status_code=400, detail="Missing email or password")
    
    try:
        user = auth.create_user(
            email=email,
            password=password
        )
        # TODO: store user in Database!
        return JSONResponse(status_code=201, content={"message": "User created successfully", "user_id": user.uid})
    except:
        return HTTPException(status_code=400, detail="User already exists or user is invalid")

# login endpoint
@app.post("/login", include_in_schema=False)
async def login(request: Request):
    req = await request.json()
    email = req["email"]
    password = req["password"]
    
    # use pyrebase for login
    try:
        user = pb.auth().sign_in_with_email_and_password(email, password)
        jwt = user["idToken"]
        return JSONResponse(status_code=200, content={"message": "User logged in successfully", "token": jwt, "status_code": 200, "user_id": user["localId"]})
    except:
        return HTTPException(status_code=400, detail="Invalid email, password or user does not exist")
    
# ping dummy endpoint
@app.post("/ping", include_in_schema=False)
async def validate(request: Request):
    header = request.headers
    jwt = header["authorization"] # send token through header to avoid await for loading data b4 validation
    print(f"jwt: {jwt}")
    user = auth.verify_id_token(jwt)    
    return user["uid"] # return user id

    # we did not add any error catching so the server will throw an error if the user is not found

# REALTIME DATABASE    
# ref = db.reference("/1") # reference to root of the datbase as /, can also be child value
# with open("app/test.json", "r") as f:
#     file_contents = json.load(f)
# ref.set(file_contents) # set the database to the contents of the file
    
# TESTING CURL COMMAND FROM A CLI / TERMINAL
# curl -X POST http://localhost:8000/todo -d '{"id": "3", "item": "Buy some testdriven."}' -H 'Content-Type: application/json'