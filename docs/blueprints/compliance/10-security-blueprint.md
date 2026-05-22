# XynPOS — Blueprint 10: Security Blueprint
> Extended Synaptic | Version 1.0 | Confidential

---

## 1. Security Philosophy

XynPOS mengelola data keuangan dan transaksi bisnis ribuan tenant. Security bukan fitur tambahan — ini adalah fondasi. Prinsip yang dianut:

- **Security by Default** — Aman dari konfigurasi awal, bukan setelah insiden
- **Least Privilege** — Setiap komponen hanya punya akses yang diperlukan
- **Defense in Depth** — Berlapis, satu layer jebol tidak fatal
- **Zero Trust** — Tidak ada yang trusted secara default, verify everything
- **Privacy by Design** — Data pelanggan dilindungi sejak arsitektur

---

## 2. Threat Model (STRIDE)

### 2.1 Aset Kritis yang Dilindungi

| Aset | Klasifikasi | Risiko jika bocor |
|------|-------------|-------------------|
| Password hash user | Confidential | Account takeover |
| JWT secrets | Critical | Full system compromise |
| Data transaksi tenant | Confidential | Reputasi, legal |
| Data pelanggan (PII) | Confidential | UU PDP violation |
| API keys payment gateway | Critical | Financial loss |
| Database credentials | Critical | Data breach total |
| Refresh tokens | Confidential | Session hijacking |

### 2.2 STRIDE Analysis

| Threat | Contoh | Mitigasi |
|--------|--------|---------|
| **S**poofing | Buat token palsu, impersonate tenant lain | JWT signature, tenant isolation ketat |
| **T**ampering | Ubah amount transaksi in-transit | HTTPS/TLS, request signing |
| **R**epudiation | Klaim tidak pernah transaksi | Immutable audit log + digital signature |
| **I**nformation Disclosure | Lihat data tenant lain | Schema isolation, RLS, no data leakage |
| **D**enial of Service | Flood request → server down | Rate limiting, Cloudflare DDoS protection |
| **E**levation of Privilege | Kasir akses laporan owner | RBAC granular, middleware validation |

---

## 3. Authentication Security

### 3.1 Password Policy

```go
// Requirement password
const (
    MinLength     = 8
    RequireUpper  = true
    RequireLower  = true
    RequireDigit  = true
    RequireSymbol = false  // Optional, tapi encouraged
    MaxLength     = 128
)

// Password hashing: bcrypt dengan cost factor 12
func HashPassword(password string) (string, error) {
    bytes, err := bcrypt.GenerateFromPassword([]byte(password), 12)
    return string(bytes), err
}
```

### 3.2 JWT Security

```go
// Access token: RS256 (asymmetric) untuk production
// Refresh token: HS512 (symmetric) — disimpan hash-nya di Redis

// Konfigurasi JWT
type JWTConfig struct {
    AccessTokenExpiry  time.Duration // 15 menit
    RefreshTokenExpiry time.Duration // 30 hari
    Algorithm         string        // RS256
    Issuer            string        // "xynpos.com"
    Audience          []string      // ["xynpos-api"]
}

// Token rotation: Setiap refresh → token lama direvoke
// Reuse detection: Jika token lama dipakai lagi → revoke seluruh token_family
func DetectTokenReuse(tokenFamily string) {
    // Jika ada request dengan token yang sudah di-rotate:
    // 1. Revoke seluruh family
    // 2. Force logout semua device
    // 3. Alert ke owner
}
```

### 3.3 Brute Force Protection

```go
// Rate limit per endpoint auth
var authRateLimits = map[string]RateLimit{
    "POST /auth/login":          {Max: 5,  Window: "15m", Block: "1h"},
    "POST /auth/register":       {Max: 3,  Window: "1h",  Block: "24h"},
    "POST /auth/forgot-password":{Max: 3,  Window: "1h",  Block: "24h"},
    "POST /auth/verify-otp":     {Max: 5,  Window: "15m", Block: "1h"},
}

// Progressive delay setelah failed attempts
// 1-2 fails: no delay
// 3 fails: 1 second delay
// 4 fails: 2 second delay  
// 5 fails: lock 15 menit
```

### 3.4 Multi-Factor Authentication (Phase 2)

- TOTP (Google Authenticator compatible)
- SMS OTP via Twilio/Vonage
- Wajib untuk akun Enterprise dan akses admin

---

## 4. Authorization Security (RBAC)

### 4.1 Permission Validation Flow

```go
// Setiap request divalidasi di middleware layer
func AuthorizationMiddleware(requiredPermission string) fiber.Handler {
    return func(c *fiber.Ctx) error {
        claims := c.Locals("claims").(*JWTClaims)
        
        // 1. Cek tenant aktif dan plan-nya
        tenant := getTenantFromCache(claims.TenantID)
        if tenant.Status != "active" {
            return ErrTenantSuspended
        }
        
        // 2. Cek plan limit (contoh: report:export butuh Pro+)
        if !isPlanAllowed(tenant.Plan, requiredPermission) {
            return ErrPlanUpgradeRequired
        }
        
        // 3. Cek role permission
        if !hasPermission(claims.Permissions, requiredPermission) {
            return ErrForbidden
        }
        
        // 4. Cek outlet scope
        if !canAccessOutlet(claims, c.Params("outletId")) {
            return ErrOutletAccessDenied
        }
        
        return c.Next()
    }
}
```

### 4.2 Tenant Isolation Guard

```go
// Setiap query wajib include tenant context
// NEVER: SELECT * FROM products WHERE id = $1
// ALWAYS: SELECT * FROM products WHERE id = $1 AND (implicit via search_path)

// Middleware yang set search_path PostgreSQL:
func TenantSchemaMiddleware() fiber.Handler {
    return func(c *fiber.Ctx) error {
        tenantID := c.Locals("tenantID").(string)
        schemaName := "tenant_" + sanitizeTenantID(tenantID)
        
        // Validasi schema name (prevent SQL injection)
        if !regexp.MustCompile(`^tenant_[a-z0-9]{8,}$`).MatchString(schemaName) {
            return ErrInvalidTenant
        }
        
        // Set untuk connection ini saja
        db.Exec("SET search_path = ?", schemaName)
        return c.Next()
    }
}
```

---

## 5. Input Validation & Injection Prevention

### 5.1 Request Validation

```go
// Setiap request struct wajib punya validation tags
type CreateProductRequest struct {
    Name         string  `json:"name" validate:"required,min=1,max=255,xss"`
    SKU          string  `json:"sku" validate:"omitempty,alphanum,max=100"`
    SellingPrice float64 `json:"selling_price" validate:"required,min=0,max=999999999"`
    CategoryID   string  `json:"category_id" validate:"required,uuid4"`
    Description  string  `json:"description" validate:"omitempty,max=2000,xss"`
}

// Custom XSS validator
func xssValidator(fl validator.FieldLevel) bool {
    value := fl.Field().String()
    // Reject HTML tags dan script injection
    return !containsHTML(value) && !containsScript(value)
}
```

### 5.2 SQL Injection Prevention

```go
// SELALU gunakan parameterized query
// ❌ NEVER: db.Exec("SELECT * FROM products WHERE name = '" + name + "'")
// ✅ ALWAYS: db.Where("name = ?", name).Find(&products)

// GORM default menggunakan parameterized query
// Raw query jika terpaksa:
db.Raw("SELECT * FROM products WHERE id = ? AND is_active = ?", id, true).Scan(&product)
```

### 5.3 File Upload Security

```go
// Validasi file upload yang ketat
func ValidateFileUpload(file *multipart.FileHeader) error {
    // 1. Check size (max 2MB untuk gambar produk)
    if file.Size > 2*1024*1024 {
        return ErrFileTooLarge
    }
    
    // 2. Check MIME type dari magic bytes (bukan dari header!)
    f, _ := file.Open()
    defer f.Close()
    buf := make([]byte, 512)
    f.Read(buf)
    mimeType := http.DetectContentType(buf)
    
    allowed := []string{"image/jpeg", "image/png", "image/webp"}
    if !slices.Contains(allowed, mimeType) {
        return ErrInvalidFileType
    }
    
    // 3. Sanitize filename
    filename := filepath.Base(file.Filename)
    filename = strings.Map(func(r rune) rune {
        if unicode.IsLetter(r) || unicode.IsDigit(r) || r == '.' || r == '-' {
            return r
        }
        return '_'
    }, filename)
    
    // 4. Generate UUID filename (prevent path traversal)
    safeFilename := uuid.New().String() + filepath.Ext(filename)
    
    return nil
}
```

---

## 6. Data Security

### 6.1 Encryption at Rest

```go
// Data sensitif dienkripsi sebelum disimpan ke database
// Gunakan AES-256-GCM

type EncryptedField struct {
    value string
}

func Encrypt(plaintext string, key []byte) (string, error) {
    block, _ := aes.NewCipher(key)
    gcm, _ := cipher.NewGCM(block)
    nonce := make([]byte, gcm.NonceSize())
    io.ReadFull(rand.Reader, nonce)
    ciphertext := gcm.Seal(nonce, nonce, []byte(plaintext), nil)
    return base64.StdEncoding.EncodeToString(ciphertext), nil
}

// Field yang WAJIB dienkripsi:
// - npwp (NPWP bisnis)
// - Nomor kartu kredit (jika disimpan — lebih baik tokenize via gateway)
// - API keys payment gateway
```

### 6.2 PII Data Masking (untuk Logs & Errors)

```go
// Jangan log data sensitif
type CustomerLog struct {
    ID    string `json:"id"`
    Name  string `json:"name"`
    Phone string `json:"phone"` // Akan di-mask: 08xx-xxxx-1234
    Email string `json:"email"` // Akan di-mask: j***@example.com
}

func MaskPhone(phone string) string {
    if len(phone) < 8 { return "****" }
    return phone[:4] + strings.Repeat("x", len(phone)-8) + phone[len(phone)-4:]
}

// Middleware: Strip sensitive fields dari request log
var sensitiveFields = []string{"password", "pin", "card_number", "cvv"}
```

### 6.3 Data Retention & Right to Erasure (UU PDP)

```go
// Endpoint untuk hapus data pelanggan (GDPR/UU PDP compliance)
// DELETE /api/v1/customers/:id/erase

func EraseCustomerData(customerID string) error {
    // 1. Anonymize PII (tidak hapus transaksi — butuh untuk pajak)
    db.Model(&Customer{}).Where("id = ?", customerID).Updates(map[string]interface{}{
        "name":  "Pelanggan Dihapus",
        "phone": nil,
        "email": nil,
        "address": nil,
        "date_of_birth": nil,
        "deleted_at": time.Now(),
    })
    
    // 2. Log aksi erasure untuk audit
    auditLog.Log("customer.erased", customerID, requestBy)
    
    return nil
}
```

---

## 7. API Security

### 7.1 Rate Limiting Strategy

```go
// Rate limiting berbasis Redis, per tenant dan per endpoint

type RateLimitConfig struct {
    Plan     string
    Endpoint string
    MaxReqs  int
    Window   time.Duration
}

var rateLimits = []RateLimitConfig{
    // POS endpoints — mission critical, limit lebih tinggi
    {Plan: "free",     Endpoint: "POST /pos/transactions", MaxReqs: 60,   Window: time.Minute},
    {Plan: "starter",  Endpoint: "POST /pos/transactions", MaxReqs: 300,  Window: time.Minute},
    {Plan: "pro",      Endpoint: "POST /pos/transactions", MaxReqs: 1500, Window: time.Minute},
    {Plan: "business", Endpoint: "POST /pos/transactions", MaxReqs: 6000, Window: time.Minute},
    
    // Report endpoints — heavy query, limit lebih rendah
    {Plan: "starter", Endpoint: "GET /reports/*", MaxReqs: 30, Window: time.Minute},
    {Plan: "pro",     Endpoint: "GET /reports/*", MaxReqs: 60, Window: time.Minute},
    
    // Global API rate limit
    {Plan: "*", Endpoint: "*", MaxReqs: 1000, Window: time.Minute},
}
```

### 7.2 CORS Configuration

```go
app.Use(cors.New(cors.Config{
    AllowOrigins: strings.Join([]string{
        "https://app.xynpos.com",
        "https://pos.xynpos.com",
        "https://admin.xynpos.com",
        // Dev origins
        "http://localhost:3000",
        "http://localhost:3001",
    }, ","),
    AllowMethods:     "GET,POST,PUT,PATCH,DELETE,OPTIONS",
    AllowHeaders:     "Origin,Content-Type,Accept,Authorization,X-Tenant-ID",
    AllowCredentials: true,
    MaxAge:           86400,
}))
```

### 7.3 Security Headers

```go
app.Use(helmet.New(helmet.Config{
    ContentSecurityPolicy:   "default-src 'self'",
    XContentTypeOptions:     "nosniff",
    XFrameOptions:           "DENY",
    ReferrerPolicy:          "no-referrer",
    CrossOriginOpenerPolicy: "same-origin",
    PermissionsPolicy:       "camera=(), microphone=(), geolocation=()",
}))
```

### 7.4 Webhook Signature Validation

```go
// Validasi webhook dari Xendit/Midtrans
func ValidateXenditWebhook(body []byte, signature string) bool {
    webhookToken := os.Getenv("XENDIT_WEBHOOK_TOKEN")
    expected := hmac.New(sha256.New, []byte(webhookToken))
    expected.Write(body)
    expectedSig := hex.EncodeToString(expected.Sum(nil))
    return hmac.Equal([]byte(signature), []byte(expectedSig))
}
```

---

## 8. Infrastructure Security

### 8.1 Network Security

```
Internet
    │
    ├── [Public] Cloudflare WAF
    │       - DDoS mitigation
    │       - Bot detection
    │       - Rate limiting (edge level)
    │       - OWASP Top 10 rules
    │
    ├── [DMZ] Load Balancer
    │       - TLS termination (TLS 1.2+)
    │       - Certificate rotation auto (Let's Encrypt/Cloudflare)
    │
    └── [Private Network] Application Servers
            - No direct internet access
            - Only accessible via LB
            - Service-to-service: private network only
            
Database Servers
    - Private network ONLY
    - IP whitelist: hanya dari app servers
    - SSL connection wajib
    - Tidak ada public IP
```

### 8.2 Secrets Management

```bash
# Hierarchy secret management

# Development: .env.local (gitignored)
# Staging: Doppler project "xynpos-staging"
# Production: Doppler project "xynpos-production" (atau HashiCorp Vault)

# TIDAK PERNAH:
# - Secret di source code
# - Secret di Docker image
# - Secret di git history
# - Secret di log files

# Secret rotation policy:
# - JWT secrets: Rotate setiap 90 hari
# - DB credentials: Rotate setiap 180 hari
# - Payment gateway keys: Rotate setelah potential exposure
# - API keys: Rotate setelah team member keluar
```

### 8.3 SSH Hardening

```bash
# /etc/ssh/sshd_config di semua server
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys
AllowUsers deploy
MaxAuthTries 3
LoginGraceTime 30
ClientAliveInterval 300
ClientAliveCountMax 2
```

---

## 9. Audit Logging

### 9.1 Audit Log Schema

```go
// Setiap aksi sensitif menghasilkan audit log yang immutable

type AuditLog struct {
    ID          uuid.UUID  `json:"id"`
    TenantID    uuid.UUID  `json:"tenant_id"`
    OutletID    *uuid.UUID `json:"outlet_id,omitempty"`
    
    ActorID     uuid.UUID  `json:"actor_id"`
    ActorEmail  string     `json:"actor_email"`
    ActorIP     string     `json:"actor_ip"`
    ActorDevice string     `json:"actor_device"`
    
    Action      string     `json:"action"`      // "transaction.voided"
    Resource    string     `json:"resource"`    // "transactions"
    ResourceID  string     `json:"resource_id"`
    
    Before      JSONB      `json:"before,omitempty"` // State sebelum
    After       JSONB      `json:"after,omitempty"`  // State setelah
    
    Metadata    JSONB      `json:"metadata"`
    
    CreatedAt   time.Time  `json:"created_at"`  // TIDAK ADA updated_at — immutable!
}
```

### 9.2 Events yang Wajib Di-audit

```go
// HIGH sensitivity events — selalu di-audit
var criticalAuditEvents = []string{
    "auth.login",
    "auth.logout",
    "auth.login_failed",
    "auth.password_changed",
    "transaction.voided",
    "transaction.refunded",
    "product.price_changed",
    "product.deleted",
    "user.invited",
    "user.role_changed",
    "user.removed",
    "subscription.plan_changed",
    "subscription.cancelled",
    "settings.updated",
    "customer.data_erased",
    "export.generated",
    "api_key.created",
    "api_key.revoked",
}
```

---

## 10. Security Incident Response

### 10.1 Incident Classification

| Level | Deskripsi | Contoh | SLA Response |
|-------|-----------|--------|-------------|
| P0 — Critical | Data breach, full system compromise | DB exposed | 15 menit |
| P1 — High | Service down, payment failure | Auth service down | 1 jam |
| P2 — Medium | Data leakage minor, feature broken | Report error | 4 jam |
| P3 — Low | Performance degradation | Slow query | 24 jam |

### 10.2 Breach Response Checklist

```
Saat terjadi insiden keamanan:

1. ISOLASI (0-15 menit)
   [ ] Identifikasi source dan scope
   [ ] Block traffic dari IP/region yang mencurigakan
   [ ] Revoke semua JWT tokens (nuclear option)
   [ ] Disable endpoint yang exploited

2. ASSESS (15-60 menit)
   [ ] Tentukan data apa yang terekspos
   [ ] Timeline: kapan mulai, berapa tenant terdampak
   [ ] Screenshot semua log yang relevan

3. CONTAIN (1-4 jam)
   [ ] Patch vulnerability
   [ ] Rotate semua secrets yang potentially exposed
   [ ] Deploy hotfix ke production

4. NOTIFY (< 72 jam — UU PDP wajib)
   [ ] Notifikasi tenant yang terdampak
   [ ] Lapor ke BSSN jika data breach > threshold
   [ ] Update status page

5. POSTMORTEM (< 7 hari)
   [ ] Root cause analysis
   [ ] Timeline lengkap
   [ ] Remediation yang sudah dilakukan
   [ ] Prevention measures ke depan
```

---

## 11. Security Checklist per Release

Setiap release wajib lewat checklist ini:

```
BEFORE DEPLOY:
[ ] golangci-lint pass (no security lints)
[ ] govulncheck — no known CVEs
[ ] Dependency audit: go mod audit
[ ] No hardcoded secrets (gitleaks scan)
[ ] OWASP dependency check

IN STAGING:
[ ] Penetration test (basic) untuk endpoint baru
[ ] OWASP ZAP scan untuk endpoint baru
[ ] Test rate limiting behavior
[ ] Test tenant isolation (coba akses data tenant lain)

QUARTERLY:
[ ] Full penetration test oleh pihak ketiga
[ ] Dependency upgrade (keamanan)
[ ] Secret rotation
[ ] Access review (siapa saja punya akses ke apa)
[ ] UU PDP compliance review
```

---

## 12. UU PDP Compliance (Indonesia)

Berdasarkan UU No. 27 Tahun 2022 tentang Perlindungan Data Pribadi:

| Kewajiban | Implementasi XynPOS |
|-----------|---------------------|
| **Consent** | Checkbox persetujuan di registrasi, simpan timestamp consent |
| **Purpose limitation** | Data pelanggan hanya untuk POS operation, tidak dijual |
| **Data minimization** | Hanya kumpulkan data yang diperlukan |
| **Accuracy** | User bisa update data mereka sendiri |
| **Retention limit** | Data dihapus sesuai policy setelah tenant non-aktif |
| **Right to access** | Endpoint untuk export semua data pelanggan |
| **Right to erasure** | Endpoint anonymize data pelanggan |
| **Security** | Enkripsi, akses terbatas, audit log |
| **Breach notification** | < 72 jam ke BSSN dan subjek data |
| **DPO** | Tunjuk Data Protection Officer saat scale (>50 karyawan) |

---

*Blueprint ini inline dengan: BP-06 (Architecture), BP-09 (Infrastructure), BP-11 (API Design)*
*Last updated: 2025 | Extended Synaptic — XynPOS*
