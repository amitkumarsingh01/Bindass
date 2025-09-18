import 'package:flutter/material.dart';

class AppDrawerModel {
  final String userName;
  final String? profileImageUrl;
  final double walletBalance;
  final List<DrawerMenuItem> menuItems;

  AppDrawerModel({
    required this.userName,
    this.profileImageUrl,
    required this.walletBalance,
    required this.menuItems,
  });

  factory AppDrawerModel.fromAuthProvider(
    Map<String, dynamic>? user,
    double balance, {
    String? profilePictureUrl,
  }) {
    return AppDrawerModel(
      userName: user?['userName'] ?? 'User',
      profileImageUrl: profilePictureUrl,
      walletBalance: balance,
      menuItems: _getDefaultMenuItems(),
    );
  }

  static List<DrawerMenuItem> _getDefaultMenuItems() {
    final items = <DrawerMenuItem>[
      DrawerMenuItem(
        id: 'profile',
        title: 'Profile Settings',
        icon: Icons.person_rounded,
        route: '/profile',
      ),
      DrawerMenuItem(
        id: 'bank',
        title: 'Bank Details',
        icon: Icons.account_balance_rounded,
        route: '/bank-details',
      ),
      DrawerMenuItem(
        id: 'how-to-play',
        title: 'How to Play',
        icon: Icons.help_rounded,
        route: '/how-to-play',
      ),
      DrawerMenuItem(
        id: 'help',
        title: 'Help & Support',
        icon: Icons.support_agent_rounded,
        route: '/help-support',
      ),
      DrawerMenuItem(
        id: 'terms',
        title: 'Terms & Conditions',
        icon: Icons.description_rounded,
        route: '/terms-conditions',
      ),
    ];
    return items;
  }

  AppDrawerModel copyWith({
    String? userName,
    String? profileImageUrl,
    double? walletBalance,
    List<DrawerMenuItem>? menuItems,
  }) {
    return AppDrawerModel(
      userName: userName ?? this.userName,
      profileImageUrl: profileImageUrl ?? this.profileImageUrl,
      walletBalance: walletBalance ?? this.walletBalance,
      menuItems: menuItems ?? this.menuItems,
    );
  }
}

class DrawerMenuItem {
  final String id;
  final String title;
  final IconData icon;
  final String route;
  final bool isEnabled;

  const DrawerMenuItem({
    required this.id,
    required this.title,
    required this.icon,
    required this.route,
    this.isEnabled = true,
  });
}
