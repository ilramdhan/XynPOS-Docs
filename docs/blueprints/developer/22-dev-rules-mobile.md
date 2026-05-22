# XynPOS — Blueprint 22: Development Rules — Mobile (Flutter/Dart)
> Extended Synaptic | Version 1.0 | Mandatory for all Mobile developers

---

## 1. Project Structure Rules

### ✅ WAJIB: Feature-First Architecture

```
lib/
├── core/          ← Infrastructure (tidak boleh import features)
├── features/      ← Business features
│   └── pos/
│       ├── data/
│       │   ├── datasources/     ← Remote & local data sources
│       │   ├── models/          ← JSON serializable data models
│       │   └── repositories/    ← Repository implementations
│       ├── domain/
│       │   ├── entities/        ← Pure business entities (no JSON annotation)
│       │   ├── repositories/    ← Repository interfaces (abstract class)
│       │   └── usecases/        ← Business use cases
│       └── presentation/
│           ├── providers/       ← Riverpod providers + state notifiers
│           ├── screens/         ← Screen widgets (route targets)
│           └── widgets/         ← Feature-specific widgets
└── shared/        ← Shared widgets & utilities
```

### ✅ WAJIB: Layer Dependency Rules

```
presentation  → dapat import domain dan shared
domain        → TIDAK BOLEH import data atau presentation
data          → dapat import domain, core
core          → TIDAK BOLEH import features

Contoh:
✅ CartProvider import CartRepository (domain/repositories)
✅ CartRepositoryImpl import CartRemoteDatasource (data)
❌ CartEntity import Dio (core/network)
❌ CartProvider import Hive langsung (harusnya via repository)
```

---

## 2. State Management Rules (Riverpod)

### ✅ WAJIB: Gunakan AsyncValue untuk Semua Async State

```dart
// ✅ BENAR: AsyncNotifier untuk async state
class ProductsNotifier extends AsyncNotifier<List<Product>> {
  @override
  Future<List<Product>> build() async {
    return ref.watch(productRepositoryProvider).getProducts();
  }
  
  Future<void> refresh() async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() =>
      ref.read(productRepositoryProvider).getProducts()
    );
  }
}

final productsProvider = AsyncNotifierProvider<ProductsNotifier, List<Product>>(
  ProductsNotifier.new,
);

// ✅ Di widget: handle semua states
Widget build(BuildContext context, WidgetRef ref) {
  final productsAsync = ref.watch(productsProvider);
  
  return productsAsync.when(
    loading: () => const LoadingSpinner(),
    error: (err, stack) => ErrorWidget(error: err),
    data: (products) => ProductGrid(products: products),
  );
}
```

### ✅ WAJIB: Provider Granularity

```dart
// ✅ BENAR: provider yang focused dan granular
final cartItemsProvider = Provider<List<CartItem>>((ref) =>
  ref.watch(cartProvider).items
);

final cartTotalProvider = Provider<double>((ref) =>
  ref.watch(cartProvider).items.fold(0, (sum, item) =>
    sum + item.price * item.quantity)
);

// Widget hanya watch apa yang dibutuhkan (tidak rebuild jika yang lain berubah)
Widget build(BuildContext context, WidgetRef ref) {
  final total = ref.watch(cartTotalProvider);  // Hanya rebuild saat total berubah
  return Text('Total: ${formatRupiah(total)}');
}

// ❌ JANGAN watch seluruh CartState jika hanya butuh total
final cartState = ref.watch(cartProvider);  // Rebuild tiap ada perubahan apapun di cart
```

### ✅ WAJIB: Dispose dan Lifecycle Management

```dart
// ✅ Gunakan ref.onDispose untuk cleanup
class WebSocketNotifier extends Notifier<ConnectionState> {
  late WebSocketChannel _channel;
  
  @override
  ConnectionState build() {
    _channel = WebSocketChannel.connect(Uri.parse(wsUrl));
    
    // Cleanup saat provider di-dispose
    ref.onDispose(() {
      _channel.sink.close();
    });
    
    return ConnectionState.connecting;
  }
}
```

---

## 3. Widget Rules

### ✅ WAJIB: ConsumerWidget bukan StatelessWidget untuk Widget yang Watch Provider

```dart
// ✅ BENAR
class ProductCard extends ConsumerWidget {
  const ProductCard({super.key, required this.product});
  final Product product;
  
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final isSelected = ref.watch(selectedProductProvider(product.id));
    return GestureDetector(/* ... */);
  }
}

// ❌ SALAH: pakai StatelessWidget lalu Consumer di dalam
class ProductCard extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Consumer(builder: (context, ref, _) {  // Unnecessary nesting
      // ...
    });
  }
}
```

### ✅ WAJIB: Extract Widget untuk Reusability

```dart
// ✅ BENAR: extract ke widget terpisah jika dipakai > 1 kali atau kompleks
class PriceTag extends StatelessWidget {
  const PriceTag({super.key, required this.price, this.style});
  final double price;
  final TextStyle? style;
  
  @override
  Widget build(BuildContext context) {
    return Text(
      formatRupiah(price),
      style: style ?? AppTextStyles.price,
    );
  }
}

// ❌ JANGAN duplikasi UI code
// File A:
Text(formatRupiah(price), style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16))
// File B:
Text(formatRupiah(price), style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16))
```

### ✅ WAJIB: const Constructor untuk Widget Static

```dart
// ✅ BENAR: const constructor → tidak rebuild unnecessarily
class LoadingSpinner extends StatelessWidget {
  const LoadingSpinner({super.key});  // ← const!
  
  @override
  Widget build(BuildContext context) {
    return const Center(child: CircularProgressIndicator());  // ← const!
  }
}

// Penggunaan:
const LoadingSpinner()  // ← const! tidak membuat instance baru setiap build
```

---

## 4. Data Layer Rules

### ✅ WAJIB: Model dan Entity Terpisah

```dart
// Entity (domain) — pure business object, tidak ada JSON annotation
class Product {
  final String id;
  final String name;
  final double price;
  final int stock;
  
  const Product({
    required this.id,
    required this.name,
    required this.price,
    required this.stock,
  });
  
  // Business logic boleh di sini
  bool get isAvailable => stock > 0 && isActive;
}

// Model (data) — untuk serialisasi JSON dari API
@JsonSerializable()
class ProductModel {
  @JsonKey(name: 'id')
  final String id;
  
  @JsonKey(name: 'name')
  final String name;
  
  @JsonKey(name: 'selling_price')
  final double sellingPrice;
  
  factory ProductModel.fromJson(Map<String, dynamic> json) =>
      _$ProductModelFromJson(json);
  
  // Konversi ke domain entity
  Product toEntity() => Product(
    id: id,
    name: name,
    price: sellingPrice,
    stock: stockQuantity,
  );
}
```

### ✅ WAJIB: Repository Pattern

```dart
// Domain: abstract class (interface)
abstract class ProductRepository {
  Future<Either<Failure, List<Product>>> getProducts({ProductFilter? filter});
  Future<Either<Failure, Product>> getProductById(String id);
  Future<Either<Failure, Product>> createProduct(CreateProductParams params);
}

// Data: implementation
class ProductRepositoryImpl implements ProductRepository {
  final ProductRemoteDatasource _remote;
  final ProductLocalDatasource _local;
  
  @override
  Future<Either<Failure, List<Product>>> getProducts({ProductFilter? filter}) async {
    try {
      // Coba dari cache dulu
      final cached = await _local.getCachedProducts();
      if (cached.isNotEmpty) return Right(cached.map((m) => m.toEntity()).toList());
      
      // Fetch dari API
      final models = await _remote.getProducts(filter: filter);
      await _local.cacheProducts(models);
      return Right(models.map((m) => m.toEntity()).toList());
    } on ServerException catch (e) {
      return Left(ServerFailure(message: e.message));
    } on NetworkException {
      return Left(NetworkFailure());
    }
  }
}
```

---

## 5. Offline Mode Rules

### ✅ WAJIB: Semua Transaksi POS Harus Bisa Offline

```dart
// Setiap transaksi kasir harus:
// 1. Simpan ke Hive lokal DULU
// 2. Update stok lokal
// 3. Coba sync ke server (jika online)
// 4. Jika offline → masuk ke sync queue

class PosRepositoryImpl implements PosRepository {
  @override
  Future<Either<Failure, Transaction>> createTransaction(
    CreateTransactionParams params
  ) async {
    // 1. Generate local ID
    final localId = '${deviceId}_${DateTime.now().millisecondsSinceEpoch}';
    
    // 2. Simpan lokal dulu
    final localTx = PendingTransactionModel(
      localId: localId,
      params: params,
      createdAt: DateTime.now(),
      isSynced: false,
    );
    await _localDatasource.savePendingTransaction(localTx);
    
    // 3. Update stok lokal (optimistic)
    await _localDatasource.updateLocalStock(params);
    
    // 4. Coba sync ke server
    if (await _networkInfo.isConnected) {
      try {
        final serverTx = await _remote.createTransaction(
          params.copyWith(localId: localId)
        );
        await _localDatasource.markAsSynced(localId, serverTx.id);
        return Right(serverTx.toEntity());
      } on ServerException {
        // Gagal sync — akan dicoba lagi nanti via SyncManager
      }
    }
    
    // Return local transaction
    return Right(localTx.toEntity());
  }
}
```

### ✅ WAJIB: Idempotency untuk Sync

```dart
// Server HARUS menangani duplikat saat sync
// Client kirim localId, server gunakan ini sebagai idempotency key
// Jika server sudah punya localId ini → return existing transaction, jangan buat baru
```

---

## 6. Error Handling Rules

### ✅ WAJIB: Either Pattern untuk Error Handling

```dart
// Gunakan Either<Failure, T> untuk return value dari repository
// Left = error, Right = success

// Di usecase:
Future<Either<Failure, Transaction>> call(CreateTransactionParams params) async {
  // Validasi
  if (params.items.isEmpty) return Left(ValidationFailure('Cart kosong'));
  
  // Delegate ke repository
  return await repository.createTransaction(params);
}

// Di Riverpod Notifier:
Future<void> createTransaction(CreateTransactionParams params) async {
  state = const AsyncValue.loading();
  
  final result = await ref.read(createTransactionUsecaseProvider).call(params);
  
  result.fold(
    (failure) => state = AsyncValue.error(failure, StackTrace.current),
    (transaction) {
      state = AsyncValue.data(transaction);
      // Navigate ke receipt screen
    },
  );
}
```

### ✅ WAJIB: Failure Types

```dart
// Definisikan semua failure types
abstract class Failure {
  final String message;
  const Failure({required this.message});
}

class ServerFailure extends Failure {
  final int? statusCode;
  const ServerFailure({required String message, this.statusCode}) : super(message: message);
}

class NetworkFailure extends Failure {
  const NetworkFailure() : super(message: 'Tidak ada koneksi internet');
}

class ValidationFailure extends Failure {
  const ValidationFailure(String message) : super(message: message);
}

class CacheFailure extends Failure {
  const CacheFailure(String message) : super(message: message);
}

class InsufficientStockFailure extends Failure {
  final String productName;
  const InsufficientStockFailure({required this.productName})
    : super(message: 'Stok $productName tidak mencukupi');
}
```

---

## 7. Performance Rules

### ✅ WAJIB: ListView.builder untuk List Panjang

```dart
// ✅ BENAR: builder — hanya render yang visible
ListView.builder(
  itemCount: products.length,
  itemBuilder: (context, index) => ProductCard(product: products[index]),
)

// ❌ SALAH: column dengan semua children — semua dirender sekaligus!
Column(
  children: products.map((p) => ProductCard(product: p)).toList(),
)
```

### ✅ WAJIB: Image Caching

```dart
// ✅ BENAR: pakai cached_network_image
CachedNetworkImage(
  imageUrl: product.imageUrl ?? '',
  placeholder: (context, url) => const ProductImagePlaceholder(),
  errorWidget: (context, url, error) => const ProductImagePlaceholder(),
  fit: BoxFit.cover,
)

// ❌ SALAH: Image.network tanpa caching
Image.network(product.imageUrl)  // Re-download setiap build!
```

### ✅ WAJIB: RepaintBoundary untuk Animasi

```dart
// Isolasi bagian yang sering repaint
RepaintBoundary(
  child: AnimatedCartBadge(count: cartCount),
)
```

---

## 8. Platform-Specific Rules

### ✅ WAJIB: Permission Request yang Sopan

```dart
// Selalu jelaskan mengapa butuh permission sebelum request
Future<bool> requestCameraPermission(BuildContext context) async {
  // Cek status dulu
  final status = await Permission.camera.status;
  if (status.isGranted) return true;
  
  // Tampilkan dialog penjelasan
  if (status.isDenied) {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Izin Kamera Diperlukan'),
        content: const Text(
          'XynPOS membutuhkan akses kamera untuk scan barcode produk. '
          'Izin ini hanya digunakan saat kamu menekan tombol scan.'
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Tidak')),
          TextButton(onPressed: () => Navigator.pop(context, true), child: const Text('Izinkan')),
        ],
      ),
    );
    if (confirmed != true) return false;
  }
  
  final result = await Permission.camera.request();
  return result.isGranted;
}
```

---

## 9. Testing Rules

### ✅ WAJIB: Test untuk Semua Business Use Cases

```dart
void main() {
  group('CreateTransactionUsecase', () {
    late MockTransactionRepository mockRepo;
    late CreateTransactionUsecase usecase;
    
    setUp(() {
      mockRepo = MockTransactionRepository();
      usecase = CreateTransactionUsecase(repository: mockRepo);
    });
    
    test('returns failure ketika cart kosong', () async {
      final result = await usecase(
        CreateTransactionParams(items: [], payments: [])
      );
      
      expect(result.isLeft(), true);
      expect(result.fold((l) => l, (_) => null), isA<ValidationFailure>());
    });
    
    test('sukses membuat transaksi dengan data valid', () async {
      when(mockRepo.createTransaction(any))
        .thenAnswer((_) async => Right(mockTransaction));
      
      final result = await usecase(validParams);
      
      expect(result.isRight(), true);
    });
  });
}
```

---

## 10. Code Review Checklist (Mobile Self-Review)

```
ARCHITECTURE:
[ ] Layer dependency tidak dilanggar (domain tidak import infra)
[ ] Semua repository pakai interface di domain
[ ] Model dan Entity terpisah

STATE MANAGEMENT:
[ ] AsyncValue dipakai untuk semua async state
[ ] Provider granular (tidak watch seluruh state jika hanya butuh sebagian)
[ ] Semua subscription di-dispose

OFFLINE:
[ ] Transaksi POS bisa jalan tanpa internet
[ ] Local ID (idempotency) ada di semua write operations
[ ] Sync queue untuk pending transactions

ERROR HANDLING:
[ ] Either<Failure, T> untuk semua repository return value
[ ] Failure types spesifik (bukan generic String)
[ ] UI menampilkan error state yang informatif

PERFORMANCE:
[ ] ListView.builder untuk list > 10 items
[ ] CachedNetworkImage untuk semua network images
[ ] const constructor untuk static widgets

TESTING:
[ ] Semua use case ada unit test
[ ] Widget test untuk komponen POS kritikal
```

---

*Last updated: 2025 | Extended Synaptic — XynPOS*
