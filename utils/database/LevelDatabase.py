from sqlalchemy import Column, Integer, String, Boolean, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Level(Base):
    __tablename__ = 'LevelDB'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    author = Column(String, default="default")
    query = Column(String)
    description = Column(String)
    code = Column(String)
    data = Column(String)
    assetFinished = Column(Boolean, default=False)
    ifReference = Column(Boolean, default=False)

class LevelDatabase:
    def __init__(self, host="localhost", user="postgres", password="password", database="postgres"):
        self.engine = create_engine(f'postgresql://{user}:{password}@{host}/{database}')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def add_level(self, title, author, query, description, code, data, assetFinished, ifReference):
        new_level = Level(title=title, author=author, query=query, description=description, code=code, data=data, assetFinished=assetFinished, ifReference=ifReference)
        self.session.add(new_level)
        self.session.commit()

    def get_all_levels(self):
        return self.session.query(Level).all()

    def get_level_by_id(self, id):
        return self.session.query(Level).filter_by(id=id).first()

    def update_level(self, id, title, author, query, description, code, data, assetFinish, ifReference):
        level = self.get_level_by_id(id)
        level.title = title
        level.author = author
        level.query = query
        level.description = description
        level.code = code
        level.data = data
        level.assetFinish = assetFinish
        level.ifReference = ifReference
        self.session.commit()

    def delete_level(self, id):
        level = self.get_level_by_id(id)
        self.session.delete(level)
        self.session.commit()