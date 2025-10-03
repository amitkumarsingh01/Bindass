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
        
        // CRITICAL: Always poll backend to verify actual payment status
        // Don't trust Razorpay success alone - backend must confirm
        // ignore: avoid_print
        print('🔄  Polling backend to verify payment status...');
        final backendVerified = await _pollPaymentStatus(orderId);
        
        if (backendVerified) {
          // ignore: avoid_print
          print('✅  Backend confirms payment SUCCESS');
          completer.complete(true);
        } else {
          // ignore: avoid_print
          print('❌  Backend says payment FAILED despite Razorpay success');
          completer.complete(false);
        }
      });

      _razorpay!.on(Razorpay.EVENT_PAYMENT_ERROR, (
        PaymentFailureResponse response,
      ) async {
        // ignore: avoid_print
        print(
          '💥  Razorpay ERROR: code=${response.code} message=${response.message}',
        );
        
        // Even on Razorpay error, poll backend once to check if payment was captured
        // ignore: avoid_print
        print('🔍  Checking backend despite Razorpay error...');
        final backendCheck = await _pollPaymentStatus(orderId);
        
        // Only complete with true if backend confirms success
        completer.complete(backendCheck);
      });

      _razorpay!.on(Razorpay.EVENT_EXTERNAL_WALLET, (
        ExternalWalletResponse response,
      ) async {
        // ignore: avoid_print
        print('👛  Razorpay EXTERNAL WALLET: ${response.walletName}');
        
        // External wallet - must poll backend to confirm
        // ignore: avoid_print
        print('🔍  External wallet used, polling backend...');
        final backendResult = await _pollPaymentStatus(orderId);
        completer.complete(backendResult);
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
        const Duration(minutes: 12), // Increased timeout slightly
        onTimeout: () {
          // ignore: avoid_print
          print('⏰  Payment timeout - still refreshing wallet balance');
          return false;
        },
      );

      // Always refresh wallet data after payment attempt, regardless of success
      try {
        // ignore: avoid_print
        print('🔄  Refreshing wallet data after payment attempt');
        await loadWalletBalance();
        await loadTransactions();
        // ignore: avoid_print
        print('✅  Wallet data refreshed successfully');
      } catch (e) {
        // ignore: avoid_print
        print('❌  Error refreshing wallet data: $e');
      }
      
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
    const totalDuration = Duration(minutes: 10); // Changed to 10 minutes as requested
    const interval = Duration(seconds: 3);
    final started = DateTime.now();
    int pollCount = 0;

    // ignore: avoid_print
    print(
      '⏰  Starting payment status polling for 10 minutes (every 3 seconds)',
    );

    while (DateTime.now().difference(started) < totalDuration) {
      pollCount++;
      try {
        final status = await _apiService!.getPaymentStatus(orderId);
        final dynamic raw = status['status'];
        final s = (raw == null ? null : raw.toString().toUpperCase());
        
        // Add extra logging for debugging
        // ignore: avoid_print
        print('📊 Full API response: $status');
        // ignore: avoid_print
        print('📡  Poll #$pollCount - Status: $status');

        // STRICT: Only accept "SUCCESS" status from backend
        // Backend code shows it sets status to "SUCCESS" only when payment is truly successful
        if (s == 'SUCCESS') {
          // ignore: avoid_print
          print('✅  Payment verified SUCCESS by backend! Status: $s');
          // Force refresh wallet balance immediately after successful payment
          try {
            await loadWalletBalance();
            await loadTransactions();
            // ignore: avoid_print
            print('💰  Wallet balance refreshed after successful payment');
          } catch (e) {
            // ignore: avoid_print
            print('⚠️  Error refreshing wallet: $e');
          }
          return true;
        }
        
        // Check for failure conditions (be strict about failure states)
        if (s == 'FAILED' || s == 'CANCELLED' || s == 'EXPIRED' || s == 'REJECTED' || s == 'PENDING') {
          if (s == 'PENDING') {
            // ignore: avoid_print
            print('⏳  Payment still PENDING (status: $s), continuing to poll...');
          } else {
            // ignore: avoid_print
            print('❌  Payment FAILED (status: $s), stopping polling');
            return false;
          }
        } else {
          // ignore: avoid_print
          print('⚠️  Unknown payment status: $s, continuing to poll...');
        }
      } catch (e) {
        // ignore: avoid_print
        print('⚠️  Polling error on attempt #$pollCount: $e');
      }
      
      // Wait before next poll
      await Future.delayed(interval);
    }

    // ignore: avoid_print
    print('⏰  Polling timeout after 10 minutes ($pollCount attempts)');
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
      // Immediately reflect debited balance on UI without waiting for a full reload
      if (_walletBalance != null) {
        final current = (_walletBalance!['walletBalance'] as num? ?? 0)
            .toDouble();
        _walletBalance!['walletBalance'] = (current - amount).clamp(
          0,
          double.infinity,
        );
        notifyListeners();
      }
      // Refresh both wallet and withdrawals list so UI reflects status and balance
      await loadWalletBalance();
      await fetchWithdrawals();
      await loadTransactions();
      return true;
    } catch (e) {
      _setError(e.toString());
      return false;
    } finally {
      _setLoading(false);
    }
  }

  Future<void> fetchWithdrawals() async {
    if (_apiService == null) return;

    try {
      final res = await _apiService!.getWithdrawals();
      _withdrawals = res['withdrawals'] ?? [];
      notifyListeners();
    } catch (_) {
      // ignore network errors silently for this refresh call
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
