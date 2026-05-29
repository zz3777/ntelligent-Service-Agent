"""RAG 检索封装（ChromaDB）"""

import chromadb
from chromadb.config import Settings as ChromaSettings
from app.core.config import settings

_chroma_client = None


def get_chroma_client():
    global _chroma_client
    if _chroma_client is None:
        _chroma_client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIR,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
    return _chroma_client


async def search_knowledge(query: str, top_k: int = 5) -> list[dict]:
    """在知识库中搜索与 query 相关的内容"""
    try:
        client = get_chroma_client()
        collection = client.get_or_create_collection(name="enterprise_knowledge")
        results = collection.query(query_texts=[query], n_results=top_k)
        documents = []
        for i, doc in enumerate(results["documents"][0]):
            documents.append({
                "content": doc,
                "score": results["distances"][0][i] if results["distances"] else 0,
            })
        return documents
    except Exception as e:
        return [{"content": f"检索失败: {e}", "score": 0}]


async def add_to_knowledgebase(text: str, document_id: str, chunk_index: int):
    """将文本切片添加到知识库"""
    try:
        client = get_chroma_client()
        collection = client.get_or_create_collection(name="enterprise_knowledge")
        collection.add(
            documents=[text],
            ids=[f"{document_id}_{chunk_index}"],
            metadatas=[{"document_id": document_id, "chunk_index": chunk_index}],
        )
        return f"{document_id}_{chunk_index}"
    except Exception as e:
        raise RuntimeError(f"向量化失败: {e}")
