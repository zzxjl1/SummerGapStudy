import jieba
from qqwry import QQwry
import asyncio
import base64
from datetime import datetime
import os
from typing import Optional
from requests import request
import uvicorn
import json

import numpy as np
from fastapi import Cookie, Depends, FastAPI, Form, Request, WebSocket, WebSocketDisconnect, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.responses import StreamingResponse

from ecloud_apis.stt import ECloudSTT
from ecloud_apis.tts import ECloudTTS
from ecloud_apis.ocr import ECloudOCR
from ecloud_apis.obj import ECloudOBJ
from ecloud_apis.nlp import ECloudNLP_Keywords
from toolutils import to_json_str
from oauth import QQLogin

import curd
import models
import schemas
from database import DBSession, engine
from sqlalchemy.orm import Session

from trending import Trending
trending = Trending()

ip2loc = QQwry()
#from qqwry import updateQQwry
#ret = updateQQwry('qqwry.dat')
ip2loc.load_file('qqwry.dat', loadindex=True)

#import crawer
#import debug


def get_db():
    db = DBSession()
    try:
        yield db
    finally:
        db.close()


models.Base.metadata.create_all(bind=engine)
app = FastAPI()
app.add_middleware(GZipMiddleware)
origins = [
    "http://localhost:5000",
    "http://localhost:4000",
    "http://aisee.idealbroker.cn",
    "https://aisee.idealbroker.cn"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


####DEBUG ONLY####
#import debug
####DEBUG ONLY####

@app.get("/ping")
async def ping():
    return "pong"


@app.get("/news/related")
async def related_news(payload: str, offset: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """获取相关新闻"""
    try:
        keywords = ECloudNLP_Keywords(payload)
        print(keywords)
    except Exception as e:
        return {"success": False, "description": str(e)}
    if not keywords:
        keywords = [payload]
    result = curd.search_news(db, keywords, offset, limit)
    t = []
    for i in result:
        t.append({
            "id": i.id,
            "title": i.title,
            "bk_img": i.background_img,
        })
    return {"success": True, "data": t}


@app.get("/news/trending")
async def get_trending_news(limit: Optional[int] = 5, db: Session = Depends(get_db)):
    """获取热门新闻"""
    most_searched = trending.get(limit)
    most_viewed = curd.get_news_most_viewed(db, limit)
    return {
        "search": most_searched,
        "view": most_viewed
    }


@app.get("/news/search")
async def search_news(payload: str, offset: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """搜索新闻"""
    trending.add(payload)
    try:
        keywords = ECloudNLP_Keywords(payload)
        print(keywords)
    except Exception as e:
        return {"success": False, "description": str(e)}
    if not keywords:
        keywords = [payload]
    result = curd.search_news(db, keywords, offset, limit)
    t = []
    for i in result:
        t.append({
            "id": i.id,
            "title": i.title,
            "bk_img": i.background_img,
        })
    return {"success": True, "data": t}


@app.post("/news/{type}")
async def toggle_news_favorite(type: str, payload: bool = Form(), news_id: int = Form(),
                               token: str = Form(), db: Session = Depends(get_db)):
    """切换新闻收藏、赞"""
    user = curd.get_user_by_token(db, token)
    if user is None:
        return {"success": False, "description": "用户未登录"}
    if type == "favorite": # 收藏
        curd.user_toggle_favorite_news(db, user.id, news_id, payload)
        return {"success": True, "description": "操作成功", "result": payload}
    elif type == "like": # 赞
        curd.news_toggle_user_like(db, user.id, news_id,  payload)
        return {"success": True, "description": "操作成功", "result": payload}


@app.get("/news/detail")
def get_news_detail(id: int, token: Optional[str], db: Session = Depends(get_db)):
    """获取新闻详情"""
    news = curd.get_news(db, id)
    curd.add_news_view_counter(db, id)
    if news is None:
        return {"success": False, "description": "news id not found"}
    self = None
    if token:
        self = curd.get_user_by_token(db, token)
    t = {
        "id": news.id,
        "title": news.title,
        "category": news.category,
        "background_img": news.background_img,
        "summary": news.summary,
        "tags": news.tags.split(",") if news.tags else [],
        "source": news.source,
        "created_at": news.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        "click_count": news.click_count,
        "like_count": news.like_count,
        "comment_count": news.comment_count,
        "content": json.loads(news.content),
        "liked": self and self.id in json.loads(news.users_like),
        "favorited": self and news.id in json.loads(self.favorites),
    }
    curd.update_news_last_view_time(db, news.id)
    return {"success": True, "result": t}


@app.get("/news/{type}")
async def fetch_news_list(type: str, offset: Optional[datetime] = None, limit: int = 5, db: Session = Depends(get_db)):
    """获取新闻列表"""
    print(type)
    news_list = []
    if offset is None:
        offset = datetime.now()
    if type == "推荐":
        result = curd.get_news_recommand(db, offset, limit)
    elif type == "最新":
        result = curd.get_latest_news(db, offset, limit)
    else:
        result = curd.get_news_by_category(db, type, offset, limit)
    for news in result:
        news_list.append({
            "id": news.id,
            "title": news.title,
            "category": news.category,
            "source": news.source,
            "summary": news.summary,
            "background_img": news.background_img,
            "tags": news.tags.split(",") if news.tags else [],
            "created_at": news.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            "click_count": news.click_count,
            "like_count": news.like_count,
            "comment_count": news.comment_count,
        })
    return news_list


@app.post("/comment/operation")
async def comment_operation(comment_id: int = Form(), operation: str = Form(),
                            token: Optional[str] = Form(None), db: Session = Depends(get_db)):
    """评论操作（赞、踩）"""
    comment = curd.get_comment(db, comment_id)
    if comment is None:  # 评论为空
        return {"success": False, "description": "comment not found"}
    user = curd.get_user_by_token(db, token)
    if token is None:
        return {"success": False, "description": "请先登录"}
    if user is None:
        return {"success": False, "description": "user is invaild"}

    users_like = json.loads(comment.users_like) if comment.users_like else []
    users_dislike = json.loads(
        comment.users_dislike) if comment.users_dislike else []
    if user.id in users_like:  # 已经点赞
        if operation == "dislike":
            return {"success": False, "description": "已经点过赞了，请先取消赞"}
        elif operation == "like":
            users_like.remove(user.id)
            comment.users_like = json.dumps(users_like)
            comment.like_count -= 1
            db.commit()
            return {"success": True, "new_val": comment.like_count, "description": "已取消赞"}
    if user.id in users_dislike:  # 已经点踩
        if operation == "like":
            return {"success": False, "description": "已经点过踩了，请先取消踩"}
        elif operation == "dislike":
            users_dislike.remove(user.id)
            comment.users_dislike = json.dumps(users_dislike)
            comment.dislike_count -= 1
            db.commit()
            return {"success": True, "new_val": comment.dislike_count, "description": "已取消踩"}

    if operation == "like":  # 点赞
        users_like.append(user.id)
        comment.users_like = json.dumps(users_like)
        comment.like_count += 1
        new_val = comment.like_count  # TODO: 这里可能会有并发问题
    elif operation == "dislike":  # 点踩
        users_dislike.append(user.id)
        comment.users_dislike = json.dumps(users_dislike)
        comment.dislike_count += 1
        new_val = comment.dislike_count  # TODO: 这里可能会有并发问题
    db.commit()
    return {"success": True, "new_val": new_val, "description": "操作成功"}


@app.get("/comment/get")
async def get_comment(news_id: int, offset: Optional[datetime] = None, limit: int = 5,
                      token: Optional[str] = Form(None), db: Session = Depends(get_db)):
    """获取评论"""
    if offset is None:  # 如果没有传入offset，则默认为当前时间
        offset = datetime.now()
    self = None
    if token is not None:  # 如果有token，则获取用户信息
        self = curd.get_user_by_token(db, token)
    news = curd.get_news(db, news_id)  # 获取新闻
    if news is None:  # 新闻不存在
        return {"success": False, "description": "news id not found"}
    comment_list = curd.get_latest_comments_by_news_id(
        db, news_id, offset, limit)
    result = []
    for comment in comment_list:
        user = curd.get_user(db, user_id=comment.user_id)
        t = {
            "id": comment.id,
            "content": comment.content,
            "created_at": comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            "geo_location": comment.geo_location,
            "like_count": comment.like_count,
            "dislike_count": comment.dislike_count,
            "liked": self and self.id in json.loads(comment.users_like),
            "disliked": self and self.id in json.loads(comment.users_dislike),
            "user": {
                "id": user.id,
                "nickname": user.nickname,
                "avatar": user.avatar
            }
        }
        result.append(t)
    return {"success": True, "result": result}


@app.post("/comment/post")
async def post_comment(request: Request, content: str = Form(),  target_id: int = Form(),
                       # is_reply: bool = Form(False), reply_target_id: Optional[int] = Form(None),
                       token: Optional[str] = Form(None), db: Session = Depends(get_db)):
    """发表评论"""
    user = curd.get_user_by_token(db, token)
    ip_address = request.client.host
    geo_location = ip2loc.lookup(ip_address)
    if geo_location:
        geo_location = " ".join(geo_location)  # 将结果拼接起来
    user_agent = request.headers.get("User-Agent")  # 获取用户ua
    if user is None:
        return {"success": False, "description": "用户未登录"}
    if len(content) < 5:  # 评论太短
        return {"success": False, "description": "评论太短"}
    curd.add_news_comment_counter(db, target_id)  # 增加评论计数
    curd.insert_comment(db, schemas.Comment(
        user_id=user.id,
        content=content,
        ip=ip_address,
        user_agent=user_agent,
        geo_location=geo_location,
        # is_reply=is_reply,
        target_id=target_id,
        created_at=datetime.now()
        # reply_target_id=reply_target_id,
    ))
    return {"success": True, "description": "评论成功"}


@app.websocket("/view_history/{news_id}")
async def update_user_history(news_id: int, ws: WebSocket, db: Session = Depends(get_db)):
    """实时维护用户浏览记录，记录停留时间"""
    await ws.accept()  # 接受连接
    token = await ws.receive_text()  # 获取token
    print(token)
    user = curd.get_user_by_token(db, token)  # 获取用户
    if user is None:  # 如果用户不存在
        # 发送错误信息
        await ws.send_json({"success": False, "description": "user not found"})
        await ws.close()  # 关闭连接
        return
    news = curd.get_news(db, news_id)  # 获取新闻
    if news is None:  # 如果新闻不存在
        # 发送错误消息
        await ws.send_json({"success": False, "description": "news not found"})
        await ws.close()  # 关闭连接
        return  # 卫函数
    await ws.send_json({"success": True, "description": "server is ready"})
    start_timestamp = datetime.now()  # 记录浏览开始时间
    end_timestamp = None  # 浏览结束时间
    try:
        while True:
            msg = await ws.receive_json()  # 阻塞接收消息
            # print(msg)
            if msg["action"] == "view_end":  # 如果收到结束消息
                end_timestamp = datetime.now()  # 记录结束时间
    except WebSocketDisconnect:
        end_timestamp = datetime.now()  # 异常退出也记录时间
    finally:
        if end_timestamp is not None:
            # milliseconds
            duration = (end_timestamp -
                        start_timestamp).total_seconds()*1000  # 计算时间差
            print("user leave at", end_timestamp, duration)
            # 将用户浏览记录插入数据库
            curd.insert_view_history(db, schemas.ViewHistory(user_id=user.id,
                                                             article_id=news.id,
                                                             view_at=start_timestamp,
                                                             leave_at=end_timestamp,
                                                             duration=duration))


@app.get("/user/favorite")
async def get_user_favorite(token: Optional[str] = None, db: Session = Depends(get_db)):
    """获取用户收藏的新闻"""
    if token is None:  # 如果没有token
        return {"success": False, "description": "用户未登录"}
    user = curd.get_user_by_token(db, token)  # 获取用户
    if user is None:  # 如果用户不存在
        return {"success": False, "description": "user is invalid"}
    news_list = []  # 创建新闻列表
    for news_id in curd.get_user_favorite_news(db, user.id):  # 遍历用户收藏的新闻id
        news = curd.get_news(db, news_id)  # 获取新闻
        news_list.append({
            "id": news.id,
            "title": news.title,
            "category": news.category,
            "created_at": news.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            "bk_img": news.background_img,
        })
    news_list = sorted(
        news_list, key=lambda x: x["created_at"], reverse=True)  # 按时间排序
    return {"success": True, "result": news_list}


@app.get("/user/avatar")
async def get_user_avatar(token: Optional[str] = None, id: Optional[str] = None, db: Session = Depends(get_db)):
    """获取用户头像"""
    path = './avatar/default.jpg'  # 默认头像
    user = curd.get_user_by_token(db, token)  # 获取用户（有token）
    if id:  # 如果有id
        user = curd.get_user_by_id(db, id)  # 获取用户（有id）
    if user:  # 如果用户存在
        path = f'./avatar/{user.avatar}'  # 头像路径
    return StreamingResponse(open(path, "rb"), media_type="image/jpeg")  # 返回头像

@app.get("/user/avatar/{img_file}")
async def get_user_avatar(img_file: str, db: Session = Depends(get_db)):
    """获取用户头像（通过静态文件名）"""
    print(img_file)
    path = f'./avatar/{img_file}' # 头像路径
    if not os.path.exists(path): # 如果文件不存在
        path = './avatar/default.jpg' # 默认头像
    return StreamingResponse(open(path, "rb"), media_type="image/jpeg") # 返回头像

@app.get("/user/details")
async def get_user_detail(token: str, db: Session = Depends(get_db)):
    """获取用户详情"""
    user = curd.get_user_by_token(db, token)  # 获取用户
    if user is None:  # 如果用户不存在
        return {"success": False, "description": "user not found"}
    return {"success": True,
            "id": user.id,
            "is_admin": user.is_admin,
            "username": user.username,
            "avatar": user.avatar,
            "nickname": user.nickname,
            "registered_at": user.registered_at}


@app.get("/oauth/qq")
async def oauth_qq(accessToken: str, db: Session = Depends(get_db)):
    """QQ登录"""
    qq_login = QQLogin(accessToken)  # 创建QQ登录对象
    result = qq_login.fetch()  # 获取登录结果
    user = curd.get_user_by_qq_unionid(db, result["unionid"])  # 获取用户
    is_new_user = False
    if user is None:  # 如果用户不存在
        # 创建用户
        user = curd.create_user(db, schemas.User(qq_union_id=result["unionid"],
                                                 nickname=result["nickname"],
                                                 avatar=result["avatar_path"]))
        is_new_user = True

    return {"success": True,
            "description": "登录成功！",
            "is_new_user": is_new_user,
            "token": user.token}


@app.post("/obj")
async def ocr_api(file: UploadFile = File(...)):
    """目标检测"""
    contents = await file.read()  # 读取文件内容
    # to base64
    base64_str = str(base64.b64encode(contents), encoding='utf8')
    try:
        result = ECloudOBJ(base64_str=base64_str)  # 创建目标检测对象
        return {"success": True, "content": result}  # 返回结果
    except Exception as e:  # 如果出错
        return {"success": False, "message": str(e)}  # 返回错误信息


@app.post("/ocr")
async def ocr_api(file: UploadFile = File(...)):
    """OCR文字识别"""
    contents = await file.read()  # 读取文件内容
    # to base64
    base64_str = str(base64.b64encode(contents), encoding='utf8')
    try:
        result = ECloudOCR(base64_str=base64_str)  # 创建OCR对象
        return {"success": True, "content": result}  # 返回结果
    except Exception as e:  # 如果出错
        return {"success": False, "message": str(e)}  # 返回错误信息


@app.get("/tts")
async def tts_api(text: str):
    """TTS语音合成"""
    print("tts text:", text)
    try:
        path = ECloudTTS(text)  # 创建TTS对象
        # 返回语音文件
        return StreamingResponse(open(path, 'rb'), media_type='audio/wav')
    except Exception as e:  # 如果出错
        return {"success": False, "message": str(e)}  # 返回错误信息


conns = []  # 所有websocket连接（调试用）


@app.websocket("/stt")
async def stt_ws(ws: WebSocket):
    """语音识别"""
    def stt_callback(text, type):  # 语音识别回调
        print(text, type)
        t = {"text": text, "type": type}
        json_str = to_json_str(t)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(ws.send_text(json_str))

    stt = ECloudSTT()  # 创建语音识别对象
    stt.set_callback(stt_callback)  # 设置回调函数
    ##########
    #TODO: 鉴权
    ##########
    await ws.accept()  # 接受连接
    conns.append(ws)  # 添加连接
    print("websocket connected")
    stt.start()  # 开始语音识别
    try:
        while True:
            data = await ws.receive_text()  # 接收文本
            pcm = [[i] for i in json.loads(data)]  # 解析json，并转换为二维数组
            pcm = np.array(pcm, dtype=np.int32)  # 转换为np数组
            # debug.add_to_pcm_queue(pcm)  # 写入本地喇叭PCM队列（DEBUG ONLY）
            # print(pcm)
            base64_data = base64.b64encode(pcm)  # 转换为base64
            base64_str = base64_data.decode('utf-8')
            # print(base64_str)
            stt.send(base64_str)  # 发送数据给移动云
    except WebSocketDisconnect:  # 如果断开连接
        conns.remove(ws)  # 移除连接
        print("websocket disconnected")
        stt.stop()  # 停止语音识别
        pass


async def broadcast(data):
    """向所有ws连接发广播（调试用）"""
    print("broadcast:", data)
    for conn in conns:
        await conn.send_text(data)


@app.get("/stt/debug")
async def stt_debug(text: str):
    """语音识别结果强制发送（调试用）"""
    t = ''
    for word in jieba.lcut(text)[:-1]:
        t += word
        json_str = to_json_str({"text": t, "type": 0})
        await broadcast(json_str)
        await asyncio.sleep(1)
    json_str = to_json_str({"text": text, "type": 1})
    await broadcast(json_str)
    return {"success": True}

uvicorn.run(app=app, host="0.0.0.0", port=4000)