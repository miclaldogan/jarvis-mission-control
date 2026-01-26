# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.x     | :white_check_mark: |

This project is currently in active development (pre-1.0). Security updates will be applied to the `dev` branch and released as needed.

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it privately:

1. **Do NOT open a public issue** for security vulnerabilities
2. Email the maintainers or create a [private security advisory](https://github.com/miclaldogan/jarvis-mission-control/security/advisories/new) on GitHub
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if available)

### Response Timeline
- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Fix Timeline**: Depends on severity:
  - Critical: 1-3 days
  - High: 1-2 weeks
  - Medium/Low: Next release cycle

### Disclosure Policy
- We will acknowledge your report within 48 hours
- We will provide a fix and release timeline
- We will credit you in the release notes (unless you prefer to remain anonymous)
- We will coordinate disclosure timing with you

## Security Best Practices

### For Deployment
- **Environment Variables**: Never commit secrets (API keys, tokens) to version control
- **HTTPS**: Always use HTTPS in production (Let's Encrypt recommended)
- **Rate Limiting**: Configure appropriate limits for public-facing endpoints
- **Redis**: Set a password in production (`requirepass` in redis.conf)
- **CORS**: Restrict `CORS_ALLOWED_ORIGINS` to your frontend domain only

### For Development
- Use `.env.example` as a template; never commit `.env`
- Keep dependencies updated: `pip list --outdated`
- Review Dependabot alerts in the GitHub Security tab

## Known Limitations (Pre-1.0)
- No authentication/authorization (intended for demo/course use)
- Rate limiting is IP-based only (not user-based)
- No input sanitization beyond FastAPI's built-in validation

These will be addressed in future versions as the project matures.

## Contact
For urgent security issues, contact the project maintainers via GitHub or email (see `package.json` or repository settings).
