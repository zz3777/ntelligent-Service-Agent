"""临时文件存储（内存中），用于文件提取场景"""

import uuid
import time
from typing import Tuple

_temp_store: dict[str, Tuple[bytes, str, float]] = {}
TTL_SECONDS = 86400


async def save_temp_file(content: bytes, file_type: str) -> str:
    file_id = uuid.uuid4().hex[:16]
    _temp_store[file_id] = (content, file_type, time.time() + TTL_SECONDS)
    return file_id


async def read_temp_file(file_id: str) -> Tuple[bytes, str] | None:
    entry = _temp_store.get(file_id)
    if entry is None:
        return None
    content, file_type, expires_at = entry
    if time.time() > expires_at:
        del _temp_store[file_id]
        return None
    return content, file_type


def cleanup_expired():
    now = time.time()
    expired = [k for k, v in _temp_store.items() if now > v[2]]
    for k in expired:
        del _temp_store[k]
