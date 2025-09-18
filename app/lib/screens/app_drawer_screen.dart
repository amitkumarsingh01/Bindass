import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../models/app_drawer_model.dart';
import '../controllers/app_drawer_controller.dart';
import '../providers/auth_provider.dart';
import '../providers/wallet_provider.dart';
import 'auth/login_screen.dart';
import 'profile/edit_profile_screen.dart';

class AppDrawerScreen extends StatelessWidget {
  final AppDrawerController controller;

  const AppDrawerScreen({super.key, required this.controller});

  @override
  Widget build(BuildContext context) {
    return Consumer2<AuthProvider, WalletProvider>(
      builder: (context, authProvider, walletProvider, child) {
        final drawerData = controller.getDrawerData(
          authProvider: authProvider,
          walletProvider: walletProvider,
        );

        return Drawer(
          backgroundColor: Colors.white,
          child: Column(
            children: [
              _buildHeader(context, drawerData),
              Expanded(child: _buildMenuItems(context, drawerData)),
              _buildFooter(context),
            ],
          ),
        );
      },
    );
  }

  Widget _buildProfilePicture(AppDrawerModel drawerData) {
    final profilePictureUrl = drawerData.profileImageUrl;

    if (profilePictureUrl != null) {
      return ClipRRect(
        borderRadius: BorderRadius.circular(37),
        child: CachedNetworkImage(
          imageUrl: 'https://server.bindassgrand.com$profilePictureUrl',
          width: 80,
          height: 80,
          fit: BoxFit.cover,
          placeholder: (context, url) => Container(
            width: 80,
            height: 80,
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.2),
              borderRadius: BorderRadius.circular(40),
            ),
            child: const Center(
              child: CircularProgressIndicator(
                color: Colors.white,
                strokeWidth: 2,
              ),
            ),
          ),
          errorWidget: (context, url, error) =>
              const Icon(Icons.person_rounded, size: 40, color: Colors.white),
        ),
      );
    } else {
      return const Icon(Icons.person_rounded, size: 40, color: Colors.white);
    }
  }

  void _navigateToEditProfile(BuildContext context) {
    Navigator.of(
      context,
    ).push(MaterialPageRoute(builder: (context) => const EditProfileScreen()));
  }

  Widget _buildHeader(BuildContext context, AppDrawerModel drawerData) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.fromLTRB(20, 60, 20, 20),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFFdb9822), Color(0xFFffb32c)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Profile Picture
          Center(
            child: Stack(
              children: [
                GestureDetector(
                  onTap: controller.onProfilePictureTap,
                  child: Container(
                    width: 80,
                    height: 80,
                    decoration: BoxDecoration(
                      color: Colors.white.withOpacity(0.2),
                      borderRadius: BorderRadius.circular(40),
                      border: Border.all(
                        color: Colors.white.withOpacity(0.3),
                        width: 3,
                      ),
                    ),
                    child: _buildProfilePicture(drawerData),
                  ),
                ),
                // Edit Icon
                Positioned(
                  bottom: 0,
                  right: 0,
                  child: GestureDetector(
                    onTap: () => _navigateToEditProfile(context),
                    child: Container(
                      width: 28,
                      height: 28,
                      decoration: BoxDecoration(
                        color: Colors.white.withOpacity(0.9),
                        shape: BoxShape.circle,
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withOpacity(0.2),
                            blurRadius: 4,
                            offset: const Offset(0, 2),
                          ),
                        ],
                      ),
                      child: const Icon(
                        Icons.edit_rounded,
                        color: Color(0xFFdb9822),
                        size: 16,
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),

          // User Name
          Center(
            child: Text(
              drawerData.userName,
              style: const TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.w700,
                color: Colors.white,
                letterSpacing: 0.5,
              ),
              textAlign: TextAlign.center,
            ),
          ),
          const SizedBox(height: 8),

          // Balance Card
          Container(
            margin: const EdgeInsets.symmetric(horizontal: 10),
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.15),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(
                color: Colors.white.withOpacity(0.2),
                width: 1,
              ),
            ),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(6),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Icon(
                    Icons.account_balance_wallet_rounded,
                    color: Colors.white,
                    size: 16,
                  ),
                ),
                const SizedBox(width: 8),
                const Text(
                  'Balance:',
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.white70,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                const SizedBox(width: 4),
                Flexible(
                  child: Text(
                    '₹${drawerData.walletBalance.toStringAsFixed(2)}',
                    style: const TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w800,
                      color: Colors.white,
                      letterSpacing: 0.3,
                    ),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMenuItems(BuildContext context, AppDrawerModel drawerData) {
    return Consumer<AuthProvider>(
      builder: (context, authProvider, child) {
        return ListView.builder(
          padding: const EdgeInsets.symmetric(vertical: 8),
          itemCount: drawerData.menuItems.length,
          itemBuilder: (context, index) {
            final item = drawerData.menuItems[index];

            if (item.id == 'profile') {
              return Column(
                children: [
                  _buildMenuItem(context, item),
                  // Active Purchases tile directly below Profile Settings (static, no count)
                  Container(
                    margin: const EdgeInsets.symmetric(
                      horizontal: 8,
                      vertical: 2,
                    ),
                    child: ListTile(
                      leading: Container(
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: const Color(0xFFdb9822).withOpacity(0.1),
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: const Icon(
                          Icons.shopping_bag_rounded,
                          color: Color(0xFFdb9822),
                          size: 20,
                        ),
                      ),
                      title: Text(
                        'Active Purchases',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                          color: Colors.grey.shade800,
                        ),
                      ),
                      trailing: Icon(
                        Icons.arrow_forward_ios_rounded,
                        size: 16,
                        color: Colors.grey.shade400,
                      ),
                      onTap: () =>
                          controller.navigateToRoute('/active-purchases'),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                      hoverColor: const Color(0xFFdb9822).withOpacity(0.05),
                      splashColor: const Color(0xFFdb9822).withOpacity(0.1),
                    ),
                  ),
                ],
              );
            }

            return _buildMenuItem(context, item);
          },
        );
      },
    );
  }

  Widget _buildMenuItem(BuildContext context, DrawerMenuItem item) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
      child: ListTile(
        leading: Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: const Color(0xFFdb9822).withOpacity(0.1),
            borderRadius: BorderRadius.circular(10),
          ),
          child: Icon(item.icon, color: const Color(0xFFdb9822), size: 20),
        ),
        title: Text(
          item.title,
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w600,
            color: item.isEnabled ? Colors.grey.shade800 : Colors.grey.shade400,
          ),
        ),
        trailing: item.isEnabled
            ? Icon(
                Icons.arrow_forward_ios_rounded,
                size: 16,
                color: Colors.grey.shade400,
              )
            : null,
        onTap: item.isEnabled ? () => controller.onMenuItemTap(item) : null,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        hoverColor: const Color(0xFFdb9822).withOpacity(0.05),
        splashColor: const Color(0xFFdb9822).withOpacity(0.1),
      ),
    );
  }

  Widget _buildFooter(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        border: Border(top: BorderSide(color: Colors.grey.shade200, width: 1)),
      ),
      child: Consumer<AuthProvider>(
        builder: (context, authProvider, child) {
          return Container(
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(12),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.08),
                  blurRadius: 8,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
            child: IconButton(
              icon: const Icon(Icons.logout_rounded, color: Color(0xFFE74C3C)),
              onPressed: () async {
                await authProvider.logout();
                if (context.mounted) {
                  Navigator.of(context).pushReplacement(
                    MaterialPageRoute(
                      builder: (context) => const LoginScreen(),
                    ),
                  );
                }
              },
            ),
          );
        },
      ),
    );
  }
}
