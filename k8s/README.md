# Kubernetes Deployment

Kubernetes manifests for deploying UpDog Monitor to a cluster.

## Prerequisites

- Kubernetes cluster (local: k3d/minikube, cloud: AKS/EKS/GKE)
- kubectl configured to point at your cluster
- Container images built and pushed to a registry

## Quick Start

```bash
# Preview what will be applied
kubectl apply -k k8s/ --dry-run=client

# Deploy everything
kubectl apply -k k8s/

# Check status
kubectl get all -n updog
```

## Configuration

**ConfigMap** (`configmap.yaml`): Non-sensitive configuration like port, check interval, and metrics username.

**Secret** (`secret.yaml`): Sensitive values - edit the placeholder values before deploying:
- `DATABASE_URL` - PostgreSQL connection string
- `DISCORD_WEBHOOK_URL` - Discord webhook for alerts
- `METRICS_PASSWORD` - Basic auth password for /metrics
- `APPLICATIONINSIGHTS_CONNECTION_STRING` - Azure Monitor (optional)

## Architecture

| Component | Kind | Replicas |
|-----------|------|----------|
| Backend | Deployment | 2 |
| Frontend | Deployment | 2 |
| PostgreSQL | StatefulSet | 1 |

## Cleanup

```bash
kubectl delete -k k8s/
```
