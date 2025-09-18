import 'package:flutter/material.dart';
import '../models/app_drawer_model.dart';
import '../providers/wallet_provider.dart';
import '../providers/auth_provider.dart';
import '../screens/profile/profile_screen.dart';
import '../screens/profile/bank_details_screen.dart';
import '../screens/wallet/how_to_play_screen.dart';
import '../screens/wallet/help_support_screen.dart';
import '../screens/wallet/terms_conditions_screen.dart';
import '../screens/profile/active_purchases_screen.dart';

class AppDrawerController {
  final GlobalKey<ScaffoldState> scaffoldKey;
  final BuildContext context;

  AppDrawerController({required this.scaffoldKey, required this.context});

  void openDrawer() {
    scaffoldKey.currentState?.openDrawer();
  }

  void closeDrawer() {
    scaffoldKey.currentState?.closeDrawer();
  }

  AppDrawerModel getDrawerData({
    required AuthProvider authProvider,
    required WalletProvider walletProvider,
  }) {
    return AppDrawerModel.fromAuthProvider(
      authProvider.user,
      walletProvider.walletBalance?['walletBalance']?.toDouble() ?? 0.0,
      profilePictureUrl: authProvider.profilePictureUrl,
    );
  }

  void navigateToRoute(String route) {
    closeDrawer();

    // Add a small delay to allow drawer to close smoothly
    Future.delayed(const Duration(milliseconds: 200), () {
      switch (route) {
        case '/profile':
          Navigator.of(context).push(
            MaterialPageRoute(builder: (context) => const ProfileScreen()),
          );
          break;
        case '/bank-details':
          Navigator.of(context).push(
            MaterialPageRoute(builder: (context) => const BankDetailsScreen()),
          );
          break;
        case '/how-to-play':
          Navigator.of(context).push(
            MaterialPageRoute(builder: (context) => const HowToPlayScreen()),
          );
          break;
        case '/active-purchases':
          Navigator.of(context).push(
            MaterialPageRoute(
              builder: (context) => const ActivePurchasesScreen(),
            ),
          );
          break;
        case '/help-support':
          Navigator.of(context).push(
            MaterialPageRoute(builder: (context) => const HelpSupportScreen()),
          );
          break;
        case '/terms-conditions':
          Navigator.of(context).push(
            MaterialPageRoute(
              builder: (context) => const TermsConditionsScreen(),
            ),
          );
          break;
        default:
          debugPrint('Unknown route: $route');
      }
    });
  }

  void onProfilePictureTap() {
    openDrawer();
  }

  void onMenuItemTap(DrawerMenuItem item) {
    if (item.isEnabled) {
      navigateToRoute(item.route);
    }
  }
}
