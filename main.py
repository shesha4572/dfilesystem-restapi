import io
from urllib.parse import quote
from fastapi import FastAPI, Path, HTTPException, UploadFile, Body
from typing import Annotated
import os
import requests
from fastapi.responses import StreamingResponse
from models import FileInfo
import random
app = FastAPI()
DFS_MASTER_NODE_URL = os.getenv("DFS_MASTER_NODE_URL")
DFS_SLAVE_SERVICE_URL = os.getenv("DFS_SLAVE_SERVICE_URL")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE"))
print(DFS_MASTER_NODE_URL , DFS_SLAVE_SERVICE_URL , CHUNK_SIZE)
@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/upload")
async def upload_file(file_name: Annotated[str, Body(title="The ID of the file to upload")] , file_id: Annotated[str, Body(title="The name of the file to upload")] , file: UploadFile):
    file_size = file.size
    print(f"Init file #{file_id} size {file_size}")
    body = {"fileName" : file_name , "fileId" : file_id , "fileSizeBytes" : file_size}
    res = requests.post(DFS_MASTER_NODE_URL + "/api/v1/file/createFile" , json=body)
    if res.status_code == 200:
        print(f"Init file #{file_id} size {file_size} successful : {res.json()}")
    else:
        print(f"Init file #{file_id} size {file_size} failed Reason : {res.json()}")
        raise HTTPException(status_code=500 , detail="Init file failed")
    i = 0
    for c in res.json():
        print(c)
        start = i * CHUNK_SIZE
        end = min(file_size, start + CHUNK_SIZE)
        file.file.seek(start)
        chunk = file.file.read(end - start)
        if not chunk:
            break
        files = {"file": (c[0], chunk, "application/octet-stream")}
        repl_no = 0
        for s in c[1:]:
            for _ in range(4):
                response = requests.post(f"http://{s}.{DFS_SLAVE_SERVICE_URL}/api/v1/slave/chunk/upload/{c[0]}/{i}/{repl_no}" , files=files)
                if response.status_code == 200:
                    print(f"Uploaded file #{file_id} chunk#{c[0]} Replica#{repl_no} to pod {s} successfully")
                    repl_no += 1
                    break
                else:
                    print(f"Failed to upload file #{file_id} chunk#{c[0]} Replica#{repl_no} to pod {s}: {response.content}")
        i += 1
    return {"chunksUploaded" : i}


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