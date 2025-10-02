import 'dart:convert';
import 'dart:io';
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
    return {'Content-Type': 'application/json', 'X-User-Id': userId};
  }

  // Auth endpoints
  Future<Map<String, dynamic>> login(String identifier, String password) async {
    // Validate credentials against backend
    final response = await http.post(
      Uri.parse('$baseUrl/auth/login'),
      headers: _headers,
      body: jsonEncode({'identifier': identifier, 'password': password}),
    );
    if (response.statusCode == 200) {
      // Persist identity locally for header-based endpoints
      await _prefs.setString('user_id', identifier);
      await _prefs.setString('user_password', password);
      return jsonDecode(response.body);
    } else {
      throw Exception('Login failed: ${response.body}');
    }
  }

  Future<Map<String, dynamic>> register(Map<String, dynamic> userData) async {
    // Prefer minimal registration endpoint with email/phone + password only
    final response = await http.post(
      Uri.parse('$baseUrl/auth/register-simple'),
      headers: _headers,
      body: jsonEncode({
        'userName': userData['userName'],
        'userId': userData['userId'],
        'email': userData['email'],
        'phoneNumber': userData['phoneNumber'],
        'password': userData['password'],
        'city': userData['city'],
        'state': userData['state'],
      }),
    );
    if (response.statusCode == 200) {
      // Also store credentials locally for header-based flows
      final identifier = userData['email'] ?? userData['phoneNumber'];
      if (identifier != null) {
        await _prefs.setString('user_id', identifier);
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

  Future<Map<String, dynamic>> getPrizeStructure(String contestId) async {
    final response = await http.get(
      Uri.parse('$baseUrl/admin/contests/$contestId/prize-structure'),
      headers: {
        'Content-Type': 'application/json',
        'accept': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to get prize structure: ${response.body}');
    }
  }

  // Seat endpoints
  Future<Map<String, dynamic>> getCategorySeats(
    String contestId,
    int categoryId,
  ) async {
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

  Future<Map<String, dynamic>> purchaseSeats(
    String contestId,
    List<int> seatNumbers,
    String paymentMethod,
  ) async {
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
  Future<Map<String, dynamic>> updateProfile(
    Map<String, dynamic> profileData,
  ) async {
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

  Future<Map<String, dynamic>> addBankDetails(
    Map<String, dynamic> bankData,
  ) async {
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
  Future<Map<String, dynamic>> createPayment(
    double amount,
    String description,
  ) async {
    // Use fresh simple payments API
    final rawUserId = _prefs.getString('user_id') ?? 'guest';
    // Extract part before @ if email is used as user_id
    final userId = rawUserId.contains('@') 
        ? rawUserId.split('@')[0] 
        : rawUserId;
    // 🧾 Log request
    // ignore: avoid_print
    print(
      '➡️  POST $baseUrl/new/payment/create?user_id=$userId&amount=$amount&description=$description',
    );
    final response = await http.post(
      Uri.parse(
        '$baseUrl/new/payment/create?user_id=${Uri.encodeComponent(userId)}&amount=$amount&description=${Uri.encodeComponent(description)}',
      ),
      headers: {'Content-Type': 'application/json'},
    );
    if (response.statusCode == 200) {
      // 📦 Log response
      // ignore: avoid_print
      print('✅  Response 200: ${response.body}');
      return jsonDecode(response.body);
    } else {
      // ❌ Log error response
      // ignore: avoid_print
      print('❌  Response ${response.statusCode}: ${response.body}');
      throw Exception('Failed to create payment: ${response.body}');
    }
  }

  Future<Map<String, dynamic>> getPaymentStatus(String orderId) async {
    // 🔁 Polling status via fresh simple payments API
    // ignore: avoid_print
    print('🔁  GET $baseUrl/new/payment/status/$orderId');
    final response = await http.get(
      Uri.parse('$baseUrl/new/payment/status/$orderId'),
      headers: {'Content-Type': 'application/json'},
    );
    if (response.statusCode == 200) {
      // ignore: avoid_print
      print('📦  Status 200: ${response.body}');
      return jsonDecode(response.body);
    } else {
      // ignore: avoid_print
      print('❌  Status ${response.statusCode}: ${response.body}');
      throw Exception('Failed to get payment status: ${response.body}');
    }
  }

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

  Future<Map<String, dynamic>> getWithdrawals({
    int limit = 20,
    int skip = 0,
  }) async {
    final response = await http.get(
      Uri.parse('$baseUrl/wallet/withdrawals?limit=$limit&skip=$skip'),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to get withdrawals: ${response.body}');
    }
  }

  Future<Map<String, dynamic>> getPayments() async {
    final userId = _prefs.getString('user_id') ?? 'guest';
    final response = await http.get(
      Uri.parse('$baseUrl/admin/payments?userId=$userId'),
      headers: {
        'Content-Type': 'application/json',
        'accept': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to get payments: ${response.body}');
    }
  }

  Future<Map<String, dynamic>> addMoneyToWallet(
    double amount,
    String description,
    String password,
  ) async {
    final response = await http.post(
      Uri.parse('$baseUrl/wallet/add-money'),
      headers: {..._headers, 'X-User-Password': password},
      body: jsonEncode({'amount': amount, 'description': description}),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to add money: ${response.body}');
    }
  }

  Future<Map<String, dynamic>> requestWithdrawal(
    double amount,
    String bankDetailsId,
    String withdrawalMethod,
  ) async {
    final response = await http.post(
      Uri.parse('$baseUrl/wallet/withdraw'),
      headers: _headers,
      body: jsonEncode({
        'amount': amount,
        'bank_details_id': bankDetailsId,
        'withdrawal_method': withdrawalMethod,
      }),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to request withdrawal: ${response.body}');
    }
  }

  // Home sliders endpoint
  Future<Map<String, dynamic>> getHomeSliders() async {
    final response = await http.get(
      Uri.parse('$baseUrl/admin/home-sliders'),
      headers: {
        'Content-Type': 'application/json',
        'accept': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to get home sliders: ${response.body}');
    }
  }

  // Profile picture endpoints
  Future<Map<String, dynamic>> uploadProfilePicture(File imageFile) async {
    final userId = _prefs.getString('user_id') ?? 'guest';
    final request = http.MultipartRequest(
      'POST',
      Uri.parse('$baseUrl/admin/users/$userId/profile-picture'),
    );

    request.headers.addAll({'accept': 'application/json'});

    request.files.add(
      await http.MultipartFile.fromPath(
        'image',
        imageFile.path,
        filename: imageFile.path.split('/').last,
      ),
    );

    final streamedResponse = await request.send();
    final response = await http.Response.fromStream(streamedResponse);

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      // Store the profile picture URL in shared preferences
      await _prefs.setString('profile_picture_url', data['imageUrl']);
      return data;
    } else {
      throw Exception('Failed to upload profile picture: ${response.body}');
    }
  }

  Future<Map<String, dynamic>> deleteProfilePicture() async {
    final userId = _prefs.getString('user_id') ?? 'guest';
    final response = await http.delete(
      Uri.parse('$baseUrl/admin/users/$userId/profile-picture'),
      headers: {'accept': 'application/json'},
    );

    if (response.statusCode == 200) {
      // Remove the profile picture URL from shared preferences
      await _prefs.remove('profile_picture_url');
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to delete profile picture: ${response.body}');
    }
  }

  String? getProfilePictureUrl() {
    return _prefs.getString('profile_picture_url');
  }

  // Purchases endpoints
  Future<Map<String, dynamic>> getUserPurchases({
    int limit = 100,
    int skip = 0,
  }) async {
    final userId = _prefs.getString('user_id') ?? 'guest';
    final encodedUserId = Uri.encodeComponent(userId);
    final response = await http.get(
      Uri.parse(
        '$baseUrl/admin/users/$encodedUserId/purchases?limit=$limit&skip=$skip',
      ),
      headers: {'accept': 'application/json'},
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to get user purchases: ${response.body}');
    }
  }

  // Contact endpoints
  Future<Map<String, dynamic>> getContactInfo() async {
    final response = await http.get(
      Uri.parse('$baseUrl/admin/contact'),
      headers: {
        'Content-Type': 'application/json',
        'accept': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to get contact info: ${response.body}');
    }
  }

  // Forgot Password endpoints
  Future<Map<String, dynamic>> forgotPassword(String email) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/forgot-password'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'email': email}),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to send reset email: ${response.body}');
    }
  }

  // Logout
  Future<void> logout() async {
    await _prefs.remove('access_token');
  }
}
