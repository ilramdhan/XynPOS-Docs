# XynPOS — Blueprint 18: Operational Runbook
> Extended Synaptic | Version 1.0 | On-Call Reference

---

## Cara Pakai Dokumen Ini

Runbook ini adalah **panduan langkah-demi-langkah** untuk menangani situasi operasional — baik rutin maupun insiden. Saat terjadi masalah di production, buka halaman yang relevan dan ikuti langkah-langkahnya.

**Prinsip:**
- Setiap langkah harus actionable — tidak boleh ada "check the logs" tanpa command spesifik
- Tanda ⚠️ = perlu ekstra hati-hati, bisa berbahaya
- Tanda 🔴 = aksi destructive, konfirmasi dulu
- Selalu dokumentasikan apa yang dilakukan dan hasilnya

---

## 1. Kontak & Eskalasi

| Level | Siapa | Kondisi | Kontak |
|-------|-------|---------|--------|
| L1 | Developer on-call | Alert muncul, service degraded | Slack #incidents |
| L2 | Lead Backend | Service down, data issue | WhatsApp langsung |
| L3 | Founder/CTO | P0 incident, data breach | Telepon |
| External | Xendit Support | Payment gateway issue | support@xendit.co |
| External | DigitalOcean Support | Infrastructure issue | DO support ticket |
| External | Cloudflare Support | CDN/WAF issue | CF support ticket |

---

## 2. Monitoring Dashboards

```
Grafana:     https://monitoring.xynpos.com (admin / vault)
Prometheus:  https://prometheus.xynpos.com
Sentry:      https://sentry.xynpos.com
Uptime:      https://status.xynpos.com
DO Console:  https://cloud.digitalocean.com
```

---

## 3. Runbook: Service Down

### 3.1 Deteksi

Alert: `ServiceDown` di Grafana / SMS dari uptime monitor

### 3.2 Diagnosis

```bash
# 1. Cek status semua container
ssh deploy@<server-ip>
docker ps -a | grep xynpos

# 2. Cek log service yang down
docker logs xynpos-pos-service --tail 100

# 3. Cek apakah service crash loop
docker inspect xynpos-pos-service | grep -A5 '"State"'

# 4. Cek resource server
htop
df -h    # Disk space
free -h  # Memory

# 5. Cek database connectivity
docker exec xynpos-postgres pg_isready -U xynpos
```

### 3.3 Restart Service

```bash
# Restart single service
docker restart xynpos-pos-service

# Verify restart berhasil
docker ps | grep pos-service
curl -f http://localhost:8005/health

# Jika masih gagal, lihat log lebih detail
docker logs xynpos-pos-service --tail 200 --follow
```

### 3.4 Restart Semua Services

```bash
# ⚠️ Hanya jika semua service terdampak
cd /opt/xynpos
docker-compose restart

# Tunggu semua healthy (60-90 detik)
watch docker ps
```

### 3.5 Jika Disk Penuh

```bash
# Cek penggunaan disk
df -h
du -sh /var/lib/docker/

# Bersihkan Docker artifacts yang tidak terpakai
docker system prune -f

# Bersihkan log lama
find /var/log -name "*.log" -mtime +30 -delete

# ⚠️ Jika masih penuh, scale up storage di DO console dulu
```

---

## 4. Runbook: Database Issues

### 4.1 PostgreSQL Down

```bash
# Cek status
docker exec xynpos-postgres pg_isready -U xynpos

# Restart jika perlu
docker restart xynpos-postgres

# Cek log
docker logs xynpos-postgres --tail 50

# Jika managed DB (DigitalOcean):
# → Buka DO console → Databases → Check status
# → Jika primary down, DO auto-failover ke standby (2-3 menit)
```

### 4.2 Koneksi Database Habis (Too Many Connections)

```bash
# Cek jumlah koneksi saat ini
docker exec xynpos-postgres psql -U xynpos -c \
  "SELECT count(*), state FROM pg_stat_activity GROUP BY state;"

# Lihat koneksi per service
docker exec xynpos-postgres psql -U xynpos -c \
  "SELECT application_name, count(*) FROM pg_stat_activity GROUP BY application_name;"

# Kill idle connections yang sudah lama (> 10 menit idle)
docker exec xynpos-postgres psql -U xynpos -c \
  "SELECT pg_terminate_backend(pid) FROM pg_stat_activity 
   WHERE state = 'idle' AND query_start < NOW() - INTERVAL '10 minutes';"

# Restart PgBouncer untuk reset pool
docker restart xynpos-pgbouncer
```

### 4.3 Query Lambat / High CPU Database

```bash
# Lihat query yang sedang berjalan dan lamanya
docker exec xynpos-postgres psql -U xynpos -c \
  "SELECT pid, now() - pg_stat_activity.query_start AS duration, query, state
   FROM pg_stat_activity
   WHERE (now() - pg_stat_activity.query_start) > interval '5 seconds'
   ORDER BY duration DESC;"

# Kill query yang berjalan > 60 detik ⚠️
docker exec xynpos-postgres psql -U xynpos -c \
  "SELECT pg_cancel_backend(pid) FROM pg_stat_activity
   WHERE (now() - query_start) > interval '60 seconds'
   AND state != 'idle';"

# Aktifkan slow query log sementara
docker exec xynpos-postgres psql -U xynpos -c \
  "ALTER SYSTEM SET log_min_duration_statement = '1000';" # log query > 1 detik
docker exec xynpos-postgres psql -U xynpos -c "SELECT pg_reload_conf();"
```

### 4.4 Restore Database dari Backup

```bash
# ⚠️ DESTRUCTIVE — Konfirmasi dengan founder dulu

# 1. List backup yang tersedia
aws s3 ls s3://xynpos-backups/daily/ | sort -r | head -10

# 2. Download backup
aws s3 cp s3://xynpos-backups/daily/postgres_20250101_020000.dump.gz .
gunzip postgres_20250101_020000.dump.gz

# 3. 🔴 Restore (menimpa database existing)
docker exec -i xynpos-postgres pg_restore \
  -U xynpos -d xynpos --clean --if-exists \
  < postgres_20250101_020000.dump

# 4. Verify restore berhasil
docker exec xynpos-postgres psql -U xynpos -c \
  "SELECT count(*) FROM public_xyn.tenants;"
```

---

## 5. Runbook: Payment Issues

### 5.1 QRIS Tidak Berfungsi

```bash
# 1. Cek Xendit status page
curl https://www.xenditstatus.com/api/v2/status.json | python3 -m json.tool

# 2. Cek webhook Xendit sampai ke server
docker logs xynpos-payment-service --tail 50 | grep "webhook"

# 3. Test koneksi ke Xendit API
curl -u xnd_production_YOUR_KEY: \
  https://api.xendit.co/payment_requests \
  -H "Content-Type: application/json"

# 4. Cek apakah webhook URL accessible dari luar
curl -X POST https://api.xynpos.com/v1/webhooks/xendit \
  -H "Content-Type: application/json" \
  -d '{"test": true}'
```

### 5.2 Pembayaran Subscription Gagal Massal

```bash
# Cek log subscription service
docker logs xynpos-subscription-service --tail 100 | grep "payment"

# Cek tabel invoice yang status failed
docker exec xynpos-postgres psql -U xynpos -c \
  "SELECT count(*), status FROM public_xyn.invoices 
   WHERE created_at > NOW() - INTERVAL '1 day'
   GROUP BY status;"

# Jika gateway issue sementara — extend grace period manual
# (via admin panel atau direct DB update setelah diskusi founder)
```

---

## 6. Runbook: High Traffic / Performance Degradation

### 6.1 API Response Lambat

```bash
# Cek p95 response time di Grafana → Dashboard "XynPOS Overview"

# Cek CPU dan memory server
ssh deploy@<server>
top
iostat -x 1 5   # Disk I/O

# Cek service mana yang paling lambat
docker stats --no-stream

# Cek apakah ada N+1 query issue
docker logs xynpos-report-service --tail 100 | grep "slow"

# Scale up container jika CPU tinggi
docker-compose scale pos-service=3
```

### 6.2 Redis Out of Memory

```bash
# Cek memory Redis
docker exec xynpos-redis redis-cli -a $REDIS_PASSWORD info memory | grep used_memory_human

# Cek keys terbanyak
docker exec xynpos-redis redis-cli -a $REDIS_PASSWORD --scan --pattern "*" | wc -l

# Flush specific pattern (cache saja, bukan session) ⚠️
docker exec xynpos-redis redis-cli -a $REDIS_PASSWORD --scan --pattern "cache:*" \
  | xargs docker exec xynpos-redis redis-cli -a $REDIS_PASSWORD del

# Cek TTL key yang tidak ada TTL (memory leak)
docker exec xynpos-redis redis-cli -a $REDIS_PASSWORD \
  --scan --pattern "*" | while read key; do
    ttl=$(docker exec xynpos-redis redis-cli -a $REDIS_PASSWORD ttl "$key")
    if [ "$ttl" = "-1" ]; then echo "No TTL: $key"; fi
  done | head -20
```

---

## 7. Runbook: Deployment

### 7.1 Deploy ke Staging

```bash
# Deploy otomatis via GitHub Actions saat push ke branch staging
# Manual trigger jika perlu:

cd /opt/xynpos
git pull origin staging

# Pull image terbaru
docker-compose pull

# Rolling restart (zero downtime)
docker-compose up -d --no-deps --build pos-service

# Verify
docker logs xynpos-pos-service --tail 20
curl http://localhost:8005/health
```

### 7.2 Deploy ke Production

```bash
# ⚠️ Selalu deploy ke staging dulu dan verify

# 1. Tag release
git tag -a v1.2.3 -m "Release v1.2.3: [deskripsi]"
git push origin v1.2.3

# 2. Monitor deploy di GitHub Actions

# 3. Verify setelah deploy
curl https://api.xynpos.com/health
# Check Grafana — tidak ada spike error rate

# 4. Jika ada masalah → rollback
docker-compose up -d --no-deps --build pos-service:previous-tag
```

### 7.3 Rollback Service

```bash
# Rollback ke image sebelumnya
docker tag ghcr.io/extendedsynaptic/xynpos/pos-service:previous \
           ghcr.io/extendedsynaptic/xynpos/pos-service:rollback

docker-compose up -d --no-deps pos-service

# Verify
curl https://api.xynpos.com/v1/health
```

---

## 8. Runbook: Database Migration

### 8.1 Jalankan Migration untuk Semua Tenant

```bash
# Script migration ke semua tenant schema
#!/bin/bash

DB_URL="postgres://xynpos:$DB_PASSWORD@localhost:5432/xynpos"

# Get semua tenant active
TENANTS=$(psql $DB_URL -t -c \
  "SELECT schema_name FROM public_xyn.tenants WHERE status='active';")

for TENANT in $TENANTS; do
  echo "Migrating $TENANT..."
  migrate -path ./migrations \
    -database "$DB_URL?search_path=$TENANT" up
  
  if [ $? -ne 0 ]; then
    echo "FAILED: $TENANT"
    exit 1
  fi
done

echo "All migrations complete!"
```

### 8.2 Rollback Migration

```bash
# Rollback 1 step untuk semua tenant
for TENANT in $TENANTS; do
  migrate -path ./migrations \
    -database "$DB_URL?search_path=$TENANT" down 1
done
```

---

## 9. Runbook: Security Incidents

### 9.1 Suspect Unauthorized Access

```bash
# Cek login dari IP mencurigakan
docker exec xynpos-postgres psql -U xynpos -c \
  "SELECT actor_ip, count(*) as attempts 
   FROM auth_svc.audit_logs 
   WHERE action = 'auth.login_failed' 
   AND created_at > NOW() - INTERVAL '1 hour'
   GROUP BY actor_ip
   ORDER BY attempts DESC
   LIMIT 20;"

# Block IP di Cloudflare (via CF dashboard atau API)
curl -X POST "https://api.cloudflare.com/client/v4/zones/$CF_ZONE/firewall/rules" \
  -H "Authorization: Bearer $CF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"filter": {"expression": "ip.src eq 1.2.3.4"}, "action": "block"}'

# Force logout semua session untuk user yang dicurigai
docker exec xynpos-redis redis-cli -a $REDIS_PASSWORD \
  --scan --pattern "session:USER_ID:*" \
  | xargs docker exec xynpos-redis redis-cli -a $REDIS_PASSWORD del
```

### 9.2 Suspected Data Breach

```
⚠️ STOP. Hubungi founder SEGERA sebelum langkah apapun.

Langkah setelah koordinasi:
1. Preserve evidence — jangan hapus log
2. Isolasi sistem yang compromised
3. Rotasi semua credentials
4. Assess scope — data apa yang terekspos
5. Notifikasi sesuai UU PDP (< 14 hari ke BSSN)
6. Notifikasi tenant yang terdampak
```

---

## 10. Runbook: Certificate & Domain

### 10.1 SSL Certificate Renewal

```bash
# Cloudflare mengelola SSL secara otomatis
# Jika pakai Let's Encrypt di server:

certbot renew --dry-run  # Test dulu
certbot renew            # Actual renewal

# Reload nginx/caddy setelah renewal
docker exec xynpos-nginx nginx -s reload
```

### 10.2 DNS Update

```
Semua DNS dikelola di Cloudflare Dashboard.
Jangan ubah DNS tanpa diskusi — bisa menyebabkan downtime.

TTL saat akan update DNS: Set ke 60 detik (1 menit) dulu,
baru update, tunggu propagasi, kemudian set kembali ke default (auto).
```

---

## 11. Jadwal Maintenance Rutin

| Frekuensi | Task | Script/Command |
|-----------|------|----------------|
| Harian | Monitor dashboard Grafana | Manual check |
| Harian | Cek backup berhasil | `aws s3 ls s3://xynpos-backups/daily/ | tail -5` |
| Mingguan | Review error log Sentry | Sentry dashboard |
| Mingguan | Update dependency (security only) | `govulncheck ./...` |
| Bulanan | Rotate API keys | Manual di setiap service |
| Bulanan | Review akses user (who has what) | Manual audit |
| Bulanan | Test restore backup | Jalankan di staging |
| Kuartalan | Penetration test | External atau internal |
| Kuartalan | Review dan update runbook ini | Manual |

---

*Runbook ini harus diupdate setiap kali ada perubahan infrastruktur atau prosedur baru.*
*Last updated: 2025 | Extended Synaptic — XynPOS*
