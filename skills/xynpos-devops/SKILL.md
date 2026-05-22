---
name: xynpos-devops
description: XynPOS DevOps, infrastructure, and deployment — use when working with Docker, CI/CD pipelines, Terraform, Kubernetes, monitoring, secrets management, or cloud infrastructure for XynPOS. Triggers when someone needs to write a Dockerfile, configure GitHub Actions, setup Kubernetes manifests, troubleshoot deployment issues, manage secrets with Doppler, setup Prometheus/Grafana monitoring, or plan infrastructure changes. Also use for backup strategy, health check configuration, or on-call incident response.
license: See LICENSE.txt
---

# XynPOS DevOps & Infrastructure

## Reference Files
- Current infra topology → `references/infra-topology.md`
- Docker patterns → `references/docker-patterns.md`
- GitHub Actions pipelines → `references/cicd-pipelines.md`
- Kubernetes manifests → `references/k8s-manifests.md`

## Current Stack (Phase 1 — DigitalOcean)

```
Internet
  → Cloudflare (WAF + DDoS + CDN, zero-config SSL)
  → DO Load Balancer (SSL termination)
  → VPS 1: 4vCPU/8GB — Auth, POS, Product services
  → VPS 2: 4vCPU/8GB — Inventory, Report, Payment services
  → DO Managed PostgreSQL 16 (Primary + 1 Standby, SGP region)
  → DO Managed Redis 7
  → Cloudflare R2 (object storage, zero egress fee)

Cost: ~$176/month
Next phase: DOKS (Kubernetes) at ~500+ tenants
```

## Dockerfile Rules

```dockerfile
# ALWAYS multi-stage — never single stage
FROM golang:1.22.3-alpine3.19 AS builder  # ← pin exact version, never :latest
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-w -s" -o /app/bin/service ./cmd/main.go

FROM alpine:3.19.1  # ← pin exact version
RUN addgroup -S app && adduser -S app -G app  # ← non-root WAJIB
WORKDIR /app
COPY --from=builder /app/bin/service .
USER app  # ← never run as root
HEALTHCHECK --interval=30s --timeout=10s CMD wget -qO- http://localhost:${PORT}/health || exit 1
EXPOSE ${PORT}
CMD ["./service"]
```

## Secrets Hierarchy

```
Development  → Doppler → inject to .env.local
Staging      → Doppler project xynpos, config staging
Production   → Doppler project xynpos, config production
CI/CD        → GitHub Secrets: DOPPLER_TOKEN

FORBIDDEN:
  ❌ Secrets in source code
  ❌ Secrets in Dockerfile or docker-compose.yml (committed)
  ❌ Secrets in container ENV in K8s manifests
  ❌ Secrets in log output

Rotation schedule:
  JWT secrets      → 90 days
  DB credentials   → 180 days  
  Payment API keys → on developer offboarding
```

## K8s Required Fields (Phase 2)

Every Deployment MUST have:
```yaml
resources:
  requests: { memory: "128Mi", cpu: "100m" }
  limits:   { memory: "512Mi", cpu: "500m" }
livenessProbe:
  httpGet: { path: /health, port: {PORT} }
  initialDelaySeconds: 30
readinessProbe:
  httpGet: { path: /ready, port: {PORT} }
  initialDelaySeconds: 5
minReplicas: 2  # always HA
```

## Scripts

`scripts/validate_dockerfile.py <path>` — checks Dockerfile for violations.
`scripts/check_k8s.py <path>` — validates K8s manifests against XynPOS rules.
