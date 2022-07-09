from sqlalchemy import exists
from db import Base,engine,Section,Formation,Unit,session

def flush():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine, checkfirst=False)

def insert_point(**args):
    is_exist = session.query(exists().where(Section.id==args["id"])).scalar()
    if is_exist:
        print("section id already exists",args)
        return
    point = Section(**args)
    session.add(point)
    session.commit()

def insert_formation(**args):
    is_exist = session.query(exists().where(Formation.id==args["id"])).scalar()
    if is_exist:
        print("formation id already exists",args)
        return
    formation = Formation(**args)
    session.add(formation)
    session.commit()

def insert_unit(**args):
    is_exist = session.query(exists().where(Unit.id==args["id"])).scalar()
    if is_exist:
        print("unit id already exists",args)
    unit = Unit(**args)
    session.add(unit)
    session.commit()
    
"""
def insert_section_formation_mapping(**args):
    mapping = SectionFormationMapping(**args)
    session.add(mapping)
    session.commit()
"""
if __name__ == "__main__":
    flush()