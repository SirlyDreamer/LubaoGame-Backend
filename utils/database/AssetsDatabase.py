import os
import json
from sqlalchemy import Column, Integer, String, Boolean, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from utils.assets import get_uuid, base64_decode

Base = declarative_base()

class Asset(Base):
    __tablename__ = 'AssetsDB'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    type = Column(String, nullable=False)
    url = Column(String, nullable=False)
    description = Column(String)

# TODO: Implement the AssetsDatabase class
class AssetsDatabase:
    def __init__(self, host="localhost", user="postgres", password="password", database="postgres"):
        self.engine = create_engine(f'postgresql://{user}:{password}@{host}/{database}')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def add_asset(self, name, asset_type, asset, allow_overwrite=False):
        if self.get_asset(name):
            if allow_overwrite:
                self.delete_asset(name)
            else:
                return 1, f"Asset {name} already exists"
        if isinstance(asset, str):
            asset_type, asset = base64_decode(asset)
        uuid = get_uuid(asset)
        if asset_type == "image":
            print(os.getcwd())
            with open(f"/app/assets/image/{uuid}.png", "wb") as f:
                f.write(asset)
            url = f"image/{uuid}.png"
        elif asset_type == "audio":
            with open(f"/app/assets/audio/{uuid}.mp3", "wb") as f:
                f.write(asset)
            url = f"audio/{uuid}.mp3"
        else:
            raise ValueError(f"Unsupported asset type: {asset_type}")
        asset = Asset(name=name, type=asset_type, url=url)
        self.session.add(asset)
        self.session.commit()
        return 0, "Asset added successfully"

    def get_assets_list(self, asset_type, names):
        if names:
            if isinstance(names, str):
                names = [names]
            return self.session.query(Asset).filter_by(type=asset_type).filter(Asset.name.in_(names)).all()
        else:
            return self.session.query(Asset).filter_by(type=asset_type).all()
    
    def get_asset(self, name):
        return self.session.query(Asset).filter_by(name=name).first()
    
    def delete_asset(self, name):
        asset = self.get_asset(name)
        if asset:
            self.session.delete(asset)
            self.session.commit()
            if os.path.exists(f"/app/assets/{asset.url}"):
                os.remove(f"/app/assets/{asset.url}")
            return True
        return False