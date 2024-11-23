import os
import json

from fastapi import FastAPI, Request, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from utils import LevelDatabase, AssetsDatabase
from lulu_exp.generate_code import gen_code

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
    levels = level_db.get_level_list()
    return [{"id": level.id, "title": level.title, "data": level.data, "author": level.author} for level in levels]

@app.post("/uploadLevel")
async def upload_level(request: Request):
    body = await request.json()
    if not isinstance(body, list):
        body = [body]
    response_body = []
    for level in body:
        code, msg = level_db.add_level(
            level.get("title"),
            level.get("author"),
            level.get("query"),
            level.get("description"),
            level.get("code"),
            level.get("data"),
            level.get("assetFinished"),
            level.get("ifReference"),
            level.get("overwrite", False)
        )
        response_body.append({"title": level.get("title"), "code": code, "message": msg})
    return response_body if len(response_body) > 1 else response_body[0]

@app.post("/getLevelList")
async def get_level_list(request: Request):
    try:
        body = await request.json()
    except json.decoder.JSONDecodeError:
        body = {}
    level_list = level_db.get_level_list(body.get("titles"))
    return [{"id": level.id, "title": level.title, "data": level.data, "author": level.author} for level in level_list]

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

@app.post("/getCode")
async def get_code(request: Request):
    body = await request.json()
    if 'query' in body:
        query = body['query']
    else:
        return {"error": "Query field missing from request body"}
    mode = body['mode'] if 'mode' in body else "python"
    model_choice = body['model_choice'] if 'model_choice' in body else "DeepSeek"
    try:
        return gen_code(query, mode, model_choice)
    except Exception as e:
        print(e)
        return {"error": str(e)}

@app.post("/updateSampleFile")
async def upload_file(sample_levels: UploadFile = File(...),
                      sample_levels_python: UploadFile = File(...)):
    with open(os.path.join('/app/lulu_exp/', sample_levels.filename), 'wb') as f:
        contents = await sample_levels.read()  # 异步读取文件内容
        f.write(contents)
    with open(os.path.join('/app/lulu_exp/', sample_levels_python.filename), 'wb') as f:
        contents = await sample_levels_python.read()  # 异步读取文件内容
        f.write(contents)
    return {"message": f"Successfully saved {sample_levels.filename} and {sample_levels_python.filename}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)