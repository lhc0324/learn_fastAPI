from datetime import datetime

from fastapi import Depends, FastAPI
from sqlalchemy import DateTime, Float, String, func, select
from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker,AsyncSession
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column
app = FastAPI()

#创建异步引擎
ASYNC_DATABATH_URL = "mysql+aiomysql://root:123456@127.0.0.1:3306/lhc"
async_engine = create_async_engine(
  ASYNC_DATABATH_URL,
  echo = True,   #可选，输出sql日志
  pool_size = 10,   #设置连接池活跃的连接数
  max_overflow = 20   #允许额外的连接数
  )

#定义模型类
class Base(DeclarativeBase):
  create_time:Mapped[datetime] = mapped_column(DateTime,server_default=func.now(),comment="创建时间")
  update_time:Mapped[datetime] = mapped_column(DateTime,server_default=func.now(),onupdate=func.now(),comment="修改时间")

class Book(Base):
  __tablename__ = "book"

  id:Mapped[int] = mapped_column(primary_key=True,comment="书籍id")
  bookname:Mapped[str] = mapped_column(String(255),comment="书名")
  author:Mapped[str] = mapped_column(String(255),comment="作者")
  price:Mapped[float] = mapped_column(Float,comment="价格")
  publisher:Mapped[str] = mapped_column(String(255),comment="出版社")

#practice
class User(Base):
  __tablename__ = "User"

  id:Mapped[int] = mapped_column(primary_key=True,comment="用户id")
  user_name:Mapped[str] = mapped_column(String(255),comment="用户名")
  password:Mapped[str] = mapped_column(String(20),comment="用户密码")

#建表：定义函数建表
async def create_tables():
  async with async_engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)   #Base  模型类的元数据创建

@app.on_event("startup")
async def startup_event():
  await create_tables()

@app.get("/")
async def root():
  return {"meassage":"Hello World"}


##异步数据库工厂
AsyncSessionLocal = async_sessionmaker(
  bind = async_engine,   ##绑定数据库引擎
  class_= AsyncSession,     ##指定会话类
  expire_on_commit=False   #提交后会话不过期，不会重新查询数据库
)

#依赖项
async def get_database():
  async with AsyncSessionLocal()  as session:
    try:
      yield session    #返回数据库会话给路由处理函数
      await session.commit()   #提交事务
    except Exception:
      await session.rollback  #有异常，回滚
      raise
    finally:
      await session.close()   #关闭会话

#查询操作，谁用ORM查询以及主键查询
@app.get("/book/books")
async def get_book_list(db: AsyncSession = Depends(get_database)):
  
  # result = await db.execute(select(Book))     ##查询，返回一个ORM对象
  # book = result.scalars().all()         ##获取所有
  # book = result.scalars().first()       ##获取单条数据
  book = await db.get(Book,ident=2)       ##获取单条数据，根据主键来获取
  return book

#查询书籍id（路径参数）
@app.get("/book/get_book/{book_id}")
async def get_book(book_id : int,db : AsyncSession = Depends(get_database)):
  result  = await db.execute(select(Book).where(Book.id == book_id))
  book =  result.scalar_one_or_none()
  return book

#查询价格大于等于20的
@app.get("/book/search_book")
async def get_search_book(db: AsyncSession =  Depends(get_database)):
  result = await db.execute(select(Book).where(Book.price>=20))
  price = result.scalars().all()
  return price

#多条件查询,书籍id列表，如果数据库里面的id在书籍id列表中 就返回
@app.get("/book/search_book_author")
async def get_book_author(db : AsyncSession = Depends(get_database)):
  # result_search =await db.execute(select(Book).where(~(Book.author.like("曹%")) & (Book.price >= 15)))
  id_list = [1,3,5,7]
  result_search = await db.execute(select(Book).where(Book.id.in_(id_list)))
  books = result_search.scalars().all()
  return books

#查询作者是某华的
@app.get("/book/search_BookIsHua")
async def search_BookIsHua(db : AsyncSession = Depends(get_database)):
  results =  await db.execute(select(Book).where(Book.author.like("_华")))
  search_book = results.scalars().all()
  return search_book

#聚合查询
@app.get("/book/count")
async def get_count(db : AsyncSession = Depends(get_database)):
  # result =await db.execute(select(func.count(Book.id)))
  # result =await db.execute(select(func.max(Book.price)))
  result =await db.execute(select(func.sum(Book.price)))
  # result =await db.execute(select(func.avg(Book.price)))
  num = result.scalar()
  return num






#####    实现流程----设计一个URL接口，然后规定一个打开fastAPI之后立即运行创建表的函数，
#####    即create_table(),在create_table中，连接sql库然后创建


#####    期间需要你去规定你要创建的表的模版，规定里面有什么内容，比如创建时间以及更新时间，然后后面的表的创建都是根据你这个模板来的，