import 'package:flutter/material.dart';
import '../services/api_service.dart';

class HomeSliderProvider with ChangeNotifier {
  List<dynamic> _sliders = [];
  bool _isLoading = false;
  String? _error;
  ApiService? _apiService;

  List<dynamic> get sliders => _sliders;
  bool get isLoading => _isLoading;
  String? get error => _error;

  void setApiService(ApiService apiService) {
    _apiService = apiService;
  }

  Future<void> loadSliders() async {
    if (_apiService == null) return;

    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final response = await _apiService!.getHomeSliders();
      _sliders = response['sliders'] ?? [];
      _error = null;
    } catch (e) {
      _error = e.toString();
      _sliders = [];
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  void clearError() {
    _error = null;
    notifyListeners();
  }
}
