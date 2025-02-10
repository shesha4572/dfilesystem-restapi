from typing import List
from pydantic import BaseModel, Field
from datetime import datetime

class Chunk(BaseModel):
    chunk_id: str = Field(..., alias="chunkId")
    file_id: str = Field(..., alias="fileId")
    chunk_index: int = Field(..., alias="chunkIndex")
    replica_pod_list: List[str] = Field(default_factory=list, alias="replicaPodList")

class FileInfo(BaseModel):
    file_id: str = Field(..., alias="fileId")
    uploaded_on: datetime = Field(..., alias="uploadedOn")
    file_name: str = Field(..., alias="fileName")
    size: int
    chunk_list: List[Chunk] = Field(default_factory=list, alias="chunkList")
