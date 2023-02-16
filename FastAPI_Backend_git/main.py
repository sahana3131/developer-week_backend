
import uvicorn
from fastapi import FastAPI ,Body, Depends, Request, Response, HTTPException 
from app.model import PostSchema, UserSchema, UserLoginSchema, GenerateSchema
from app.auth.auth_bearer import JWTBearer
from app.auth.auth_handler import get_password_hash , signJWT , verify_password
from app.helpers.helpers import *
import httpx
from starlette.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware 
import mysql.connector
import pymysql
import requests
from github import Github
from pydantic import BaseSettings
import openai


class Settings(BaseSettings):
    OPENAI_API_KEY: str = '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'
    
    class Config:
        env_file = '.env'

settings = Settings()

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
    '*'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



github_client_id = '***'
github_client_secret = '***'
openai.api_key = '***'


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

''' ====================== MYSQL Cloud Connection ======================'''
conn = pymysql.connect(
    host='*****',
    user='***',
    password='****',
    port = '***',
    database='****'
)

def main():
    try:
        cursor = conn.cursor()
        # cursor.execute("DROP TABLE users")
        cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTO_INCREMENT, username TEXT , password TEXT)")  #MYSQL
        conn.commit()

        print("Connection to MySQL DB successful")
    except mysql.connector.Error as error: 
        print(f"Failed to connect to MySQL: {error}")

def get_db():
    try:
        return conn
    except mysql.connector.Error as error:
        raise HTTPException(status_code=500, detail="Unable to connect to the database")


# route handlers

''' ====================== Test Urls ======================'''
# testing
@app.get("/", tags=["test"])
def greet():
    return {"hello": "world!."}

''' ====================== CRUD Urls ======================'''

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


''' ====================== Github OAUTH ======================'''

@app.get('/gh-authorize')
async def github_login():
    return RedirectResponse(f'https://github.com/login/oauth/authorize?client_id={github_client_id}&scope=repo', status_code=302)


#TODO: "/callback" url should be added in amirta github oauth app settings

@app.get('/callback')
async def callback(request: Request):
    code = request.query_params.get("code")

    params = {
            'client_id' : github_client_id,
            'client_secret' : github_client_secret,
            'code' : code
        }
    
    headers = {'Accept': 'application/json'}
    async with httpx.AsyncClient() as client:
        response = await client.post(url='https://github.com/login/oauth/access_token',params=params, headers=headers)
    
    response_json = response.json()
    print(response_json)
    access_token=response_json['access_token']  
    print(access_token)

    async with httpx.AsyncClient() as client:
        headers.update({'Authorization': f'Bearer {access_token}'})
        response = await client.get('https://api.github.com/user', headers=headers)
    print(response.json())
    return {
        "gh_token" : access_token
    }


''' ====================== User AUTH ======================'''

@app.post("/register", tags=["user"])
def create_user(user: UserSchema = Body(...) , conn: mysql.connector.MySQLConnection = Depends(get_db)):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    if any(x[1] == user.username for x in users):
        raise HTTPException(status_code=400, detail='Username already exists') 
    
    print("160",user.password , user.username) 
    hashed_password = get_password_hash(user.password)  

    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (user.username, hashed_password))  
    conn.commit() 
    
    return signJWT(user.username)


@app.post("/login", tags=["user"])
def user_login(auth_details: UserLoginSchema = Body(...),conn: mysql.connector.MySQLConnection = Depends(get_db)):
    
    cursor = conn.cursor()
    user = None

    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()  
    print("173",users)
    for x in users:
        print(x[1] , x[2], auth_details.username)
        if x[1] == auth_details.username:
            user = x 
            break
    if (user is None) or (not verify_password(auth_details.password, user[2])):
        raise HTTPException(status_code=401, detail='Invalid username and/or password')
    return signJWT(user[1])

''' ====================== Github API urls ======================'''
@app.get("/file-content",
        status_code=200 , 
        dependencies=[Depends(JWTBearer())],
        tags=["github"]
        )
async def content(gh_token: str, repo: str , file : str):
    gh = Github(gh_token)
    return get_file_content(gh, repo , file)

@app.get("/repo", status_code=200 , 
        dependencies=[Depends(JWTBearer())],
        tags=["github"]
         )
async def repos(gh_token: str): 
    gh = Github(gh_token)
    return get_repos(gh)

@app.get("/content" , status_code=200 ,
        dependencies=[Depends(JWTBearer())],
        tags=["github"]
         )
async def content(gh_token: str, repo: str):
    gh = Github(gh_token)
    return get_repo_content(gh, repo)

@app.post("/generate")
async def generate(
    schema: GenerateSchema = Body(...),
    dependencies=[Depends(JWTBearer())],
    tags=["github"]
    ):
    responses = []
    gh = Github(schema.gh_token)
    for f in schema.files:
        responses.append(openai.Completion.create(
            model="text-davinci-002",
            prompt=generate_prompt(gh, schema.repo, f),
            max_tokens=1024,
            n=1,
            stop=None,
            temperature=0.5,
        ).choices[0].text.strip())

        responses.append(openai.Completion.create(
            engine="davinci",
            prompt=generate_time_complexity(gh, schema.repo, f),
            max_tokens=50,
            n=1,
            stop=None,
            temperature=0.5, 
        ).choices[0].text.strip()) 

        responses.append(openai.Completion.create(
            engine = "davinci",
            prompt=generate_debug(gh, schema.repo, f),
            temperature=0.5, 
            n=1,
            stop= None,
        ).choices[0].text.strip()) 
    return responses

@app.post("/edit",status_code=200 , 
        )
async def edit(gh_token: str, repo: str, file: str, content: str):
    gh = Github(gh_token)
    repo = gh.get_repo(f"{gh.get_user().login}/{repo}") 

    repo.update_file(file, "Update file", content, repo.get_contents(file).sha)
    return {"status": "success"}


if __name__ == "__main__":
    main()
    uvicorn.run(app, host='0.0.0.0', port=8000)
