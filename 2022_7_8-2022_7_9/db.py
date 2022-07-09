import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy import REAL, TEXT, INTEGER, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column
from sqlalchemy import event
from sqlalchemy.orm import relationship


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
    INTEGER: validate_int,
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


class Section(Base):

    __tablename__ = 'sections'

    id = Column(INTEGER, primary_key=True)
    name = Column(TEXT)
    collection_count = Column(INTEGER)
    #formation_ids = Column(TEXT)
    formaton_count = Column(INTEGER)
    main_formation_id = Column(INTEGER)
    fossil_count = Column(INTEGER)
    longitude = Column(REAL)
    latitude = Column(REAL)

    formations = relationship("Formation", back_populates="section")
    units = relationship("Unit", back_populates="section")


class Formation(Base):

    __tablename__ = 'formations'

    id = Column(INTEGER, primary_key=True)
    #ref_id = Column(INTEGER)
    section_id = Column(INTEGER, ForeignKey('sections.id'))
    #geology_id = Column(INTEGER)
    geology_location = Column(TEXT)
    geology_locality = Column(TEXT)
    group = Column(TEXT)
    member = Column(TEXT)
    no = Column(INTEGER)
    name = Column(TEXT)
    bed = Column(TEXT)
    overlying = Column(TEXT)
    underline = Column(TEXT)
    color = Column(TEXT)
    lithology = Column(TEXT)
    longitude = Column(REAL)
    latitude = Column(REAL)
    thick_sign = Column(TEXT)
    thick = Column(REAL)
    thick_unit = Column(TEXT)
    conta_base = Column(TEXT)
    paleoenvironment = Column(TEXT)
    accessibility = Column(INTEGER)
    release_date = Column(TEXT)
    early_interval = Column(TEXT)
    intage_max = Column(TEXT)
    epoch_max = Column(TEXT)
    emlperiod_max = Column(TEXT)
    period_max = Column(TEXT)
    early_age = Column(REAL)
    late_age = Column(REAL)
    age_color = Column(TEXT)
    erathem_max = Column(TEXT)
    section_name = Column(TEXT)

    section = relationship("Section", back_populates="formations")
    units = relationship("Unit", back_populates="formations")

"""
class SectionFormationMapping(Base):
    __tablename__ = 'section_formation_mapping'

    section_id = Column(INTEGER, ForeignKey('sections.id'), primary_key=True)
    formation_id = Column(INTEGER, ForeignKey(
        'formations.id'), primary_key=True)
"""

class Unit(Base):

    __tablename__ = 'units'

    id = Column(INTEGER, primary_key=True)
    no = Column(INTEGER)
    formation_id = Column(INTEGER, ForeignKey('formations.id'), primary_key=True)
    #ref_id = Column(INTEGER)
    section_id = Column(INTEGER, ForeignKey('sections.id'))
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

    formations = relationship("Formation", back_populates="units")
    section = relationship("Section", back_populates="units")


path = os.path.abspath(__file__)  # 获取当前文件的绝对路径
dir_path = os.path.dirname(path)  # 所在目录路径

db_file_path = os.path.join(dir_path, 'geo.sqlite')
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
