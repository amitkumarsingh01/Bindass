import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Profile'),
        backgroundColor: const Color(0xFF6A1B9A),
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () async {
              final authProvider = Provider.of<AuthProvider>(context, listen: false);
              await authProvider.logout();
              if (mounted) {
                Navigator.of(context).pushReplacement(
                  MaterialPageRoute(builder: (context) => const LoginScreen()),
                );
              }
            },
          ),
        ],
      ),
      body: Consumer<AuthProvider>(
        builder: (context, authProvider, child) {
          if (authProvider.user == null) {
            return const Center(
              child: CircularProgressIndicator(),
            );
          }

          final user = authProvider.user!;

          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                // Profile Header
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(24),
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(
                      colors: [Color(0xFF6A1B9A), Color(0xFF8E24AA)],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Column(
                    children: [
                      CircleAvatar(
                        radius: 50,
                        backgroundColor: Colors.white,
                        backgroundImage: user['profilePicture'] != null
                            ? NetworkImage(user['profilePicture'])
                            : null,
                        child: user['profilePicture'] == null
                            ? const Icon(
                                Icons.person,
                                size: 50,
                                color: Color(0xFF6A1B9A),
                              )
                            : null,
                      ),
                      const SizedBox(height: 16),
                      Text(
                        user['userName'] ?? 'User',
                        style: const TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        user['email'] ?? '',
                        style: const TextStyle(
                          fontSize: 16,
                          color: Colors.white70,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        user['phoneNumber'] ?? '',
                        style: const TextStyle(
                          fontSize: 14,
                          color: Colors.white70,
                        ),
                      ),
                    ],
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
                          value: '₹${walletProvider.walletBalance?['walletBalance']?.toStringAsFixed(2) ?? '0.00'}',
                          valueColor: Colors.green,
                        ),
                        _ProfileItem(
                          icon: Icons.verified,
                          label: 'Status',
                          value: user['isActive'] == true ? 'Active' : 'Inactive',
                          valueColor: user['isActive'] == true ? Colors.green : Colors.red,
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
      applicationIcon: const Icon(
        Icons.casino,
        size: 48,
        color: Color(0xFF6A1B9A),
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

  const _ProfileSection({
    required this.title,
    required this.children,
  });

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
            color: Color(0xFF6A1B9A),
          ),
        ),
        const SizedBox(height: 16),
        Card(
          child: Column(
            children: children,
          ),
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
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      child: Row(
        children: [
          Icon(
            icon,
            size: 20,
            color: Colors.grey[600],
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  label,
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.grey[600],
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  value,
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: valueColor ?? Colors.black,
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
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: const Color(0xFF6A1B9A).withOpacity(0.1),
          child: Icon(
            icon,
            color: const Color(0xFF6A1B9A),
          ),
        ),
        title: Text(
          title,
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        subtitle: Text(subtitle),
        trailing: const Icon(Icons.arrow_forward_ios, size: 16),
        onTap: onTap,
      ),
    );
  }
}
