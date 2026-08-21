"""PullSense Server — Agents: Google Vertex AI / GenAI Runner."""

from __future__ import annotations

import json
from typing import Any

from google import genai
from google.genai import types

from server.config import Settings, get_settings
from server.infrastructure import get_logger

logger = get_logger(__name__)

_genai_client: genai.Client | None = None


def get_genai_client(settings: Settings | None = None) -> genai.Client:
    """Initialize or return the cached Google GenAI Client configured for Vertex AI."""
    global _genai_client
    settings = settings or get_settings()

    if _genai_client is None:
        # Configure Vertex AI client using GCP Project ID and Region
        if settings.gcp_project_id:
            _genai_client = genai.Client(
                vertexai=True,
                project=settings.gcp_project_id,
                location=settings.gcp_region,
            )
            logger.info(
                "genai_client_initialized_vertex",
                project=settings.gcp_project_id,
                region=settings.gcp_region,
            )
        else:
            # Fallback to local default / ADC
            _genai_client = genai.Client(vertexai=True)
            logger.info("genai_client_initialized_default_adc")

    return _genai_client


class AgentExecutionResult:
    """Structured result returned by an agent invocation."""

    def __init__(
        self,
        raw_text: str,
        parsed_json: dict[str, Any],
        input_tokens: int = 0,
        output_tokens: int = 0,
        duration_ms: int = 0,
    ) -> None:
        self.raw_text = raw_text
        self.parsed_json = parsed_json
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        self.duration_ms = duration_ms


async def run_gemini_agent(
    model_name: str,
    system_instruction: str,
    user_prompt: str,
    temperature: float = 0.2,
    max_output_tokens: int = 4096,
    settings: Settings | None = None,
) -> AgentExecutionResult:
    """Execute a prompt against Gemini on Vertex AI with JSON response formatting."""
    import time

    client = get_genai_client(settings)
    start_time = time.perf_counter()

    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=temperature,
        max_output_tokens=max_output_tokens,
        response_mime_type="application/json",
    )

    response = await client.aio.models.generate_content(
        model=model_name,
        contents=user_prompt,
        config=config,
    )

    elapsed_ms = int((time.perf_counter() - start_time) * 1000)

    raw_text = response.text or "{}"
    try:
        parsed_json = json.loads(raw_text)
    except json.JSONDecodeError:
        # Fallback if markdown fence was included
        clean_text = raw_text.strip()
        if clean_text.startswith("```"):
            clean_text = clean_text.split("\n", 1)[-1].rsplit("\n", 1)[0].strip()
        parsed_json = json.loads(clean_text)

    input_tokens = 0
    output_tokens = 0
    if response.usage_metadata:
        input_tokens = getattr(response.usage_metadata, "prompt_token_count", 0) or 0
        output_tokens = getattr(response.usage_metadata, "candidates_token_count", 0) or 0

    logger.info(
        "agent_run_completed",
        model=model_name,
        duration_ms=elapsed_ms,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
    )

    return AgentExecutionResult(
        raw_text=raw_text,
        parsed_json=parsed_json,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        duration_ms=elapsed_ms,
    )


async def generate_embeddings(
    texts: list[str] | str,
    model_name: str | None = None,
    settings: Settings | None = None,
) -> list[list[float]]:
    """Generate vector embeddings for input text(s) using Vertex AI."""
    settings = settings or get_settings()
    client = get_genai_client(settings)
    model = model_name or settings.embedding_model

    input_list = [texts] if isinstance(texts, str) else texts
    if not input_list:
        return []

    try:
        embeddings: list[list[float]] = []
        for text in input_list:
            response = await client.aio.models.embed_content(
                model=model,
                contents=text,
            )
            # Extract embedding values
            values: list[float] = []
            if hasattr(response, "embedding") and hasattr(response.embedding, "values"):
                values = list(response.embedding.values)
            elif hasattr(response, "embeddings") and response.embeddings:
                values = list(response.embeddings[0].values)
            embeddings.append(values)

        return embeddings
    except Exception as e:
        logger.warning("generate_embeddings_failed", model=model, error=str(e))
        # Return empty embeddings on error for graceful fallback
        return [[] for _ in input_list]
