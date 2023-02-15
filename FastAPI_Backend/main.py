import uvicorn
from fastapi import FastAPI, Body, Depends, HTTPException
from app.model import PostSchema, UserSchema, UserLoginSchema
from app.auth.auth_bearer import JWTBearer
from app.auth.auth_handler import signJWT
from typing import List
from sqlalchemy.orm import Session
from .app import crud, model
from app.database import SessionLocal, engine

giturl = [
    {
        "id": 1,
        "title": "URL1 ",
        "text": "API key"
    },
    {
        "id": 2,
        "title": "URL 2",
        "text": "API key"
    },
    {
        "id": 3,
        "title": "URL 3",
        "text": "API Key"
    },
]

users = []

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def check_user(data: UserSchema):
    for user in users:
        if user.email == data.email and user.password == data.password:
            return True
    return False


# route handlers

# testing
@app.get("/", tags=["test"])
def greet():
    return {"hello": "world!."}


# Get Posts
@app.get("/giturl", tags=["giturl"])
def get_posts():
    return { "data": giturl }


@app.get("/giturl/{id}", tags=["giturl"])
def get_single_post(id: int):
    if id > len(giturl):
        return {
            "error": "No such Page with the supplied ID."
        }

    for post in giturl:
        if post["id"] == id:
            return {
                "data": post
            }


@app.post("/giturl", dependencies=[Depends(JWTBearer())], tags=["giturl"])
def add_post(post: PostSchema):
    post.id = len(giturl) + 1
    giturl.append(post.dict())
    return {
        "data": "post added."
    }

# without db
@app.post("/user/signup", tags=["user"])
def create_user(user: UserSchema = Body(...)):
    users.append(user) # replace with db call, making sure to hash the password first
    return signJWT(user.email)


@app.post("/user/login", tags=["user"])
def user_login(user: UserLoginSchema = Body(...)):
    if check_user(user):
        return signJWT(user.email)
    return {
        "error": "Wrong login details!"
    }

# with db
@app.post("/users/", response_model=model.User)
def create_user(user: model.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=List[model.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=model.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
