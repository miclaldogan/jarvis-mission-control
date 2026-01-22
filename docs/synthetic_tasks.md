# Synthetic Tasks Generator Spec (100k / 1M)

## Goal
Generate deterministic synthetic tasks for load/caching tests.

## Requirements
- Deterministic seed
- Configurable task count: 100k, 1M
- Payload strategy supports:
  - repeated keys (to trigger cache hits)
  - random keys (to trigger cache misses)

## Output
- JSONL preferred
- Each row: { id, created_at, payload }
