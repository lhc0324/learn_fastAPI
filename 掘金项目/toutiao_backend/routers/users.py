from fastapi import APIRouter, Depends, HTTPException,status
from config.db_config import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.users import UserAuthResponse, UserInfoResponse, UserRequest
from crud import users
from utils import security
from utils.response import success_response

router = APIRouter(prefix="/api/user",tags=["users"])

@router.post("/register")
async def register(user_data:UserRequest,db : AsyncSession = Depends(get_db),):
  #注册逻辑->验证用户是否存在->创建用户->生成token->相应结果
  existing_user = await users.get_user_by_username(db,user_data.username)
  if existing_user:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="用户已存在")
  user = await users.create_user(db,user_data)
  token = await users.create_token(db,user.id)
  # return {
  #   "code":200,
  #   "message":"注册成功",
  #   "data":{
  #     "token":token,
  #     "userInfo":{
  #       "id":user.id,
  #       "username":user.username,
  #       "bio":user.bio,
  #       "avatar":user.avatar
  #     }
  #   }
  # }
  response_data = UserAuthResponse(token = token,user_info = UserInfoResponse.model_validate(user))
  return success_response(message="注册成功",data=response_data)
@router.post("/login")
async def login(user_data:UserRequest,db: AsyncSession = Depends(get_db)):
  #登录逻辑->验证用户是否存在->验证密码->生成/更新token->返回结果
  user = await users.get_user_by_username(db,user_data.username)
  if not user:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="用户不存在")
  if not security.verify_password(user_data.password,user.password):
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="密码错误")
  token = await users.create_token(db,user.id)
  return {
    "code":200,
    "message":"登录成功",
    "data":{
      "token":token,
      "userInfo":{
        "id":user.id,
        "username":user.username,
        "bio":user.bio,
        "avatar":user.avatar
      }
    }
  }


