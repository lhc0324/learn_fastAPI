from fastapi import FastAPI,Query
app = FastAPI()
@app.get("/")
async def root():
  return {"message" : "hello world"}


@app.get("/news/news_list")
async def get_news_list(
  skip : int = Query(0,description="跳过的记录数",lt=100),
  limit : int = Query(10,description="返回的记录数")
):
  return{"skip" : skip,"limit" : limit}

#练习
@app.get("/book/book_list")
async def book_list(
  classify : str = Query(0,max_length=255,min_length=5),
  price : int = Query(50,lt = 101,gt = 49)
):
  return{"book_classify" : classify,"book_price" : price}