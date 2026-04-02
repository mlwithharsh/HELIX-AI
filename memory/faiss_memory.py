from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import faiss
import numpy as np


@dataclass
class MemoryRecord:
    text: str
    emotional_pattern: List[float]
    metadata: Dict[str, object]


class VectorMemoryStore:
    def __init__(self, dimension: int = 64, index_path: str = "memory/faiss.index"):
        self.dimension = dimension
        self.index_path = Path(index_path)
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        self.index = faiss.IndexFlatL2(dimension)
        self.records: List[MemoryRecord] = []

    def _embed(self, text: str) -> np.ndarray:
        vector = np.zeros(self.dimension, dtype=np.float32)
        for index, byte in enumerate(text.encode("utf-8", errors="ignore")):
            vector[index % self.dimension] += float((byte % 29) / 28.0)
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector /= norm
        return vector.reshape(1, -1)

    def add(self, record: MemoryRecord) -> None:
        embedding = self._embed(record.text)
        self.index.add(embedding)
        self.records.append(record)

    def search(self, query_text: str, top_k: int = 3) -> List[MemoryRecord]:
        if self.index.ntotal == 0:
            return []
        distances, indices = self.index.search(self._embed(query_text), top_k)
        matches: List[MemoryRecord] = []
        for idx in indices[0]:
            if idx == -1:
                continue
            matches.append(self.records[int(idx)])
        return matches

    def save(self) -> None:
        faiss.write_index(self.index, str(self.index_path))

    def load(self) -> None:
        if self.index_path.exists():
            self.index = faiss.read_index(str(self.index_path))
