# XynPOS — Blueprint 23: Development Rules — Infrastructure & DevOps
> Extended Synaptic | Version 1.0 | Mandatory for all Infra/DevOps work

---

## 1. Infrastructure as Code (IaC) Rules

### ✅ WAJIB: Semua Infrastruktur via Terraform

```hcl
# TIDAK BOLEH membuat resource cloud secara manual via console
# Setiap resource HARUS didefinisikan di Terraform

# ✅ BENAR: resource di Terraform
resource "digitalocean_droplet" "app_server_1" {
  name   = "xynpos-app-${var.environment}-1"
  image  = "ubuntu-22-04-x64"
  size   = "s-4vcpu-8gb"
  region = "sgp1"
  
  tags = [
    "xynpos",
    var.environment,
    "app-server",
  ]
  
  # User data untuk initial setup
  user_data = file("scripts/cloud-init.sh")
}

# ❌ JANGAN buat resource manual di DO console tanpa Terraform
# → Resource tersebut tidak ter-track, bisa terhapus/berubah tanpa trace
```

### ✅ WAJIB: State Management Terraform

```hcl
# State disimpan di remote backend (bukan lokal)
terraform {
  backend "s3" {
    bucket = "xynpos-terraform-state"
    key    = "production/terraform.tfstate"
    region = "us-east-1"
    # Atau gunakan Cloudflare R2 yang S3-compatible
  }
  
  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.0"
    }
  }
}

# ✅ Lock state file agar tidak ada concurrent apply
# terraform init -lock=true (default)
```

### ✅ WAJIB: Terraform Plan Review Sebelum Apply

```bash
# WAJIB jalankan plan dulu, review output, baru apply
terraform plan -out=tfplan

# Review output! Perhatikan:
# + = resource baru (aman)
# ~ = update (cek apa yang berubah)
# - = destroy (HATI-HATI! Konfirmasi dulu)

# Apply setelah review
terraform apply tfplan

# ❌ JANGAN langsung apply tanpa plan
terraform apply  # JANGAN — tidak tahu apa yang akan berubah
```

### ✅ WAJIB: Tagging Semua Resources

```hcl
# Semua resource wajib punya tags yang konsisten
locals {
  common_tags = {
    Project     = "xynpos"
    Environment = var.environment
    ManagedBy   = "terraform"
    Owner       = "extended-synaptic"
  }
}

resource "digitalocean_database_cluster" "postgres" {
  name = "xynpos-db-${var.environment}"
  tags = [
    "xynpos",
    var.environment,
    "database",
  ]
}
```

---

## 2. Secrets Management Rules

### ✅ WAJIB: Zero Secrets in Code atau Git

```bash
# Pre-commit hook untuk detect secrets
# Sudah terkonfigurasi di .pre-commit-config.yaml

# Manual scan:
gitleaks detect --source . --verbose

# Jika ada secret yang sudah ter-commit:
# 1. SEGERA rotate secret tersebut
# 2. Hapus dari git history: git filter-branch atau BFG Repo Cleaner
# 3. Force push
# 4. Notifikasi team
```

### ✅ WAJIB: Hierarchy Secret Management

```
Development → .env.local (gitignored, isi dari Doppler)
Staging     → Doppler project "xynpos" config "staging"
Production  → Doppler project "xynpos" config "production"
CI/CD       → GitHub Secrets (referencing Doppler token)

TIDAK BOLEH:
- Secret di .env yang ter-commit
- Secret di Dockerfile
- Secret di docker-compose.yml yang ter-commit
- Secret di kode sumber
- Secret di log
```

### ✅ WAJIB: Secret Rotation Policy

```
JWT secrets         → Rotate setiap 90 hari
DB credentials      → Rotate setiap 180 hari
Payment API keys    → Rotate setelah developer keluar atau suspek compromise
SSH keys            → Rotate setiap 1 tahun atau saat perubahan team
```

---

## 3. Docker Rules

### ✅ WAJIB: Multi-Stage Build untuk Semua Service

```dockerfile
# ✅ BENAR: multi-stage, hasilnya image kecil dan aman
FROM golang:1.22-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-w -s" -o /app/bin/service ./cmd/main.go

FROM alpine:3.19
# ✅ Non-root user
RUN addgroup -S app && adduser -S app -G app
WORKDIR /app
COPY --from=builder /app/bin/service .
COPY --from=builder /app/migrations ./migrations
USER app
HEALTHCHECK --interval=30s --timeout=10s CMD wget -qO- http://localhost:${PORT}/health || exit 1
EXPOSE ${PORT}
CMD ["./service"]

# ❌ JANGAN: single stage, run as root
FROM golang:1.22
WORKDIR /app
COPY . .
RUN go build -o service .
CMD ["./service"]  # Root user, besar image-nya
```

### ✅ WAJIB: .dockerignore yang Lengkap

```dockerignore
# .dockerignore
.git
.env*
.env.local
*.env
*_test.go
**/*_test.go
README.md
docs/
.gitignore
Makefile
*.md
node_modules/
.next/
coverage/
```

### ✅ WAJIB: Pin Image Versions

```dockerfile
# ✅ BENAR: pin exact version
FROM golang:1.22.3-alpine3.19 AS builder
FROM alpine:3.19.1

# ❌ JANGAN: floating tag — bisa berubah kapan saja
FROM golang:latest
FROM alpine:latest
```

---

## 4. Kubernetes Rules (Phase 2+)

### ✅ WAJIB: Resource Requests dan Limits

```yaml
# Setiap container WAJIB ada resource requests dan limits
containers:
  - name: pos-service
    resources:
      requests:         # Minimum yang dijamin tersedia
        memory: "128Mi"
        cpu: "100m"
      limits:           # Maximum yang boleh dipakai
        memory: "512Mi"
        cpu: "500m"

# ❌ JANGAN deploy tanpa resource limits
# → Container bisa makan semua resource dan crash node yang lain
```

### ✅ WAJIB: Liveness dan Readiness Probe

```yaml
livenessProbe:    # Restart container jika ini gagal
  httpGet:
    path: /health
    port: 8005
  initialDelaySeconds: 30
  periodSeconds: 10
  failureThreshold: 3

readinessProbe:   # Remove dari load balancer jika ini gagal
  httpGet:
    path: /ready
    port: 8005
  initialDelaySeconds: 5
  periodSeconds: 5
  failureThreshold: 2

# ⚠️ Bedakan /health (liveness) dan /ready (readiness)
# /health → selalu UP jika process berjalan
# /ready  → DOWN jika dependency (DB, Redis) tidak ready
```

### ✅ WAJIB: Horizontal Pod Autoscaler

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: pos-service-hpa
spec:
  minReplicas: 2        # Selalu minimal 2 untuk HA
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70  # Scale up saat CPU > 70%
```

---

## 5. CI/CD Pipeline Rules

### ✅ WAJIB: Pipeline Stages yang Tidak Boleh Skip

```
Untuk setiap PR:
1. Lint        → WAJIB pass
2. Unit Test   → WAJIB pass, coverage >= 70%
3. Security Scan → govulncheck / npm audit
4. Build       → WAJIB success

Untuk deploy ke staging:
5. Integration Test → WAJIB pass
6. Build Docker Image
7. Push ke registry
8. Deploy ke staging
9. Smoke test (health check endpoints)

Untuk deploy ke production:
10. Manual approval (tidak auto-deploy)
11. Deploy dengan rolling update
12. Verify health checks setelah deploy
```

### ✅ WAJIB: Rollback Otomatis jika Healthcheck Gagal

```yaml
# Docker Swarm
docker service update \
  --rollback-delay 10s \
  --rollback-failure-action rollback \
  --update-failure-action rollback \
  xynpos_pos-service

# Kubernetes
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1
    maxUnavailable: 0      # Zero downtime

# Jika post-deploy healthcheck gagal → otomatis rollback
```

### ✅ WAJIB: Environment Isolation di CI/CD

```yaml
# Setiap environment punya secret sendiri di GitHub
# Staging secrets: STAGING_HOST, STAGING_DB_URL, dll
# Production secrets: PROD_HOST, PROD_DB_URL, dll

# TIDAK BOLEH pakai production credentials di staging pipeline
# TIDAK BOLEH pakai staging credentials di production pipeline
```

---

## 6. Monitoring Rules

### ✅ WAJIB: SLO (Service Level Objectives) per Service

```yaml
# SLO yang harus dipantau:
SLOs:
  pos-service:
    availability: 99.9%        # Error budget: 43 menit/bulan downtime
    latency_p95: 300ms          # 95% request selesai < 300ms
    latency_p99: 1000ms         # 99% request selesai < 1000ms
    error_rate: < 0.1%          # Maksimal 0.1% error rate
  
  auth-service:
    availability: 99.95%
    latency_p95: 200ms
  
  payment-service:
    availability: 99.9%
    latency_p95: 500ms          # Payment bisa sedikit lebih lambat
```

### ✅ WAJIB: Alert yang Actionable

```yaml
# Setiap alert WAJIB ada runbook di BP-18
# Alert tanpa runbook = alert yang tidak bisa di-act

groups:
  - name: pos-service
    rules:
      - alert: PosServiceHighLatency
        expr: histogram_quantile(0.95, http_request_duration_seconds_bucket{job="pos-service"}) > 0.3
        for: 5m
        annotations:
          summary: "POS Service P95 latency > 300ms"
          runbook_url: "https://docs.xynpos.com/runbook#pos-high-latency"  # ← WAJIB ada link runbook
          description: "Current P95: {{ $value }}s"
```

### ✅ WAJIB: Log Retention Policy

```
Development logs → tidak perlu retention
Staging logs     → 7 hari
Production logs  → 90 hari (untuk audit)
Security/Audit logs → 2 tahun (UU PDP requirement)
```

---

## 7. Backup Rules

### ✅ WAJIB: Test Restore Berkala

```bash
# Backup yang tidak pernah di-test = backup yang tidak bisa dipercaya
# Schedule: Test restore ke staging setiap bulan

# Script test restore:
#!/bin/bash
LATEST_BACKUP=$(aws s3 ls s3://xynpos-backups/daily/ | sort -r | head -1 | awk '{print $4}')
aws s3 cp "s3://xynpos-backups/daily/$LATEST_BACKUP" /tmp/

# Restore ke staging database
pg_restore -h staging-db-host -U xynpos -d xynpos_restore /tmp/$LATEST_BACKUP

# Verify: hitung jumlah tenant
COUNT=$(psql -h staging-db-host -U xynpos -d xynpos_restore -t -c \
  "SELECT count(*) FROM public_xyn.tenants;")
echo "Tenants in restored backup: $COUNT"

# Log hasil test
echo "$(date): Backup restore test - $LATEST_BACKUP - Tenants: $COUNT" \
  >> /var/log/backup-tests.log
```

### ✅ WAJIB: 3-2-1 Backup Rule

```
3 copies of data:
  1. Primary database (DigitalOcean Managed DB)
  2. Daily backup di Cloudflare R2
  3. Weekly backup di lokasi berbeda (DO Spaces region berbeda atau AWS S3)

2 different storage types:
  1. Managed database storage
  2. Object storage (R2/S3)

1 offsite copy:
  1. Backup di region/provider berbeda dari primary
```

---

## 8. Security Operations Rules

### ✅ WAJIB: Principle of Least Privilege untuk Semua Akses

```bash
# Service accounts hanya punya permission yang diperlukan
# Contoh: Report service hanya butuh READ ke database

# PostgreSQL: buat user dengan permission minimal
CREATE USER xynpos_report WITH PASSWORD '...';
GRANT CONNECT ON DATABASE xynpos TO xynpos_report;
GRANT USAGE ON SCHEMA tenant_abc123 TO xynpos_report;
GRANT SELECT ON ALL TABLES IN SCHEMA tenant_abc123 TO xynpos_report;
-- Tidak ada INSERT, UPDATE, DELETE untuk report user

# AWS/DO: IAM dengan policy minimal
# Hanya S3 read access untuk service yang butuh baca file
```

### ✅ WAJIB: Tidak Ada Public Database Port

```hcl
# Database TIDAK BOLEH accessible dari internet
resource "digitalocean_database_firewall" "postgres" {
  cluster_id = digitalocean_database_cluster.postgres.id
  
  # Hanya dari app servers
  rule {
    type  = "droplet"
    value = digitalocean_droplet.app_server_1.id
  }
  
  rule {
    type  = "droplet"
    value = digitalocean_droplet.app_server_2.id
  }
  
  # ❌ JANGAN tambahkan "all" atau "0.0.0.0/0"
}
```

---

## 9. Cost Optimization Rules

### ✅ WAJIB: Monitor dan Alert untuk Cost Anomaly

```
Setup budget alert di DigitalOcean:
- Alert jika cost > Rp 3.000.000/bulan (threshold ~170% dari expected)

Audit resource secara bulanan:
[ ] Hapus snapshot yang tidak diperlukan
[ ] Hapus volume yang tidak attached
[ ] Review load balancer yang tidak dipakai
[ ] Audit R2 storage growth
```

### ✅ WAJIB: Auto-scale Down saat Off-Peak

```yaml
# Kubernetes: scale down di luar jam sibuk
# Transaksi POS umumnya ramai 06:00–22:00 WIB
# Bisa scale down services non-kritikal di 22:00–06:00

# CronJob untuk scale down
apiVersion: batch/v1
kind: CronJob
metadata:
  name: scale-down-night
spec:
  schedule: "0 22 * * *"  # 22:00 WIB
  jobTemplate:
    spec:
      template:
        spec:
          containers:
            - name: kubectl
              command:
                - kubectl
                - scale
                - deployment/report-service
                - --replicas=1  # Kurangi dari 3 ke 1 malam hari
```

---

## 10. Infra Code Review Checklist

```
TERRAFORM:
[ ] Semua resource ada di Terraform (tidak ada manual resource)
[ ] terraform plan di-review sebelum apply
[ ] State di remote backend
[ ] Semua resource ada tags

DOCKER:
[ ] Multi-stage build
[ ] Non-root user
[ ] Image version pinned (tidak pakai :latest)
[ ] .dockerignore ada dan lengkap
[ ] Healthcheck dikonfigurasi

KUBERNETES:
[ ] Resource requests dan limits ada
[ ] Liveness dan Readiness probe ada
[ ] HPA dikonfigurasi
[ ] Minimum 2 replicas untuk semua critical service

SECRETS:
[ ] Tidak ada secret di kode atau git
[ ] Rotasi schedule terdokumentasi
[ ] Semua secrets via Doppler/Vault

MONITORING:
[ ] SLO terdefinisi
[ ] Alert ada runbook link
[ ] Log retention policy sesuai

SECURITY:
[ ] Database tidak accessible dari internet
[ ] Least privilege untuk semua service accounts
[ ] Tidak ada port yang unnecessary open
```

---

*Last updated: 2025 | Extended Synaptic — XynPOS*
