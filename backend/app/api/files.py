from fastapi import APIRouter, UploadFile, File
from app.schemas.file import FileUploadResponse
from app.services.temp_file_store import save_temp_file
from app.services.knowledge_service import extract_text_from_file

router = APIRouter(prefix="/api/files", tags=["files"])


@router.post("/upload-temp", response_model=FileUploadResponse)
async def upload_temp_file(file: UploadFile = File(...)):
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else "unknown"
    type_map = {"pdf": "pdf", "docx": "docx", "doc": "docx", "xlsx": "xlsx", "xls": "xlsx",
                "png": "image", "jpg": "image", "jpeg": "image", "bmp": "image"}
    file_type = type_map.get(ext, "unknown")

    content = await file.read()
    file_id = await save_temp_file(content, file_type)

    text = await extract_text_from_file(content, file_type)

    return FileUploadResponse(
        file_id=file_id,
        filename=file.filename,
        text=text,
        storage_type="temp",
    )
