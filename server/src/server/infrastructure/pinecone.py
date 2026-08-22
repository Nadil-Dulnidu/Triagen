"""PullSense Server — Infrastructure: Pinecone vector database integration."""

from __future__ import annotations

from typing import Any

from server.config import Settings, get_settings
from server.infrastructure import get_logger

logger = get_logger(__name__)

# Global Pinecone client cache
_pinecone_client: Any = None


def get_pinecone_client(settings: Settings | None = None) -> Any | None:
    """Get or initialize the Pinecone client singleton."""
    global _pinecone_client
    if _pinecone_client is not None:
        return _pinecone_client

    settings = settings or get_settings()
    if not settings.pinecone_api_key:
        logger.debug("pinecone_api_key_not_configured")
        return None

    try:
        from pinecone import Pinecone

        _pinecone_client = Pinecone(api_key=settings.pinecone_api_key)
        logger.info("pinecone_client_initialized")
        return _pinecone_client
    except Exception as e:
        logger.warning("pinecone_init_failed", error=str(e))
        return None


class PineconeVectorStore:
    """Vector storage and similarity search wrapper for Pinecone."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.index_name = self.settings.pinecone_index_name
        self._client = get_pinecone_client(self.settings)

    @property
    def is_available(self) -> bool:
        """Check if Pinecone client is configured and available."""
        return self._client is not None

    def get_index(self) -> Any | None:
        """Get the Pinecone Index handle."""
        if not self.is_available:
            return None
        try:
            return self._client.Index(self.index_name)
        except Exception as e:
            logger.warning("pinecone_get_index_failed", index=self.index_name, error=str(e))
            return None

    async def upsert_vectors(
        self,
        vectors: list[dict[str, Any]],
        namespace: str,
    ) -> int:
        """Upsert a list of vector records into a given namespace.

        vectors: list of dicts with keys: `id`, `values` (float vector), `metadata` (dict)
        """
        index = self.get_index()
        if not index:
            logger.debug("pinecone_upsert_skipped_no_index")
            return 0

        try:
            index.upsert(vectors=vectors, namespace=namespace)
            logger.info("pinecone_vectors_upserted", count=len(vectors), namespace=namespace)
            return len(vectors)
        except Exception as e:
            logger.error("pinecone_upsert_error", namespace=namespace, error=str(e))
            return 0

    async def query_similar(
        self,
        vector: list[float],
        namespace: str,
        top_k: int = 5,
        filter_metadata: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Query top-K most similar vectors within a namespace."""
        index = self.get_index()
        if not index:
            return []

        try:
            query_kwargs: dict[str, Any] = {
                "vector": vector,
                "top_k": top_k,
                "namespace": namespace,
                "include_metadata": True,
            }
            if filter_metadata:
                query_kwargs["filter"] = filter_metadata

            response = index.query(**query_kwargs)
            matches = []
            for match in getattr(response, "matches", []):
                matches.append(
                    {
                        "id": match.id,
                        "score": match.score,
                        "metadata": match.metadata,
                    }
                )
            return matches
        except Exception as e:
            logger.warning("pinecone_query_failed", namespace=namespace, error=str(e))
            return []

    async def delete_namespace(self, namespace: str) -> bool:
        """Delete all vectors in a namespace."""
        index = self.get_index()
        if not index:
            return False

        try:
            index.delete(delete_all=True, namespace=namespace)
            logger.info("pinecone_namespace_deleted", namespace=namespace)
            return True
        except Exception as e:
            logger.warning("pinecone_delete_namespace_failed", namespace=namespace, error=str(e))
            return False
