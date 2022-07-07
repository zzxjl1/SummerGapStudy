from datetime import datetime
from lib2to3.pgen2 import token
from typing import List, Optional, Union
from pydantic import BaseModel
from toolutils import random_str


class Comment(BaseModel):
    id: int = None
    user_id: int
    content: str
    like_count: int = 0
    users_like: str = '[]'
    dislike_count: int = 0
    users_dislike: str = '[]'
    ip: str
    user_agent: str
    geo_location: str = "未知"
    #is_reply: bool = False
    created_at: datetime = datetime.now()
    target_id: int
    #reply_target_id: int = None

    class Config:
        orm_mode = True


class Article(BaseModel):
    id: int = None
    title: str
    category: str
    source: str
    background_img: str
    summary: str
    content: str
    tags: str = ""
    created_at: datetime = datetime.now()
    owner_id: int
    click_count: int = 0
    like_count: int = 0
    users_like: str = '[]'
    comment_count: int = 0
    last_viewed_at: datetime = datetime.now()

    comments: List[Comment] = []

    class Config:
        orm_mode = True


class ViewHistory(BaseModel):
    id: int = None
    user_id: int
    article_id: int
    view_at: datetime
    leave_at: datetime
    duration: int

    class Config:
        orm_mode = True


class User(BaseModel):
    id: int = None
    token: str = random_str()  # generate random string
    is_admin: bool = False
    qq_union_id: str
    username: Optional[str]
    password: Optional[str]
    avatar: str = "default.jpg"
    nickname: str = "annonymous"
    registered_at: datetime = datetime.now()
    favorites: str = "[]"

    comments: List[Comment] = []
    articles: List[Article] = []
    view_history: List[ViewHistory] = []

    class Config:
        orm_mode = True
