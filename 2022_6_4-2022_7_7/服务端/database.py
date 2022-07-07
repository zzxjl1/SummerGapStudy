from matplotlib.style import use
from requests_toolbelt import user_agent
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

USER_NAME = 'aisee'
PASSWORD = 'EPJs8dGpNkKprGkP'
HOST = 'idealbroker.cn'
PORT = '3306'
DATABASE = 'aisee'
#'数据库类型+数据库驱动名称://用户名:口令@机器地址:端口号/数据库名'
SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{USER_NAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={},pool_size=100, max_overflow=-1, pool_recycle=3600
)
DBSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
