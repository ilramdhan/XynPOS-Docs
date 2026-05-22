# XynPOS — Blueprint 09: Infrastructure & DevOps Blueprint
> Extended Synaptic | Version 1.0 | Confidential

---

## 1. Infrastructure Overview

### Phase 1 (0–500 tenant) — DigitalOcean

```
Internet
    │
    ▼
Cloudflare (DNS + WAF + CDN)
    │
    ▼
DigitalOcean Load Balancer
    │
    ├──▶ VPS 1: App Server (Auth, POS, Product Services)
    ├──▶ VPS 2: App Server (Inventory, Report, Payment Services)
    │
    ├──▶ DO Managed PostgreSQL (Primary + 1 Standby)
    ├──▶ DO Managed Redis
    └──▶ Cloudflare R2 (Object Storage)
```

**Resources Phase 1:**
| Resource | Spec | Cost/month |
|----------|------|-----------|
| VPS 1 (App) | 4 vCPU, 8GB RAM, 80GB SSD | ~$48 |
| VPS 2 (App) | 4 vCPU, 8GB RAM, 80GB SSD | ~$48 |
| Managed PostgreSQL | 2 vCPU, 4GB RAM, 50GB SSD | ~$50 |
| Managed Redis | 1GB | ~$15 |
| Load Balancer | — | ~$12 |
| Cloudflare R2 | 50GB + 10M req | ~$3 |
| **Total** | | **~$176/bulan** |

### Phase 2 (500–10K tenant) — Kubernetes on DO

```
Cloudflare
    │
    ▼
DOKS (DigitalOcean Kubernetes)
├── Node Pool: General (3x 8vCPU/16GB)
├── Node Pool: Database-adjacent (2x 4vCPU/8GB)
│
├── Managed PostgreSQL HA (3 nodes)
├── Managed Redis HA (Sentinel)
└── Cloudflare R2 + backup to DO Spaces
```

---

## 2. Docker Configuration

### 2.1 Multi-Stage Dockerfile for Go Service

```dockerfile
# backend/services/pos-service/Dockerfile

# ---- Build Stage ----
FROM golang:1.22-alpine AS builder

WORKDIR /app

# Install dependencies
COPY go.mod go.sum ./
RUN go mod download

# Copy source
COPY . .

# Build binary
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 \
    go build -ldflags="-w -s" -o /app/bin/pos-service ./cmd/main.go

# ---- Runtime Stage ----
FROM alpine:3.19

# Security: non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

WORKDIR /app

# Copy binary
COPY --from=builder /app/bin/pos-service .

# Copy migrations
COPY --from=builder /app/migrations ./migrations

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget -qO- http://localhost:${PORT}/health || exit 1

USER appuser

EXPOSE ${PORT}

CMD ["./pos-service"]
```

### 2.2 Docker Compose for Local Dev

```yaml
# docker-compose.yml

version: '3.9'

networks:
  xynpos-net:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
  meilisearch_data:

services:

  # ========================
  # INFRASTRUCTURE
  # ========================
  
  postgres:
    image: postgres:16-alpine
    container_name: xynpos-postgres
    networks: [xynpos-net]
    environment:
      POSTGRES_DB: xynpos
      POSTGRES_USER: xynpos
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-dev_password_change_me}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./infra/docker/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U xynpos"]
      interval: 10s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: xynpos-redis
    networks: [xynpos-net]
    command: redis-server --requirepass ${REDIS_PASSWORD:-dev_redis_password}
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]

  nats:
    image: nats:2-alpine
    container_name: xynpos-nats
    networks: [xynpos-net]
    ports:
      - "4222:4222"  # Client
      - "8222:8222"  # Monitoring

  meilisearch:
    image: getmeili/meilisearch:v1.7
    container_name: xynpos-search
    networks: [xynpos-net]
    ports:
      - "7700:7700"
    volumes:
      - meilisearch_data:/meili_data
    environment:
      MEILI_MASTER_KEY: ${MEILI_MASTER_KEY:-dev_master_key}

  # ========================
  # API GATEWAY
  # ========================

  kong:
    image: kong:3.6-alpine
    container_name: xynpos-gateway
    networks: [xynpos-net]
    environment:
      KONG_DATABASE: "off"
      KONG_DECLARATIVE_CONFIG: /etc/kong/kong.yml
      KONG_PROXY_ACCESS_LOG: /dev/stdout
      KONG_ADMIN_ACCESS_LOG: /dev/stdout
      KONG_PROXY_ERROR_LOG: /dev/stderr
      KONG_ADMIN_ERROR_LOG: /dev/stderr
    volumes:
      - ./backend/gateway/kong.yml:/etc/kong/kong.yml
    ports:
      - "8000:8000"   # HTTP proxy
      - "8001:8001"   # Admin API
    healthcheck:
      test: ["CMD", "kong", "health"]
    depends_on:
      - auth-service
      - pos-service

  # ========================
  # BACKEND SERVICES  
  # ========================

  auth-service:
    build:
      context: ./backend/services/auth-service
      dockerfile: Dockerfile
    container_name: xynpos-auth
    networks: [xynpos-net]
    env_file: ./backend/services/auth-service/.env.local
    ports:
      - "8001:8001"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped

  pos-service:
    build:
      context: ./backend/services/pos-service
      dockerfile: Dockerfile
    container_name: xynpos-pos
    networks: [xynpos-net]
    env_file: ./backend/services/pos-service/.env.local
    ports:
      - "8005:8005"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      nats:
        condition: service_started
    restart: unless-stopped

  # ... (similar untuk services lain)

  # ========================
  # FRONTEND
  # ========================

  web-dashboard:
    build:
      context: ./frontend/apps/web-dashboard
    container_name: xynpos-dashboard
    networks: [xynpos-net]
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
    depends_on:
      - kong

  # ========================
  # MONITORING (dev)
  # ========================

  prometheus:
    image: prom/prometheus:latest
    container_name: xynpos-prometheus
    networks: [xynpos-net]
    volumes:
      - ./infra/monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana:latest
    container_name: xynpos-grafana
    networks: [xynpos-net]
    ports:
      - "3001:3000"
    environment:
      GF_SECURITY_ADMIN_PASSWORD: admin
```

---

## 3. CI/CD Pipeline (GitHub Actions)

### 3.1 Backend Service Pipeline

```yaml
# .github/workflows/pos-service.yml

name: POS Service CI/CD

on:
  push:
    branches: [main, staging]
    paths:
      - 'backend/services/pos-service/**'
      - 'backend/shared/**'
  pull_request:
    branches: [main]
    paths:
      - 'backend/services/pos-service/**'

env:
  SERVICE: pos-service
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}/pos-service

jobs:

  # ---- Test & Lint ----
  test:
    name: Test & Lint
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_DB: xynpos_test
          POSTGRES_USER: xynpos
          POSTGRES_PASSWORD: test_password
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-retries 5
      
      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Go
        uses: actions/setup-go@v5
        with:
          go-version: '1.22'
          cache: true
      
      - name: Run linter
        uses: golangci/golangci-lint-action@v4
        with:
          working-directory: backend/services/pos-service
      
      - name: Run tests
        working-directory: backend/services/pos-service
        env:
          DATABASE_URL: postgres://xynpos:test_password@localhost/xynpos_test
          REDIS_URL: redis://localhost:6379
        run: |
          go test ./... -v -race -coverprofile=coverage.out
          go tool cover -func=coverage.out
      
      - name: Check coverage threshold
        run: |
          COVERAGE=$(go tool cover -func=coverage.out | grep total | awk '{print $3}' | sed 's/%//')
          if (( $(echo "$COVERAGE < 70" | bc -l) )); then
            echo "Coverage $COVERAGE% is below 70% threshold"
            exit 1
          fi

  # ---- Build & Push Docker ----
  build:
    name: Build & Push Image
    runs-on: ubuntu-latest
    needs: test
    if: github.event_name == 'push'
    
    permissions:
      contents: read
      packages: write
    
    outputs:
      image: ${{ steps.meta.outputs.tags }}
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Log in to GHCR
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=sha,prefix=sha-
      
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: backend/services/pos-service
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  # ---- Deploy Staging ----
  deploy-staging:
    name: Deploy to Staging
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/staging'
    environment: staging
    
    steps:
      - name: Deploy to staging server
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.STAGING_HOST }}
          username: deploy
          key: ${{ secrets.STAGING_SSH_KEY }}
          script: |
            docker pull ${{ needs.build.outputs.image }}
            docker service update --image ${{ needs.build.outputs.image }} xynpos_pos-service
            echo "Deployed pos-service to staging"

  # ---- Deploy Production ----
  deploy-production:
    name: Deploy to Production
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/main'
    environment: production
    
    steps:
      - name: Deploy to production
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.PROD_HOST }}
          username: deploy
          key: ${{ secrets.PROD_SSH_KEY }}
          script: |
            docker pull ${{ needs.build.outputs.image }}
            # Blue-green deployment
            docker service update --image ${{ needs.build.outputs.image }} \
              --update-parallelism 1 \
              --update-delay 10s \
              xynpos_pos-service
```

### 3.2 Mobile App Pipeline (Flutter)

```yaml
# .github/workflows/mobile-app.yml

name: Flutter Mobile CI/CD

on:
  push:
    branches: [main, staging]
    paths:
      - 'mobile/**'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.22.x'
          channel: stable
      - working-directory: mobile/xynpos_mobile
        run: |
          flutter pub get
          flutter analyze
          flutter test --coverage

  build-android:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      - uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.22.x'
      - name: Setup signing
        run: |
          echo "${{ secrets.KEYSTORE_BASE64 }}" | base64 --decode > mobile/xynpos_mobile/android/app/keystore.jks
      - working-directory: mobile/xynpos_mobile
        run: flutter build appbundle --release
      - name: Upload to Play Store
        uses: r0adkll/upload-google-play@v1
        with:
          serviceAccountJsonPlainText: ${{ secrets.PLAY_SERVICE_ACCOUNT }}
          packageName: com.extendedsynaptic.xynpos
          releaseFiles: mobile/xynpos_mobile/build/app/outputs/bundle/release/*.aab
          track: internal

  build-ios:
    needs: test
    runs-on: macos-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      - uses: subosito/flutter-action@v2
      - working-directory: mobile/xynpos_mobile
        run: flutter build ipa --release
      - name: Upload to TestFlight
        uses: apple-actions/upload-testflight-build@v1
        with:
          app-path: mobile/xynpos_mobile/build/ios/ipa/*.ipa
          issuer-id: ${{ secrets.APPSTORE_ISSUER_ID }}
          api-key-id: ${{ secrets.APPSTORE_KEY_ID }}
          api-private-key: ${{ secrets.APPSTORE_PRIVATE_KEY }}
```

---

## 4. Kubernetes Manifests (Phase 2)

### 4.1 Deployment Example

```yaml
# infra/kubernetes/services/pos-service/deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: pos-service
  namespace: xynpos
  labels:
    app: pos-service
    version: "1.0"
spec:
  replicas: 2
  selector:
    matchLabels:
      app: pos-service
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    metadata:
      labels:
        app: pos-service
    spec:
      containers:
        - name: pos-service
          image: ghcr.io/extendedsynaptic/xynpos/pos-service:latest
          ports:
            - containerPort: 8005
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: xynpos-secrets
                  key: DATABASE_URL
            - name: REDIS_URL
              valueFrom:
                secretKeyRef:
                  name: xynpos-secrets
                  key: REDIS_URL
          resources:
            requests:
              memory: "128Mi"
              cpu: "100m"
            limits:
              memory: "512Mi"
              cpu: "500m"
          livenessProbe:
            httpGet:
              path: /health
              port: 8005
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /ready
              port: 8005
            initialDelaySeconds: 5
            periodSeconds: 5
      imagePullSecrets:
        - name: ghcr-secret

---
apiVersion: v1
kind: Service
metadata:
  name: pos-service
  namespace: xynpos
spec:
  selector:
    app: pos-service
  ports:
    - port: 8005
      targetPort: 8005

---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: pos-service-hpa
  namespace: xynpos
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: pos-service
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
```

---

## 5. Monitoring Stack

### 5.1 Prometheus Config

```yaml
# infra/monitoring/prometheus.yml

global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'xynpos-services'
    static_configs:
      - targets:
          - 'auth-service:8001'
          - 'pos-service:8005'
          - 'product-service:8003'
          # ... all services
    metrics_path: '/metrics'

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']

  - job_name: 'kong'
    static_configs:
      - targets: ['kong:8001']
    metrics_path: '/metrics'
```

### 5.2 Grafana Dashboards yang Dibuat

| Dashboard | Metrik Dipantau |
|-----------|----------------|
| **XynPOS Overview** | Total requests/sec, error rate, response time p95/p99 |
| **Service Health** | Uptime per service, restart count, resource usage |
| **Database** | Query duration, connections, cache hit ratio |
| **Business Metrics** | Transaksi/jam, tenant aktif, MRR (dari app metrics) |
| **Tenant Health** | Per-tenant request volume, error rate |

### 5.3 Alerting Rules

```yaml
# infra/monitoring/alerts.yml

groups:
  - name: xynpos-critical
    rules:
      - alert: ServiceDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service {{ $labels.job }} is DOWN"
          
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Error rate > 5% on {{ $labels.job }}"
          
      - alert: DatabaseConnectionsHigh
        expr: pg_stat_database_numbackends > 80
        for: 2m
        labels:
          severity: warning
          
      - alert: DiskSpaceHigh
        expr: (node_filesystem_size_bytes - node_filesystem_free_bytes) / node_filesystem_size_bytes > 0.85
        for: 5m
        labels:
          severity: critical
```

---

## 6. Backup Strategy

### 6.1 Database Backup

```bash
#!/bin/bash
# infra/scripts/backup-db.sh

DATE=$(date +%Y%m%d_%H%M%S)
S3_BUCKET="s3://xynpos-backups"

# Full backup (daily, 2AM)
pg_dump -Fc -h $DB_HOST -U $DB_USER $DB_NAME | \
  gzip | \
  aws s3 cp - $S3_BUCKET/daily/postgres_$DATE.dump.gz \
  --sse aws:kms

# Retention: Keep 30 daily, 12 monthly, 7 yearly
aws s3 ls $S3_BUCKET/daily/ | \
  sort -r | tail -n +31 | \
  awk '{print $4}' | \
  xargs -I {} aws s3 rm $S3_BUCKET/daily/{}

echo "Backup completed: postgres_$DATE.dump.gz"
```

### 6.2 Backup Schedule

| Jenis | Frekuensi | Retention | Storage |
|-------|-----------|-----------|---------|
| WAL Streaming | Continuous | 7 hari | DO Managed |
| Full Dump | Daily 2AM | 30 hari | R2/S3 |
| Weekly Snapshot | Minggu 3AM | 3 bulan | R2/S3 |
| Monthly Archive | Bulan 1 4AM | 1 tahun | R2 Cold |
| Media files (R2) | Daily incremental | 90 hari | R2 |

---

## 7. Environment Configuration

### 7.1 Environment Variables Template

```bash
# .env.example (template, commit ke repo)
# Copy ke .env.local (gitignored)

# ===== App =====
APP_ENV=development               # development, staging, production
APP_PORT=8005
APP_LOG_LEVEL=debug               # debug, info, warn, error

# ===== Database =====
DATABASE_URL=postgres://xynpos:password@localhost:5432/xynpos?sslmode=disable
DATABASE_MAX_CONNS=25
DATABASE_MIN_CONNS=5

# ===== Redis =====
REDIS_URL=redis://:password@localhost:6379/0

# ===== JWT =====
JWT_ACCESS_SECRET=your_very_long_secret_key_here
JWT_REFRESH_SECRET=another_very_long_secret_key_here
JWT_ACCESS_EXPIRY=15m
JWT_REFRESH_EXPIRY=720h

# ===== NATS =====
NATS_URL=nats://localhost:4222

# ===== Payment Gateways =====
XENDIT_SECRET_KEY=xnd_...
XENDIT_WEBHOOK_TOKEN=...
MIDTRANS_SERVER_KEY=SB-...
MIDTRANS_CLIENT_KEY=SB-...

# ===== Firebase =====
FIREBASE_PROJECT_ID=xynpos-prod
FIREBASE_CREDENTIALS_JSON=path/to/firebase-credentials.json

# ===== Email =====
RESEND_API_KEY=re_...
EMAIL_FROM=noreply@xynpos.com

# ===== Storage =====
R2_ACCOUNT_ID=...
R2_ACCESS_KEY_ID=...
R2_SECRET_ACCESS_KEY=...
R2_BUCKET=xynpos-media
R2_PUBLIC_URL=https://cdn.xynpos.com

# ===== Meilisearch =====
MEILI_HOST=http://localhost:7700
MEILI_MASTER_KEY=...

# ===== Monitoring =====
SENTRY_DSN=https://...@sentry.io/...
```

### 7.2 Secret Management (Doppler)

```bash
# Setup Doppler untuk secret management
doppler setup --project xynpos --config production

# Inject secrets ke Docker run
doppler run -- docker-compose up

# CI/CD: Use DOPPLER_TOKEN secret in GitHub Actions
- name: Inject secrets
  run: doppler run -- ./deploy.sh
  env:
    DOPPLER_TOKEN: ${{ secrets.DOPPLER_TOKEN }}
```

---

## 8. Health Check Standard

Setiap service wajib implement endpoint ini:

```go
// GET /health — Quick check (Kubernetes liveness probe)
func HealthHandler(c *fiber.Ctx) error {
    return c.JSON(fiber.Map{
        "status": "ok",
        "service": "pos-service",
        "version": os.Getenv("APP_VERSION"),
    })
}

// GET /ready — Full dependency check (Kubernetes readiness probe)
func ReadyHandler(c *fiber.Ctx) error {
    checks := map[string]string{}
    
    // Check database
    if err := db.Ping(); err != nil {
        checks["database"] = "unhealthy: " + err.Error()
    } else {
        checks["database"] = "healthy"
    }
    
    // Check Redis
    if err := rdb.Ping(ctx).Err(); err != nil {
        checks["redis"] = "unhealthy"
    } else {
        checks["redis"] = "healthy"
    }
    
    status := "ready"
    httpStatus := 200
    for _, v := range checks {
        if strings.HasPrefix(v, "unhealthy") {
            status = "not ready"
            httpStatus = 503
            break
        }
    }
    
    return c.Status(httpStatus).JSON(fiber.Map{
        "status": status,
        "checks": checks,
    })
}

// GET /metrics — Prometheus metrics
// (auto-exposed by prometheus middleware)
```

---

*Blueprint ini inline dengan: BP-05 (Tech Stack), BP-06 (Architecture), BP-10 (Security)*
*Last updated: 2025 | Extended Synaptic — XynPOS*
