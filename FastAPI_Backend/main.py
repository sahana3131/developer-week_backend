import uvicorn
from fastapi import FastAPI, Body, Depends, HTTPException
from app.model import PostSchema, UserSchema, UserLoginSchema
from app.auth.auth_bearer import JWTBearer
from app.auth.auth_handler import signJWT
import httpx
from starlette.responses import RedirectResponse

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
github_client_id = 'b0a94e000593ed9730a0'
github_client_secret = '6a996f48c85b58803ccbd4674fdd87bc468b195f'


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

@app.get('/github-login')
async def github_login():
    return RedirectResponse(f'https://github.com/login/oauth/authorize?client_id={github_client_id}', status_code=302)

@app.get('/github-code')
async def github_code(code: str):
    params = {
            'client_id' : github_client_id,
            'client_secret' : github_client_secret,
            'code' : code
        }
    headers = {'Accept': 'application/json'}
    async with httpx.AsyncClient() as client:
        response = await client.post(url='https://github.com/login/oauth/access_token',params=params, headers=headers)
    response_json = response.json()
    access_token=response_json['access_token']
    async with httpx.AsyncClient() as client:
        headers.update({'Authorization': f'Bearer {access_token}'})
        response = await client.get('https://api.github.com/user', headers=headers)
    return response.json() 

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



