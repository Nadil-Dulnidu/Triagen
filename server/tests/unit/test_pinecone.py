"""Unit tests for Pinecone vector store wrapper."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from server.infrastructure.pinecone import PineconeVectorStore


@pytest.mark.asyncio
async def test_pinecone_vector_store_fallback() -> None:
    """Test vector store gracefully handles missing API key or unconfigured index."""
    store = PineconeVectorStore()
    store.get_index = MagicMock(return_value=None)  # type: ignore[method-assign]

    # When no index is available
    count = await store.upsert_vectors([], namespace="test/repo")
    assert count == 0

    results = await store.query_similar([0.1, 0.2], namespace="test/repo")
    assert results == []

    deleted = await store.delete_namespace("test/repo")
    assert not deleted


@pytest.mark.asyncio
async def test_pinecone_vector_store_operations() -> None:
    """Test vector store upsert and query with mock index."""
    store = PineconeVectorStore()
    mock_index = MagicMock()
    mock_index.upsert.return_value = None
    mock_match = MagicMock(id="v-1", score=0.92, metadata={"file": "main.py"})
    mock_index.query.return_value = MagicMock(matches=[mock_match])

    store.get_index = MagicMock(return_value=mock_index)  # type: ignore[method-assign]
    store._client = MagicMock()

    # Test upsert
    upserted = await store.upsert_vectors(
        [{"id": "v-1", "values": [0.1, 0.2], "metadata": {"file": "main.py"}}],
        namespace="org/repo",
    )
    assert upserted == 1
    mock_index.upsert.assert_called_once()

    # Test query
    matches = await store.query_similar([0.1, 0.2], namespace="org/repo", top_k=3)
    assert len(matches) == 1
    assert matches[0]["id"] == "v-1"
    assert matches[0]["score"] == 0.92
