from sqlalchemy import exists
from db import Base,engine,Point,Formation,Unit,session

def flush():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine, checkfirst=False)

def insert_point(**args):
    point = Point(**args)
    session.add(point)
    session.commit()

def insert_formation(**args):
    formation = Formation(**args)
    session.add(formation)
    session.commit()

def insert_unit(**args):
    is_exist = session.query(exists().where(Unit.id==args["id"])).scalar()
    if is_exist:
        print("unit id already exists")
        return
    unit = Unit(**args)
    session.add(unit)
    session.commit()