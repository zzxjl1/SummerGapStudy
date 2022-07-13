from sqlalchemy import exists
from db import Base, engine, session, Section, Formation, Unit, Collection, Fossil, SectionFormationMapping


def flush():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine, checkfirst=False)


def disable_section_formation_mapping():
    # drop table section_formation_mapping
    session.execute("DROP TABLE section_formation_mapping")


def insert_point(**args):
    is_exist = session.query(exists().where(Section.id == args["id"])).scalar()
    if is_exist:
        print("section id already exists", args)
        return
    point = Section(**args)
    session.add(point)
    session.commit()


def insert_formation(**args):
    is_exist = session.query(exists().where(
        Formation.id == args["id"])).scalar()
    if is_exist:
        print("formation id already exists", args)
        return
    formation = Formation(**args)
    session.add(formation)
    session.commit()


def insert_unit(**args):
    is_exist = session.query(exists().where(Unit.id == args["id"])).scalar()
    if is_exist:
        print("unit id already exists", args)
    unit = Unit(**args)
    session.add(unit)
    session.commit()


def insert_collection(**args):
    is_exist = session.query(exists().where(
        Collection.id == args["id"])).scalar()
    if is_exist:
        print("collection id already exists", args)
        return
    collection = Collection(**args)
    session.add(collection)
    session.commit()


def insert_fossil(**args):
    is_exist = session.query(exists().where(
        Fossil.id == args["id"])).scalar()
    if is_exist:
        print("fossil id already exists", args)
        return
    fossil = Fossil(**args)
    session.add(fossil)
    session.commit()


def insert_section_formation_mapping(**args):
    mapping = SectionFormationMapping(**args)
    session.add(mapping)
    session.commit()


if __name__ == "__main__":
    flush()
