import os
from pydoc import describe

from fastapi import FastAPI, Request
from utils import LevelDatabase
app = FastAPI()

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)