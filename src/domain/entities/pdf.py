from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Pdf:
    source_id: str
    filename: str
    chunks_count: int
    created_at: datetime
    metadata: Optional[dict] = None