#新闻相关的缓存方法:新闻分类的读取和写入
from typing import Any, Dict, List, Optional

from config.cache_config import get_json_cache, set_cache


CATEGORIES_KEY = "news:categories"
NEWS_LIST_PREFIX = "news_list:"
NEWS_DETAIL_PREFIX = "news:detail:"
NEWS_RELATED_PREFIX = "news:related:"


#获取新闻分类缓存
async def get_cache_categories():
  return await get_json_cache(CATEGORIES_KEY)


#写入新闻分类缓存:缓存的数据，过期时间
#分类，配置7200；列表 600；详细 1800 ；验证码 120 数据越稳定，缓存越持久
#可以避免所有key同时过期，引起缓存雪崩

async def set_cache_categories(data:List[Dict[str,Any]],expire: int = 7200):
  return await set_cache(CATEGORIES_KEY,data,expire)




#写入缓存-新闻列表,key = news_list:分类id：页码：每页数量  + 列表数据 + 过期时间
async def set_cache_news_list(category_id: Optional[int],page: int, size: int,news_list: List[Dict[str,Any]],expire:int = 1800):
  #调用前面封装的redis设置方法，存新闻列表到缓存
  category_part = category_id if category_id is not None else "all"
  key = f"{NEWS_LIST_PREFIX}{category_part}:{page}:{size}"
  await set_cache(key,news_list,expire)




#读取缓存-新闻列表
async def get_cache_news_list(category_id: Optional[int],page: int, size: int):
  category_part = category_id if category_id is not None else "all"
  key = f"{NEWS_LIST_PREFIX}{category_part}:{page}:{size}"
  return await get_json_cache(key)

#读取缓存-获取新闻详情
async def get_cache_news_detail(news_id: int):
  return await get_json_cache(f"{NEWS_DETAIL_PREFIX}{news_id}")

#写入缓存 - 获取新闻详情
async def set_cache_news_detail(news_id: int,data: Dict[str,Any],expire: int = 1800):
  await set_cache(f"{NEWS_DETAIL_PREFIX}{news_id}",data,expire)

#读取缓存 - 新闻相关推荐
async def get_cache_news_related(news_id : int):
  return await get_json_cache(f"{NEWS_RELATED_PREFIX}{news_id}")

#写入缓存 - 新闻相关推荐
async def set_cache_news_related(news_id : int,data: List[Dict[str,Any]],expire: int = 600):
  await set_cache(f"{NEWS_RELATED_PREFIX}{news_id}",data,expire)