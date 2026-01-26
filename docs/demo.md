# Demo (curl + cache proof)

## Prereq
- Backend running on http://127.0.0.1:8000

## 1) Health
curl http://127.0.0.1:8000/api/v1/health

## 2) Context (first call)
curl http://127.0.0.1:8000/api/v1/context

## 3) Context (second call)
curl http://127.0.0.1:8000/api/v1/context

## Expected
- Response includes `data.sources_ok` with `weather`, `github`
- Second call should be faster / should show cache behavior if enabled
