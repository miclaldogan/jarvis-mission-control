# API Contract

## Base
- Prefix: `/api/v1`
- Response headers (when applicable): `X-Cache`, `X-Compute-Time-ms`

## Endpoints

### GET /api/v1/health
- Purpose:
- Request:
- Response example:
- Error cases:
- Cache:
- Headers:

### POST /api/v1/context/ingest
- Purpose:
- Request params/body:
- Response example:
- Error cases:
- Cache:
- Headers:

### POST /api/v1/missions/generate
- Purpose:
- Request params/body:
- Response example:
- Error cases:
- Cache:
- Headers:

### GET /api/v1/missions/today
- Purpose:
- Request params:
- Response example:
- Error cases:
- Cache:
- Headers:

### POST /api/v1/missions/complete/{id}
- Purpose:
- Request params/body:
- Response example:
- Error cases:
- Cache:
- Headers:

### POST /api/v1/synthetic/tasks?n=1000000&seed=42
- Purpose:
- Request params:
- Response example:
- Error cases:
- Cache:
- Headers:

### GET /api/v1/reports/mission-load?window=30d&bucket=hour
- Purpose:
- Request params:
- Response example:
- Error cases:
- Cache:
- Headers:
