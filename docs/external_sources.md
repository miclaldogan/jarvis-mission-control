# External Sources & Rate Limit Notes

This document lists the external data sources used by Jarvis Mission Control,
along with authentication, rate limit considerations, and demo-related notes.

---

## Weather Source

- **Provider:** Open-Meteo
- **Endpoint:** https://api.open-meteo.com
- **Authentication:** None (public API)
- **Rate Limit:** No strict documented limit (fair-use based)
- **Data Used:**
  - Current temperature
  - Weather condition code
- **Reason for Selection:**
  - Free and no API key required
  - Stable and simple for demos
  - Suitable for real-time context ingestion
- **Demo Risk Notes:**
  - Minimal risk; public endpoint
  - If unavailable, weather context can be skipped without breaking the system

---

## GitHub Source

- **Provider:** GitHub REST API
- **Endpoints:**
  - /repos/{owner}/{repo}/issues
  - /repos/{owner}/{repo}/pulls
- **Authentication:** Optional (via `GITHUB_TOKEN`)
- **Rate Limits:**
  - **Unauthenticated:** 60 requests/hour
  - **Authenticated:** 5,000 requests/hour
- **Data Used:**
  - Open issues count
  - Open pull requests count
- **Reason for Selection:**
  - Direct integration with the project repository
  - Clear numerical signals for workload estimation
- **Demo Risk Notes:**
  - Without token, rate limit is low
  - For live demos, `GITHUB_TOKEN` is recommended
  - Fallback: reuse last successful snapshot

---

## News Source

- **Provider:** Hacker News (Algolia API)
- **Endpoint:** https://hn.algolia.com/api/v1/search
- **Authentication:** None
- **Rate Limit:** Not strictly enforced (fair use)
- **Data Used:**
  - Title
  - URL
  - Source identifier
- **Reason for Selection:**
  - No API key required
  - Technology-focused content
  - Suitable for AI / regulation / engineering news signals
- **Demo Risk Notes:**
  - Public API, generally reliable
  - If unavailable, news context can be omitted gracefully

---

## General Notes

- All external sources are treated as **soft dependencies**
- Failure of a single source must not block the mission generation pipeline
- Context ingestion is designed to be:
  - Best-effort
  - Fault-tolerant
  - Snapshot-based for demo stability
