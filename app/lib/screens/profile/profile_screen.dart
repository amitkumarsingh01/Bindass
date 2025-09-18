import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../../providers/auth_provider.dart';
import '../../providers/wallet_provider.dart';
import 'edit_profile_screen.dart';
import 'bank_details_screen.dart';
import '../auth/login_screen.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      Provider.of<WalletProvider>(context, listen: false).loadBankDetails();
    });
  }

  Widget _buildProfilePicture(AuthProvider authProvider) {
    final profilePictureUrl = authProvider.profilePictureUrl;

    if (profilePictureUrl != null) {
      return ClipRRect(
        borderRadius: BorderRadius.circular(60),
        child: CachedNetworkImage(
          imageUrl: 'https://server.bindassgrand.com$profilePictureUrl',
          width: 120,
          height: 120,
          fit: BoxFit.cover,
          placeholder: (context, url) => Container(
            width: 120,
            height: 120,
            decoration: BoxDecoration(
              color: Colors.grey.shade200,
              borderRadius: BorderRadius.circular(60),
            ),
            child: const Center(
              child: CircularProgressIndicator(
                color: Color(0xFFdb9822),
                strokeWidth: 2,
              ),
            ),
          ),
          errorWidget: (context, url, error) => Container(
            width: 120,
            height: 120,
            decoration: BoxDecoration(
              color: Colors.grey.shade200,
              borderRadius: BorderRadius.circular(60),
            ),
            child: const Icon(
              Icons.person_rounded,
              size: 60,
              color: Color(0xFFdb9822),
            ),
          ),
        ),
      );
    } else {
      return Container(
        width: 120,
        height: 120,
        decoration: BoxDecoration(
          color: Colors.grey.shade200,
          borderRadius: BorderRadius.circular(60),
        ),
        child: const Icon(
          Icons.person_rounded,
          size: 60,
          color: Color(0xFFdb9822),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'Profile',
          style: TextStyle(
            color: Colors.black87,
            fontWeight: FontWeight.w600,
            fontSize: 20,
          ),
        ),
        backgroundColor: Colors.white,
        foregroundColor: Colors.black87,
        elevation: 0,
        shadowColor: Colors.transparent,
        surfaceTintColor: Colors.transparent,
        actions: [
          Container(
            margin: const EdgeInsets.only(right: 8),
            decoration: BoxDecoration(
              color: const Color(0xFFdb9822).withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: IconButton(
              icon: const Icon(
                Icons.logout_rounded,
                color: Color(0xFFdb9822),
                size: 22,
              ),
              onPressed: () async {
                final authProvider = Provider.of<AuthProvider>(
                  context,
                  listen: false,
                );
                await authProvider.logout();
                if (mounted) {
                  Navigator.of(context).pushReplacement(
                    MaterialPageRoute(
                      builder: (context) => const LoginScreen(),
                    ),
                  );
                }
              },
            ),
          ),
        ],
      ),
      body: Consumer<AuthProvider>(
        builder: (context, authProvider, child) {
          if (authProvider.user == null) {
            return const Center(child: CircularProgressIndicator());
          }

          final user = authProvider.user!;

          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                // Profile Picture Header
                Center(
                  child: Container(
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      gradient: LinearGradient(
                        colors: [
                          const Color(0xFFdb9822).withOpacity(0.1),
                          const Color(0xFFffb32c).withOpacity(0.1),
                        ],
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                      ),
                      boxShadow: [
                        BoxShadow(
                          color: const Color(0xFFdb9822).withOpacity(0.2),
                          blurRadius: 20,
                          offset: const Offset(0, 8),
                        ),
                      ],
                    ),
                    padding: const EdgeInsets.all(8),
                    child: Container(
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        border: Border.all(
                          color: const Color(0xFFdb9822),
                          width: 3,
                        ),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withOpacity(0.1),
                            blurRadius: 15,
                            offset: const Offset(0, 5),
                          ),
                        ],
                      ),
                      child: _buildProfilePicture(authProvider),
                    ),
                  ),
                ),

                const SizedBox(height: 24),

                // Profile Information
                _ProfileSection(
                  title: 'Personal Information',
                  children: [
                    _ProfileItem(
                      icon: Icons.person,
                      label: 'Full Name',
                      value: user['userName'] ?? 'Not set',
                    ),
                    _ProfileItem(
                      icon: Icons.badge,
                      label: 'User ID',
                      value: user['userId'] ?? 'Not set',
                    ),
                    _ProfileItem(
                      icon: Icons.email,
                      label: 'Email',
                      value: user['email'] ?? 'Not set',
                    ),
                    _ProfileItem(
                      icon: Icons.phone,
                      label: 'Phone Number',
                      value: user['phoneNumber'] ?? 'Not set',
                    ),
                    _ProfileItem(
                      icon: Icons.location_city,
                      label: 'City',
                      value: user['city'] ?? 'Not set',
                    ),
                    _ProfileItem(
                      icon: Icons.map,
                      label: 'State',
                      value: user['state'] ?? 'Not set',
                    ),
                  ],
                ),

                const SizedBox(height: 24),

                // Wallet Information
                Consumer<WalletProvider>(
                  builder: (context, walletProvider, child) {
                    return _ProfileSection(
                      title: 'Wallet Information',
                      children: [
                        _ProfileItem(
                          icon: Icons.account_balance_wallet,
                          label: 'Balance',
                          value:
                              '₹${walletProvider.walletBalance?['walletBalance']?.toStringAsFixed(2) ?? '0.00'}',
                          valueColor: Colors.green,
                        ),
                        _ProfileItem(
                          icon: Icons.verified,
                          label: 'Status',
                          value: user['isActive'] == true
                              ? 'Active'
                              : 'Inactive',
                          valueColor: user['isActive'] == true
                              ? Colors.green
                              : Colors.red,
                        ),
                      ],
                    );
                  },
                ),

                const SizedBox(height: 24),

                // Action Buttons
                Column(
                  children: [
                    _ActionButton(
                      icon: Icons.edit,
                      title: 'Edit Profile',
                      subtitle: 'Update your personal information',
                      onTap: () {
                        Navigator.of(context).push(
                          MaterialPageRoute(
                            builder: (context) => const EditProfileScreen(),
                          ),
                        );
                      },
                    ),
                    const SizedBox(height: 12),
                    _ActionButton(
                      icon: Icons.account_balance,
                      title: 'Bank Details',
                      subtitle: 'Manage your bank account information',
                      onTap: () {
                        Navigator.of(context).push(
                          MaterialPageRoute(
                            builder: (context) => const BankDetailsScreen(),
                          ),
                        );
                      },
                    ),
                    const SizedBox(height: 12),
                    _ActionButton(
                      icon: Icons.help,
                      title: 'Help & Support',
                      subtitle: 'Get help and contact support',
                      onTap: () {
                        // Navigate to help screen
                      },
                    ),
                    const SizedBox(height: 12),
                    _ActionButton(
                      icon: Icons.info,
                      title: 'About',
                      subtitle: 'App version and information',
                      onTap: () {
                        _showAboutDialog(context);
                      },
                    ),
                  ],
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  void _showAboutDialog(BuildContext context) {
    showAboutDialog(
      context: context,
      applicationName: 'BINDASS GRAND',
      applicationVersion: '1.0.0',
      applicationIcon: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          gradient: const LinearGradient(
            colors: [Color(0xFFdb9822), Color(0xFFffb32c)],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
          borderRadius: BorderRadius.circular(16),
        ),
        child: const Icon(Icons.casino_rounded, size: 32, color: Colors.white),
      ),
      children: [
        const Text('Your Lucky Numbers Await'),
        const SizedBox(height: 16),
        const Text(
          'BINDASS GRAND is a lottery platform where you can participate in exciting contests and win amazing prizes.',
        ),
      ],
    );
  }
}

class _ProfileSection extends StatelessWidget {
  final String title;
  final List<Widget> children;

  const _ProfileSection({required this.title, required this.children});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: const TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
            color: Color(0xFFdb9822),
            letterSpacing: 0.5,
          ),
        ),
        const SizedBox(height: 16),
        Card(
          elevation: 2,
          shadowColor: Colors.grey.withOpacity(0.1),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
          child: Column(children: children),
        ),
      ],
    );
  }
}

class _ProfileItem extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;
  final Color? valueColor;

  const _ProfileItem({
    required this.icon,
    required this.label,
    required this.value,
    this.valueColor,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 4, vertical: 2),
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
      decoration: BoxDecoration(
        color: Colors.grey[50],
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey[200]!, width: 1),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: const Color(0xFFdb9822).withOpacity(0.1),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(icon, size: 20, color: const Color(0xFFdb9822)),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  label,
                  style: TextStyle(
                    fontSize: 13,
                    color: Colors.grey[600],
                    fontWeight: FontWeight.w500,
                    letterSpacing: 0.3,
                  ),
                ),
                const SizedBox(height: 6),
                Text(
                  value,
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                    color: valueColor ?? Colors.black87,
                    letterSpacing: 0.2,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _ActionButton extends StatelessWidget {
  final IconData icon;
  final String title;
  final String subtitle;
  final VoidCallback onTap;

  const _ActionButton({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 1,
      shadowColor: Colors.grey.withOpacity(0.1),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          borderRadius: BorderRadius.circular(16),
          onTap: onTap,
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: Row(
              children: [
                ShaderMask(
                  shaderCallback: (bounds) => const LinearGradient(
                    colors: [Color(0xFFdb9822), Color(0xFFffb32c)],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ).createShader(bounds),
                  child: Icon(icon, color: Colors.white, size: 24),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        title,
                        style: const TextStyle(
                          fontWeight: FontWeight.w600,
                          fontSize: 16,
                          color: Colors.black87,
                          letterSpacing: 0.3,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        subtitle,
                        style: TextStyle(
                          fontSize: 14,
                          color: Colors.grey[600],
                          fontWeight: FontWeight.w400,
                        ),
                      ),
                    ],
                  ),
                ),
                Icon(
                  Icons.arrow_forward_ios_rounded,
                  size: 16,
                  color: Colors.grey[400],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
