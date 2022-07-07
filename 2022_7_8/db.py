import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy import REAL, TEXT, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import event
import datetime
Base = declarative_base()


def validate_int(value):
    if value is not None:
        assert isinstance(value, int)
    return value

def validate_float(value):
    if value is not None:
        assert isinstance(value, float) or isinstance(value, int)
    return value

def validate_string(value):
    if value is not None:
        assert isinstance(value, str)
    return value


validators = {
    Integer: validate_int,
    TEXT: validate_string,
    REAL: validate_float,
}

"""类型校验监听"""
@event.listens_for(Base, 'attribute_instrument')
def configure_listener(class_, key, inst):
    if not hasattr(inst.property, 'columns'):
        return

    @event.listens_for(inst, "set", retval=True)
    def set_(instance, value, oldvalue, initiator):
        validator = validators.get(inst.property.columns[0].type.__class__)
        if validator:
            return validator(value)
        else:
            return value


class Point(Base):

    __tablename__ = 'points'

    id = Column(Integer, primary_key=True)
    name = Column(TEXT)
    collection_count = Column(Integer)
    formation_ids = Column(TEXT)
    formaton_count = Column(Integer)
    main_formation_id = Column(Integer)
    fossil_count = Column(Integer)
    longitude = Column(REAL)
    latitude = Column(REAL)

class Formation(Base):

    __tablename__ = 'formations'

    id = Column(Integer, primary_key=True)#
    #ref_id = Column(Integer)
    section_id = Column(Integer)#
    geology_id = Column(Integer)
    geology_location = Column(TEXT)
    geology_locality = Column(TEXT)
    group = Column(TEXT)
    member = Column(TEXT)
    no = Column(Integer)
    name = Column(TEXT)#
    bed = Column(TEXT)
    overlying = Column(TEXT)
    underline = Column(TEXT)
    color = Column(TEXT)
    lithology = Column(TEXT)
    longitude = Column(REAL)
    latitude = Column(REAL)
    thick_sign = Column(TEXT)
    thick = Column(REAL)#
    thick_unit = Column(TEXT)
    conta_base = Column(TEXT)
    paleoenvironment = Column(TEXT)
    accessibility = Column(Integer)
    release_date = Column(TEXT)
    early_interval = Column(TEXT)
    intage_max = Column(TEXT)
    epoch_max = Column(TEXT)
    emlperiod_max = Column(TEXT)
    period_max = Column(TEXT)
    early_age = Column(REAL)#
    late_age = Column(REAL)#
    age_color = Column(TEXT)
    erathem_max = Column(TEXT)
    section_name = Column(TEXT)#

class Unit(Base):

    __tablename__ = 'units'

    id = Column(Integer, primary_key=True)
    no = Column(Integer)
    formation_id = Column(Integer)
    #ref_id = Column(Integer)
    section_id = Column(Integer)
    sum = Column(REAL)
    thick_sign = Column(TEXT)
    thick = Column(REAL)
    thick_unit = Column(TEXT)
    con_base = Column(TEXT)
    lithology1a = Column(TEXT)
    main_lithogya = Column(TEXT)
    release_date = Column(TEXT)
    early_interval = Column(TEXT)
    early_age = Column(REAL)
    late_age = Column(REAL)


path = os.path.abspath(__file__)  # 获取当前文件的绝对路径
dir_path = os.path.dirname(path)  # 所在目录路径

db_file_path = os.path.join(dir_path, 'geo.db')
print(db_file_path)
engine = create_engine(
    f"sqlite:///{db_file_path}?check_same_thread=False", echo=False)
Session = sessionmaker(bind=engine)

# 创建Session类实例
session = Session()


#######################
# TODO: 
# 1.FOREIGN KEY
# 2.SQLALCHEMY RELATION
#######################
