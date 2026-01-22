# Demo Plan

1. Start backend (uvicorn)
2. Show `/api/v1/health`
3. Show `/api/v1/context` returns real data:
   - weather: temp + condition
   - github: open_issues + open_prs
4. Repeat `/api/v1/context` to demonstrate caching
5. Explain normalized response schema and partial-failure behavior
