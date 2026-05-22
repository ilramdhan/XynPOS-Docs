---
name: xynpos-mobile
description: XynPOS Flutter mobile development — use when writing Flutter/Dart code for the XynPOS mobile app including the POS kasir screen, offline transaction handling, Riverpod state management, Bluetooth thermal printer integration, barcode scanning, or push notifications. Triggers when working on any Flutter feature, fixing Flutter bugs, designing mobile UI, implementing offline-first functionality, or asking about Flutter architecture patterns. Also triggers for questions about offline sync, Hive storage, WorkManager background tasks, or mobile-specific POS features.
license: See LICENSE.txt
---

# XynPOS Flutter Mobile Development

The Flutter app (`mobile/xynpos_mobile/`) is the **primary kasir interface** — 80%+ of daily POS usage happens here.

## Reference Files
- Architecture & feature structure → `references/flutter-arch.md`  
- Offline mode implementation → `references/offline-mode.md`
- Bluetooth printer guide → `references/bt-printer.md`

## Stack

```yaml
flutter_riverpod: ^2.5    # State management
go_router: ^14            # Navigation  
dio: ^5.4                 # HTTP with interceptors
hive_flutter: ^1.1        # Offline key-value storage
sqflite: ^2.3             # Offline relational queries
freezed: ^2.5             # Immutable data classes
json_serializable: ^6.8   # JSON serialization
dartz: ^0.10              # Either<Failure, T>
mobile_scanner: ^5        # Barcode/QR scanner
flutter_bluetooth_printer  # Thermal printer
cached_network_image       # Image caching
connectivity_plus           # Network detection
workmanager: ^0.5          # Background sync
```

## Architecture (Feature-First + Clean)

```
lib/
├── core/                  Infrastructure (NO business logic)
│   ├── network/dio_client.dart
│   ├── storage/hive_service.dart
│   ├── offline/sync_manager.dart
│   └── di/injection.dart
└── features/pos/
    ├── data/
    │   ├── datasources/     Remote API + local Hive
    │   ├── models/          JSON-annotated (fromJson/toJson)
    │   └── repositories/    Implements domain interface
    ├── domain/
    │   ├── entities/        Pure Dart classes (NO JSON)
    │   ├── repositories/    abstract class (interface)
    │   └── usecases/        Single-responsibility business actions
    └── presentation/
        ├── providers/       Riverpod AsyncNotifier/Notifier
        ├── screens/         Route targets
        └── widgets/         Reusable UI
```

## Non-Negotiable Rules

```dart
// ✅ AsyncValue for ALL async state
ref.watch(transactionsProvider).when(
  loading: () => const LoadingSpinner(),
  error: (e, _) => ErrorWidget(message: e.toString()),
  data: (txs) => TransactionList(transactions: txs),
);

// ✅ Either<Failure, T> from repositories
Future<Either<Failure, Transaction>> createTransaction(params) async { ... }

// ✅ Separate Model (data) from Entity (domain)
// ProductModel has fromJson/toJson — ProductEntity has business methods

// ✅ const constructor for static widgets
class LoadingSpinner extends StatelessWidget {
  const LoadingSpinner({super.key});
}

// ✅ ListView.builder for lists (NEVER Column+children for lists > 10)
ListView.builder(itemCount: n, itemBuilder: (_, i) => ItemWidget(items[i]))

// ✅ CachedNetworkImage (NEVER Image.network)
CachedNetworkImage(imageUrl: url, placeholder: (_, __) => Skeleton())

// ✅ ALL POS transactions must work offline
// Save to Hive first → update local stock → try sync → queue if offline
```

## Offline First Pattern

```dart
Future<Either<Failure, Transaction>> createTransaction(params) async {
  // 1. Always save locally first (idempotency key)
  final localId = '${deviceId}_${DateTime.now().ms}';
  await _local.savePending(PendingTx(localId: localId, ...));
  await _local.decrementStock(params.items);  // optimistic
  
  // 2. Try server if online
  if (await _connectivity.isConnected) {
    try {
      final serverTx = await _remote.createTransaction(params.copyWith(localId: localId));
      await _local.markSynced(localId, serverTx.id);
      return Right(serverTx.toEntity());
    } catch (_) { /* will sync later */ }
  }
  return Right(localTx);  // return local version
}
```

## Scripts

Run `scripts/check_flutter_rules.py <path>` to scan Flutter files for violations.
