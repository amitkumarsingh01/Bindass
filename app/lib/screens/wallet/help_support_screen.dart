import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../providers/contact_provider.dart';

class HelpSupportScreen extends StatefulWidget {
  const HelpSupportScreen({super.key});

  @override
  State<HelpSupportScreen> createState() => _HelpSupportScreenState();
}

class _HelpSupportScreenState extends State<HelpSupportScreen> {
  @override
  void initState() {
    super.initState();
    // Load contact info when screen initializes
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<ContactProvider>().loadContactInfo();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'Help & Support',
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
      ),
      body: Consumer<ContactProvider>(
        builder: (context, contactProvider, child) {
          if (contactProvider.isLoading) {
            return const Center(
              child: CircularProgressIndicator(
                valueColor: AlwaysStoppedAnimation<Color>(Color(0xFFdb9822)),
              ),
            );
          }

          if (contactProvider.error != null) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.error_outline, size: 64, color: Colors.red),
                  const SizedBox(height: 16),
                  Text(
                    'Failed to load contact information',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.w600,
                      color: Colors.grey[800],
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    contactProvider.error!,
                    style: TextStyle(fontSize: 14, color: Colors.grey[600]),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 24),
                  ElevatedButton(
                    onPressed: () => contactProvider.loadContactInfo(),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFFdb9822),
                      foregroundColor: Colors.white,
                    ),
                    child: const Text('Retry'),
                  ),
                ],
              ),
            );
          }

          final contactInfo = contactProvider.contactInfo;
          if (contactInfo == null) {
            return const Center(
              child: Text('No contact information available'),
            );
          }

          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                // Header
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(28),
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      colors: [
                        const Color(0xFFdb9822).withOpacity(0.8),
                        const Color(0xFFffb32c).withOpacity(0.9),
                      ],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                    borderRadius: BorderRadius.circular(20),
                    boxShadow: [
                      BoxShadow(
                        color: const Color(0xFFdb9822).withOpacity(0.15),
                        blurRadius: 15,
                        offset: const Offset(0, 6),
                      ),
                    ],
                  ),
                  child: const Column(
                    children: [
                      Icon(Icons.help_rounded, size: 48, color: Colors.white),
                      SizedBox(height: 12),
                      Text(
                        'Help & Support',
                        style: TextStyle(
                          fontSize: 22,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                          letterSpacing: 0.5,
                        ),
                      ),
                      SizedBox(height: 8),
                      Text(
                        'Get help and contact our support team',
                        style: TextStyle(
                          fontSize: 14,
                          color: Colors.white,
                          fontWeight: FontWeight.w500,
                        ),
                        textAlign: TextAlign.center,
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 24),
                // Support Options
                _SupportOption(
                  icon: Icons.phone_rounded,
                  title: 'Call Support',
                  subtitle: contactInfo.contactNo,
                  onTap: () => _makePhoneCall(contactInfo.contactNo),
                ),
                const SizedBox(height: 12),
                _SupportOption(
                  icon: Icons.email_rounded,
                  title: 'Email Support',
                  subtitle: contactInfo.email,
                  onTap: () => _sendEmail(contactInfo.email),
                ),
                const SizedBox(height: 12),
                _SupportOption(
                  icon: Icons.web_rounded,
                  title: 'Visit Website',
                  subtitle: contactInfo.website,
                  onTap: () => _openWebsite(contactInfo.website),
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  Future<void> _makePhoneCall(String phoneNumber) async {
    final Uri phoneUri = Uri(scheme: 'tel', path: phoneNumber);
    try {
      if (await canLaunchUrl(phoneUri)) {
        await launchUrl(phoneUri);
      } else {
        _showErrorSnackBar('Could not make phone call');
      }
    } catch (e) {
      _showErrorSnackBar('Error making phone call: $e');
    }
  }

  Future<void> _sendEmail(String email) async {
    final Uri emailUri = Uri(
      scheme: 'mailto',
      path: email,
      query: 'subject=Support Request&body=Hello, I need help with...',
    );
    try {
      if (await canLaunchUrl(emailUri)) {
        await launchUrl(emailUri);
      } else {
        _showErrorSnackBar('Could not open email client');
      }
    } catch (e) {
      _showErrorSnackBar('Error opening email: $e');
    }
  }

  Future<void> _openWebsite(String website) async {
    try {
      // Ensure the website URL has a proper protocol
      String url = website.trim();
      if (url.isEmpty) {
        _showErrorSnackBar('Website URL is empty');
        return;
      }

      if (!url.startsWith('http://') && !url.startsWith('https://')) {
        url = 'https://$url';
      }

      final Uri websiteUri = Uri.parse(url);

      // Validate the URI
      if (websiteUri.scheme.isEmpty || websiteUri.host.isEmpty) {
        _showErrorSnackBar('Invalid website URL: $url');
        return;
      }

      // Try different launch modes
      bool launched = false;

      // First try with external application mode
      if (await canLaunchUrl(websiteUri)) {
        launched = await launchUrl(
          websiteUri,
          mode: LaunchMode.externalApplication,
        );
      }

      // If external launch failed, try with platform default
      if (!launched) {
        if (await canLaunchUrl(websiteUri)) {
          launched = await launchUrl(
            websiteUri,
            mode: LaunchMode.platformDefault,
          );
        }
      }

      if (!launched) {
        _showWebsiteDialog(url);
      }
    } catch (e) {
      _showErrorSnackBar('Error opening website: $e');
    }
  }

  void _showWebsiteDialog(String url) {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text('Cannot Open Website'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('Unable to open the website automatically.'),
              const SizedBox(height: 8),
              const Text('Website URL:'),
              const SizedBox(height: 4),
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.grey[100],
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.grey[300]!),
                ),
                child: SelectableText(
                  url,
                  style: const TextStyle(fontFamily: 'monospace'),
                ),
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('Close'),
            ),
            ElevatedButton(
              onPressed: () {
                Navigator.of(context).pop();
                // Try to copy to clipboard
                // You can add clipboard functionality here if needed
                _showErrorSnackBar('Please copy the URL manually');
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFFdb9822),
                foregroundColor: Colors.white,
              ),
              child: const Text('Copy URL'),
            ),
          ],
        );
      },
    );
  }

  void _showErrorSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), backgroundColor: Colors.red),
    );
  }
}

class _SupportOption extends StatelessWidget {
  final IconData icon;
  final String title;
  final String subtitle;
  final VoidCallback onTap;

  const _SupportOption({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 2,
      shadowColor: Colors.grey.withOpacity(0.1),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
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
                child: Icon(icon, size: 24, color: Colors.white),
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
    );
  }
}
