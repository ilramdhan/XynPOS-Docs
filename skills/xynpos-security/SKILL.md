---
name: xynpos-security
description: XynPOS security review and audit — use when reviewing code for security vulnerabilities, implementing security features, ensuring UU PDP compliance, auditing tenant isolation, or handling security incidents. Triggers when someone asks for a security review, wants to check for SQL injection or XSS, needs to implement rate limiting or JWT token rotation, reviews webhook signature validation, asks about UU PDP compliance requirements, or reports a potential security issue. Also use when designing authentication flows, permission systems, or audit logging.
license: See LICENSE.txt
---

# XynPOS Security Review

XynPOS handles financial and business data for thousands of tenants. Security is not optional.

## Reference Files
- Full STRIDE threat model → `references/threat-model.md`
- UU PDP compliance checklist → `references/uu-pdp.md`
- Audit log event catalog → `references/audit-events.md`

## The 10 Critical Rules

```
1. tenantID ALWAYS from c.Locals("tenantID") — NEVER from request
2. Parameterized queries ONLY — NEVER string concat SQL
3. Secrets NEVER in code, Dockerfiles, or logs
4. Sensitive data (password, PIN, NPWP, card) NEVER in logs
5. File uploads: validate MIME from magic bytes, not Content-Type header
6. JWT: 15min access token, rotation on refresh, reuse detection
7. Webhook: validate HMAC-SHA256 signature EVERY time
8. Rate limit: auth endpoints 5 req/15min, block 1hr on exceed
9. Audit log: all sensitive actions immutably recorded
10. UU PDP: right to erasure endpoint, consent at signup, breach notification <14 days
```

## Security Review Checklist

For every PR touching security-relevant code:

```go
// ✅ tenantID source
tenantID := c.Locals("tenantID").(string)  // CORRECT
tenantID := c.Query("tenant_id")           // BLOCKER: injection

// ✅ SQL parameterized
db.Where("id = ? AND deleted_at IS NULL", id).First(&p)  // CORRECT
db.Exec("SELECT * WHERE id = '" + id + "'")               // BLOCKER: injection

// ✅ File upload: magic bytes
buf := make([]byte, 512)
file.Read(buf)
mimeType := http.DetectContentType(buf)  // check actual bytes
allowed := []string{"image/jpeg","image/png","image/webp"}
// NOT: header.Get("Content-Type") — client can spoof this

// ✅ Webhook validation
func ValidateXenditWebhook(body []byte, sig string) bool {
    mac := hmac.New(sha256.New, []byte(os.Getenv("XENDIT_WEBHOOK_TOKEN")))
    mac.Write(body)
    return hmac.Equal([]byte(sig), []byte(hex.EncodeToString(mac.Sum(nil))))
}

// ✅ Sensitive masking in logs
logger.Info("user login",
    zap.String("email", maskEmail(req.Email)),  // j***@example.com
    // NEVER: zap.String("password", req.Password)
)
```

## Scripts

`scripts/security_scan.py <path>` — comprehensive security pattern scanner for all languages.
