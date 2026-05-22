---
name: xynpos-code-review
description: XynPOS code review assistant — use when reviewing Go, Flutter, or Next.js code for quality, security, architecture compliance, and XynPOS conventions. Triggers when a developer asks to review their code, check a PR, evaluate a code snippet for XynPOS compliance, get feedback on implementation quality, or understand whether their code follows XynPOS patterns. Runs automated checks via scripts and provides structured BLOCKER vs SUGGESTION feedback with specific fix recommendations.
license: See LICENSE.txt
---

# XynPOS Code Review Assistant

Perform structured code review using XynPOS rules. Always distinguish:
- 🔴 **BLOCKER** — must fix before merge
- 💡 **SUGGESTION** — improves quality, not blocking

## How to Use

1. When code is provided, run the appropriate automated checker first:
   - Go code → `python scripts/review_go.py <path>`
   - Flutter code → `python scripts/review_flutter.py <path>`
   - TypeScript/React → `python scripts/review_typescript.py <path>`
   
2. Supplement with qualitative review covering:
   - Architecture compliance (clean layers, proper separation)
   - Business logic correctness
   - Error handling completeness
   - Test coverage adequacy

3. Format findings with severity, explanation, and concrete fix example.

## Master Review Checklist

### Go (Backend)
```
BLOCKERS:
[ ] tenantID from JWT locals, never from request
[ ] No SQL string concatenation
[ ] No fmt.Println — zap structured logging only
[ ] Error wrapped with context: fmt.Errorf("ctx: %w", err)
[ ] No hardcoded secrets
[ ] No panic in non-main files
[ ] Standard response format (response.Success/Error)
[ ] Input validation in handler layer
[ ] Test coverage >= 70%

SUGGESTIONS:
[ ] Specify columns in SELECT (not SELECT *)
[ ] Context timeout for external calls
[ ] Table-driven tests for multiple cases
[ ] Benchmark for hot path functions
```

### Flutter (Mobile)
```
BLOCKERS:
[ ] ConsumerWidget (not StatelessWidget) for provider watchers
[ ] Either<Failure, T> from repositories
[ ] Domain entities have NO JSON annotations
[ ] ListView.builder for lists (not Column+.map)
[ ] CachedNetworkImage (not Image.network)
[ ] POS transactions offline-capable

SUGGESTIONS:
[ ] const constructor on static widgets
[ ] Granular providers (not watching full state)
[ ] AsyncValue for all async operations
```

### Next.js (Frontend)
```
BLOCKERS:
[ ] TanStack Query for server state (not useState+useEffect)
[ ] No 'any' TypeScript type
[ ] API calls via lib/api.ts (not direct fetch)
[ ] Zod validation for all forms
[ ] Loading AND error states present

SUGGESTIONS:
[ ] Error boundary in layouts
[ ] Empty state for lists
[ ] useMemo only for expensive computations
```

## Review Communication Style

```
✅ Constructive: "Consider using fmt.Errorf here to add context — when this
   error surfaces in logs, you'll know exactly which operation failed."

✅ Specific: Show the corrected code, not just describe the problem.

✅ Explain WHY: "SELECT * loads all columns unnecessarily — with 20+ columns
   in the transactions table, this adds ~15% query overhead."

❌ Avoid: "This is wrong", "Bad code", "Why did you do this?"
```

## Scripts

```bash
# Go backend
python scripts/review_go.py <path>

# Flutter mobile  
python scripts/review_flutter.py <path>

# TypeScript frontend
python scripts/review_typescript.py <path>
```
