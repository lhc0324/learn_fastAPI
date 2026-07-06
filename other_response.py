from fastapi import FastAPI
from fastapi.responses import HTMLResponse,FileResponse

app = FastAPI()

@app.get("/")
async def root():
  return {"meassage":"Hello World"}

#接口相应 HTML 代码
@app.get("/html",response_class=HTMLResponse)
async def get_heml():
  return "<h1>这是一级标题</h1>"

#接口：返回一张图片内容
@app.get("/file")
async def file():
  path = "./files/1.jpeg"
  return FileResponse(path)