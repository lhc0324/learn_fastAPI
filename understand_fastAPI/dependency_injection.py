from fastapi import FastAPI,Query,Depends

app = FastAPI()

async def common_parameter(
  skip: int = Query(default = 0,le=10),
  limit: int = Query(default = 10,le = 60 )
):
  return{"skip":skip,"limit":limit}

#声明依赖项
@app.get("/news/news_list")
async def get_news_list(commons = Depends(common_parameter)):
  return  commons

@app.get("/users/users_list")
async def get_users_list(commons = Depends(common_parameter)):
  return commons