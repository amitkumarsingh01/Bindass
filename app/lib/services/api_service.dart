import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class ApiService {
  static const String baseUrl = 'https://server.bindassgrand.com/api';
  late SharedPreferences _prefs;

  ApiService(SharedPreferences prefs) {
    _prefs = prefs;
  }

  // Headers: userId based access
  Map<String, String> get _headers {
    final userId = _prefs.getString('user_id') ?? 'guest';
    return {
      'Content-Type': 'application/json',
      'X-User-Id': userId,
    };
  }

  // Auth endpoints
  Future<Map<String, dynamic>> login(String userId, String password) async {
    // Validate credentials against backend
    final response = await http.post(
      Uri.parse('$baseUrl/auth/login'),
      headers: _headers,
      body: jsonEncode({ 'userId': userId, 'password': password }),
    );
    if (response.statusCode == 200) {
      // Persist identity locally for header-based endpoints
      await _prefs.setString('user_id', userId);
      await _prefs.setString('user_password', password);
      return jsonDecode(response.body);
    } else {
      throw Exception('Login failed: ${response.body}');
    }
  }

  Future<Map<String, dynamic>> register(Map<String, dynamic> userData) async {
    // Keep calling backend registration to create user with password
    final response = await http.post(
      Uri.parse('$baseUrl/auth/register'),
      headers: _headers,
      body: jsonEncode(userData),
    );
    if (response.statusCode == 200) {
      // Also store credentials locally for header-based flows
      if (userData['userId'] != null) {
        await _prefs.setString('user_id', userData['userId']);
      }
      if (userData['password'] != null) {
        await _prefs.setString('user_password', userData['password']);
      }
      return jsonDecode(response.body);
    } else {
      throw Exception('Registration failed: ${response.body}');
    }
  }

  Future<Map<String, dynamic>> getCurrentUser() async {
    final response = await http.get(
      Uri.parse('$baseUrl/auth/me'),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to get user info: ${response.body}');
    }
  }

  // Contest endpoints
  Future<List<dynamic>> getContests() async {
    final response = await http.get(
      Uri.parse('$baseUrl/contests/'),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to get contests: ${response.body}');
    }
  }

  Future<Map<String, dynamic>> getContest(String contestId) async {
    final response = await http.get(
      Uri.parse('$baseUrl/contests/$contestId'),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to get contest: ${response.body}');
    }
  }

  Future<Map<String, dynamic>> getContestCategories(String contestId) async {
    final response = await http.get(
      Uri.parse('$baseUrl/contests/$contestId/categories'),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to get contest categories: ${response.body}');
    }
  }

  Future<Map<String, dynamic>> getContestLeaderboard(String contestId) async {
    final response = await http.get(
      Uri.parse('$baseUrl/contests/$contestId/leaderboard'),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to get leaderboard: ${response.body}');
    }
  }

  Future<Map<String, dynamic>> getContestWinners(String contestId) async {
    final response = await http.get(
      Uri.parse('$baseUrl/contests/$contestId/winners'),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to get winners: ${response.body}');
    }
  }

  Future<Map<String, dynamic>> getMyContestPurchases(String contestId) async {
    final response = await http.get(
      Uri.parse('$baseUrl/contests/$contestId/my-purchases'),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to get my purchases: ${response.body}');
    }
  }

  // Seat endpoints
  Future<Map<String, dynamic>> getCategorySeats(String contestId, int categoryId) async {
    final response = await http.get(
      Uri.parse('$baseUrl/seats/$contestId/category/$categoryId'),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to get category seats: ${response.body}');
    }
  }

  Future<Map<String, dynamic>> purchaseSeats(String contestId, List<int> seatNumbers, String paymentMethod) async {
    final response = await http.post(
      Uri.parse('$baseUrl/seats/purchase'),
      headers: _headers,
      body: jsonEncode({
        'contestId': contestId,
        'seatNumbers': seatNumbers,
        'paymentMethod': paymentMethod,
      }),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to purchase seats: ${response.body}');
    }
  }

  // User endpoints
  Future<Map<String, dynamic>> updateProfile(Map<String, dynamic> profileData) async {
    final response = await http.put(
      Uri.parse('$baseUrl/users/profile'),
      headers: _headers,
      body: jsonEncode(profileData),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to update profile: ${response.body}');
    }
  }

  Future<Map<String, dynamic>> addBankDetails(Map<String, dynamic> bankData) async {
    final response = await http.post(
      Uri.parse('$baseUrl/users/bank-details'),
      headers: _headers,
      body: jsonEncode(bankData),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return data['bankDetails'] ?? {};
    } else {
      throw Exception('Failed to add bank details: ${response.body}');
    }
  }

  Future<Map<String, dynamic>> getBankDetails() async {
    final response = await http.get(
      Uri.parse('$baseUrl/users/bank-details'),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to get bank details: ${response.body}');
    }
  }

  // Wallet endpoints
  Future<Map<String, dynamic>> getWalletBalance() async {
    final response = await http.get(
      Uri.parse('$baseUrl/wallet/balance'),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to get wallet balance: ${response.body}');
    }
  }

  Future<Map<String, dynamic>> getWalletTransactions() async {
    final response = await http.get(
      Uri.parse('$baseUrl/wallet/transactions'),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to get wallet transactions: ${response.body}');
    }
  }

  Future<Map<String, dynamic>> addMoneyToWallet(double amount, String description, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/wallet/add-money'),
      headers: {
        ..._headers,
        'X-User-Password': password,
      },
      body: jsonEncode({ 'amount': amount, 'description': description }),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to add money: ${response.body}');
    }
  }

  Future<Map<String, dynamic>> requestWithdrawal(double amount, String bankDetailsId, String withdrawalMethod) async {
    final response = await http.post(
      Uri.parse('$baseUrl/wallet/withdraw'),
      headers: _headers,
      body: jsonEncode({ 'amount': amount, 'bank_details_id': bankDetailsId, 'withdrawal_method': withdrawalMethod }),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to request withdrawal: ${response.body}');
    }
  }

  // Logout
  Future<void> logout() async {
    await _prefs.remove('access_token');
  }
}
