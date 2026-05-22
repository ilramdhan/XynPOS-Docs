# XynPOS — Blueprint 14: Testing Strategy Blueprint
> Extended Synaptic | Version 1.0 | Confidential

---

## 1. Testing Philosophy

> "Test what matters, skip what doesn't. A 70% coverage that tests critical paths is better than 95% coverage of trivial getters."

**Prinsip:**
- **Test pyramid** — Banyak unit test, lebih sedikit integration, lebih sedikit E2E
- **Test behavior, not implementation** — Test apa yang dilakukan, bukan bagaimana
- **Fast feedback** — Unit test harus selesai < 10 detik
- **Deterministic** — Test tidak boleh flaky (hasil berbeda tiap run)
- **CI-first** — Semua test harus lulus di CI sebelum merge

---

## 2. Test Pyramid XynPOS

```
         ┌─────────────────────┐
         │    E2E Tests        │  ← Sedikit, lambat, mahal
         │   (Playwright/      │    Test critical user journeys
         │   Flutter Driver)   │
         ├─────────────────────┤
         │ Integration Tests   │  ← Cukup, sedang
         │  (DB + API level)   │    Test service boundary
         ├─────────────────────┤
         │    Unit Tests       │  ← Banyak, cepat, murah
         │  (usecase, utils,   │    Test business logic
         │   domain logic)     │
         └─────────────────────┘
           
Rasio Target: 70% unit : 20% integration : 10% E2E
```

---

## 3. Backend Testing (Go)

### 3.1 Test Structure per Service

```
backend/services/pos-service/
├── internal/
│   ├── domain/
│   │   ├── transaction.go
│   │   └── transaction_test.go         ← Unit test domain logic
│   ├── usecase/
│   │   ├── transaction_usecase_impl.go
│   │   └── transaction_usecase_test.go ← Unit test (dengan mock repo)
│   └── delivery/http/
│       ├── transaction_handler.go
│       └── transaction_handler_test.go ← Integration test (dengan test DB)
└── integration/
    └── transaction_flow_test.go        ← Full flow test
```

### 3.2 Unit Test — Usecase Layer

```go
// internal/usecase/transaction_usecase_test.go

package usecase_test

import (
    "context"
    "testing"
    
    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/mock"
    
    "xynpos/pos-service/internal/domain"
    "xynpos/pos-service/internal/usecase"
    "xynpos/pos-service/internal/repository/mock"
)

func TestCreateTransaction_Success(t *testing.T) {
    // Arrange
    mockTxRepo   := mocks.NewTransactionRepository(t)
    mockInvRepo  := mocks.NewInventoryRepository(t)
    mockProdRepo := mocks.NewProductRepository(t)
    
    product := &domain.Product{
        ID:    "prod-1",
        Name:  "Kopi Susu",
        Price: 25000,
        Stock: 10,
    }
    
    mockProdRepo.On("FindByID", mock.Anything, "prod-1").Return(product, nil)
    mockInvRepo.On("CheckStock", mock.Anything, "prod-1", "outlet-1").Return(10.0, nil)
    mockInvRepo.On("DeductStock", mock.Anything, mock.Anything).Return(nil)
    mockTxRepo.On("Create", mock.Anything, mock.MatchedBy(func(tx *domain.Transaction) bool {
        return tx.TotalAmount == 25000 && len(tx.Items) == 1
    })).Return(nil)
    
    uc := usecase.NewTransactionUsecase(mockTxRepo, mockInvRepo, mockProdRepo)
    
    req := usecase.CreateTransactionRequest{
        OutletID: "outlet-1",
        Items: []usecase.CartItem{
            {ProductID: "prod-1", Quantity: 1},
        },
        Payments: []usecase.Payment{
            {Method: "cash", Amount: 25000},
        },
    }
    
    // Act
    result, err := uc.CreateTransaction(context.Background(), "tenant-1", req)
    
    // Assert
    assert.NoError(t, err)
    assert.NotNil(t, result)
    assert.Equal(t, 25000.0, result.TotalAmount)
    mockTxRepo.AssertExpectations(t)
    mockInvRepo.AssertExpectations(t)
}

func TestCreateTransaction_InsufficientStock(t *testing.T) {
    mockInvRepo := mocks.NewInventoryRepository(t)
    mockProdRepo := mocks.NewProductRepository(t)
    
    mockProdRepo.On("FindByID", mock.Anything, "prod-1").
        Return(&domain.Product{ID: "prod-1", Stock: 0}, nil)
    mockInvRepo.On("CheckStock", mock.Anything, "prod-1", "outlet-1").
        Return(0.0, nil)
    
    uc := usecase.NewTransactionUsecase(
        mocks.NewTransactionRepository(t), mockInvRepo, mockProdRepo,
    )
    
    _, err := uc.CreateTransaction(context.Background(), "tenant-1",
        usecase.CreateTransactionRequest{
            Items: []usecase.CartItem{{ProductID: "prod-1", Quantity: 5}},
        },
    )
    
    assert.ErrorIs(t, err, domain.ErrInsufficientStock)
}
```

### 3.3 Integration Test — HTTP Handler

```go
// internal/delivery/http/transaction_handler_test.go

package http_test

import (
    "encoding/json"
    "net/http/httptest"
    "testing"
    
    "github.com/gofiber/fiber/v2"
    "github.com/stretchr/testify/assert"
    
    "xynpos/pos-service/internal/delivery/http"
    testutil "xynpos/pos-service/internal/testutil"
)

func TestTransactionHandler_Create_Integration(t *testing.T) {
    // Setup test database (testcontainers)
    db := testutil.SetupTestDB(t)
    defer testutil.TeardownTestDB(t, db)
    
    app := fiber.New()
    handler := http.NewTransactionHandler(
        usecase.NewTransactionUsecase(/* real repos with test DB */),
    )
    
    app.Post("/transactions", 
        testutil.MockAuthMiddleware("tenant-test", "user-1", "cashier"),
        handler.Create,
    )
    
    body := map[string]interface{}{
        "outlet_id": "outlet-1",
        "items": []map[string]interface{}{
            {"product_id": testutil.SeedProductID, "quantity": 1},
        },
        "payments": []map[string]interface{}{
            {"method": "cash", "amount": 25000},
        },
    }
    
    bodyBytes, _ := json.Marshal(body)
    req := httptest.NewRequest("POST", "/transactions", bytes.NewReader(bodyBytes))
    req.Header.Set("Content-Type", "application/json")
    req.Header.Set("Authorization", "Bearer "+testutil.GenerateTestJWT("tenant-test", "cashier"))
    
    resp, err := app.Test(req, 5000) // 5 second timeout
    
    assert.NoError(t, err)
    assert.Equal(t, 201, resp.StatusCode)
    
    var response map[string]interface{}
    json.NewDecoder(resp.Body).Decode(&response)
    assert.True(t, response["success"].(bool))
}
```

### 3.4 Test Utilities

```go
// internal/testutil/helpers.go

package testutil

import (
    "testing"
    "github.com/testcontainers/testcontainers-go"
)

// Setup PostgreSQL test container
func SetupTestDB(t *testing.T) *gorm.DB {
    t.Helper()
    
    ctx := context.Background()
    container, err := postgres.RunContainer(ctx,
        testcontainers.WithImage("postgres:16-alpine"),
        postgres.WithDatabase("xynpos_test"),
        postgres.WithUsername("xynpos"),
        postgres.WithPassword("test"),
        testcontainers.WithWaitStrategy(
            wait.ForLog("database system is ready to accept connections").
                WithOccurrence(2).WithStartupTimeout(5*time.Second)),
    )
    
    t.Cleanup(func() { container.Terminate(ctx) })
    
    // Run migrations
    connStr, _ := container.ConnectionString(ctx, "sslmode=disable")
    db := database.NewPostgres(connStr)
    RunMigrations(db, "tenant_test")
    SeedTestData(db)
    
    return db
}

// Generate valid JWT for tests
func GenerateTestJWT(tenantID, role string) string {
    return jwt.Sign(jwt.Claims{
        TenantID: tenantID,
        Role:     role,
        UserID:   "test-user-1",
    }, "test-secret")
}
```

### 3.5 Coverage Requirements

| Layer | Minimum Coverage |
|-------|-----------------|
| Domain (entities, business rules) | 90% |
| Usecase (business logic) | 80% |
| Handler (HTTP layer) | 70% |
| Repository (data access) | 60% |
| Utility packages | 85% |
| **Overall** | **70%** |

---

## 4. Frontend Testing (Next.js)

### 4.1 Stack

| Tool | Kegunaan |
|------|---------|
| **Vitest** | Unit test runner (faster Jest alternative) |
| **React Testing Library** | Component testing |
| **MSW (Mock Service Worker)** | API mocking |
| **Playwright** | E2E testing |
| **Storybook** | Component development + visual testing |

### 4.2 Unit Test — Hook

```typescript
// frontend/apps/web-pos/src/hooks/__tests__/useCart.test.ts

import { renderHook, act } from '@testing-library/react'
import { createWrapper } from '@/test-utils/providers'
import { useCart } from '../useCart'

describe('useCart', () => {
  it('adds item to cart', () => {
    const { result } = renderHook(() => useCart(), { wrapper: createWrapper() })
    
    act(() => {
      result.current.addItem({ id: 'prod-1', name: 'Kopi', price: 25000 })
    })
    
    expect(result.current.items).toHaveLength(1)
    expect(result.current.total).toBe(25000)
  })
  
  it('increases quantity if same item added twice', () => {
    const { result } = renderHook(() => useCart(), { wrapper: createWrapper() })
    const product = { id: 'prod-1', name: 'Kopi', price: 25000 }
    
    act(() => { result.current.addItem(product) })
    act(() => { result.current.addItem(product) })
    
    expect(result.current.items[0].quantity).toBe(2)
    expect(result.current.total).toBe(50000)
  })
  
  it('calculates discount correctly', () => {
    const { result } = renderHook(() => useCart(), { wrapper: createWrapper() })
    
    act(() => { result.current.addItem({ id: 'p1', name: 'A', price: 100000 }) })
    act(() => { result.current.applyDiscount({ type: 'percentage', value: 10 }) })
    
    expect(result.current.discountAmount).toBe(10000)
    expect(result.current.total).toBe(90000)
  })
})
```

### 4.3 Component Test

```typescript
// frontend/apps/web-pos/src/components/__tests__/ProductCard.test.tsx

import { render, screen, fireEvent } from '@testing-library/react'
import { ProductCard } from '../ProductCard'

const mockProduct = {
  id: 'prod-1',
  name: 'Kopi Susu',
  price: 25000,
  category: 'Minuman',
  imageUrl: null,
  hasVariants: false,
}

describe('ProductCard', () => {
  it('renders product name and price', () => {
    render(<ProductCard product={mockProduct} onSelect={vi.fn()} />)
    
    expect(screen.getByText('Kopi Susu')).toBeInTheDocument()
    expect(screen.getByText('Rp 25.000')).toBeInTheDocument()
  })
  
  it('calls onSelect when clicked', async () => {
    const onSelect = vi.fn()
    render(<ProductCard product={mockProduct} onSelect={onSelect} />)
    
    fireEvent.click(screen.getByRole('button', { name: /kopi susu/i }))
    
    expect(onSelect).toHaveBeenCalledWith(mockProduct)
  })
  
  it('shows out-of-stock badge when stock is 0', () => {
    render(<ProductCard product={{ ...mockProduct, stock: 0 }} onSelect={vi.fn()} />)
    
    expect(screen.getByText('Habis')).toBeInTheDocument()
  })
})
```

### 4.4 E2E Test (Playwright)

```typescript
// frontend/e2e/pos-checkout.spec.ts

import { test, expect } from '@playwright/test'
import { loginAsCashier, seedTestData } from './helpers'

test.describe('POS Checkout Flow', () => {
  test.beforeEach(async ({ page }) => {
    await seedTestData()
    await loginAsCashier(page)
  })
  
  test('complete cash transaction', async ({ page }) => {
    // Navigate to POS
    await page.goto('/pos')
    await expect(page.locator('[data-testid="pos-screen"]')).toBeVisible()
    
    // Add product
    await page.click('[data-testid="product-card-kopi-susu"]')
    await expect(page.locator('[data-testid="cart-item"]')).toHaveCount(1)
    
    // Click checkout
    await page.click('[data-testid="checkout-button"]')
    await expect(page.locator('[data-testid="payment-screen"]')).toBeVisible()
    
    // Select cash payment
    await page.click('[data-testid="payment-method-cash"]')
    await page.fill('[data-testid="cash-input"]', '50000')
    
    // Confirm
    await page.click('[data-testid="confirm-payment"]')
    
    // Verify receipt
    await expect(page.locator('[data-testid="receipt-screen"]')).toBeVisible()
    await expect(page.locator('[data-testid="change-amount"]')).toContainText('25.000')
    
    // Verify transaction count increased
    await expect(page.locator('[data-testid="session-tx-count"]')).toContainText('1')
  })
  
  test('QRIS payment with real-time confirmation', async ({ page }) => {
    await page.goto('/pos')
    await page.click('[data-testid="product-card-kopi-susu"]')
    await page.click('[data-testid="checkout-button"]')
    await page.click('[data-testid="payment-method-qris"]')
    
    // QR should be displayed
    await expect(page.locator('[data-testid="qris-qr-image"]')).toBeVisible()
    
    // Simulate payment received (mock webhook)
    await page.evaluate(() => {
      window.__mockPaymentReceived('qris-ref-123')
    })
    
    // Should auto-navigate to receipt
    await expect(page.locator('[data-testid="receipt-screen"]')).toBeVisible({ timeout: 5000 })
  })
})
```

---

## 5. Mobile Testing (Flutter)

### 5.1 Test Types

```
test/
├── unit/
│   ├── cart_notifier_test.dart
│   ├── currency_formatter_test.dart
│   └── offline_sync_test.dart
├── widget/
│   ├── product_card_test.dart
│   ├── cart_panel_test.dart
│   └── payment_screen_test.dart
└── integration/
    └── pos_flow_test.dart
```

### 5.2 Unit Test — Provider

```dart
// test/unit/cart_notifier_test.dart

void main() {
  group('CartNotifier', () {
    late ProviderContainer container;
    
    setUp(() {
      container = ProviderContainer();
    });
    
    tearDown(() {
      container.dispose();
    });
    
    test('menambah item ke cart', () {
      final product = Product(id: 'p1', name: 'Kopi', price: 25000);
      
      container.read(cartProvider.notifier).addItem(product);
      
      final cart = container.read(cartProvider);
      expect(cart.items.length, 1);
      expect(cart.total, 25000);
    });
    
    test('menambah kuantitas saat item sama ditambah lagi', () {
      final product = Product(id: 'p1', name: 'Kopi', price: 25000);
      
      container.read(cartProvider.notifier).addItem(product);
      container.read(cartProvider.notifier).addItem(product);
      
      final cart = container.read(cartProvider);
      expect(cart.items.first.quantity, 2);
      expect(cart.total, 50000);
    });
  });
}
```

### 5.3 Widget Test

```dart
// test/widget/product_card_test.dart

void main() {
  testWidgets('ProductCard menampilkan nama dan harga', (tester) async {
    final product = Product(id: 'p1', name: 'Kopi Susu', price: 25000);
    bool onSelectCalled = false;
    
    await tester.pumpWidget(
      ProviderScope(
        child: MaterialApp(
          home: Scaffold(
            body: ProductCard(
              product: product,
              onSelect: (_) => onSelectCalled = true,
            ),
          ),
        ),
      ),
    );
    
    expect(find.text('Kopi Susu'), findsOneWidget);
    expect(find.text('Rp 25.000'), findsOneWidget);
    
    await tester.tap(find.byType(ProductCard));
    expect(onSelectCalled, true);
  });
}
```

### 5.4 Integration Test (flutter_driver)

```dart
// integration_test/pos_flow_test.dart

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();
  
  testWidgets('Complete POS transaction flow', (tester) async {
    app.main();
    await tester.pumpAndSettle();
    
    // Login
    await tester.enterText(find.byKey(Key('email_field')), 'test@xynpos.com');
    await tester.enterText(find.byKey(Key('password_field')), 'test123');
    await tester.tap(find.byKey(Key('login_button')));
    await tester.pumpAndSettle();
    
    // Verify POS screen
    expect(find.byKey(Key('pos_screen')), findsOneWidget);
    
    // Add product
    await tester.tap(find.byKey(Key('product_kopi_susu')));
    await tester.pumpAndSettle();
    
    // Verify cart has item
    expect(find.byKey(Key('cart_item_0')), findsOneWidget);
    
    // Checkout
    await tester.tap(find.byKey(Key('checkout_button')));
    await tester.pumpAndSettle();
    
    // Select cash payment
    await tester.tap(find.byKey(Key('payment_cash')));
    await tester.enterText(find.byKey(Key('cash_amount_input')), '50000');
    
    await tester.tap(find.byKey(Key('confirm_payment')));
    await tester.pumpAndSettle();
    
    // Verify receipt
    expect(find.byKey(Key('receipt_screen')), findsOneWidget);
  });
}
```

---

## 6. Test Environment Setup

### 6.1 Test Database (Go — testcontainers)

```go
// Gunakan testcontainers untuk isolasi
// Setiap test suite punya database sendiri
// Data di-seed fresh untuk setiap test
```

### 6.2 Mock External Services

```go
// Payment gateway: pakai sandbox mode di integration test
// Email: intercept dengan mailtrap.io atau mock
// Firebase FCM: mock saat unit test

// config_test.go
func TestMain(m *testing.M) {
    // Override env untuk test
    os.Setenv("XENDIT_SECRET_KEY", "test_mode_key")
    os.Setenv("EMAIL_PROVIDER", "mock")
    os.Exit(m.Run())
}
```

---

## 7. CI Test Execution

```yaml
# Di GitHub Actions (ringkasan)

jobs:
  test-backend:
    steps:
      - name: Run unit tests
        run: go test ./internal/... -v -short  # -short skip integration
        
      - name: Run integration tests  
        run: go test ./... -v -run Integration
        # (butuh postgres + redis dari services: block)
        
      - name: Check coverage
        run: |
          go test ./... -coverprofile=coverage.out
          go tool cover -func=coverage.out | grep total  # >= 70%

  test-frontend:
    steps:
      - run: pnpm test --coverage   # Vitest
      - run: pnpm playwright test    # E2E (staging env)

  test-mobile:
    steps:
      - run: flutter test --coverage
      - run: flutter test integration_test/  # (emulator)
```

---

## 8. Test Data Management

### 8.1 Seed Data Strategy

```go
// internal/testutil/seed.go

func SeedTestData(db *gorm.DB) {
    // Seed dalam urutan dependency
    SeedTenant(db)
    SeedOutlet(db)
    SeedCategories(db)
    SeedProducts(db)     // Minimal: 5 produk dengan berbagai konfigurasi
    SeedUsers(db)        // Owner, manager, cashier
    SeedCustomers(db)    // 3 pelanggan test
}

// Produk test yang wajib ada:
// 1. Produk sederhana (no variant, no modifier) — Rp 25.000
// 2. Produk dengan variant (size: S/M/L)
// 3. Produk dengan modifier (topping, add-on)
// 4. Produk stok nol (out-of-stock)
// 5. Produk tidak aktif
```

### 8.2 Test Fixtures

```go
var TestProducts = map[string]*domain.Product{
    "simple":      {ID: "prod-simple", Name: "Kopi", Price: 25000, Stock: 100},
    "with-variant":{ID: "prod-variant", Name: "Teh", HasVariants: true},
    "out-of-stock":{ID: "prod-empty", Name: "Snack", Price: 15000, Stock: 0},
}
```

---

## 9. Performance Testing (Tahap Lanjut)

### k6 Load Test

```javascript
// infra/tests/k6/pos-checkout.js

import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  scenarios: {
    normal_load: {
      executor: 'constant-vus',
      vus: 50,           // 50 kasir serentak
      duration: '5m',
    },
    spike_test: {
      executor: 'ramping-vus',
      stages: [
        { duration: '1m', target: 200 },  // Spike ke 200 kasir
        { duration: '2m', target: 200 },
        { duration: '1m', target: 0 },
      ],
    },
  },
  thresholds: {
    'http_req_duration': ['p(95)<300'],  // 95% request < 300ms
    'http_req_failed':   ['rate<0.01'],  // Error rate < 1%
  },
};

export default function() {
  const token = getBearerToken();
  
  const payload = JSON.stringify({
    outlet_id: 'test-outlet',
    items: [{ product_id: 'prod-simple', quantity: 1 }],
    payments: [{ method: 'cash', amount: 25000 }],
  });
  
  const res = http.post(
    `${BASE_URL}/v1/transactions`,
    payload,
    { headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' } },
  );
  
  check(res, {
    'status is 201': (r) => r.status === 201,
    'has transaction id': (r) => r.json('data.id') !== '',
  });
  
  sleep(1);
}
```

---

*Blueprint ini inline dengan: BP-07 (Project Structure), BP-13 (CLAUDE.md), BP-09 (CI/CD)*
*Last updated: 2025 | Extended Synaptic — XynPOS*
