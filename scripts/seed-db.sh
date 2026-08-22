#!/usr/bin/env bash
# ==============================================================================
# PullSense — Seed Database with Demo PRs, Repositories, and Reviews
# ==============================================================================

API_URL="${API_URL:-http://localhost:8000}"

echo "🌱 Seeding database via ${API_URL}/api/v1/reviews/seed..."

RESPONSE=$(curl -s -X POST "${API_URL}/api/v1/reviews/seed" -H "Content-Type: application/json")

echo "Server response: $RESPONSE"
echo "✅ Database successfully seeded."
