from fastapi import FastAPI,Path
import json
from fastapi.responses import Response

#创建 fastapi 实例
app = FastAPI()

@app.get("/")
async def root():
  return {"message":"Hello World"}

@app.get("/hello/{name}")
async def say_hello(name:str):
  return {"message":f"Hello {name}"}
  
@app.get("/hello")
async def gew_hellp():
  return {"msg":"你好 Fast API"}

@app.get("/user/hello")
async def test():
  return {"msg":"我正在学习 Fast API"}

@app.get("/book/{id}")
async def get_book(id : int ):
  data = {"id" : id, "title" : f"这是第{id}本书"}
  return Response(
    content=json.dumps(data,indent=2,ensure_ascii=False),
    media_type="application/json"
  )

@app.get("/user/{id}")
async def get_user(id : int = Path(...,gt=0,lt=101,description="用户的id,取值范围1-100")):
  return {"id" : id, "name" : f"普通用户{id}"}



@app.get("/author/{name}")
async def get_name(name : str = Path(...,max_length=10,min_length=2)):
  return{"msg":f"这是{name}的信息"}



#自我练习
@app.get("/journal/id/{id}")
async def get_journal(id : int = Path(...,gt=0,lt=101,description="规定新闻分类的id范围")):
  return{"id": id ,"name" : f"新闻分类{id}" }

@app.get("/journal/name/{name}")
async def get_journal_name(name : str = Path(...,max_length=10,min_length=2,description="规定新闻分类名称的长度")):
  return{"msg" : f"这是{name}的新闻信息"}