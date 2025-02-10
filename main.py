import io
from urllib.parse import quote

from fastapi import FastAPI, Path, HTTPException
from typing import Annotated
import os
import requests
from fastapi.responses import StreamingResponse

from models import FileInfo
import random
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
async def read_file(fileID: Annotated[str, Path(title="The ID of the file to read")]):
    uri = DFS_MASTER_NODE_URL + "/api/v1/file/getAllFileChunks/" + fileID
    res = requests.get(uri)
    file_info = None
    if res.status_code == 200:
        file_info = FileInfo(**res.json())
        print(f"Reading metadata of file #{fileID} successful File info = {file_info}")
    else:
        print(f"Reading metadata of file #{fileID} unsuccessful")
        raise HTTPException(status_code=500 , detail="Reading metadata failed")
    print(f"Reading file #{fileID}")
    chunks = []
    for i in sorted(file_info.chunk_list , key=lambda c: c.chunk_id):
        for _ in range(3):
            slave_choice = random.choice(i.replica_pod_list)
            print(f"Downloading file #{file_info.file_id} chunk #{i.chunk_id} from {slave_choice}")
            res = requests.get(f"http://{slave_choice}.{DFS_SLAVE_SERVICE_URL}/api/v1/slave/chunk/get/{i.chunk_id}")
            if res.status_code == 200:
                chunks.append(res.content)
                print(f"Downloaded file #{file_info.file_id} chunk #{i.chunk_id} from {slave_choice} successfully")
                break
            print(f"Downloading file #{file_info.file_id} chunk #{i.chunk_id} from {slave_choice} unsuccessful. Failure reason {res}")

    whole_file = io.BytesIO(b"".join(chunks))
    whole_file.seek(0)
    encoded_filename = quote(file_info.file_name)
    return StreamingResponse(
        whole_file,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
        }
    )