from fastapi import Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from config.db_config import get_db
from crud import users

#整合 根据token查询用户，返回用户
async def get_current_user(
  authorization:str = Header(...,alias = "Authorization"),
  db: AsyncSession = Depends(get_db)
):
  token = authorization.replace("Bearer","")
  user = await users.get_user_by_token(db,token)
  if not user:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="无效的令牌或者是过期的令牌")
  return user