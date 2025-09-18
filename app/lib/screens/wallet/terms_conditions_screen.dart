import 'package:flutter/material.dart';

class TermsConditionsScreen extends StatelessWidget {
  const TermsConditionsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'Terms & Conditions',
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
      body: SingleChildScrollView(
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
                  Icon(
                    Icons.description_rounded,
                    size: 48,
                    color: Colors.white,
                  ),
                  SizedBox(height: 12),
                  Text(
                    'Terms & Conditions',
                    style: TextStyle(
                      fontSize: 22,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                      letterSpacing: 0.5,
                    ),
                  ),
                  SizedBox(height: 8),
                  Text(
                    'Please read our terms and conditions carefully',
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
            // Terms Content
            _TermsSection(
              title: '1. Acceptance of Terms',
              content: 'By using this application, you agree to be bound by these terms and conditions. If you do not agree to these terms, please do not use the application.',
            ),
            const SizedBox(height: 16),
            _TermsSection(
              title: '2. Eligibility',
              content: 'You must be at least 18 years old to use this application. You must provide accurate and complete information when registering.',
            ),
            const SizedBox(height: 16),
            _TermsSection(
              title: '3. Contest Rules',
              content: 'All contests are subject to specific rules and regulations. Prizes are awarded based on the contest results and are non-transferable.',
            ),
            const SizedBox(height: 16),
            _TermsSection(
              title: '4. Payment Terms',
              content: 'All payments are processed securely. Refunds are subject to our refund policy and may take 5-7 business days to process.',
            ),
            const SizedBox(height: 16),
            _TermsSection(
              title: '5. Privacy Policy',
              content: 'Your privacy is important to us. Please review our privacy policy to understand how we collect, use, and protect your information.',
            ),
            const SizedBox(height: 16),
            _TermsSection(
              title: '6. Limitation of Liability',
              content: 'We are not liable for any indirect, incidental, special, or consequential damages arising from your use of the application.',
            ),
            const SizedBox(height: 16),
            _TermsSection(
              title: '7. Changes to Terms',
              content: 'We reserve the right to modify these terms at any time. Continued use of the application constitutes acceptance of the modified terms.',
            ),
          ],
        ),
      ),
    );
  }
}

class _TermsSection extends StatelessWidget {
  final String title;
  final String content;

  const _TermsSection({
    required this.title,
    required this.content,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 2,
      shadowColor: Colors.grey.withOpacity(0.1),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: const TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 16,
                color: Color(0xFFdb9822),
                letterSpacing: 0.3,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              content,
              style: TextStyle(
                fontSize: 14,
                color: Colors.grey[700],
                fontWeight: FontWeight.w400,
                height: 1.5,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
