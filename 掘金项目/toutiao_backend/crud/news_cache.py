from fastapi.encoders import jsonable_encoder
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from cache.news_cache import get_cache_categories, set_cache_categories
from models.news import Category, News

#获取分类
async def get_categories(db:AsyncSession,skip : int = 0,limit : int = 100):
  #先尝试从缓存中获取数据
  cache_categories = await get_cache_categories()
  if cache_categories:
    return cache_categories

  stmt = select(Category).offset(skip).limit(limit)
  result =  await db.execute(stmt)
  categories =  result.scalars().all()

  #写入缓存
  if categories:
    categories = jsonable_encoder(categories)
    await set_cache_categories(categories)

  #返回数据
  return categories



#获取所有新闻
async def get_news_list(
    db : AsyncSession,
    category_id : int,
    skip : int = 0,
    limit : int = 10
):
  stmt = select(News).where(News.category_id == category_id).offset(skip).limit(limit)
  result =  await db.execute(stmt)
  return result.scalars().all()

#获取新闻数量
async def get_news_count(db : AsyncSession,category_id : int):
  stmt = select(func.count(News.id)).where(News.category_id == category_id)
  result = await db.execute(stmt)
  return result.scalar_one()      #只能有一个结果，多了报错

async def get_news_detail(db : AsyncSession,news_id : int):
  stmt = select(News).where(News.id == news_id)
  result = await db.execute(stmt)
  return result.scalar_one_or_none()

async def increase_news_views(db : AsyncSession,news_id : int):
  stmt = update(News).where(News.id == news_id).values(views=News.views + 1)
  result = await db.execute(stmt)
  await db.commit()

   #检查数据库是否真的命中了数据
  return result.rowcount > 0

async def get_related_news(db : AsyncSession,news_id,category_id : int, limit: int = 5):
  stmt = select(News).where(
    News.category_id == category_id,
    News.id != news_id
  ).order_by(
    News.views.desc(),    #降序排序，使得浏览量高的在前面
    News.publish_time.desc()       #发布时间最新的排在前面
  ).limit(limit)    #order_by 来使得浏览量最高的来推送
  result = await db.execute(stmt)
  # return result.scalars().all()
  related_news =  result.scalars().all()
  return [{
    "id": news_detail.id,
      "title": news_detail.title,
      "content": news_detail.content,
      "image": news_detail.image,
      "author": news_detail.author,
      "publishTime": news_detail.publish_time,
      "categoryId" : news_detail.category_id,
      "views" : news_detail.views
  } for news_detail in related_news]