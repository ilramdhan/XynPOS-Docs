---
skill_id: SKILL-04
name: XynPOS Flutter Mobile Development
category: mobile
description: Skill untuk Flutter mobile app — kasir, offline mode, Riverpod, BT printer
version: 1.0.0
applies_to: [mobile, flutter, dart, ios, android]
depends_on: [SKILL-00]
---

# SKILL-04: Flutter Mobile Development

## Stack

```yaml
# pubspec.yaml key dependencies
flutter_riverpod: ^2.5       # State management
go_router: ^14               # Navigation
dio: ^5.4                    # HTTP client
hive_flutter: ^1.1           # Offline key-value storage
sqflite: ^2.3                # Offline SQLite
freezed: ^2.5                # Immutable data classes
json_serializable: ^6.8      # JSON serialization
dartz: ^0.10                 # Either<Failure, T>
mobile_scanner: ^5           # Barcode/QR scanner
flutter_bluetooth_printer: ^5 # BT thermal printer
cached_network_image: ^3.3   # Image caching
connectivity_plus: ^6        # Network detection
workmanager: ^0.5            # Background sync
flutter_secure_storage: ^9   # Token storage
firebase_messaging: ^15      # Push notifications
firebase_crashlytics: ^4     # Crash reporting
```

## Architecture (Feature-First + Clean Architecture)

```
lib/
├── core/                    ← Infrastructure
│   ├── network/dio_client.dart
│   ├── storage/hive_service.dart
│   ├── offline/sync_manager.dart
│   └── di/injection.dart
├── features/
│   └── pos/
│       ├── data/
│       │   ├── datasources/pos_remote_datasource.dart
│       │   ├── models/transaction_model.dart     ← JSON annotations
│       │   └── repositories/pos_repository_impl.dart
│       ├── domain/
│       │   ├── entities/transaction.dart         ← Pure business entity
│       │   ├── repositories/pos_repository.dart  ← Abstract interface
│       │   └── usecases/create_transaction_usecase.dart
│       └── presentation/
│           ├── providers/cart_provider.dart
│           ├── screens/pos_screen.dart
│           └── widgets/product_card.dart
└── shared/widgets/          ← Shared UI components
```

## Layer Rules

```dart
// ✅ Domain entity: pure, no JSON, no framework
class Transaction {
  final String id;
  final double totalAmount;
  final List<TransactionItem> items;
  bool get isPaid => paidAmount >= totalAmount;
}

// ✅ Data model: JSON serializable
@JsonSerializable()
class TransactionModel {
  @JsonKey(name: 'total_amount') final double totalAmount;
  Transaction toEntity() => Transaction(totalAmount: totalAmount, ...);
}

// ❌ Domain entity TIDAK BOLEH import Dio, Hive, Flutter
// ❌ Domain entity TIDAK BOLEH have fromJson/toJson
```

## Riverpod State Patterns

```dart
// ✅ AsyncNotifier untuk async state
class TransactionsNotifier extends AsyncNotifier<List<Transaction>> {
  @override
  Future<List<Transaction>> build() async =>
    ref.watch(transactionRepositoryProvider).getTransactions();
}
final transactionsProvider = AsyncNotifierProvider<TransactionsNotifier, List<Transaction>>(
  TransactionsNotifier.new,
);

// ✅ AsyncValue handling di UI — handle all 3 states
ref.watch(transactionsProvider).when(
  loading: () => const LoadingSpinner(),
  error: (e, _) => ErrorWidget(message: e.toString()),
  data: (txs) => TransactionList(transactions: txs),
);

// ✅ Granular provider — watch only what you need
final cartTotalProvider = Provider<double>((ref) =>
  ref.watch(cartProvider).items.fold(0.0, (sum, i) => sum + i.subtotal)
);

// ✅ Cleanup resources
ref.onDispose(() => _subscription.cancel());
```

## Either Error Handling

```dart
// Repository returns Either<Failure, T>
abstract class TransactionRepository {
  Future<Either<Failure, Transaction>> createTransaction(CreateTransactionParams p);
}

// Failure types
abstract class Failure { final String message; }
class ServerFailure extends Failure { final int? statusCode; }
class NetworkFailure extends Failure { const NetworkFailure() : super(message: 'No internet'); }
class InsufficientStockFailure extends Failure { final String productName; }

// Use in notifier
Future<void> createTransaction(CreateTransactionParams params) async {
  state = const AsyncValue.loading();
  final result = await ref.read(createTransactionUsecaseProvider)(params);
  result.fold(
    (failure) => state = AsyncValue.error(failure.message, StackTrace.current),
    (tx) {
      state = AsyncValue.data(tx);
      ref.read(cartProvider.notifier).clear();
      context.go('/receipt', extra: tx);
    },
  );
}
```

## Offline Mode (CRITICAL for POS)

```dart
// ✅ Transaksi kasir WAJIB bisa offline
Future<Either<Failure, Transaction>> createTransaction(params) async {
  // 1. Generate local ID (idempotency key)
  final localId = '${deviceId}_${DateTime.now().millisecondsSinceEpoch}';
  
  // 2. Save to Hive FIRST
  await _local.savePending(PendingTransactionModel(localId: localId, params: params));
  
  // 3. Update local stock (optimistic)
  await _local.decrementStock(params.items);
  
  // 4. Try sync if online
  if (await _connectivity.isConnected) {
    try {
      final serverTx = await _remote.createTransaction(params.copyWith(localId: localId));
      await _local.markSynced(localId, serverTx.id);
      return Right(serverTx.toEntity());
    } on Exception { /* will sync later */ }
  }
  
  return Right(localId: localId, ...); // return local transaction
}

// WorkManager background sync
@pragma('vm:entry-point')
void callbackDispatcher() {
  Workmanager().executeTask((task, _) async {
    await SyncManager().syncPendingTransactions();
    return true;
  });
}
```

## Bluetooth Printer

```dart
Future<void> printReceipt(ReceiptData receipt) async {
  final printer = await _getConnectedPrinter();
  final gen = Generator(PaperSize.mm58, await CapabilityProfile.load());
  List<int> bytes = [];
  
  bytes += gen.text(receipt.businessName,
    styles: PosStyles(bold: true, align: PosAlign.center, height: PosTextSize.size2));
  bytes += gen.hr();
  
  for (final item in receipt.items) {
    bytes += gen.row([
      PosColumn(text: '${item.qty}x ${item.name}', width: 8),
      PosColumn(text: formatRupiah(item.total), width: 4,
        styles: PosStyles(align: PosAlign.right)),
    ]);
  }
  
  bytes += gen.hr(ch: '=');
  bytes += gen.row([
    PosColumn(text: 'TOTAL', width: 8, styles: PosStyles(bold: true)),
    PosColumn(text: formatRupiah(receipt.total), width: 4,
      styles: PosStyles(bold: true, align: PosAlign.right)),
  ]);
  bytes += gen.feed(3);
  bytes += gen.cut();
  
  await FlutterBluetoothPrinter.printBytes(printer.address, bytes);
}
```

## Widget Rules

```dart
// ✅ const constructor untuk static widgets
class LoadingSpinner extends StatelessWidget {
  const LoadingSpinner({super.key});
  @override Widget build(ctx) => const Center(child: CircularProgressIndicator());
}

// ✅ ConsumerWidget untuk widgets yang watch provider
class CartTotal extends ConsumerWidget {
  @override Widget build(ctx, ref) {
    final total = ref.watch(cartTotalProvider);
    return Text(formatRupiah(total), style: AppTextStyles.totalAmount);
  }
}

// ✅ ListView.builder untuk list (BUKAN Column + children)
ListView.builder(
  itemCount: products.length,
  itemBuilder: (ctx, i) => ProductCard(product: products[i]),
)

// ✅ CachedNetworkImage untuk semua network images
CachedNetworkImage(
  imageUrl: product.imageUrl ?? '',
  placeholder: (_, __) => const ProductImageSkeleton(),
  errorWidget: (_, __, ___) => const ProductImageFallback(),
)
```

## Checklist Sebelum PR

```
[ ] Layer dependency tidak dilanggar (domain bebas dari infra)
[ ] Model dan Entity TERPISAH
[ ] Either<Failure, T> untuk semua repository return value
[ ] Failure types spesifik
[ ] AsyncValue untuk semua async state
[ ] Transaksi POS bisa offline
[ ] Local ID (idempotency) di semua write operations
[ ] const constructor untuk static widgets
[ ] ListView.builder untuk list > 10 items
[ ] CachedNetworkImage untuk network images
[ ] Unit test untuk semua use cases
[ ] Widget test untuk POS critical components
```
