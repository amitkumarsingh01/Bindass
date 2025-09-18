import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/contact_model.dart';
import '../services/api_service.dart';

class ContactProvider with ChangeNotifier {
  final SharedPreferences _prefs;
  late ApiService _apiService;

  bool _isLoading = false;
  ContactModel? _contactInfo;
  String? _error;

  ContactProvider(this._prefs) {
    _apiService = ApiService(_prefs);
  }

  bool get isLoading => _isLoading;
  ContactModel? get contactInfo => _contactInfo;
  String? get error => _error;

  Future<void> loadContactInfo() async {
    _setLoading(true);
    _clearError();

    try {
      final response = await _apiService.getContactInfo();
      _contactInfo = ContactModel.fromJson(response);
      notifyListeners();
    } catch (e) {
      _setError(e.toString());
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
