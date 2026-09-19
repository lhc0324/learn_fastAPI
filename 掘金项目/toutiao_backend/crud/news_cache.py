from fastapi.encoders import jsonable_encoder
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from cache.news_cache import get_cache_categories, get_cache_news_detail, get_cache_news_list, get_cache_news_related, set_cache_categories, set_cache_news_detail, set_cache_news_list, set_cache_news_related
from models.news import Category, News
from schemas.base import NewsItemBase

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
  #先尝试从缓存获取新闻列表
  page = skip // limit + 1
  cached_list = await get_cache_news_list(category_id,page,limit)
  if cached_list:
    return [News(**item) for item in cached_list]

  stmt = select(News).where(News.category_id == category_id).offset(skip).limit(limit)
  result =  await db.execute(stmt)
  news_list = result.scalars().all()

  if news_list:
    #先把orm格式数据转换成字典，才能写入缓存
    #ORM 转成 pydantic 再转成字典
    news_data = [NewsItemBase.model_validate(item).model_dump(mode= "json",by_alias=False) for item in news_list]
    await set_cache_news_list(category_id,page,limit,news_data)


  return news_list

#获取新闻数量
async def get_news_count(db : AsyncSession,category_id : int):
  stmt = select(func.count(News.id)).where(News.category_id == category_id)
  result = await db.execute(stmt)
  return result.scalar_one()      #只能有一个结果，多了报错

async def get_news_detail(db : AsyncSession,news_id : int):
  #先查缓存
  cached = await get_cache_news_detail(news_id)
  if cached:
    return News(**cached)
  
  stmt = select(News).where(News.id == news_id)
  result = await db.execute(stmt)
  news_detail = result.scalar_one_or_none()

  #写缓存
  if news_detail:
    data = jsonable_encoder(news_detail)
    await set_cache_news_detail(news_id,data)

  return news_detail

async def increase_news_views(db : AsyncSession,news_id : int):
  stmt = update(News).where(News.id == news_id).values(views=News.views + 1)
  result = await db.execute(stmt)
  await db.commit()

   #检查数据库是否真的命中了数据
  return result.rowcount > 0

async def get_related_news(db : AsyncSession,news_id,category_id : int, limit: int = 5):
  #读取缓存
  cached = await get_cache_news_related(news_id)
  if cached:
    return cached
  
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
  related = [{
    "id": news_detail.id,
      "title": news_detail.title,
      "content": news_detail.content,
      "image": news_detail.image,
      "author": news_detail.author,
      "publishTime": news_detail.publish_time,
      "categoryId" : news_detail.category_id,
      "views" : news_detail.views
  } for news_detail in related_news]

  if related:
    await set_cache_news_related(news_id,related,expire = 600)
  return related