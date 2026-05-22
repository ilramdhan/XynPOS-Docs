---
skill_id: SKILL-05
name: XynPOS DevOps & Infrastructure
category: infrastructure
description: Skill untuk Docker, CI/CD, Terraform, Kubernetes, monitoring, dan secrets management
version: 1.0.0
applies_to: [devops, infrastructure, docker, kubernetes, terraform, cicd]
depends_on: [SKILL-00]
---

# SKILL-05: DevOps & Infrastructure

## Current Infrastructure (Phase 1 — DigitalOcean)

```
Internet → Cloudflare (WAF, DDoS, CDN, DNS)
         → DO Load Balancer (SSL termination)
         → VPS 1: 4vCPU/8GB (Auth, POS, Product)
         → VPS 2: 4vCPU/8GB (Inventory, Report, Payment)
         → DO Managed PostgreSQL 16 (Primary + 1 Standby)
         → DO Managed Redis 7
         → Cloudflare R2 (object storage, zero egress)
         
Kong Gateway: port 8000 (proxy), 8001 (admin)
Total cost Phase 1: ~$176/bulan
```

## Multi-Stage Dockerfile (Go)

```dockerfile
FROM golang:1.22-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-w -s" -o /app/bin/service ./cmd/main.go

FROM alpine:3.19
RUN addgroup -S app && adduser -S app -G app  # ← non-root user
WORKDIR /app
COPY --from=builder /app/bin/service .
COPY --from=builder /app/migrations ./migrations
USER app
HEALTHCHECK --interval=30s --timeout=10s \
  CMD wget -qO- http://localhost:${PORT}/health || exit 1
EXPOSE ${PORT}
CMD ["./service"]
```

## Docker Rules

```dockerfile
# ✅ Pin exact versions
FROM golang:1.22.3-alpine3.19  # ✅
FROM golang:latest              # ❌

# ✅ Non-root user WAJIB
RUN addgroup -S app && adduser -S app -G app
USER app

# ✅ Multi-stage (build ≠ runtime)
# ✅ .dockerignore lengkap (.git, *.env, *_test.go, node_modules/)
# ✅ Healthcheck dikonfigurasi
```

## GitHub Actions CI/CD Pipeline

```yaml
# Stages yang TIDAK BOLEH di-skip:
# PR: lint → test (coverage ≥70%) → security scan → build
# Staging deploy: integration test → build image → push → deploy → smoke test
# Production deploy: manual approval → rolling update → verify

# Key patterns:
jobs:
  test:
    services:
      postgres: {image: postgres:16-alpine}  # real DB untuk integration test
      redis: {image: redis:7-alpine}
    steps:
      - run: golangci-lint run ./...
      - run: go test ./... -coverprofile=coverage.out
      - run: |
          COVERAGE=$(go tool cover -func=coverage.out | grep total | awk '{print $3}' | tr -d '%')
          [ $(echo "$COVERAGE >= 70" | bc) -eq 1 ] || exit 1

  deploy-production:
    environment: production       # ← Manual approval required
    steps:
      - run: docker service update --update-failure-action rollback xynpos_pos-service
```

## Kubernetes Manifests (Phase 2+)

```yaml
# WAJIB ada di setiap Deployment:
containers:
  - name: pos-service
    resources:
      requests: {memory: "128Mi", cpu: "100m"}
      limits:   {memory: "512Mi", cpu: "500m"}
    livenessProbe:
      httpGet: {path: /health, port: 8005}
      initialDelaySeconds: 30
      periodSeconds: 10
    readinessProbe:
      httpGet: {path: /ready, port: 8005}
      initialDelaySeconds: 5
      periodSeconds: 5

# HPA wajib untuk critical services
spec:
  minReplicas: 2   # ← selalu min 2 untuk HA
  maxReplicas: 10
  metrics:
    - type: Resource
      resource: {name: cpu, target: {type: Utilization, averageUtilization: 70}}
```

## Secrets Management

```
Hierarchy:
  Development  → Doppler → inject ke .env.local
  Staging      → Doppler project xynpos, config staging
  Production   → Doppler project xynpos, config production
  CI/CD        → GitHub Secrets (DOPPLER_TOKEN)

TIDAK BOLEH:
  ❌ Secret di source code
  ❌ Secret di Dockerfile atau image
  ❌ Secret di docker-compose.yml yang di-commit
  ❌ Secret di log output

Rotation policy:
  JWT secrets      → 90 hari
  DB credentials   → 180 hari
  Payment API keys → Setelah developer keluar / suspek compromise
  SSH keys         → 1 tahun
```

## Terraform Rules

```hcl
# ✅ Semua resource di Terraform (WAJIB)
# ✅ terraform plan WAJIB review sebelum apply
# ✅ Remote backend untuk state
terraform {
  backend "s3" {
    bucket = "xynpos-terraform-state"
    key    = "production/terraform.tfstate"
  }
}

# ✅ Tagging semua resources
locals {
  common_tags = {
    Project     = "xynpos"
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

# ✅ Database tidak accessible dari internet
resource "digitalocean_database_firewall" "postgres" {
  cluster_id = digitalocean_database_cluster.postgres.id
  rule {
    type  = "droplet"
    value = digitalocean_droplet.app_server_1.id
  }
}
```

## Health Check Endpoints

```go
// Setiap service WAJIB implement:
// GET /health  → liveness (selalu UP jika process berjalan)
// GET /ready   → readiness (DOWN jika dependency tidak ready)
// GET /metrics → Prometheus metrics

func HealthHandler(c *fiber.Ctx) error {
  return c.JSON(fiber.Map{"status": "ok", "service": "pos-service"})
}

func ReadyHandler(c *fiber.Ctx) error {
  checks := map[string]string{}
  if err := db.Ping(); err != nil { checks["database"] = "unhealthy: " + err.Error() }
  else { checks["database"] = "healthy" }
  
  if err := rdb.Ping(ctx).Err(); err != nil { checks["redis"] = "unhealthy" }
  else { checks["redis"] = "healthy" }
  
  for _, v := range checks {
    if strings.HasPrefix(v, "unhealthy") {
      return c.Status(503).JSON(fiber.Map{"status": "not ready", "checks": checks})
    }
  }
  return c.JSON(fiber.Map{"status": "ready", "checks": checks})
}
```

## Monitoring SLOs

```yaml
SLOs:
  pos-service:    {availability: 99.9%, latency_p95: 300ms, error_rate: 0.1%}
  auth-service:   {availability: 99.95%, latency_p95: 200ms}
  payment-service:{availability: 99.9%, latency_p95: 500ms}

# Alert WAJIB punya runbook URL:
annotations:
  runbook_url: "https://github.com/ilramdhan/XynPOS-Docs/blob/main/docs/runbooks/18-operational-runbook.md"
```

## Backup (3-2-1 Rule)

```
3 copies: Primary DB + Daily dump (R2) + Weekly snapshot (different region)
2 media types: Managed DB storage + Object storage
1 offsite: Different provider/region dari primary

Schedule:
  WAL streaming    → Continuous (DO Managed)
  Full dump        → Daily 2AM → R2
  Weekly snapshot  → Sunday 3AM → DO Spaces (region berbeda)
  Monthly archive  → 1st of month 4AM → R2 Cold tier
  
Test restore: Bulanan ke staging environment
```

## Checklist Sebelum Deploy

```
[ ] Docker image pakai multi-stage + non-root user
[ ] Image version pinned (tidak :latest)
[ ] Tidak ada secret di image atau code
[ ] Health + ready endpoints berfungsi
[ ] Resource limits di-set (K8s)
[ ] HPA dikonfigurasi (K8s)
[ ] Backup strategy aktif
[ ] Alert dan runbook sudah siap
[ ] terraform plan di-review (jika infra change)
[ ] Database migration sudah di-test di staging
```
