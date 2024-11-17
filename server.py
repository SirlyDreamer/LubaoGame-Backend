import os

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)