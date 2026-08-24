from datetime import datetime, timedelta
import uuid

from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from models.users import User, UserToken
from schemas.users import UserRequest, UserUpdateRequest
from utils import security

#根据用户名来查询数据库
async def get_user_by_username(db : AsyncSession,username: str):
  stmt = select(User).where(User.username == username)
  result = await db.execute(stmt)
  return result.scalar_one_or_none()

#创建用户
async def create_user(db : AsyncSession,user_data : UserRequest):
  #先加密处理，之后add
  hashed_password = security.get_hash_password(user_data.password)
  user = User(username = user_data.username,password = hashed_password)
  db.add(user)
  await db.commit()
  await db.refresh(user)
  return user

#生成token
async def create_token(db : AsyncSession,user_id : int):
  #生成token，设置过期时间，查询是否有token，有：更新，没有：添加
  token = str(uuid.uuid4())
  expires_at = datetime.now() + timedelta(days=7)     #设置过期时间
  query = select(UserToken).where(UserToken.user_id == user_id)
  result = await db.execute(query)
  user_token =  result.scalar_one_or_none()
  if user_token:
    user_token.token = token
    user_token.expires_at = expires_at
  else:
    user_token = UserToken(user_id = user_id,token = token,expires_at = expires_at)
    db.add(user_token)
    await db.commit()
  
  return token


async def authenticate_user(db : AsyncSession,username : str,password : str):
  user = await get_user_by_username(db,username)
  if not user:
    return None
  if not security.verify_password(password,user.password):
    return None
  
  return user

#根据token来查询用户:验证token,查询用户
async def get_user_by_token(db: AsyncSession,token:str):
  query = select(UserToken).where(UserToken.token == token)
  result = await db.execute(query)
  db_token = result.scalar_one_or_none()

  if not db_token or db_token.expires_at < datetime.now():
    return None
  
  query = select(User).where(User.id == db_token.user_id)
  result = await db.execute(query)
  return result.scalar_one_or_none()

#更新用户信息
async def update_user(db: AsyncSession,username: str,user_data: UserUpdateRequest):
  ##model_dump用来将user_data的pydantic类型转换为字典类型，然后**将字典解包来去掉大括号
  query = update(User).where(User.username == username).values(**user_data.model_dump(   
    exclude_unset = True,    ##设置没有设置值的不更新，保留初始值
    exclude_none= True
  ))
  result = await db.execute(query)
  await db.commit()      #commit提交之后查看命中率，如果为零则raise报异常

  if result.rowcount == 0:
    raise HTTPException(status_code=404,detail="用户不存在")

  updated_user = await get_user_by_username(db,username)
  return updated_user


#修改密码：验证就密码，新密码加密，修改密码
async def change_password(db:AsyncSession,user: User,old_password: str,new_password: str):
  if not security.verify_password(old_password,user.password):
    return False

  hashed_new_pwd = security.get_hash_password(new_password)
  user.password = hashed_new_pwd
  #更新: 由sqlalchemy真正接管这个User对象，确保可以commit
  #规避由于session过期或者关闭导致的不能提交的问题
  db.add(user)
  await db.commit()
  await db.refresh(user)
  return True