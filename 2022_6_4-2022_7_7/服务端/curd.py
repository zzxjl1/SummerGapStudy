from datetime import datetime
import json
from typing import List
from sqlalchemy import and_, desc, func, or_
from sqlalchemy.orm import Session

import models
import schemas

#################################################
# 以下为 USER
#################################################


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_qq_unionid(db: Session, qq_unionid: str):
    return db.query(models.User).filter(models.User.qq_union_id == qq_unionid).first()


def get_user_by_token(db: Session, token: str):
    if token is None:
        return None
    return db.query(models.User).filter(models.User.token == token).first()


def get_all_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.User):
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def user_toggle_favorite_news(db: Session, user_id: int, news_id: int, payload: bool):
    user = get_user(db, user_id)
    if user is None:
        return
    news = get_news(db, news_id)
    if news is None:
        return
    t = json.loads(user.favorites)
    if payload:
        if news_id in t:
            return
        t.append(news_id)
    else:
        if news_id not in t:
            return
        t.remove(news_id)
    user.favorites = json.dumps(t)
    db.commit()
    return


def get_user_favorite_news(db: Session, user_id: int):
    user = get_user(db, user_id)
    if user is None:
        return
    return json.loads(user.favorites)


#################################################
# 以下为 NEWS
#################################################


def get_news_recommand(db: Session, offset: datetime, limit: int = 5):
    return db.query(models.Article).filter(models.Article.created_at < offset)  \
                                   .order_by(func.random()).limit(limit).all()


def get_latest_news(db: Session, offset: datetime, limit: int = 5):
    return db.query(models.Article).filter(models.Article.created_at < offset) \
                                   .order_by(desc(models.Article.created_at)).limit(limit).all()


def get_news(db: Session, news_id: int):
    return db.query(models.Article).filter(models.Article.id == news_id).first()


def get_news_by_category(db: Session, category: str, offset: datetime, limit: int = 5):
    return db.query(models.Article) \
             .filter(and_(models.Article.category == category, models.Article.created_at < offset)) \
             .order_by(desc(models.Article.created_at)).limit(limit).all()


def get_news_by_title(db: Session, title: str):
    return db.query(models.Article).filter(models.Article.title == title).first()


def add_news_view_counter(db: Session, news_id: int):
    news = get_news(db, news_id)
    if news is None:
        return
    news.click_count += 1  # TODO: 存在并发问题
    db.commit()


def add_news_comment_counter(db: Session, news_id: int):
    news = get_news(db, news_id)
    if news is None:
        return
    news.comment_count += 1  # TODO: 存在并发问题
    db.commit()


def insert_news(db: Session, news: schemas.Article):
    is_exists = get_news_by_title(db, news.title)
    if is_exists:
        return
    db_news = models.Article(**news.dict())
    db.add(db_news)
    db.commit()
    db.refresh(db_news)
    return db_news


def news_toggle_user_like(db: Session, user_id: int, news_id: int, payload: bool):
    user = get_user(db, user_id)
    if user is None:
        return
    news = get_news(db, news_id)
    if news is None:
        return
    t = json.loads(news.users_like)
    if payload:
        if user_id in t:
            return
        t.append(user_id)
        news.like_count += 1
    else:
        if user_id not in t:
            return
        t.remove(user_id)
        news.like_count -= 1
    news.users_like = json.dumps(t)
    db.commit()
    return


def update_news_last_view_time(db: Session, news_id: int):
    news = get_news(db, news_id)
    if news is None:
        return
    news.last_viewed_at = datetime.now()
    db.commit()
    return


def get_news_most_viewed(db: Session, limit: int = 5):
    result = db.query(models.Article).order_by(
        desc(models.Article.click_count)).limit(limit).all()
    return [i.title for i in result]


def search_news(db: Session, keywords: List[str], offset: int = 0, limit: int = 20):
    """ 
    TODO: 使用倒排索引中间件以提升性能和准确度 
    """
    keywords = list(set(keywords))  # 去重
    keywords = [f"%{i}%" for i in keywords]
    rule1 = or_(*[models.Article.title.like(keyword) for keyword in keywords])
    #rule2 = or_(*[models.Article.content.like(keyword) for keyword in keywords])
    return db.query(models.Article)\
        .filter(rule1) \
        .order_by(desc(models.Article.created_at))\
        .offset(offset).limit(limit).all()


#################################################
# 以下为 VIEW HISTORY
#################################################


def insert_view_history(db: Session, view_history: schemas.ViewHistory):
    db_history = models.ViewHistory(**view_history.dict())
    db.add(db_history)
    db.commit()
    db.refresh(db_history)
    return db_history


#################################################
# 以下为 COMMENT
#################################################


def insert_comment(db: Session, comment: schemas.Comment):
    db_comment = models.Comment(**comment.dict())
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


def get_comment(db: Session, comment_id: int):
    return db.query(models.Comment).filter(models.Comment.id == comment_id).first()


def get_latest_comments_by_news_id(db: Session, target_id: int, offset: datetime, limit: int = 5):
    return db.query(models.Comment)\
        .filter(and_(models.Comment.target_id == target_id, models.Comment.created_at < offset))\
        .order_by(desc(models.Comment.created_at)).limit(limit).all()


if __name__ == "__main__":
    ########################################
    # DEBUG ONLY
    ########################################
    from database import DBSession, engine
    import uuid

    db = DBSession()
    print(get_user(db, user_id=1))
    #print(create_user(db, schemas.UserCreate(qq_union_id=uuid.uuid4().hex)))
    print(get_all_users(db))
