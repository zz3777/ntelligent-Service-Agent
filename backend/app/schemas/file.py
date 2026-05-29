from pydantic import BaseModel


class FileUploadResponse(BaseModel):
    file_id: str
    filename: str
    text: str | None = None
    storage_type: str
