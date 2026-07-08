from fastapi import FastAPI,HTTPException

app = FastAPI()

@app.get("/")
async def root():
  return {"meassage":"Hello World"}

#需求：按id 查询新闻，1-6正常，其他异常

@app.get("/news/{id}")
async def news(id : int):
  id_list = {1,2,3,4,5,6}
  if id not in id_list:
    raise HTTPException(status_code=404,detail="您查找的新闻不存在")

  return {"id": id}