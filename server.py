import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from utils.assets import get_initial_assets

from utils import LevelDatabase
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

@app.post("/getAllAssets")
async def get_all_assets():
    # TODO: Implement this function
    return get_initial_assets()

@app.post("/getCode")
async def get_code(request: Request):
    body = await request.json()
    print(body)
    if 'query' in body:
        query = body['query']
    mode = body['mode'] if 'mode' in body else "python"
    model_choice = body['model_choice'] if 'model_choice' in body else "DeepSeek"
    try:
        return gen_code(query, mode, model_choice)
    except Exception as e:
        print(e)
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)