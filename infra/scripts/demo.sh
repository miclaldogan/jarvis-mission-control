#!/usr/bin/env bash
set -euo pipefail

API_BASE_URL="${API_BASE_URL:-http://localhost:8000}"

PASS_COUNT=0
FAIL_COUNT=0

_pass() {
	PASS_COUNT=$((PASS_COUNT + 1))
	echo "PASS: $*"
}

_fail() {
	FAIL_COUNT=$((FAIL_COUNT + 1))
	echo "FAIL: $*" >&2
}

_cleanup() {
	echo
	echo "== Cleanup (docker compose down) =="
	docker compose down >/dev/null 2>&1 || true

	echo
	echo "== Summary =="
	echo "PASS=$PASS_COUNT FAIL=$FAIL_COUNT"

	if [[ "$FAIL_COUNT" -gt 0 ]]; then
		exit 1
	fi
}

trap _cleanup EXIT

echo "== Compose up (build) =="
docker compose up -d --build

# Wait briefly for backend to accept connections
for _ in {1..40}; do
	if curl -fsS "$API_BASE_URL/api/v1/health" >/dev/null 2>&1; then
		break
	fi
	sleep 0.25
done

echo "== Health =="
if curl -fsS "$API_BASE_URL/api/v1/health" >/dev/null; then
	_pass "health endpoint reachable"
else
	_fail "health endpoint not reachable"
fi

curl -is "$API_BASE_URL/api/v1/health" | sed -n '1,25p'

echo
echo "== Request ID example (from /health) =="
REQ_ID_LINE=$(curl -is "$API_BASE_URL/api/v1/health" \
	| awk 'BEGIN{IGNORECASE=1} /^x-request-id:/{gsub("\r","",$0); print; exit}')

if [[ -n "$REQ_ID_LINE" ]]; then
	echo "$REQ_ID_LINE"
	_pass "X-Request-Id header present"
else
	_fail "X-Request-Id header missing"
fi

echo
echo "== Synthetic (MISS) n=100000 seed=42 =="
MISS_HEADERS=$(curl -is "$API_BASE_URL/api/v1/synthetic/tasks?n=100000&seed=42" \
	| awk 'BEGIN{IGNORECASE=1} /^x-cache:|^x-cache-key:|^x-compute-time-ms:/{gsub("\r","",$0); print} /^\{/{exit}')
echo "$MISS_HEADERS"

if echo "$MISS_HEADERS" | grep -qi '^x-cache: MISS'; then
	_pass "cache MISS on first call"
else
	_fail "expected cache MISS on first call"
fi

MISS_CT=$(echo "$MISS_HEADERS" | awk 'BEGIN{IGNORECASE=1} /^x-compute-time-ms:/{print $2; exit}')

echo
echo "== Synthetic (HIT) n=100000 seed=42 =="
HIT_HEADERS=$(curl -is "$API_BASE_URL/api/v1/synthetic/tasks?n=100000&seed=42" \
	| awk 'BEGIN{IGNORECASE=1} /^x-cache:|^x-cache-key:|^x-compute-time-ms:/{gsub("\r","",$0); print} /^\{/{exit}')
echo "$HIT_HEADERS"

if echo "$HIT_HEADERS" | grep -qi '^x-cache: HIT'; then
	_pass "cache HIT on second call"
else
	_fail "expected cache HIT on second call"
fi

HIT_CT=$(echo "$HIT_HEADERS" | awk 'BEGIN{IGNORECASE=1} /^x-compute-time-ms:/{print $2; exit}')

echo
echo "== Compute time comparison (ms) =="
echo "MISS: ${MISS_CT:-unknown}"
echo "HIT:  ${HIT_CT:-unknown}"

if [[ -n "${MISS_CT:-}" && -n "${HIT_CT:-}" ]]; then
	if [[ "$HIT_CT" -le "$MISS_CT" ]]; then
		_pass "HIT compute time <= MISS"
	else
		_fail "HIT compute time > MISS"
	fi
else
	_fail "missing X-Compute-Time-ms"
fi

echo
echo "== Synthetic (MISS; different seed) n=100000 seed=43 =="
SEED_HEADERS=$(curl -is "$API_BASE_URL/api/v1/synthetic/tasks?n=100000&seed=43" \
	| awk 'BEGIN{IGNORECASE=1} /^x-cache:|^x-cache-key:|^x-compute-time-ms:/{gsub("\r","",$0); print} /^\{/{exit}')
echo "$SEED_HEADERS"

if echo "$SEED_HEADERS" | grep -qi '^x-cache: MISS'; then
	_pass "cache MISS when seed changes"
else
	_fail "expected cache MISS when seed changes"
fi

echo
echo "== Report (missions preview) =="
curl -s "$API_BASE_URL/api/v1/report?window=30d&bucket=hour" \
	| sed -n '1,200p'

echo
echo "== Metrics snapshot (after demo) =="
if curl -fsS "$API_BASE_URL/metrics" >/dev/null 2>&1; then
	curl -s "$API_BASE_URL/metrics" \
		| grep -E '^(cache_hits_total|cache_misses_total|synthetic_tasks_generated_total)\b' \
		| sed -n '1,10p'
	_pass "/metrics reachable"
else
	_fail "/metrics not reachable"
fi
