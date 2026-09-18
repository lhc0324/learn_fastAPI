import json
from typing import Any

import redis.asyncio as redis

REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0

#创建 Redis 连接对象
redis_client = redis.Redis(
  host = REDIS_HOST,    #主机地址
  port = REDIS_PORT,     #端口号
  db=REDIS_DB,          #数据库编号
  decode_responses=True     #是否将字节数据解码为字符串
)

#设置和读取（字符串 和 列表或字典）"[{}]"
#读取：字符串
async def get_cache(key: str):
  try:
    return await redis_client.get(key)
  except Exception as e:
    print(f"获取缓存失败{e}")
    return None


#读取：列表或字典
async def get_json_cache(key: str):
  try:
    data = await redis_client.get(key)
    if data:
      return json.loads(data)          #序列化，来去掉"[{}]"中的引号，使得拿到的就是一个列表或者字典
    return None
  except Exception as e:
    print(f"获取json形式的缓存失败{e}")
    return None


#设置缓存    setex(key,expire,value)
async def set_cache(key:str,value:Any,expire:int = 3600 ):             #expire : 过期时间
  try:
    if isinstance(value, (dict,list)):
      #转字符串再存
      value = json.dumps(value,ensure_ascii=False)    #中文正常保存
    await redis_client.setex(key,expire,value)
    return True
  except Exception as e:
    print(f"设置缓存失败{e}")
    return False
