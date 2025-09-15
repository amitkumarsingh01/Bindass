import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../services/api_service.dart';

class AuthProvider with ChangeNotifier {
  final SharedPreferences _prefs;
  late ApiService _apiService;
  
  bool _isLoading = false;
  bool _isAuthenticated = false;
  Map<String, dynamic>? _user;
  String? _error;

  AuthProvider(this._prefs) {
    _apiService = ApiService(_prefs);
    _checkAuthStatus();
  }

  ApiService get apiService => _apiService;

  bool get isLoading => _isLoading;
  bool get isAuthenticated => _isAuthenticated;
  Map<String, dynamic>? get user => _user;
  String? get error => _error;

  void _checkAuthStatus() {
    final userId = _prefs.getString('user_id');
    if (userId != null && userId.isNotEmpty) {
      _isAuthenticated = true;
      _loadUserData();
    }
  }

  Future<void> _loadUserData() async {
    try {
      _user = await _apiService.getCurrentUser();
      notifyListeners();
    } catch (e) {
      await logout();
    }
  }

  Future<bool> login(String identifier, String password) async {
    _setLoading(true);
    _clearError();

    try {
      await _apiService.login(identifier, password);
      // Persist password for subsequent privileged actions (e.g., wallet add/withdraw)
      await _prefs.setString('user_password', password);
      _isAuthenticated = true;
      await _loadUserData();
      notifyListeners();
      return true;
    } catch (e) {
      _setError(e.toString());
      return false;
    } finally {
      _setLoading(false);
    }
  }

  Future<bool> register(Map<String, dynamic> userData) async {
    _setLoading(true);
    _clearError();

    try {
      await _apiService.register(userData);
      return true;
    } catch (e) {
      _setError(e.toString());
      return false;
    } finally {
      _setLoading(false);
    }
  }

  Future<void> logout() async {
    await _apiService.logout();
    _isAuthenticated = false;
    _user = null;
    _clearError();
    notifyListeners();
  }

  Future<bool> updateProfile(Map<String, dynamic> profileData) async {
    _setLoading(true);
    _clearError();

    try {
      _user = await _apiService.updateProfile(profileData);
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
