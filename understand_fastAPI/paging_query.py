from datetime import datetime

from fastapi import Depends, FastAPI
from sqlalchemy import DateTime, Float, String, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
app = FastAPI()

@app.get("/")
async def root():
  return {"message" : "Hello World"}

#创建异步引擎，设置sql怎么连接
ASYNC_DATABATH_URL = "mysql+aiomysql://root:123456@127.0.0.1:3306/lhc"    #设置URL，数据库路径
async_engine = create_async_engine(
  ASYNC_DATABATH_URL,
  echo = True,     #输出sql日志
  pool_size = 10,    #连接池的活跃的连接数量
  max_overflow = 20    #允许额外的连接数 20
)

#定义模型类
class Base(DeclarativeBase):
  create_time:Mapped[datetime] = mapped_column(DateTime,server_default = func.now(),comment =  "创建时间")
  update_time:Mapped[datetime] = mapped_column(DateTime,server_default = func.now(),onupdate = func.now(),comment="更新时间")

class Book(Base):
  __tablename__ = "book"
  id:Mapped[int] = mapped_column(primary_key=True,comment="图书id")
  bookname:Mapped[str] = mapped_column(String(255),comment="书名")
  author : Mapped[str] = mapped_column(String(255),comment="作者")
  price : Mapped[float] = mapped_column(Float,comment="价格")
  publisher : Mapped[str] = mapped_column(String(255),comment="出版社")

async def create_tables():
  async with async_engine.begin() as conn:      #连接mysql，建立通道
    await conn.run_sync(Base.metadata.create_all)    #将模型转换成sql发给mysql建表

#建立触发函数，只要打开fastAPI就执行建表函数
@app.on_event("startup")
async def startup_event():
  await create_tables()

#异步数据化工厂，自动创建会话
AsyncSessionLocal = async_sessionmaker(
  bind = async_engine,    #绑定异步引擎
  class_ = AsyncSession,     #规定会话类
  expire_on_commit= False      #提交后会话不过期，不会重新查询数据库      
)

#定义依赖项
async def get_database():
  async with AsyncSessionLocal() as session:
    try:
      yield session
      await session.commit()
    except:
      await session.rollback()
      raise
    finally:
      await session.close()

@app.get("/book/get_book_list")
async def get_book_list(
  page : int = 1,
  page_size : int = 2,
  db : AsyncSession = Depends(get_database)
):
  skip = (page - 1) * page_size
  stmt = select(Book).offset(skip).limit(page_size)
  result =await db.execute(stmt)
  books = result.scalars().all()
  return books

