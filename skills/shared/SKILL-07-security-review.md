---
skill_id: SKILL-07
name: XynPOS Security Review
category: shared
description: Skill untuk code review keamanan, security audit, dan UU PDP compliance
version: 1.0.0
applies_to: [security, review, compliance, privacy]
depends_on: [SKILL-00]
---

# SKILL-07: Security Review

## Threat Model (STRIDE)

| Threat | Contoh Serangan | Mitigasi |
|--------|-----------------|---------|
| Spoofing | JWT palsu, impersonate tenant | JWT RS256 signature, short expiry |
| Tampering | Modifikasi amount in-transit | HTTPS/TLS, request signing |
| Repudiation | Klaim tidak pernah transaksi | Immutable audit log |
| Info Disclosure | Data tenant A bocor ke tenant B | Schema isolation, RLS |
| DoS | Flood API → server down | Rate limiting, Cloudflare |
| Privilege Escalation | Kasir akses laporan owner | RBAC granular per endpoint |

## Critical Security Rules

### 1. Tenant Isolation (PALING KRITIS)

```go
// ✅ tenantID SELALU dari JWT
tenantID := c.Locals("tenantID").(string)  // dari middleware

// ❌ TIDAK PERNAH dari request
tenantID := c.Query("tenant_id")   // SANGAT BERBAHAYA
tenantID := req.TenantID           // SANGAT BERBAHAYA

// ✅ search_path dari sanitized tenantID
schemaName := "tenant_" + tenantID
if !regexp.MustCompile(`^tenant_[a-z0-9\-]{8,}$`).MatchString(schemaName) {
    return ErrInvalidTenant
}
```

### 2. SQL Injection Prevention

```go
// ❌ TIDAK PERNAH string concatenation untuk SQL
db.Exec("SELECT * FROM products WHERE name = '" + name + "'") // SQL INJECTION!

// ✅ Selalu parameterized
db.Where("name ILIKE ?", "%"+name+"%").Find(&products)
db.Raw("SELECT * FROM products WHERE id = ?", id).Scan(&p)
```

### 3. JWT Security

```go
// Access token: 15 menit, RS256
// Refresh token: 30 hari, stored hash di Redis
// Token rotation: setiap refresh → token lama direvoke
// Reuse detection via token_family

// Refresh token reuse attack:
// Jika token yang sudah di-rotate dipakai lagi →
// Revoke SEMUA token dalam family + force logout semua device
```

### 4. Rate Limiting per Plan

```
Free:     10 req/min global, 60 tx/min POS
Starter:  100 req/min, 300 tx/min POS
Pro:      500 req/min, 1500 tx/min POS
Business: 2000 req/min, 6000 tx/min POS

Auth endpoints (anti-brute force):
  POST /auth/login:           5 attempts / 15 menit → block 1 jam
  POST /auth/forgot-password: 3 attempts / 1 jam → block 24 jam
```

### 5. Input Validation

```go
// Semua input WAJIB divalidasi sebelum diproses
type CreateProductRequest struct {
    Name  string  `validate:"required,min=1,max=255"`
    Price float64 `validate:"required,min=0.01,max=999999999"`
    SKU   string  `validate:"omitempty,alphanum,max=100"`
}

// File upload: validate dari magic bytes, BUKAN dari Content-Type header
buf := make([]byte, 512)
file.Read(buf)
mimeType := http.DetectContentType(buf)
if !slices.Contains([]string{"image/jpeg","image/png","image/webp"}, mimeType) {
    return ErrInvalidFileType
}
```

### 6. Logging — No Sensitive Data

```go
// ❌ JANGAN log data sensitif
logger.Info("login attempt", zap.String("password", password))     // JANGAN!
logger.Info("payment", zap.String("card_number", cardNum))          // JANGAN!
logger.Info("user", zap.String("npwp", user.NPWP))                  // JANGAN!

// ✅ Mask atau exclude
logger.Info("login attempt",
    zap.String("email", maskEmail(email)),   // j***@example.com
    zap.String("ip", clientIP),
)
```

### 7. Security Headers

```go
app.Use(helmet.New(helmet.Config{
    ContentSecurityPolicy:   "default-src 'self'",
    XContentTypeOptions:     "nosniff",
    XFrameOptions:           "DENY",
    ReferrerPolicy:          "no-referrer",
}))

// CORS: whitelist specific origins
AllowOrigins: "https://app.xynpos.com,https://pos.xynpos.com"
```

### 8. Webhook Validation

```go
// WAJIB validate signature dari payment gateway
func ValidateXenditWebhook(body []byte, signature string) bool {
    expected := hmac.New(sha256.New, []byte(os.Getenv("XENDIT_WEBHOOK_TOKEN")))
    expected.Write(body)
    return hmac.Equal([]byte(signature), []byte(hex.EncodeToString(expected.Sum(nil))))
}
// Jika signature tidak valid → return 401, log attempt
```

## UU PDP Compliance Checklist

```
[ ] Privacy Policy mencakup: data collected, purpose, retention, rights
[ ] Consent saat registrasi (checkbox + timestamp disimpan)
[ ] Right to erasure: DELETE /v1/customers/:id/erase → anonymize PII
[ ] Right to access: GET /v1/my-data → export semua data
[ ] Data enkripsi at-rest untuk: NPWP, nomor kartu (via tokenization)
[ ] Audit log untuk semua aksi sensitif (immutable)
[ ] Breach notification plan: < 14 hari ke BSSN, < 72 jam ke subjek
[ ] Tidak menjual data ke pihak ketiga
[ ] Data retention policy diimplementasikan
```

## Audit Log — Events yang WAJIB Di-log

```go
// Semua event ini WAJIB masuk audit_service:
var criticalEvents = []string{
    "auth.login", "auth.logout", "auth.login_failed", "auth.password_changed",
    "transaction.voided", "transaction.refunded",
    "product.price_changed", "product.deleted",
    "user.invited", "user.role_changed", "user.removed",
    "subscription.plan_changed", "subscription.cancelled",
    "customer.data_erased", "export.generated",
    "api_key.created", "api_key.revoked",
}

// Audit log fields (IMMUTABLE — tidak ada updated_at):
// actor_id, actor_email, actor_ip, action, resource, resource_id, before, after, created_at
```

## Security Review Checklist

```go
// Untuk setiap PR, cek:
[ ] Tidak ada hardcoded secret/token/password di kode
[ ] tenantID dari JWT, bukan dari request
[ ] SQL: parameterized query (tidak ada string concatenation)
[ ] Input validation di semua handler
[ ] Sensitive data tidak ter-log (password, PIN, NPWP, kartu)
[ ] File upload: validate MIME dari magic bytes
[ ] Webhook: signature di-validate
[ ] Rate limiting dikonfigurasi untuk endpoint baru
[ ] Authorization middleware ada untuk setiap route
[ ] Error response tidak expose stack trace ke client
[ ] CORS origins spesifik (tidak *)
```

## Incident Response Summary

```
P0 (Critical — data breach, full compromise): Response < 15 menit
  1. Isolasi sistem (block IP, disable endpoint)
  2. Preserve evidence (jangan hapus log)
  3. Rotasi semua secrets
  4. Assess scope
  5. Notif BSSN < 14 hari, subjek data < 72 jam

P1 (High — service down): Response < 1 jam
  → Lihat runbook: docs/runbooks/18-operational-runbook.md

P2 (Medium — data leakage minor): Response < 4 jam
P3 (Low — performance): Response < 24 jam
```
