from fastapi import FastAPI , Path
from typing import Annotated
import os
import requests
app = FastAPI()
DFS_MASTER_NODE_URL = os.getenv("DFS_MASTER_NODE_URL")
DFS_SLAVE_SERVICE_URL = os.getenv("DFS_SLAVE_SERVICE_URL")
print(DFS_MASTER_NODE_URL , DFS_SLAVE_SERVICE_URL)
@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/upload")
async def upload_file():
    pass

@app.get("/read/{fileID}")
async def read_file(fileID: Annotated[int, Path(title="The ID of the file to read")]):
    uri = DFS_MASTER_NODE_URL + "/api/v1/file/getAllFileChunks/" + str(fileID)
    res = requests.get(uri)
    print(res.content)


