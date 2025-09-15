import 'package:flutter/material.dart';
import '../services/api_service.dart';
import 'package:shared_preferences/shared_preferences.dart';

class WalletProvider with ChangeNotifier {
  ApiService? _apiService;
  
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
      final response = await _apiService!.getWalletTransactions();
      _transactions = response['transactions'] ?? [];
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
      await _apiService!.addMoneyToWallet(amount, description);
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

  Future<bool> requestWithdrawal(double amount, String bankDetailsId, String withdrawalMethod) async {
    if (_apiService == null) return false;
    
    _setLoading(true);
    _clearError();

    try {
      await _apiService!.requestWithdrawal(amount, bankDetailsId, withdrawalMethod);
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
      await _apiService!.addBankDetails(bankData);
      await loadBankDetails();
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
