# DB Schema Draft: tasks / context / reports

## tasks
- id (pk)
- created_at
- payload (json)
- status (enum: queued/running/done/failed)

## context
- id (pk)
- fetched_at
- source (weather/github/news/...)
- data (json)
- ok (bool)
- error (text nullable)

## reports
- id (pk)
- created_at
- window (text)
- metric (text)
- value (float)
- source (nullable)
