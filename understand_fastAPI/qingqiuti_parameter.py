from fastapi import FastAPI

from pydantic import BaseModel,Field


app = FastAPI()
@app.get("/")
async def root():
  return {"message":"hello world"}




#注册用户名和密码

#定义类型
class User(BaseModel):
  username: str = Field(default="张三",min_length=2,max_length=10,description="用户名长度要求2-10个字")
  password: str = Field(min_length=3,max_length=20)

#类型注解
@app.post("/register")
async def register(user : User):
  return user





#practice
class Add_Book(BaseModel):
  book_name: str = Field(...,min_length=2,max_length=20)
  author: str = Field(min_length=2,max_length=10)
  press: str = Field(default="黑马出版社")
  price: float = Field(...,gt=0)

@app.post("/book")
async def  book(add_book:Add_Book):
  return add_book




