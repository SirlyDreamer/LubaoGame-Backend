import os
from pydoc import describe

from fastapi import FastAPI
from utils import LevelDatabase
app = FastAPI()

level_db = LevelDatabase(
    host=os.getenv("POSTGRES_HOST", "localhost"),
    user=os.getenv("POSTGRES_USER", "postgres"),
    password=os.getenv("POSTGRES_PASSWD","password"),
    database=os.getenv("POSTGRES_DB", "postgres")
)

@app.get("/getAllLevels")
def get_all_levels():
    """
    Get all levels from the database
    :return:
    [{
        "id": int(8),
        "title": string,
        "data": {

        },
        "author": string,
    }]
    """
    levels = level_db.get_all_levels()
    return [{"id": level.id, "title": level.title, "data": level.data, "author": level.author} for level in levels]

@app.post("/uploadLevel")
def upload_level(response: dict):
    """
    Create a level
    :param title: string
    :param data: dict
    :param author: string
    :return:
    """
    title = response.get("title")
    author = response.get("author")
    query = response.get("query")
    data = response.get("data")
    description = response.get("description")
    code = response.get("code")
    assetFinished = response.get("assetFinished")
    ifReference = response.get("ifReference")
    level = level_db.add_level(title, author, query, description, code, data, assetFinished, ifReference)
    return {"id": level.id, "title": level.title, "data": level.data, "author": level.author}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)