# UpDog Monitor - Operational Runbooks

This directory contains operational runbooks for common incidents and scenarios.

## What are Runbooks?

Runbooks are step-by-step guides for responding to operational issues. They help:
- Reduce Mean Time To Resolution (MTTR)
- Enable consistent incident response
- Allow any team member to handle common issues
- Document tribal knowledge

## Available Runbooks

| Runbook | Severity | Description |
|---------|----------|-------------|
| [False Positive DOWN](./false-positive-down.md) | Medium | Monitor shows DOWN but target is actually responding |
| [High Latency](./high-latency.md) | Medium-High | Latency SLO breach or error budget depletion |
| [Database Connection Failure](./database-connection-failure.md) | Critical | UpDog cannot connect to PostgreSQL |

## Runbook Structure

Each runbook follows a consistent structure:

1. **Symptoms** - How to identify this issue
2. **Severity** - Impact level and urgency
3. **Immediate Actions** - First steps to take
4. **Possible Causes** - Root cause investigation
5. **Resolution** - How to fix each cause
6. **Escalation** - When and how to escalate
7. **Prevention** - How to prevent recurrence

## SLO Context

When responding to incidents, consider the SLO impact:

- **Availability SLO**: 99.5% over 30 days (~3.6 hours allowed downtime)
- **Latency SLO**: 95% of checks < 500ms

Check error budget status at: `GET /api/slo/monitors/{id}`

## Contributing

When adding new runbooks:
1. Use the existing structure
2. Include specific commands (not just descriptions)
3. Add to the table above
4. Test the commands before documenting
