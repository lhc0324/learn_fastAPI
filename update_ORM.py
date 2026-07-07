from datetime import datetime

from fastapi import Depends, FastAPI,HTTPException
from sqlalchemy import DateTime, Float, String, func
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from pydantic import BaseModel
app = FastAPI()


@app.get("/")
async def root():
  return {"message" : "Hello World"}

#定义URL路径来连接数据库，之后创建引擎使用路径来连接，规定模型类，用模型类创建自己的库
#设置创建函数，启动fastAPI自动创建，之后设置窗口，加建立依赖项，使得每次窗口的操作一样，避免每次重复敲同一些代码

ASYNC_DATABATH_URL = "mysql+aiomysql://root:123456@127.0.0.1:3306/lhc"
async_engine = create_async_engine(
  ASYNC_DATABATH_URL,
  echo = True,  #看日志
  pool_size = 10,   #小项目可以不写
  max_overflow = 20   #小项目可以不写
)

class Base(DeclarativeBase):
  create_time : Mapped[datetime] = mapped_column(DateTime,insert_default=func.now(),default=func.now,comment="创建时间")
  update_time : Mapped[datetime] = mapped_column(DateTime,insert_default=func.now(),default=func.now,onupdate=func.now(),comment="更新时间")

class Book(Base):
  __tablename__ = "book"
  id : Mapped[int] = mapped_column(primary_key=True,comment="书籍id")
  bookname : Mapped[str] = mapped_column(String(255),comment="书名")
  author : Mapped[str] = mapped_column(String(255),comment="作者")
  price : Mapped[float] = mapped_column(Float,comment="价格")
  publisher : Mapped[str] = mapped_column(String(255),comment="出版社")

async def create_tables():
  async with async_engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)

@app.on_event("startup")
async def startup_event():
  await create_tables()

AsyncSessionLocal = async_sessionmaker(
  bind= async_engine,
  class_=AsyncSession,
  expire_on_commit= False
)

async def get_database():
  async with AsyncSessionLocal() as session:
    try:
      yield session
      await session.commit()
    except Exception:
      await session.roolback()
      raise
    finally:
      await session.close()

#修改图书信息，先查再改
#设计思路：路径参数id，作用查找；请求体参数：更新为新数据

class BookUpdate(BaseModel):
  bookname : str
  author : str
  price : float
  publisher  : str

@app.put("/book/update_book/{book_id}")
async def update_book(book_id : int,data : BookUpdate,db : AsyncSession = Depends(get_database)):
  db_book =  await db.get(Book,book_id)
  if db_book is None:
    raise HTTPException(
      status_code=404,
      detail="查无此书"
    )
  
  #修改，重新赋值
  db_book.bookname = data.bookname
  db_book.author = data.author
  db_book.publisher = data.publisher
  db_book.price = data.price

  await db.commit()
  return db_book