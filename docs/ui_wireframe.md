\# P3 UI Wireframe — dashboard / context / lab



This document describes the UI page list, navigation, per-page data needs, and cache badge behavior for Jarvis Mission Control.



\## Goals (Acceptance Criteria)

\- Page list + navigation described

\- Per-page data needed listed

\- Cache badge behavior described



---



\## 1) Page list + navigation



\### Global navigation (top nav or left sidebar)

\- \*\*Dashboard\*\* → `/dashboard` (default)

\- \*\*Context\*\* → `/context`

\- \*\*Lab\*\* → `/lab`



Optional nav items (later):

\- Docs → `/docs` (link to repo docs)

\- API → `/api` (link to OpenAPI swagger if added)



\*\*Default route\*\*

\- `/` redirects to `/dashboard`



---



\## 2) Pages



\## A) Dashboard — `/dashboard`



\### Purpose

Quick system overview: latest context snapshot summary + cache status.



\### Wireframe (rough)

\- Header: "Jarvis Mission Control"

\- Row of cards:

&nbsp; - Weather card

&nbsp; - GitHub card

&nbsp; - News card

\- Footer/metadata:

&nbsp; - Observed/fetched timestamp

&nbsp; - Sources ok / failed counts

\- Cache badge (HIT/MISS) shown when page triggers any cached endpoint (see Cache section)



\### Data needed (API + fields)

Primary API:

\- `GET /api/v1/context`



Use:

\- `data.fetched\_at`

\- `data.weather` (summary view)

&nbsp; - `city`, `temp\_c`, `condition` (show "N/A" if null)

\- `data.github` (summary view)

&nbsp; - `owner`, `repo`, `open\_issues`, `open\_prs` (show "N/A" if null)

\- `data.news` (summary view)

&nbsp; - show first 3 items: `title`, `url`

\- `data.sources\_ok` (display pills/tags)

\- `data.sources\_failed` (display error count + expandable details)



Empty/failure states:

\- If `weather` is null → show "Weather unavailable"

\- If `github` is null → show "GitHub unavailable"

\- If `news` is empty → show "No news" (or "News unavailable")

\- If `sources\_failed` not empty → show warning banner (non-blocking)



---



\## B) Context — `/context`



\### Purpose

Detailed inspection of the normalized context schema returned from `/api/v1/context`.



\### Wireframe (rough)

\- Page title: "Context"

\- Sections:

&nbsp; - Weather (card)

&nbsp; - GitHub (card)

&nbsp; - News (list)

&nbsp; - Source health (two lists: OK / Failed)



\### Data needed (API + fields)

Primary API:

\- `GET /api/v1/context`



Display:

\- `data.fetched\_at`

\- `data.weather`

&nbsp; - `city`, `lat`, `lon`, `tz`, `temp\_c`, `condition`

\- `data.github`

&nbsp; - `owner`, `repo`, `open\_issues`, `open\_prs`

\- `data.news\[]`

&nbsp; - `title`, `url`

\- `data.sources\_ok\[]`

\- `data.sources\_failed\[]`

&nbsp; - `source`, `error`



UX rules:

\- Use "N/A" for missing fields

\- If a section is null/empty, still render the section with a clear "unavailable" state

\- Failed source errors should be visible but collapsible (accordion)



---



\## C) Lab — `/lab`



\### Purpose

Playground for synthetic task generation + demonstrate cache HIT/MISS behavior.



\### Wireframe (rough)

\- Page title: "Lab"

\- Form (left/top):

&nbsp; - Input: `n` (default 1000, max per API contract)

&nbsp; - Input: `seed` (optional; default empty)

&nbsp; - Button: "Generate"

\- Result (right/below):

&nbsp; - Cache badge: HIT/MISS

&nbsp; - Compute time: X-Compute-Time-ms (if present)

&nbsp; - Response preview (first 20 rows or summary)

&nbsp; - Error panel (if response ok=false)



\### Data needed (API + fields)

Primary API:

\- `GET /api/v1/synthetic/tasks?n=<int>\&seed=<int?>`



Display:

\- Response envelope:

&nbsp; - `ok`, `data`, `meta.request\_id`, `meta.ts`, `error` (if any)

\- Cache headers (if present):

&nbsp; - `X-Cache` (HIT/MISS)

&nbsp; - `X-Compute-Time-ms`

&nbsp; - optional: `X-Cache-Key`



UX rules:

\- If request fails (ok=false) show error banner with `error.code` and `error.message`

\- If `data` is large, render a compact preview + "download" later (optional future)



---



\## 3) Cache badge behavior (MUST)



\### Scope (for this sprint)

Cache badge behavior must be implemented for:

\- `GET /api/v1/synthetic/tasks`



\### Rules

\- First request with a specific param set `(n, seed)`:

&nbsp; - Badge: \*\*MISS\*\*

&nbsp; - Compute time should be visible (header or derived)

\- Second request with the same `(n, seed)` within TTL:

&nbsp; - Badge: \*\*HIT\*\*

\- Change any parameter (e.g., seed changes):

&nbsp; - Badge returns to \*\*MISS\*\*

\- If headers are missing, badge should show "Unknown" (neutral state)



\### Visual suggestions

\- HIT: green pill "HIT"

\- MISS: yellow pill "MISS"

\- UNKNOWN: gray pill "—"



---



\## 4) Notes / Non-goals

\- This document defines UI shape and data needs; implementation may vary.

\- Any new endpoints or fields beyond the v1 contract must update `docs/api\_contract.md`.



