# Report Aggregation Spec (bucket/window)

## Goal
Aggregate signals over time windows for dashboards.

## Windowing
- Supported windows: 1m, 5m, 15m, 1h
- Bucket key: source + metric + window + time_bucket_start

## Example Metrics
- requests_total
- cache_hit_total / cache_miss_total
- cache_hit_ratio = hit / (hit + miss)

## Output
- Stored per window with timestamp
- Used by dashboard/report endpoints
