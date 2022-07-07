from time import time
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship

from database import Base, engine, DBSession


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    token = Column(Text)
    is_admin = Column(Boolean, default=False)
    qq_union_id = Column(String(36), unique=True, index=True)
    username = Column(String(10), unique=True, index=True)
    password = Column(Text)
    avatar = Column(Text)
    nickname = Column(Text)
    registered_at = Column(DateTime, default=time)
    favorites = Column(Text, default="[]")

    comments = relationship("Comment", back_populates="owner", lazy="dynamic")
    articles = relationship("Article", back_populates="author", lazy="dynamic")
    view_history = relationship(
        "ViewHistory", back_populates="owner", lazy="dynamic")

    def generate_hashed_password(self, password):
        import hashlib
        # add salt
        salt = "aisee"
        result = password+salt
        return hashlib.sha256(
            result.encode(encoding='utf-8')).hexdigest()

    def validate_password(self, password):
        return self.password == self.generate_hashed_password(password)


class ViewHistory(Base):
    __tablename__ = "view_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    article_id = Column(Integer, ForeignKey("articles.id"))
    view_at = Column(DateTime, default=time)
    leave_at = Column(DateTime, default=time)
    duration = Column(Integer)

    owner = relationship("User", back_populates="view_history")


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(50), unique=True, nullable=False)
    category = Column(Text, nullable=False)
    source = Column(Text, nullable=False)
    background_img = Column(Text, default="")
    summary = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    tags = Column(Text, default="")
    created_at = Column(DateTime, default=time)
    owner_id = Column(Integer, ForeignKey("users.id"))
    click_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    users_like = Column(Text, default="[]")
    comment_count = Column(Integer, default=0)
    last_viewed_at = Column(DateTime, default=time)

    author = relationship("User", back_populates="articles")
    comments = relationship(
        "Comment", back_populates="article", lazy="dynamic")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text)
    like_count = Column(Integer, default=0)
    users_like = Column(Text, default="[]")
    dislike_count = Column(Integer, default=0)
    users_dislike = Column(Text, default="[]")
    ip = Column(Text)
    user_agent = Column(Text)
    geo_location = Column(Text)
    #is_reply = Column(Boolean, default=False)
    created_at = Column(DateTime, default=time)
    target_id = Column(Integer, ForeignKey("articles.id"))
    #reply_target_id = Column(Integer, ForeignKey("comments.id"))

    owner = relationship("User", back_populates="comments")
    article = relationship("Article", back_populates="comments")


if __name__ == "__main__":
    Base.metadata.drop_all(engine)  # 删除表结构
    Base.metadata.create_all(engine)  # 创建表结构
