# XynPOS — Blueprint 12: Mobile App Blueprint
> Extended Synaptic | Version 1.0 | Confidential

---

## 1. Mobile App Overview

XynPOS Mobile adalah aplikasi Flutter yang menjadi **primary device** untuk kasir di lapangan. Mayoritas pengguna (estimasi 80%) akan menggunakan mobile sebagai interface utama, bukan web.

**Platform target:**
- Android 8.0+ (API level 26+)
- iOS 14+

**App ID:**
- Android: `com.extendedsynaptic.xynpos`
- iOS: `com.extendedsynaptic.xynpos`

---

## 2. App Architecture

### 2.1 Clean Architecture + Feature-First

```
lib/
├── core/           ← Infrastruktur (network, storage, DI)
├── features/       ← Fitur bisnis (auth, pos, products, ...)
│   └── feature_x/
│       ├── data/         ← Repository impl + API calls
│       ├── domain/       ← Entities + use cases
│       └── presentation/ ← Screens + Widgets + Providers
└── shared/         ← Widget umum yang di-share
```

### 2.2 State Management: Riverpod 2

```dart
// Provider hierarchy

AppStateProvider              // Top-level: auth state, tenant info
    ├── AuthProvider          // Login status, JWT tokens
    ├── TenantProvider        // Tenant & outlet info, subscription plan
    ├── OutletProvider        // Outlet yang dipilih
    └── CartProvider          // State keranjang belanja aktif
        ├── ProductsProvider  // Katalog produk (cached)
        ├── PaymentProvider   // Payment flow state
        └── SessionProvider   // Kasir session aktif
```

---

## 3. Navigation (go_router)

### 3.1 Route Structure

```dart
// lib/shared/router/app_router.dart

final router = GoRouter(
  initialLocation: '/splash',
  redirect: (context, state) {
    final isLoggedIn = ref.read(authProvider).isLoggedIn;
    final isOnAuthRoute = state.matchedLocation.startsWith('/auth');
    
    if (!isLoggedIn && !isOnAuthRoute) return '/auth/login';
    if (isLoggedIn && isOnAuthRoute) return '/pos';
    return null;
  },
  routes: [
    GoRoute(path: '/splash',        builder: (c,s) => SplashScreen()),
    GoRoute(path: '/auth/login',    builder: (c,s) => LoginScreen()),
    GoRoute(path: '/auth/register', builder: (c,s) => RegisterScreen()),
    GoRoute(path: '/outlet-select', builder: (c,s) => OutletSelectScreen()),
    
    ShellRoute(
      builder: (c, s, child) => PosShell(child: child),
      routes: [
        GoRoute(path: '/pos',         builder: (c,s) => PosScreen()),
        GoRoute(path: '/pos/payment', builder: (c,s) => PaymentScreen()),
        GoRoute(path: '/pos/receipt', builder: (c,s) => ReceiptScreen()),
        GoRoute(path: '/pos/tables',  builder: (c,s) => TablesScreen()),
        GoRoute(path: '/pos/held',    builder: (c,s) => HeldOrdersScreen()),
      ],
    ),
    
    ShellRoute(
      builder: (c, s, child) => DashboardShell(child: child),
      routes: [
        GoRoute(path: '/dashboard',   builder: (c,s) => DashboardScreen()),
        GoRoute(path: '/products',    builder: (c,s) => ProductsScreen()),
        GoRoute(path: '/inventory',   builder: (c,s) => InventoryScreen()),
        GoRoute(path: '/customers',   builder: (c,s) => CustomersScreen()),
        GoRoute(path: '/reports',     builder: (c,s) => ReportsScreen()),
        GoRoute(path: '/settings',    builder: (c,s) => SettingsScreen()),
      ],
    ),
  ],
);
```

---

## 4. Core Features

### 4.1 POS Kasir Screen

**Layout (Landscape-optimized, tapi harus bagus di Portrait juga):**

```
┌─────────────────────────────────────────────────────────┐
│ Header: Outlet Name | Shift: Open | User: Budi          │
├───────────────────────────┬─────────────────────────────┤
│ PRODUCT AREA (60%)        │ CART AREA (40%)             │
│                           │                             │
│ [Search bar + scan btn]   │ [Cart item 1]               │
│                           │ [Cart item 2]               │
│ [Kategori tabs]           │ ...                         │
│                           │                             │
│ [Product Grid]            │ ─────────────────           │
│  ┌──────┐ ┌──────┐        │ Subtotal: Rp 50.000         │
│  │Kopi  │ │ Es   │        │ Diskon:   -Rp 5.000         │
│  │Susu  │ │ Teh  │        │ Pajak:    Rp 4.950          │
│  │25.000│ │12.000│        │ TOTAL: Rp 49.950            │
│  └──────┘ └──────┘        │                             │
│                           │ [BAYAR]                     │
└───────────────────────────┴─────────────────────────────┘
```

```dart
// features/pos/presentation/screens/pos_screen.dart

class PosScreen extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final cartState = ref.watch(cartProvider);
    final productsState = ref.watch(filteredProductsProvider);
    
    return Scaffold(
      body: Row(
        children: [
          // Product panel (60%)
          Expanded(
            flex: 6,
            child: Column(
              children: [
                ProductSearchBar(),
                CategoryTabs(),
                Expanded(child: ProductGrid(products: productsState)),
              ],
            ),
          ),
          // Cart panel (40%)
          SizedBox(
            width: 380,
            child: CartPanel(cart: cartState),
          ),
        ],
      ),
    );
  }
}
```

### 4.2 Product Grid

```dart
// features/pos/presentation/widgets/product_grid.dart

class ProductGrid extends StatelessWidget {
  final List<Product> products;
  
  @override
  Widget build(BuildContext context) {
    return GridView.builder(
      gridDelegate: SliverGridDelegateWithMaxCrossAxisExtent(
        maxCrossAxisExtent: 150,     // Adaptif — lebih banyak kolom di tablet
        childAspectRatio: 0.85,
        crossAxisSpacing: 8,
        mainAxisSpacing: 8,
      ),
      itemBuilder: (ctx, i) => ProductCard(product: products[i]),
    );
  }
}

class ProductCard extends ConsumerWidget {
  final Product product;
  
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return GestureDetector(
      onTap: () {
        if (product.hasVariants || product.hasModifiers) {
          // Buka bottom sheet pilih variant/modifier
          showModalBottomSheet(
            context: context,
            builder: (_) => ProductOptionsSheet(product: product),
          );
        } else {
          // Langsung tambah ke cart
          ref.read(cartProvider.notifier).addItem(product);
          HapticFeedback.lightImpact(); // Feedback sentuhan
        }
      },
      child: ProductCardContent(product: product),
    );
  }
}
```

### 4.3 Payment Flow

```dart
// Payment screen mengelola semua metode pembayaran

class PaymentScreen extends ConsumerStatefulWidget {
  @override
  ConsumerState createState() => _PaymentScreenState();
}

class _PaymentScreenState extends ConsumerState<PaymentScreen> {
  List<PaymentEntry> payments = [];
  double get totalPaid => payments.fold(0, (sum, p) => sum + p.amount);
  double get remaining => cartTotal - totalPaid;
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        children: [
          // Summary
          PaymentSummaryHeader(remaining: remaining),
          
          // Payment method selector
          PaymentMethodGrid(
            methods: ['cash', 'qris', 'transfer', 'ewallet'],
            onSelect: _addPayment,
          ),
          
          // Current payments list
          PaymentsList(payments: payments, onRemove: _removePayment),
          
          // Confirm button (hanya aktif jika remaining == 0)
          ConfirmPaymentButton(
            enabled: remaining <= 0,
            onConfirm: _confirmPayment,
          ),
        ],
      ),
    );
  }
}
```

### 4.4 QRIS Payment

```dart
// Real-time QRIS dengan polling/WebSocket

class QrisPaymentWidget extends ConsumerStatefulWidget {
  final String transactionId;
  
  @override
  ConsumerState createState() => _QrisPaymentWidgetState();
}

class _QrisPaymentWidgetState extends ConsumerState {
  late Timer _pollTimer;
  String? qrImageUrl;
  PaymentStatus status = PaymentStatus.pending;
  
  @override
  void initState() {
    super.initState();
    _generateQris();
    // Poll setiap 3 detik untuk cek status
    _pollTimer = Timer.periodic(Duration(seconds: 3), (_) => _checkStatus());
  }
  
  Future<void> _generateQris() async {
    final result = await ref.read(paymentRepositoryProvider)
        .generateQris(widget.transactionId);
    setState(() => qrImageUrl = result.qrImageUrl);
  }
  
  Future<void> _checkStatus() async {
    final status = await ref.read(paymentRepositoryProvider)
        .checkQrisStatus(widget.transactionId);
    if (status == PaymentStatus.completed) {
      _pollTimer.cancel();
      setState(() => this.status = status);
      // Navigate ke receipt
    }
  }
  
  @override
  void dispose() {
    _pollTimer.cancel();
    super.dispose();
  }
}
```

---

## 5. Offline Mode

### 5.1 Architecture

```
Online Flow:
API Call → Response → Update UI

Offline Flow:
Action → Write to Hive (local) → Update UI optimistically
                                              ↓
                              [Internet restored]
                                              ↓
                         WorkManager Sync Job → Read Hive → POST /transactions/sync
                                              ↓
                                    Mark as synced in Hive
```

### 5.2 Local Database (Hive + SQLite)

```dart
// Hive: untuk object storage (produk cache, cart, pending transactions)
// SQLite: untuk relational data yang perlu query kompleks

// lib/core/offline/offline_database.dart

// Hive boxes:
// - products_box: Map<String, ProductLocal> (cache dari API)
// - pending_transactions_box: List<PendingTransaction>
// - cart_box: CartState (current cart state)
// - sync_queue_box: List<SyncQueueItem>

@HiveType(typeId: 1)
class PendingTransaction extends HiveObject {
  @HiveField(0) late String localId;         // UUID generated di device
  @HiveField(1) late String outletId;
  @HiveField(2) late List<CartItemLocal> items;
  @HiveField(3) late List<PaymentLocal> payments;
  @HiveField(4) late double totalAmount;
  @HiveField(5) late DateTime createdAt;
  @HiveField(6) late bool isSynced;
  @HiveField(7) String? serverTransactionId; // Diisi setelah sync
}
```

### 5.3 Sync Manager

```dart
// lib/core/offline/sync_manager.dart

class SyncManager {
  final TransactionRepository txRepo;
  final ConnectivityPlus connectivity;
  
  Future<void> syncPendingTransactions() async {
    // Cek koneksi
    final isConnected = await connectivity.checkConnectivity()
        != ConnectivityResult.none;
    if (!isConnected) return;
    
    final pendingBox = Hive.box<PendingTransaction>('pending_transactions');
    final pending = pendingBox.values
        .where((t) => !t.isSynced)
        .toList();
    
    if (pending.isEmpty) return;
    
    try {
      // Batch sync ke server
      final results = await txRepo.syncBatch(pending);
      
      // Mark as synced
      for (final result in results) {
        final localTx = pendingBox.values
            .firstWhere((t) => t.localId == result.localId);
        localTx.isSynced = true;
        localTx.serverTransactionId = result.serverId;
        await localTx.save();
      }
    } catch (e) {
      // Log error, retry next time
      logger.error('Sync failed', e);
    }
  }
}

// WorkManager: background sync setiap kali ada koneksi
@pragma('vm:entry-point')
void callbackDispatcher() {
  Workmanager().executeTask((task, inputData) async {
    await SyncManager().syncPendingTransactions();
    return Future.value(true);
  });
}
```

---

## 6. Bluetooth Printer Integration

```dart
// lib/core/printer/bluetooth_printer.dart

class BluetoothPrinterService {
  Future<List<BluetoothDevice>> scanDevices() async {
    return await FlutterBluetoothPrinter.scan();
  }
  
  Future<void> printReceipt(ReceiptData receipt) async {
    final printer = await _getConnectedPrinter();
    if (printer == null) throw PrinterNotConnectedException();
    
    // Build ESC/POS commands
    final generator = Generator(PaperSize.mm58, await CapabilityProfile.load());
    List<int> bytes = [];
    
    // Header bisnis
    bytes += generator.text(
      receipt.businessName,
      styles: PosStyles(bold: true, align: PosAlign.center, height: PosTextSize.size2),
    );
    bytes += generator.text(receipt.outletAddress, styles: PosStyles(align: PosAlign.center));
    bytes += generator.hr();
    
    // Tanggal dan nomor transaksi
    bytes += generator.row([
      PosColumn(text: 'No: ${receipt.txNumber}', width: 8),
      PosColumn(text: DateFormat('dd/MM/yy HH:mm').format(receipt.date), width: 4),
    ]);
    bytes += generator.hr();
    
    // Items
    for (final item in receipt.items) {
      bytes += generator.row([
        PosColumn(text: item.name, width: 8),
        PosColumn(text: formatRupiah(item.total), width: 4, styles: PosStyles(align: PosAlign.right)),
      ]);
      if (item.modifiers.isNotEmpty) {
        bytes += generator.text('  + ${item.modifiers.join(", ")}', 
            styles: PosStyles(fontType: PosFontType.fontB));
      }
    }
    
    bytes += generator.hr(ch: '=');
    bytes += generator.row([
      PosColumn(text: 'TOTAL', width: 8, styles: PosStyles(bold: true)),
      PosColumn(text: formatRupiah(receipt.total), width: 4, 
          styles: PosStyles(bold: true, align: PosAlign.right)),
    ]);
    
    // Payment details
    for (final payment in receipt.payments) {
      bytes += generator.row([
        PosColumn(text: payment.method.toUpperCase(), width: 8),
        PosColumn(text: formatRupiah(payment.amount), width: 4, 
            styles: PosStyles(align: PosAlign.right)),
      ]);
    }
    
    if (receipt.change > 0) {
      bytes += generator.row([
        PosColumn(text: 'KEMBALI', width: 8),
        PosColumn(text: formatRupiah(receipt.change), width: 4, 
            styles: PosStyles(align: PosAlign.right)),
      ]);
    }
    
    bytes += generator.hr();
    bytes += generator.text(receipt.footer ?? 'Terima kasih!', 
        styles: PosStyles(align: PosAlign.center));
    bytes += generator.feed(3);
    bytes += generator.cut();
    
    await FlutterBluetoothPrinter.printBytes(printer.address, bytes);
  }
}
```

---

## 7. Barcode Scanner

```dart
// lib/features/pos/presentation/widgets/barcode_scanner_button.dart

class BarcodeScannerButton extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return IconButton(
      icon: Icon(Icons.qr_code_scanner),
      onPressed: () => _openScanner(context, ref),
    );
  }
  
  void _openScanner(BuildContext context, WidgetRef ref) {
    showModalBottomSheet(
      context: context,
      builder: (_) => SizedBox(
        height: 300,
        child: MobileScanner(
          onDetect: (capture) {
            final barcode = capture.barcodes.first.rawValue;
            if (barcode != null) {
              Navigator.pop(context);
              // Cari produk berdasarkan barcode
              ref.read(cartProvider.notifier).addByBarcode(barcode);
            }
          },
        ),
      ),
    );
  }
}
```

---

## 8. Push Notifications

```dart
// lib/core/notifications/fcm_service.dart

class FCMService {
  Future<void> initialize() async {
    // Request permission
    await FirebaseMessaging.instance.requestPermission(
      alert: true, badge: true, sound: true,
    );
    
    // Get token dan kirim ke server
    final token = await FirebaseMessaging.instance.getToken();
    await _updateDeviceToken(token!);
    
    // Listen token refresh
    FirebaseMessaging.instance.onTokenRefresh.listen(_updateDeviceToken);
    
    // Handle foreground notifications
    FirebaseMessaging.onMessage.listen(_handleForegroundMessage);
    
    // Handle background tap
    FirebaseMessaging.onMessageOpenedApp.listen(_handleNotificationTap);
  }
  
  void _handleForegroundMessage(RemoteMessage message) {
    // Show local notification
    FlutterLocalNotificationsPlugin().show(
      0,
      message.notification?.title,
      message.notification?.body,
      NotificationDetails(/* ... */),
    );
  }
}

// Notification types yang dikirim ke mobile:
// - stock.low_alert: Stok produk hampir habis
// - payment.received: Pembayaran QRIS berhasil (real-time update)
// - subscription.expiring: Subscription akan habis
// - sync.conflict: Konflik saat sync offline
```

---

## 9. UI/UX Guidelines Mobile

### 9.1 Design Principles

- **Touch target minimum: 48x48dp** — Jari orang berbeda ukurannya
- **Landscape-first untuk POS screen** — Kasir sering pakai landscape di tablet
- **Portrait-first untuk dashboard** — Owner cek laporan di portrait
- **Adaptif untuk phone dan tablet** — Responsive layout
- **Feedback haptic** — Setiap tap produk ke cart berikan haptic feedback
- **Optimistic UI** — Update UI dulu, sync ke server belakang

### 9.2 Color Palette

```dart
// lib/core/constants/app_colors.dart

class AppColors {
  // Brand
  static const primary     = Color(0xFF1E40AF);   // Blue-700
  static const secondary   = Color(0xFF7C3AED);   // Violet-600
  
  // Semantic
  static const success     = Color(0xFF16A34A);   // Green-600
  static const warning     = Color(0xFFD97706);   // Amber-600
  static const error       = Color(0xFFDC2626);   // Red-600
  
  // Neutral
  static const surface     = Color(0xFFFFFFFF);
  static const background  = Color(0xFFF8FAFC);
  static const border      = Color(0xFFE2E8F0);
  static const textPrimary = Color(0xFF0F172A);
  static const textMuted   = Color(0xFF64748B);
}
```

### 9.3 Typography

```dart
class AppTextStyles {
  static const h1 = TextStyle(fontSize: 28, fontWeight: FontWeight.bold);
  static const h2 = TextStyle(fontSize: 22, fontWeight: FontWeight.w600);
  static const h3 = TextStyle(fontSize: 18, fontWeight: FontWeight.w600);
  static const body = TextStyle(fontSize: 14, fontWeight: FontWeight.normal);
  static const caption = TextStyle(fontSize: 12, color: AppColors.textMuted);
  
  // POS specific
  static const price = TextStyle(
    fontSize: 16, 
    fontWeight: FontWeight.bold,
    fontFeatures: [FontFeature.tabularFigures()], // Angka lebar sama (alignment rapi)
  );
  static const totalAmount = TextStyle(
    fontSize: 24, 
    fontWeight: FontWeight.bold,
    color: AppColors.primary,
  );
}
```

---

## 10. App Distribution

### 10.1 Versioning Strategy

```
Version: MAJOR.MINOR.PATCH+BUILD
Contoh:  1.3.2+45

MAJOR: Breaking change (login baru, UI total redesign)
MINOR: Fitur baru (wave baru selesai)
PATCH: Bug fix
BUILD: Auto-increment di CI/CD
```

### 10.2 Release Channels

| Channel | Audience | Frekuensi | Cara Distribusi |
|---------|----------|-----------|----------------|
| **Dev** | Tim internal | Setiap push | Firebase App Distribution |
| **Beta** | Early adopters | Mingguan | Play Store Internal Track / TestFlight |
| **Staging** | QA + pilot users | 2 mingguan | Play Store Beta / TestFlight |
| **Production** | Semua user | Per fitur selesai | Play Store / App Store |

### 10.3 Force Update Mechanism

```dart
// Saat app launch, cek minimum supported version
Future<void> checkMinimumVersion() async {
  final remoteConfig = FirebaseRemoteConfig.instance;
  await remoteConfig.fetchAndActivate();
  
  final minVersion = remoteConfig.getString('min_app_version'); // "1.2.0"
  final currentVersion = await PackageInfo.fromPlatform().then(p => p.version);
  
  if (compareVersions(currentVersion, minVersion) < 0) {
    // Force update dialog — tidak bisa dismiss
    showForceUpdateDialog();
  }
}
```

---

## 11. Performance Targets

| Metrik | Target | Pengukuran |
|--------|--------|-----------|
| App cold start | < 3 detik | Firebase Performance |
| POS screen load | < 1 detik | Custom trace |
| Add item to cart | < 100ms | — |
| Barcode scan ke cart | < 500ms | Custom trace |
| Receipt print start | < 1 detik | — |
| Offline → sync time | < 30 detik setelah online | — |
| Memory usage (idle) | < 150MB | Firebase Performance |
| Frame rate | 60fps konsisten | DevTools |
| APK size | < 30MB | — |

---

*Blueprint ini inline dengan: BP-03 (MVP Features), BP-05 (Tech Stack), BP-07 (Project Structure)*
*Last updated: 2025 | Extended Synaptic — XynPOS*
