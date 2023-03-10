from pydantic import BaseModel, Field, EmailStr

class PostSchema(BaseModel):
    id: int = Field(default=None)
    title: str = Field(...)
    content: str = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "title": "Securing FastAPI applications with JWT.",
                "content": "In this tutorial, you'll learn how to secure your application by enabling authentication using JWT. We'll be using PyJWT to sign, encode and decode JWT tokens...."
            }
        }


class GenerateSchema(BaseModel):
    gh_token: str
    repo: str
    files: list[str]  
    
class UserSchema(BaseModel):
    username: str = Field(...) 
    password: str = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "username": "Joe Doe", 
                "password": "any"
            }
        }

class UserLoginSchema(BaseModel):
    username: str = Field(...)
    password: str = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "username": "joe@xyz.com",
                "password": "any"
            }
        }
