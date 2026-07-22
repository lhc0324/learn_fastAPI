from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
def success_response(message : str = "success",data = None):
  content = {
    "code" : 200,
    "message" : message,
    "data" : data
  }
  
  #把任何的fastapi pydantic ORM 对象都要正常相应，变成code、message、data的形式
  return JSONResponse(content = jsonable_encoder(content))