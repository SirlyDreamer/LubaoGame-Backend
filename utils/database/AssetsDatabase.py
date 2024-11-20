import json
from sqlalchemy import Column, Integer, String, Boolean, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Asset(Base):
    __tablename__ = 'AssetsDB'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    description = Column(String)

# TODO: Implement the AssetsDatabase class
class AssetsDatabase:
    def __init__(self, host="localhost", user="postgres", password="password", database="postgres"):
        self.engine = create_engine(f'postgresql://{user}:{password}@{host}/{database}')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def add_asset(self, name, asset, description):
        pass