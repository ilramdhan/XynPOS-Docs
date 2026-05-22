# XynPOS Claude Skills — Quick Reference Card
> Print ini atau bookmark untuk referensi cepat saat mulai sesi Claude

---

## 1-Minute Setup

```
1. Buka claude.ai → Projects → XynPOS Development
2. Pastikan Project Instructions sudah berisi SKILL-00 + skill role kamu
3. Mulai chat dengan konteks spesifik
```

---

## Pilih Skill Berdasarkan Task

| Kamu mau ngapain | Skill yang dipakai |
|------------------|-------------------|
| Buat Go service / endpoint baru | SKILL-01 + SKILL-06 |
| Debug query database lambat | SKILL-02 |
| Buat/review komponen Next.js | SKILL-03 |
| Kerjakan fitur Flutter | SKILL-04 |
| Setup Docker / CI/CD / K8s | SKILL-05 |
| Design atau review API | SKILL-06 |
| Security audit kode | SKILL-07 |
| Review PR | SKILL-08 |
| Update blueprint / tulis ADR | SKILL-09 |
| Sprint planning / estimasi | SKILL-10 |

**Selalu SKILL-00 sebagai base — sudah include di Project Instructions**

---

## Prompt Templates

### Generate Code
```
"Di [service-name], tolong generate [layer: usecase/handler/repository] untuk
 [feature]. Berikut [existing entity/interface]: [paste kode]"
```

### Review Code
```
"Tolong review kode ini sesuai XynPOS dev rules.
 Bedakan BLOCKER vs SUGGESTION: [paste kode]"
```

### Debug
```
"Error: [paste error]
 Kode yang bermasalah: [paste kode]
 Context: [env, service, action yang dilakukan]"
```

### Architecture Decision
```
"Saya perlu memutuskan [X]. Tolong buat ADR dengan context, options,
 consequences, dan rekomendasi sesuai format XynPOS."
```

### Write Test
```
"Tolong generate unit test table-driven untuk [usecase/function].
 Test cases yang harus di-cover: [list cases]"
```

---

## Key Rules Ringkasan

```
GO:
  ✓ Clean arch: delivery→usecase→repo(interface)←domain
  ✓ Error: fmt.Errorf("context: %w", err)
  ✓ tenantID HANYA dari JWT (c.Locals)
  ✗ No fmt.Println | No SELECT * | No SQL concat

FLUTTER:
  ✓ AsyncValue untuk async state
  ✓ Either<Failure, T> dari repository
  ✓ Offline support untuk POS transactions
  ✗ No StatelessWidget yang watch provider (pakai ConsumerWidget)

NEXT.JS:
  ✓ TanStack Query untuk server state
  ✓ Zustand untuk client state
  ✓ API calls via lib/api.ts only
  ✗ No `any` | No useState+useEffect untuk server data

ALL:
  ✓ Test coverage >= 70%
  ✓ No hardcoded secrets
  ✓ Standard response format: { success, data, error }
```

---

*Extended Synaptic — XynPOS | v1.0*
