# UpDog Monitor Documentation

## Overview

- [Project Charter](./PROJECT_CHARTER.md) — Goals, scope, milestones, tech stack, lessons learned

## Architecture

- [Overview](./architecture/overview.md) — System design, component diagram, data flows
- [Data Model](./architecture/data-model.md) — Database schema and SQLAlchemy models

## Guides

- [Local Development](./guides/local-development.md) — Setting up and running locally

## Reference

- [API Docs (Swagger)](https://updog-monitor-production.up.railway.app/docs) — Interactive API documentation
- [Grafana Dashboard](../grafana-dashboard.json) — Importable dashboard JSON

## Live Demo

| Service | URL |
|---------|-----|
| Frontend | https://valiant-amazement-production-5a84.up.railway.app |
| Backend API | https://updog-monitor-production.up.railway.app |
| API Docs | https://updog-monitor-production.up.railway.app/docs |

## Version History

| Version | Highlights |
|---------|------------|
| 0.9 | Railway deployment, Grafana Cloud monitoring |
| 0.8 | GitHub Actions CI/CD, test suite |
| 0.7 | SLO calculations, error budgets |
| 0.6 | Discord webhook alerts |
| 0.5 | Docker Compose full stack |
| 0.4 | Prometheus /metrics endpoint |
| 0.3 | Charts, demo seed script |
| 0.2 | React frontend |
| 0.1 | Backend API, background worker |
