import 'package:flutter/material.dart';
import '../services/api_service.dart';
import 'package:razorpay_flutter/razorpay_flutter.dart';
import 'dart:async';

class WalletProvider with ChangeNotifier {
  ApiService? _apiService;
  Razorpay? _razorpay;

  bool _isLoading = false;
  Map<String, dynamic>? _walletBalance;
  List<dynamic> _transactions = [];
  List<dynamic> _withdrawals = [];
  Map<String, dynamic>? _bankDetails;
  String? _error;

  WalletProvider();

  void setApiService(ApiService apiService) {
    _apiService = apiService;
  }

  void _initRazorpay() {
    if (_razorpay == null) {
      _razorpay = Razorpay();
      // ignore: avoid_print
      print('🔧  Razorpay initialized');
    }
  }

  void disposeRazorpay() {
    _razorpay!.clear();
    _razorpay = null;
  }

  bool get isLoading => _isLoading;
  Map<String, dynamic>? get walletBalance => _walletBalance;
  List<dynamic> get transactions => _transactions;
  List<dynamic> get withdrawals => _withdrawals;
  Map<String, dynamic>? get bankDetails => _bankDetails;
  String? get error => _error;

  Future<void> loadWalletBalance() async {
    if (_apiService == null) return;

    _setLoading(true);
    _clearError();

    try {
      _walletBalance = await _apiService!.getWalletBalance();
      notifyListeners();
    } catch (e) {
      _setError(e.toString());
    } finally {
      _setLoading(false);
    }
  }

  Future<void> loadTransactions() async {
    if (_apiService == null) return;

    _setLoading(true);
    _clearError();

    try {
      final response = await _apiService!.getPayments();
      _transactions = response['items'] ?? [];
      notifyListeners();
    } catch (e) {
      _setError(e.toString());
    } finally {
      _setLoading(false);
    }
  }

  Future<bool> addMoneyToWallet(double amount, String description) async {
    if (_apiService == null) return false;

    _setLoading(true);
    _clearError();

    try {
      _initRazorpay();

      // 1) Create Razorpay order via backend
      final create = await _apiService!.createPayment(amount, description);
      // ignore: avoid_print
      print('🧾  Created payment: $create');
      final orderId = create['order_id'] as String;
      final razorpayOrderId = create['razorpay_order_id'] as String?;
      final razorpayKeyId = create['razorpay_key_id'] as String?;

      if (razorpayOrderId == null || razorpayKeyId == null) {
        throw Exception('Invalid Razorpay order response');
      }

      final completer = Completer<bool>();

      // Set up Razorpay event handlers
      _razorpay!.on(Razorpay.EVENT_PAYMENT_SUCCESS, (
        PaymentSuccessResponse response,
      ) async {
        // ignore: avoid_print
        print(
          '🎉  Razorpay SUCCESS: paymentId=${response.paymentId} orderId=${response.orderId} signature=${response.signature}',
        );
        // Start polling to confirm payment and credit wallet
        final ok = await _pollPaymentStatus(orderId);
        completer.complete(ok);
      });

      _razorpay!.on(Razorpay.EVENT_PAYMENT_ERROR, (
        PaymentFailureResponse response,
      ) async {
        // ignore: avoid_print
        print(
          '💥  Razorpay ERROR: code=${response.code} message=${response.message}',
        );
        // Still poll in case of late capture
        await _pollPaymentStatus(orderId);
        completer.complete(false);
      });

      _razorpay!.on(Razorpay.EVENT_EXTERNAL_WALLET, (
        ExternalWalletResponse response,
      ) async {
        // ignore: avoid_print
        print('👛  Razorpay EXTERNAL WALLET: ${response.walletName}');
        // External wallet chosen; proceed to poll backend
        final ok = await _pollPaymentStatus(orderId);
        completer.complete(ok);
      });

      // 2) Open Razorpay checkout
      final options = {
        'key': razorpayKeyId,
        'amount': (amount * 100).toInt(),
        'currency': 'INR',
        'name': 'Bindass Grand',
        'description': description,
        'order_id': razorpayOrderId,
        'timeout': 300, // 5 minutes
        'prefill': {'contact': '', 'email': ''},
        'theme': {'color': '#db9822'},
      };

      // ignore: avoid_print
      print('🧰  Opening Razorpay checkout with options: $options');
      _razorpay!.open(options);

      final success = await completer.future.timeout(
        const Duration(minutes: 16),
        onTimeout: () => false,
      );

      // Refresh data regardless
      await loadWalletBalance();
      await loadTransactions();
      return success;
    } catch (e) {
      // ignore: avoid_print
      print('🛑  Add money flow error: $e');
      _setError(e.toString());
      return false;
    } finally {
      _setLoading(false);
    }
  }

  Future<bool> _pollPaymentStatus(String orderId) async {
    if (_apiService == null) return false;
    const totalDuration = Duration(minutes: 15);
    const interval = Duration(seconds: 3);
    final started = DateTime.now();

    // ignore: avoid_print
    print(
      '⏰  Starting payment status polling for 15 minutes (every 3 seconds)',
    );

    while (DateTime.now().difference(started) < totalDuration) {
      try {
        final status = await _apiService!.getPaymentStatus(orderId);
        final dynamic raw = status['status'];
        final s = (raw == null ? null : raw.toString().toUpperCase());
        // ignore: avoid_print
        print('📡  Polled status: $status');

        if (s == 'SUCCESS') {
          // ignore: avoid_print
          print('✅  Payment successful!');
          return true;
        }
        if (s == 'FAILED' || s == 'CANCELLED' || s == 'EXPIRED') {
          // ignore: avoid_print
          print('❌  Payment failed/cancelled/expired');
          return false;
        }

        // ignore: avoid_print
        print('⏳  Payment still pending, waiting 3 seconds...');
      } catch (e) {
        // ignore: avoid_print
        print('⚠️  Polling error: $e');
      }
      await Future.delayed(interval);
    }

    // ignore: avoid_print
    print('⏰  Polling timeout after 15 minutes');
    return false;
  }

  Future<bool> requestWithdrawal(
    double amount,
    String bankDetailsId,
    String withdrawalMethod,
  ) async {
    if (_apiService == null) return false;

    _setLoading(true);
    _clearError();

    try {
      await _apiService!.requestWithdrawal(
        amount,
        bankDetailsId,
        withdrawalMethod,
      );
      await loadWalletBalance();
      await loadTransactions();
      return true;
    } catch (e) {
      _setError(e.toString());
      return false;
    } finally {
      _setLoading(false);
    }
  }

  Future<void> loadBankDetails() async {
    if (_apiService == null) return;

    _setLoading(true);
    _clearError();

    try {
      _bankDetails = await _apiService!.getBankDetails();
      notifyListeners();
    } catch (e) {
      _setError(e.toString());
    } finally {
      _setLoading(false);
    }
  }

  Future<bool> addBankDetails(Map<String, dynamic> bankData) async {
    if (_apiService == null) return false;

    _setLoading(true);
    _clearError();

    try {
      final res = await _apiService!.addBankDetails(bankData);
      _bankDetails = res;
      notifyListeners();
      return true;
    } catch (e) {
      _setError(e.toString());
      return false;
    } finally {
      _setLoading(false);
    }
  }

  void _setLoading(bool loading) {
    _isLoading = loading;
    notifyListeners();
  }

  void _setError(String error) {
    _error = error;
    notifyListeners();
  }

  void _clearError() {
    _error = null;
    notifyListeners();
  }
}
