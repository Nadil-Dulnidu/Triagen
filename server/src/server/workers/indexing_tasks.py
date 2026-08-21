"""PullSense Server — Workers: Background Celery tasks for codebase vector indexing."""

from __future__ import annotations

import asyncio
import uuid
from typing import Any

from sqlalchemy import select

from server.domains.agents.runner import generate_embeddings
from server.domains.github.client import GitHubClient
from server.domains.reviews.models import Repository
from server.infrastructure import get_logger
from server.infrastructure.celery_app import celery_app
from server.infrastructure.database import create_engine, create_session_factory
from server.infrastructure.pinecone import PineconeVectorStore

logger = get_logger(__name__)


def _run_async(coro: Any) -> Any:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(
    name="server.workers.indexing_tasks.index_repository_codebase",
    max_retries=2,
)
def index_repository_codebase(
    repository_id: str,
    installation_id: int,
    file_paths: list[str] | None = None,
) -> dict[str, Any]:
    """Celery background task to embed and index repository source code into Pinecone."""
    return _run_async(_execute_indexing(repository_id, installation_id, file_paths))


async def _execute_indexing(
    repository_id: str,
    installation_id: int,
    file_paths: list[str] | None = None,
) -> dict[str, Any]:
    engine = create_engine()
    session_factory = create_session_factory(engine)

    async with session_factory() as session:
        stmt = select(Repository).where(Repository.id == repository_id)
        result = await session.execute(stmt)
        repo = result.scalar_one_or_none()

        if not repo:
            return {"status": "error", "message": "Repository not found"}

        owner, repo_name = repo.full_name.split("/", 1)
        gh_client = GitHubClient(installation_id)
        vector_store = PineconeVectorStore()

        if not vector_store.is_available:
            logger.info("pinecone_not_configured_skipping_indexing")
            return {"status": "skipped", "message": "Pinecone not configured"}

        target_paths = file_paths or []
        vectors_to_upsert: list[dict[str, Any]] = []

        for path in target_paths:
            content = await gh_client.get_file_content(owner, repo_name, path)
            if not content or len(content) > 50000:
                continue

            # Split file into logical chunks (e.g. 500-char chunks with overlap)
            chunk_size = 800
            overlap = 100
            chunks = []
            for i in range(0, len(content), chunk_size - overlap):
                chunk = content[i : i + chunk_size].strip()
                if chunk:
                    chunks.append(chunk)

            if not chunks:
                continue

            embeddings = await generate_embeddings(chunks)
            for idx, (chunk_text, embedding) in enumerate(zip(chunks, embeddings, strict=False)):
                if not embedding:
                    continue
                vectors_to_upsert.append(
                    {
                        "id": f"{repo.id}_{uuid.uuid5(uuid.NAMESPACE_DNS, f'{path}_{idx}')}",
                        "values": embedding,
                        "metadata": {
                            "org_id": repo.organization_id,
                            "repo_id": repo.id,
                            "file_path": path,
                            "chunk_index": idx,
                            "text": chunk_text[:500],
                        },
                    }
                )

        namespace = f"{repo.organization_id}/{repo.id}"
        upserted_count = await vector_store.upsert_vectors(vectors_to_upsert, namespace=namespace)

        logger.info(
            "repository_codebase_indexed",
            repo=repo.full_name,
            files_indexed=len(target_paths),
            vectors_upserted=upserted_count,
        )

        return {
            "status": "success",
            "files_indexed": len(target_paths),
            "vectors_upserted": upserted_count,
        }
