# Mission Generation Rules v1

## Inputs
- latest context snapshot (weather/github/other sources)

## Rules
1. Prefer sources that are available (`sources_ok`)
2. If a source failed, do not block overall mission generation
3. Rank tasks by:
   - freshness of context
   - user priority / tags
4. Fallback to synthetic tasks if all sources unavailable
