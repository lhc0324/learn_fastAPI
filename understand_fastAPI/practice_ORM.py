from datetime import datetime

from fastapi import FastAPI
from sqlalchemy import DateTime, Float, String, func
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column
app = FastAPI()

ASYNC_DATABASE_URL = "mysql+aiomysql://root:123456@127.0.0.1:3306/lhc"

async_engine = create_async_engine(
  ASYNC_DATABASE_URL,
  echo=True,
  pool_size = 10,
  max_overflow = 20
)
#
class Base(DeclarativeBase):
  create_time : Mapped[datetime] = mapped_column(DateTime,insert_default=func.now(),default=func.now,comment="创建时间")
  update_time : Mapped[datetime] = mapped_column(DateTime,insert_default=func.now(),default=func.now,onupdate=func.now,comment="更新时间")


class Book(Base):
  __tablename__ = "book"
  id:Mapped[int] = mapped_column(primary_key=True,comment="书籍id")
  bookname:Mapped[str] = mapped_column(String(255),comment= "书名")
  author:Mapped[str] = mapped_column(String(255),comment="作者")
  price:Mapped[float] = mapped_column(Float,comment="价格")
  publisher:Mapped[str] = mapped_column(String(255),comment="出版社")

async def create_tables():
  async with async_engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)

@app.on_event("startup")
async def startup_event():
  return create_tables



@app.get("/")
async def root():
  return{"message":"hello world"}