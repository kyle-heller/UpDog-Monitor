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
| Frontend | React | Most common, good to know |
| Styling | Tailwind CSS | Fast, utility-first |
| Containers | Docker Compose | Easy local development |
| Metrics | Prometheus | SRE standard |
| Alerting | Discord webhooks | Simple, free |
| Orchestration | Kubernetes (k3d locally, AKS for prod) | Industry standard |

## Milestones

| Version | What's Done |
|---------|-------------|
| 0.1 | Backend API, worker pings URLs, stores results |
| 0.2 | Basic React frontend, view monitors and status |
| 0.3 | History view, simple charts |
| 0.4 | Prometheus /metrics endpoint |
| 0.5 | Docker Compose full stack |
| 0.6 | Alerting (Discord webhook) |
| 0.7 | Auth (login, user accounts) |
| 0.8 | Local Kubernetes (k3d) + Helm chart |
| 0.9 | SLO dashboard, runbooks, chaos testing |
| 1.0 | Azure AKS deployment (live demo) |

## Success Criteria

- Clean GitHub repo with professional commit history
- Comprehensive documentation (architecture, guides, runbooks)
- Working live demo deployed on Azure AKS
- Confidence to contribute to production codebases

## Links

- GitHub: `https://github.com/[username]/updog-monitor`
- Live Demo: (TBD — Azure AKS)
