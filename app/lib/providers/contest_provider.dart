import 'package:flutter/material.dart';
import '../services/api_service.dart';
import 'package:shared_preferences/shared_preferences.dart';

class ContestProvider with ChangeNotifier {
  ApiService? _apiService;

  bool _isLoading = false;
  List<dynamic> _contests = [];
  Map<String, dynamic>? _currentContest;
  Map<String, dynamic>? _contestCategories;
  Map<String, dynamic>? _contestLeaderboard;
  Map<String, dynamic>? _contestWinners;
  Map<String, dynamic>? _myPurchases;
  Map<String, dynamic>? _categorySeats;
  String? _error;

  ContestProvider();

  void setApiService(ApiService apiService) {
    _apiService = apiService;
  }

  bool get isLoading => _isLoading;
  List<dynamic> get contests => _contests;
  Map<String, dynamic>? get currentContest => _currentContest;
  Map<String, dynamic>? get contestCategories => _contestCategories;
  Map<String, dynamic>? get contestLeaderboard => _contestLeaderboard;
  Map<String, dynamic>? get contestWinners => _contestWinners;
  Map<String, dynamic>? get myPurchases => _myPurchases;
  Map<String, dynamic>? get categorySeats => _categorySeats;
  String? get error => _error;

  Future<void> loadContests() async {
    if (_apiService == null) return;

    _setLoading(true);
    _clearError();

    try {
      _contests = await _apiService!.getContests();
      notifyListeners();
    } catch (e) {
      _setError(e.toString());
    } finally {
      _setLoading(false);
    }
  }

  Future<void> loadContest(String contestId) async {
    if (_apiService == null) return;

    _setLoading(true);
    _clearError();

    try {
      _currentContest = await _apiService!.getContest(contestId);
      notifyListeners();
    } catch (e) {
      _setError(e.toString());
    } finally {
      _setLoading(false);
    }
  }

  Future<void> loadContestCategories(String contestId) async {
    if (_apiService == null) return;

    _setLoading(true);
    _clearError();

    try {
      _contestCategories = await _apiService!.getContestCategories(contestId);
      notifyListeners();
    } catch (e) {
      _setError(e.toString());
    } finally {
      _setLoading(false);
    }
  }

  Future<void> loadContestLeaderboard(String contestId) async {
    if (_apiService == null) return;

    _setLoading(true);
    _clearError();

    try {
      _contestLeaderboard = await _apiService!.getContestLeaderboard(contestId);
      notifyListeners();
    } catch (e) {
      _setError(e.toString());
    } finally {
      _setLoading(false);
    }
  }

  Future<void> loadContestWinners(String contestId) async {
    if (_apiService == null) return;

    _setLoading(true);
    _clearError();

    try {
      _contestWinners = await _apiService!.getContestWinners(contestId);
      notifyListeners();
    } catch (e) {
      _setError(e.toString());
    } finally {
      _setLoading(false);
    }
  }

  Future<void> loadMyPurchases(String contestId) async {
    if (_apiService == null) return;

    _setLoading(true);
    _clearError();

    try {
      _myPurchases = await _apiService!.getMyContestPurchases(contestId);
      notifyListeners();
    } catch (e) {
      _setError(e.toString());
    } finally {
      _setLoading(false);
    }
  }

  Future<void> loadCategorySeats(String contestId, int categoryId) async {
    if (_apiService == null) return;

    _setLoading(true);
    _clearError();

    try {
      _categorySeats = await _apiService!.getCategorySeats(
        contestId,
        categoryId,
      );
      notifyListeners();
    } catch (e) {
      _setError(e.toString());
    } finally {
      _setLoading(false);
    }
  }

  Future<bool> purchaseSeats(
    String contestId,
    List<int> seatNumbers,
    String paymentMethod,
  ) async {
    if (_apiService == null) return false;

    _setLoading(true);
    _clearError();

    try {
      await _apiService!.purchaseSeats(contestId, seatNumbers, paymentMethod);
      // Refresh contest data after purchase
      await loadContest(contestId);
      await loadContestCategories(contestId);
      await loadMyPurchases(contestId);
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

  void clearCurrentContest() {
    _currentContest = null;
    _contestCategories = null;
    _contestLeaderboard = null;
    _contestWinners = null;
    _myPurchases = null;
    _categorySeats = null;
    notifyListeners();
  }
}
