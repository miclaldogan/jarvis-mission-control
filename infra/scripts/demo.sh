#!/usr/bin/env bash
set -euo pipefail

API_BASE_URL="${API_BASE_URL:-http://localhost:8000}"

echo "== Health =="
curl -is "$API_BASE_URL/api/v1/health" | sed -n '1,25p'

echo
echo "== Synthetic (MISS) n=100000 seed=42 =="
curl -is "$API_BASE_URL/api/v1/synthetic/tasks?n=100000&seed=42" \
	| awk 'BEGIN{IGNORECASE=1} /^x-cache:|^x-cache-key:|^x-compute-time-ms:/{print} /^\{/{print; exit}'

echo
echo "== Synthetic (HIT) n=100000 seed=42 =="
curl -is "$API_BASE_URL/api/v1/synthetic/tasks?n=100000&seed=42" \
	| awk 'BEGIN{IGNORECASE=1} /^x-cache:|^x-cache-key:|^x-compute-time-ms:/{print} /^\{/{print; exit}'

echo
echo "== Synthetic (MISS; different seed) n=100000 seed=43 =="
curl -is "$API_BASE_URL/api/v1/synthetic/tasks?n=100000&seed=43" \
	| awk 'BEGIN{IGNORECASE=1} /^x-cache:|^x-cache-key:|^x-compute-time-ms:/{print} /^\{/{print; exit}'

echo
echo "== Report (missions preview) =="
curl -s "$API_BASE_URL/api/v1/report?window=30d&bucket=hour" \
	| sed -n '1,200p'
