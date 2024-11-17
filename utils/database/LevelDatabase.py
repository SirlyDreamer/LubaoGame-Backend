import json
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

    def add_level(self, title, author, query, description, code, data, assetFinished=False, ifReference=False):
        new_level = Level(
            title=title,
            author=author,
            query=query,
            description=description,
            code=json.dumps(code),
            data=json.dumps(data),
            assetFinished=assetFinished,
            ifReference=ifReference
        )
        self.session.add(new_level)
        self.session.commit()

    def get_all_levels(self):
        return self.session.query(Level).all()

    def get_level_by_id(self, level_id):
        return self.session.query(Level).filter_by(id=level_id).first()

    def update_level(self, level_id, title, author, query, description, code, data, assetFinished, ifReference):
        level = self.get_level_by_id(level_id)
        level.title = title
        level.author = author
        level.query = query
        level.description = description
        level.code = json.dumps(code)
        level.data = json.dumps(data)
        level.assetFinished = assetFinished
        level.ifReference = ifReference
        self.session.commit()

    def delete_level(self, level_id):
        level = self.get_level_by_id(level_id)
        self.session.delete(level)
        self.session.commit()