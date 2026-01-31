# Project Charter: UpDog Monitor

> "What's updog?" — "Not much, what's up with you?"

## Purpose

A web application that monitors URLs for uptime, tracks response times, and alerts when services go down.

Built as a portfolio project to demonstrate full-stack development and SRE practices.

## Goals

1. Learn FastAPI backend development (routes, models, async)
2. Learn React frontend development (components, state, API calls)
3. Learn SRE practices (SLOs, Prometheus metrics, runbooks)
4. Build a clean, well-documented GitHub repo demonstrating best practices
5. Gain confidence to contribute to production codebases

## Non-Goals

- Not a production SaaS — this is for learning
- Not competing with real monitoring tools on features
- Not focused on visual design or polish
- Not supporting multiple users or teams (single user)
- Not optimizing for scale or performance
- Not supporting multiple notification channels (Discord only)

## Principles

1. **Simplicity over features** — Do less, but do it well
2. **Clean commits** — Small, focused, well-messaged
3. **Document as you go** — Don't leave docs for "later"
4. **Understand before copying** — No code you can't explain
5. **Working software over perfect software** — Ship, then improve

## Tech Stack

| Layer | Choice | Why |
|-------|--------|-----|
| Backend | FastAPI | Modern, async, industry standard |
| Database | PostgreSQL | Industry standard |
| ORM | SQLAlchemy (async) | Learn proper data modeling |
| Frontend | React + TypeScript | Most common, good to know |
| Styling | Tailwind CSS | Fast, utility-first |
| Charts | Recharts | Simple React charting library |
| Containers | Docker Compose | Easy local development |
| Metrics | Prometheus | SRE standard |
| Monitoring | Grafana Cloud | Industry standard dashboards |
| Alerting | Discord webhooks | Simple, free |
| Hosting | Railway | Simple PaaS, free tier |
| CI/CD | GitHub Actions | Standard, integrated |

## Milestones

| Version | Status | What's Done |
|---------|--------|-------------|
| 0.1 | Done | Backend API, worker pings URLs, stores results |
| 0.2 | Done | Basic React frontend, view monitors and status |
| 0.3 | Done | History view, simple charts, demo seed script |
| 0.4 | Done | Prometheus /metrics endpoint |
| 0.5 | Done | Docker Compose full stack |
| 0.6 | Done | Alerting (Discord webhook on state change) |
| 0.7 | Done | SLO calculations, error budgets |
| 0.8 | Done | CI/CD with GitHub Actions, test suite |
| 0.9 | Done | Deploy to Railway + Grafana Cloud monitoring |
| 1.0 | Next | Polish, comprehensive testing, documentation |

## Success Criteria

- [x] Clean GitHub repo with professional commit history
- [x] Comprehensive documentation (architecture, guides)
- [x] Working live demo deployed to cloud
- [x] Prometheus metrics with Grafana dashboards
- [ ] Runbooks for common incidents
- [ ] Confidence to discuss SRE practices in interviews

## Links

- **GitHub:** https://github.com/kyle-heller/UpDog-Monitor
- **Live Demo (Frontend):** https://valiant-amazement-production-5a84.up.railway.app
- **Live Demo (API):** https://updog-monitor-production.up.railway.app
- **API Docs:** https://updog-monitor-production.up.railway.app/docs
- **Grafana Dashboard:** Grafana Cloud (kylehellerdev stack)

## Lessons Learned

### Railway Deployment (v0.9)

1. **Vite environment variables are build-time, not runtime**
   - `VITE_*` vars must be in `.env.production` file, not just Railway UI
   - Railway UI env vars are for runtime, Vite bakes vars in at build

2. **Railway internal networking vs public URLs**
   - Internal: `service.railway.internal` (no port needed, HTTP only)
   - Public: `*.up.railway.app` (HTTPS)
   - For cross-service calls, public URLs with CORS are simpler than internal networking

3. **SQLAlchemy datetime handling**
   - Database columns without timezone info need naive datetimes
   - `datetime.utcnow()` (deprecated but works) vs `datetime.now(timezone.utc)` (preferred)
   - Mixing them causes "can't subtract offset-naive and offset-aware datetimes"

4. **Grafana Cloud setup**
   - "Hosted Collector" can scrape public endpoints directly
   - Metrics endpoints should have basic auth for security
   - Dashboard JSON can be version-controlled and imported

### CI/CD (v0.8)

1. **Tests requiring external services (DB) should be skippable in CI**
   - Use pytest markers: `@pytest.mark.db_required`
   - Check `os.environ.get("CI")` to conditionally skip

2. **Ruff linting catches SQLAlchemy issues**
   - `== True` should be `.is_(True)` for SQLAlchemy boolean comparisons
   - Forward references need `TYPE_CHECKING` imports

### General

1. **Keep architecture simple initially**
   - nginx proxy for API calls added complexity; direct API calls with CORS worked fine
   - Don't over-engineer until you hit actual problems

2. **Fictional commit dates for portfolio projects**
   - Use `GIT_AUTHOR_DATE` and `GIT_COMMITTER_DATE` environment variables
   - Both must be set for consistent history
