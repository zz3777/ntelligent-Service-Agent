from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class DocumentOut(BaseModel):
    id: UUID
    filename: str
    file_type: str
    file_size: int
    status: str
    storage_type: str
    chunk_count: int
    error_message: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentChunkOut(BaseModel):
    id: UUID
    content: str
    chunk_index: int
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentDetailOut(DocumentOut):
    chunks: list[DocumentChunkOut]


class TestSearchRequest(BaseModel):
    query: str
    top_k: int = 5


class TestSearchResult(BaseModel):
    content: str
    score: float
    document_name: str
