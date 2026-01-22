# External Sources + Rate Limit Notes (P3)

## Sources selected
### Weather
- Provider: existing weather source (already implemented)
- Notes: short TTL cache for demo (e.g., 30-60s)

### GitHub (issues/PRs)
- Provider: GitHub REST API
- Notes:
  - Optional: conditional requests / ETag later
  - Cache short TTL to reduce API calls

### News (1 source)
- Provider: RSS feed (no API key)
- Default: BBC World RSS
- Notes:
  - Cache recommended (e.g., 60-300s)
  - Fail-soft: if RSS fails, still return other sources

## Rate limiting strategy (general)
- Add per-source TTL cache to prevent repeated calls during UI refresh.
- Add timeouts and fail-soft behavior:
  - On failure return `sources_failed += [source]` and keep other sources.
- For API-based sources (GitHub):
  - Respect HTTP 403/429 and back off for a TTL window.
