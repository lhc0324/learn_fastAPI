from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.users import User
from schemas.users import UserRequest
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