import 'package:flutter/material.dart';
import '../services/api_service.dart';
import 'package:razorpay_flutter/razorpay_flutter.dart';
import 'package:url_launcher/url_launcher.dart';
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
    _razorpay ??= Razorpay();
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

      // 1) Create payment link via backend
      final create = await _apiService!.createPayment(amount, description);
      // ignore: avoid_print
      print('🧾  Created payment: $create');
      final orderId = create['order_id'] as String;
      final paymentLink = create['payment_link'] as String?;

      if (paymentLink == null) {
        throw Exception('Invalid payment link response');
      }

      // 2) Open payment link in browser
      // ignore: avoid_print
      print('🔗  Opening payment link: $paymentLink');

      final uri = Uri.parse(paymentLink);
      if (await canLaunchUrl(uri)) {
        await launchUrl(uri, mode: LaunchMode.externalApplication);
        // ignore: avoid_print
        print('🌐  Payment link opened in browser');
      } else {
        throw Exception('Could not open payment link');
      }

      // Start polling immediately for 15 minutes
      final success = await _pollPaymentStatus(orderId);

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
