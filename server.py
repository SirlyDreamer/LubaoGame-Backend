import os
import json

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from utils import LevelDatabase, AssetsDatabase

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

level_db = LevelDatabase(
    host=os.getenv("POSTGRES_HOST", "localhost"),
    user=os.getenv("POSTGRES_USER", "postgres"),
    password=os.getenv("POSTGRES_PASSWD","password"),
    database=os.getenv("POSTGRES_DB", "postgres")
)

asset_db = AssetsDatabase(
    host=os.getenv("POSTGRES_HOST", "localhost"),
    user=os.getenv("POSTGRES_USER", "postgres"),
    password=os.getenv("POSTGRES_PASSWD","password"),
    database=os.getenv("POSTGRES_DB", "postgres")
)

@app.get("/getAllLevels")
async def get_all_levels():
    levels = level_db.get_all_levels()
    return [{"id": level.id, "title": level.title, "data": level.data, "author": level.author} for level in levels]

@app.post("/uploadLevel")
async def upload_level(request: Request):
    body = await request.json()
    if not isinstance(body, list):
        body = [body]
    for level in body:
        level_db.add_level(
            level.get("title"),
            level.get("author"),
            level.get("query"),
            level.get("description"),
            level.get("code"),
            level.get("data"),
            level.get("assetFinished"),
            level.get("ifReference")
        )
    return {"message": f"Successully added {len(body)} levels"}

@app.post("/getImageList")
async def get_image_list(request: Request):
    try:
        body = await request.json()
    except json.decoder.JSONDecodeError:
        body = {}
    image_list = asset_db.get_assets_list("image", body.get("names"))
    image_set = {image.name : image.url for image in image_list}
    return image_set

@app.post("/getAudioList")
async def get_audio_list(request: Request):
    try:
        body = await request.json()
    except json.decoder.JSONDecodeError:
        body = {}
    audio_list = asset_db.get_assets_list("audio", body.get("names"))
    audio_set = {audio.name : audio.url for audio in audio_list}
    return audio_set

@app.post("/uploadAsset")
async def upload_asset(request: Request):
    try:
        body = await request.json()
    except json.decoder.JSONDecodeError:
        return {"message": "Request body must be JSON"}, 400
    if not isinstance(body, list):
        body = [body]
    return_body = []
    for asset in body:
        code, msg = asset_db.add_asset(
            asset.get("name"),
            asset.get("type"),
            asset.get("asset"),
            asset.get("overwrite", False)
        )
        return_body.append({"name": asset.get("name"), "code": code, "message": msg})
    return return_body if len(return_body) > 1 else return_body[0]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)