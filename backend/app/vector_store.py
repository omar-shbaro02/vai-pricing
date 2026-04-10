from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import chromadb
from chromadb.config import Settings

from .schemas import RecommendationRecord, SKURecord


class VectorStore:
    EMBEDDING_DIMENSIONS = 64

    def __init__(self, persist_dir: Path) -> None:
        self.client = chromadb.PersistentClient(
            path=str(persist_dir),
            settings=Settings(anonymized_telemetry=False),
        )
        self._reset_collection_if_needed("skus_collection")
        self._reset_collection_if_needed("recommendations_collection")
        self.skus_collection = self.client.get_or_create_collection("skus_collection")
        self.recommendations_collection = self.client.get_or_create_collection(
            "recommendations_collection"
        )

    @staticmethod
    def _sku_embedding_text(record: SKURecord) -> str:
        return (
            f"{record.product_name} | {record.category} | {record.subcategory} | "
            f"{record.brand} | {record.pack_size}"
        )

    @classmethod
    def _embed_text(cls, text: str) -> list[float]:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        values: list[float] = []
        while len(values) < cls.EMBEDDING_DIMENSIONS:
            for byte in digest:
                values.append((byte / 127.5) - 1.0)
                if len(values) == cls.EMBEDDING_DIMENSIONS:
                    break
            digest = hashlib.sha256(digest).digest()
        return values

    @classmethod
    def _embed_texts(cls, texts: list[str]) -> list[list[float]]:
        return [cls._embed_text(text) for text in texts]

    @staticmethod
    def _sanitize_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
        return {key: value for key, value in metadata.items() if value is not None}

    def _reset_collection_if_needed(self, name: str) -> None:
        try:
            collection = self.client.get_collection(name)
        except Exception:
            return

        try:
            count = collection.count()
            if count == 0:
                return
            sample = collection.get(limit=1, include=["embeddings"])
            embeddings = sample.get("embeddings") or []
            if embeddings and len(embeddings[0]) != self.EMBEDDING_DIMENSIONS:
                self._safe_delete_collection(name)
        except Exception:
            self._safe_delete_collection(name)

    def _safe_delete_collection(self, name: str) -> None:
        try:
            self.client.delete_collection(name)
        except Exception:
            pass

    def seed_skus(self, records: list[SKURecord]) -> None:
        if self.skus_collection.count() > 0:
            return

        documents = [self._sku_embedding_text(record) for record in records]
        self.skus_collection.add(
            ids=[record.sku for record in records],
            documents=documents,
            embeddings=self._embed_texts(documents),
            metadatas=[self._sanitize_metadata(record.model_dump(mode="json")) for record in records],
        )

    def upsert_recommendations(self, recommendations: list[RecommendationRecord]) -> None:
        documents = [rec.reason for rec in recommendations]
        self.recommendations_collection.upsert(
            ids=[rec.sku for rec in recommendations],
            documents=documents,
            embeddings=self._embed_texts(documents),
            metadatas=[self._sanitize_metadata(rec.model_dump(mode="json")) for rec in recommendations],
        )

    def get_reason_context(self, sku: str, fallback_reason: str) -> str:
        result = self.recommendations_collection.get(ids=[sku], include=["documents", "metadatas"])
        if result["ids"]:
            metadata = result["metadatas"][0]
            if metadata and isinstance(metadata, dict):
                return str(metadata.get("reason", fallback_reason))
        return fallback_reason

    def similar_recommendations(self, reason: str, limit: int = 3) -> list[dict[str, Any]]:
        result = self.recommendations_collection.query(
            query_embeddings=[self._embed_text(reason)],
            n_results=limit,
        )
        matches: list[dict[str, Any]] = []
        for docs, metas, ids in zip(
            result.get("documents", [[]]),
            result.get("metadatas", [[]]),
            result.get("ids", [[]]),
        ):
            for doc, meta, sku in zip(docs, metas, ids):
                matches.append({"sku": sku, "reason": doc, "metadata": meta})
        return matches
