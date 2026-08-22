#!/usr/bin/env bash
# ==============================================================================
# PullSense — OpenAPI JSON Spec Export and Schema Generator
# ==============================================================================

set -e

echo "📄 Exporting FastAPI OpenAPI schema..."

cd server
uv run python -c "
import json
from server.main import create_app
from fastapi.openapi.utils import get_openapi

app = create_app()
schema = get_openapi(
    title=app.title,
    version=app.version,
    openapi_version=app.openapi_version,
    description=app.description,
    routes=app.routes,
)
with open('../client/openapi.json', 'w') as f:
    json.dump(schema, f, indent=2)
print('✅ Saved schema to client/openapi.json')
"

echo "🎉 OpenAPI sync complete."
