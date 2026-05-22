# XynPOS Subscription Plans

## Plan Tiers

| Plan | Price/Month | Outlets | Users | Transactions |
|------|-------------|---------|-------|-------------|
| **Free** | Rp 0 | 1 | 1 kasir | 100/month |
| **Starter** | Rp 149.000 | 1 | 3 | Unlimited |
| **Pro** | Rp 349.000 | 3 | 10 | Unlimited |
| **Business** | Rp 749.000 | 10 | 30 | Unlimited |
| **Enterprise** | Custom (min Rp 2.000.000) | Unlimited | Unlimited | Unlimited |

Annual billing: 20% discount.

## Business Model: Hybrid Freemium + Trial

1. **Free plan** — permanent but very limited (100 tx/month cap)
2. **Trial Pro 30 days** — all signups get full Pro access automatically
3. **After 30 days** — auto-downgrade to Free if no upgrade
4. **Conversion trigger** — losing Pro features after trial drives upgrade

## Feature Availability by Plan

| Feature | Free | Starter | Pro | Business | Enterprise |
|---------|------|---------|-----|----------|------------|
| Products | 50 items | 500 | Unlimited | Unlimited | Unlimited |
| Advanced reports | ❌ | ❌ | ✅ | ✅ | ✅ |
| Purchase Order | ❌ | ❌ | ✅ | ✅ | ✅ |
| Kitchen Display | ❌ | ❌ | ✅ | ✅ | ✅ |
| Loyalty program | ❌ | Basic | Advanced | Advanced | Custom |
| API access | ❌ | ❌ | Read-only | Full | Full+Webhook |
| Multi-outlet dashboard | ❌ | ❌ | ❌ | ✅ | ✅ |
| White label | ❌ | ❌ | ❌ | ❌ | ✅ |
| Dedicated CSM | ❌ | ❌ | ❌ | ❌ | ✅ |
| SLA uptime | best-effort | 99.5% | 99.9% | 99.9% | 99.99% |

## JWT Plan Claims

The plan is embedded in the JWT access token. API Gateway middleware checks plan before routing. Plan-gated endpoints return `PLAN_LIMIT_REACHED` (402) for insufficient plans.

```go
type JWTClaims struct {
    Sub       string `json:"sub"`       // user UUID
    TenantID  string `json:"tenant_id"`
    OutletID  string `json:"outlet_id"`
    Role      string `json:"role"`      // owner|manager|cashier|inventory
    Plan      string `json:"plan"`      // free|starter|pro|business|enterprise
    IsTrial   bool   `json:"is_trial"`
    Permissions []string `json:"permissions"`
}
```

## Data Retention

| Tenant State | Retention | Action |
|-------------|-----------|--------|
| Active | Permanent | — |
| Free, cancelled > 30 days | 30 days | Delete schema |
| Paid, cancelled > 1 year | 1 year | Archive to cold storage |
| After deletion | — | Schema dropped permanently |
