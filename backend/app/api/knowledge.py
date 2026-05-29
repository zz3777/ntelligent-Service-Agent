import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.core.db import get_db
from app.schemas.knowledge import DocumentOut, DocumentDetailOut, DocumentChunkOut, TestSearchRequest, TestSearchResult
from app.models.knowledge_base import Document, DocumentChunk
from app.services.knowledge_service import process_document, extract_text_from_file

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


@router.post("/upload", response_model=DocumentOut)
async def upload_document(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else "unknown"
    type_map = {"pdf": "pdf", "docx": "docx", "doc": "docx", "xlsx": "xlsx", "xls": "xlsx",
                "png": "image", "jpg": "image", "jpeg": "image", "bmp": "image"}
    file_type = type_map.get(ext, "unknown")

    doc = Document(
        filename=file.filename,
        file_type=file_type,
        file_size=0,
        status="processing",
        storage_type="knowledge",
    )
    db.add(doc)
    await db.commit()

    content = await file.read()
    doc.file_size = len(content)

    try:
        text = await extract_text_from_file(content, file_type)
        chunk_count = await process_document(doc.id, text, db)
        doc.status = "ready"
        doc.chunk_count = chunk_count
    except Exception as e:
        doc.status = "failed"
        doc.error_message = str(e)

    await db.commit()
    await db.refresh(doc)
    return DocumentOut.model_validate(doc)


@router.get("/list", response_model=list[DocumentOut])
async def list_documents(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Document).where(Document.storage_type == "knowledge").order_by(Document.created_at.desc())
    )
    return [DocumentOut.model_validate(d) for d in result.scalars().all()]


@router.get("/{doc_id}", response_model=DocumentDetailOut)
async def get_document(doc_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Document).where(Document.id == doc_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    return DocumentDetailOut.model_validate(doc)


@router.delete("/{doc_id}")
async def delete_document(doc_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Document).where(Document.id == doc_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")

    # 清理 ChromaDB 中的向量
    try:
        from app.agent.rag import get_chroma_client
        client = get_chroma_client()
        collection = client.get_or_create_collection(name="enterprise_knowledge")
        # 查找该文档的所有向量并删除
        existing = collection.get(where={"document_id": str(doc_id)})
        if existing and existing["ids"]:
            collection.delete(ids=existing["ids"])
    except Exception:
        pass

    await db.execute(delete(DocumentChunk).where(DocumentChunk.document_id == doc_id))
    await db.delete(doc)
    await db.commit()
    return {"message": "已删除"}


@router.post("/{doc_id}/reprocess", response_model=DocumentOut)
async def reprocess_document(doc_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Document).where(Document.id == doc_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    doc.status = "processing"
    await db.commit()
    try:
        text = "重新处理占位"
        chunk_count = await process_document(doc.id, text, db)
        doc.status = "ready"
        doc.chunk_count = chunk_count
    except Exception as e:
        doc.status = "failed"
        doc.error_message = str(e)
    await db.commit()
    await db.refresh(doc)
    return DocumentOut.model_validate(doc)


@router.post("/test-search", response_model=list[TestSearchResult])
async def test_search(request: TestSearchRequest):
    return [TestSearchResult(content="开发中", score=0.0, document_name="")]
