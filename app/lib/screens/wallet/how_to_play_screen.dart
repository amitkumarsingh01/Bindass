import 'package:flutter/material.dart';

class HowToPlayScreen extends StatefulWidget {
  const HowToPlayScreen({super.key});

  @override
  State<HowToPlayScreen> createState() => _HowToPlayScreenState();
}

class _HowToPlayScreenState extends State<HowToPlayScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'How to Play',
          style: TextStyle(
            color: Colors.black87,
            fontWeight: FontWeight.w600,
            fontSize: 18,
          ),
        ),
        backgroundColor: Colors.white,
        foregroundColor: Colors.black87,
        elevation: 0,
        shadowColor: Colors.transparent,
        surfaceTintColor: Colors.transparent,
        bottom: TabBar(
          controller: _tabController,
          labelColor: const Color(0xFFdb9822),
          unselectedLabelColor: Colors.grey[600],
          indicatorColor: const Color(0xFFdb9822),
          indicatorWeight: 3,
          tabs: const [
            Tab(text: 'English'),
            Tab(text: 'हिंदी'),
            Tab(text: 'ಕನ್ನಡ'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildEnglishContent(),
          _buildHindiContent(),
          _buildKannadaContent(),
        ],
      ),
    );
  }

  Widget _buildEnglishContent() {
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
                // Icon(Icons.play_circle_rounded, size: 48, color: Colors.white),
                // SizedBox(height: 12),
                Text(
                  'Welcome to Bindass Grand',
                  style: TextStyle(
                    fontSize: 22,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                    letterSpacing: 0.5,
                  ),
                ),
                SizedBox(height: 8),
                Text(
                  'where fun meets fortune! Follow these simple steps to start playing and win exciting prizes.',
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
          // Steps
          _PlayStep(
            stepNumber: 1,
            title: 'Choose Your Contest',
            description:
                'Contests start from ₹100, ₹200, ₹300, and so on.\n\nPick the contest you want to participate in based on your preference and budget.',
          ),
          const SizedBox(height: 16),
          _PlayStep(
            stepNumber: 2,
            title: 'Select Vehicle Category',
            description:
                'After choosing the contest, you will select a vehicle category range.\n\nThe categories are like 1 – 1000, 1001 – 2000, and so on, up to 10,000.\n\nEach category contains 10,000 slots.',
          ),
          const SizedBox(height: 16),
          _PlayStep(
            stepNumber: 3,
            title: 'Pick Your Number',
            description:
                'Each slot represents a unique number.\n\nSelect the number you want to play with.\n\nThe price will be charged based on the contest amount you chose.',
          ),
          const SizedBox(height: 16),
          _PlayStep(
            stepNumber: 4,
            title: 'Lock Your Number',
            description:
                'Once you purchase a number, it gets locked.\n\nNobody else can select the same number once it is bought.',
          ),
          const SizedBox(height: 16),
          _PlayStep(
            stepNumber: 5,
            title: 'Wait for the Contest to Complete',
            description:
                'When all 10,000 slots in a category are filled, the contest will be completed.\n\nThe result will be announced.',
          ),
          const SizedBox(height: 16),
          _PlayStep(
            stepNumber: 6,
            title: 'Win and Withdraw',
            description:
                'Based on the result, winners will be selected.\n\nThe prize amount will be credited to the user\'s account.\n\nYou can withdraw the prize within 48 hours.',
          ),
          const SizedBox(height: 24),
          // Additional Information
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: Colors.blue[50],
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: Colors.blue[200]!),
            ),
            child: const Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Additional Information',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Colors.blue,
                  ),
                ),
                SizedBox(height: 12),
                Text(
                  '• Make sure to double-check your selected number before purchasing.\n'
                  '• Keep your account details safe.\n'
                  '• Play responsibly and enjoy the excitement!\n'
                  '• Support is available if you face any issues during the game.\n\n'
                  'Get ready to play, have fun, and win big with Bindass Grand!',
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.black87,
                    height: 1.5,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildHindiContent() {
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
                // Icon(Icons.play_circle_rounded, size: 48, color: Colors.white),
                // SizedBox(height: 12),
                Text(
                  'Bindass Grand में आपका स्वागत है!',
                  style: TextStyle(
                    fontSize: 22,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                    letterSpacing: 0.5,
                  ),
                ),
                SizedBox(height: 8),
                Text(
                  'यहाँ मज़ा और जीत का शानदार मौका है। नीचे दिए गए आसान चरणों का पालन करें और पुरस्कार जीतें।',
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
          // Steps
          _PlayStep(
            stepNumber: 1,
            title: 'अपना कंटेस्ट चुनें',
            description:
                'कंटेस्ट ₹100, ₹200, ₹300 आदि से शुरू होते हैं।\n\nअपनी पसंद और बजट के अनुसार कोई कंटेस्ट चुनें।',
          ),
          const SizedBox(height: 16),
          _PlayStep(
            stepNumber: 2,
            title: 'वाहन श्रेणी चुनें',
            description:
                'कंटेस्ट चुनने के बाद वाहन श्रेणी चुनें।\n\nश्रेणियाँ 1 – 1000, 1001 – 2000 और इसी तरह 10,000 तक उपलब्ध हैं।\n\nप्रत्येक श्रेणी में 10,000 स्लॉट्स होते हैं।',
          ),
          const SizedBox(height: 16),
          _PlayStep(
            stepNumber: 3,
            title: 'अपना नंबर चुनें',
            description:
                'प्रत्येक स्लॉट एक अलग नंबर को दर्शाता है।\n\nजिस नंबर पर खेलना चाहते हैं उसे चुनें।\n\nचयनित कंटेस्ट के अनुसार राशि आपके खाते से कटेगी।',
          ),
          const SizedBox(height: 16),
          _PlayStep(
            stepNumber: 4,
            title: 'नंबर लॉक करें',
            description:
                'नंबर खरीदते ही लॉक हो जाएगा।\n\nकोई दूसरा उपयोगकर्ता वही नंबर नहीं चुन सकता।',
          ),
          const SizedBox(height: 16),
          _PlayStep(
            stepNumber: 5,
            title: 'कंटेस्ट पूरा होने का इंतजार करें',
            description:
                'जब किसी श्रेणी के सभी 10,000 स्लॉट्स भर जाएँगे तो कंटेस्ट पूरा होगा।\n\nपरिणाम घोषित किए जाएँगे।',
          ),
          const SizedBox(height: 16),
          _PlayStep(
            stepNumber: 6,
            title: 'जीतें और पैसे निकालें',
            description:
                'परिणाम के आधार पर विजेता चुने जाएँगे।\n\nपुरस्कार राशि आपके खाते में जमा की जाएगी।\n\nआप 48 घंटे के अंदर राशि निकाल सकते हैं।',
          ),
          const SizedBox(height: 24),
          // Additional Information
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: Colors.blue[50],
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: Colors.blue[200]!),
            ),
            child: const Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'अतिरिक्त जानकारी',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Colors.blue,
                  ),
                ),
                SizedBox(height: 12),
                Text(
                  '• नंबर खरीदने से पहले उसे ज़रूर जांच लें।\n'
                  '• अपने खाते की जानकारी सुरक्षित रखें।\n'
                  '• जिम्मेदारी से खेलें और खेल का आनंद लें।\n'
                  '• कोई समस्या हो तो सहायता टीम से संपर्क करें।\n\n'
                  'तैयार हो जाइए और Bindass Grand में खेलकर बड़ा इनाम जीतिए!',
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.black87,
                    height: 1.5,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildKannadaContent() {
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
                // Icon(Icons.play_circle_rounded, size: 48, color: Colors.white),
                // SizedBox(height: 12),
                Text(
                  'Bindass Grand ಗೆ ಸ್ವಾಗತ!',
                  style: TextStyle(
                    fontSize: 22,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                    letterSpacing: 0.5,
                  ),
                ),
                SizedBox(height: 8),
                Text(
                  'ಇಲ್ಲಿ ಮಜಾ ಮತ್ತು ಬಹುಮಾನ ಗಳಿಸಲು ಸುಲಭವಾದ ಅವಕಾಶ ಇದೆ। ಕೆಳಗಿನ ಹಂತಗಳನ್ನು ಅನುಸರಿಸಿ ಆಟವನ್ನು ಪ್ರಾರಂಭಿಸಿ।',
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
          // Steps
          _PlayStep(
            stepNumber: 1,
            title: 'ನಿಮ್ಮ ಕಾನ್ಟೆಸ್ಟ್ ಆಯ್ಕೆ ಮಾಡಿ',
            description:
                'ಕಾನ್ಟೆಸ್ಟ್‌ಗಳು ₹100, ₹200, ₹300 ಇವುಗಳಿಂದ ಪ್ರಾರಂಭವಾಗುತ್ತವೆ.\n\nನಿಮ್ಮ ಇಷ್ಟ ಮತ್ತು ಬಜೆಟ್‌ಗೆ ತಕ್ಕಂತೆ ಒಂದು ಕಾನ್ಟೆಸ್ಟ್ ಆಯ್ಕೆ ಮಾಡಿ।',
          ),
          const SizedBox(height: 16),
          _PlayStep(
            stepNumber: 2,
            title: 'ವಾಹನ ವರ್ಗವನ್ನು ಆಯ್ಕೆ ಮಾಡಿ',
            description:
                'ಕಾನ್ಟೆಸ್ಟ್ ಆಯ್ಕೆ ಮಾಡಿದ ನಂತರ ವಾಹನ ವರ್ಗವನ್ನು ಆಯ್ಕೆ ಮಾಡಿ.\n\nವರ್ಗಗಳು 1 – 1000, 1001 – 2000 ಹೀಗೆ 10,000 ವರೆಗೆ ಇರುತ್ತವೆ.\n\nಪ್ರತಿ ವರ್ಗದಲ್ಲೂ 10,000 ಸ್ಲಾಟ್‌ಗಳು ಇರುತ್ತವೆ।',
          ),
          const SizedBox(height: 16),
          _PlayStep(
            stepNumber: 3,
            title: 'ನಿಮ್ಮ ಸಂಖ್ಯೆಯನ್ನು ಆಯ್ಕೆ ಮಾಡಿ',
            description:
                'ಪ್ರತಿ ಸ್ಲಾಟ್ ಒಂದು ವಿಶೇಷ ಸಂಖ್ಯೆಯನ್ನು ಸೂಚಿಸುತ್ತದೆ.\n\nನೀವು ಆಡಲು ಇಚ್ಛಿಸುವ ಸಂಖ್ಯೆಯನ್ನು ಆಯ್ಕೆ ಮಾಡಿ.\n\nಆಯ್ಕೆ ಮಾಡಿದ ಕಾನ್ಟೆಸ್ಟ್‌ಗೆ ಅನುಗುಣವಾಗಿ ಹಣ ಕತ್ತರಿಸಲಾಗುತ್ತದೆ।',
          ),
          const SizedBox(height: 16),
          _PlayStep(
            stepNumber: 4,
            title: 'ಸಂಖ್ಯೆಯನ್ನು ಲಾಕ್ ಮಾಡಿ',
            description:
                'ಒಂದು ಸಂಖ್ಯೆಯನ್ನು ಖರೀದಿಸಿದ ಕೂಡಲೇ ಲಾಕ್ ಆಗುತ್ತದೆ.\n\nಬೇರೆ ಯಾರೂ ಅದೇ ಸಂಖ್ಯೆಯನ್ನು ಆಯ್ಕೆ ಮಾಡಲು ಸಾಧ್ಯವಾಗುವುದಿಲ್ಲ।',
          ),
          const SizedBox(height: 16),
          _PlayStep(
            stepNumber: 5,
            title: 'ಕಾನ್ಟೆಸ್ಟ್ ಮುಗಿಯುವವರೆಗೆ ಕಾಯಿರಿ',
            description:
                'ಒಂದು ವರ್ಗದ ಎಲ್ಲಾ 10,000 ಸ್ಲಾಟ್‌ಗಳು ತುಂಬಿದ ನಂತರ ಕಾನ್ಟೆಸ್ಟ್ ಮುಗಿಯುತ್ತದೆ.\n\nಫಲಿತಾಂಶವನ್ನು ಪ್ರಕಟಿಸಲಾಗುತ್ತದೆ।',
          ),
          const SizedBox(height: 16),
          _PlayStep(
            stepNumber: 6,
            title: 'ಗೆದ್ದು ಹಣವನ್ನು ಹಿಂಪಡೆಯಿರಿ',
            description:
                'ಫಲಿತಾಂಶದ ಆಧಾರದ ಮೇಲೆ ವಿಜೇತರನ್ನು ಆಯ್ಕೆ ಮಾಡಲಾಗುತ್ತದೆ.\n\nಬಹುಮಾನವನ್ನು ನಿಮ್ಮ ಖಾತೆಗೆ ಜಮಾ ಮಾಡಲಾಗುತ್ತದೆ.\n\nನೀವು 48 ಗಂಟೆಗಳೊಳಗೆ ಹಣವನ್ನು ಹಿಂಪಡೆಯಬಹುದು।',
          ),
          const SizedBox(height: 24),
          // Additional Information
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: Colors.blue[50],
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: Colors.blue[200]!),
            ),
            child: const Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'ಹೆಚ್ಚುವರಿ ಮಾಹಿತಿ',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Colors.blue,
                  ),
                ),
                SizedBox(height: 12),
                Text(
                  '• ಸಂಖ್ಯೆಯನ್ನು ಖರೀದಿಸುವ ಮೊದಲು ಖಚಿತವಾಗಿ ಪರಿಶೀಲಿಸಿ.\n'
                  '• ನಿಮ್ಮ ಖಾತೆ ವಿವರಗಳನ್ನು ಸುರಕ್ಷಿತವಾಗಿರಿಸಿ.\n'
                  '• ಜವಾಬ್ದಾರಿಯಿಂದ ಆಟವಾಡಿ ಮತ್ತು ಮಜಾ ಮಾಡಿ!\n'
                  '• ಯಾವುದೇ ಸಮಸ್ಯೆ ಎದುರಾದಲ್ಲಿ ಸಹಾಯಕ್ಕಾಗಿ ಸಂಪರ್ಕಿಸಿ.\n\n'
                  'ಆಟ ಪ್ರಾರಂಭಿಸಿ, ಮಜಾ ಮಾಡಿ ಮತ್ತು Bindass Grand ನಲ್ಲಿ ದೊಡ್ಡ ಬಹುಮಾನಗಳನ್ನು ಗೆದ್ದಿರಿ!',
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.black87,
                    height: 1.5,
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

class _PlayStep extends StatelessWidget {
  final int stepNumber;
  final String title;
  final String description;

  const _PlayStep({
    required this.stepNumber,
    required this.title,
    required this.description,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 2,
      shadowColor: Colors.grey.withOpacity(0.1),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              width: 40,
              height: 40,
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [Color(0xFFdb9822), Color(0xFFffb32c)],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(20),
              ),
              child: Center(
                child: Text(
                  stepNumber.toString(),
                  style: const TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                    fontSize: 18,
                  ),
                ),
              ),
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
                  const SizedBox(height: 8),
                  Text(
                    description,
                    style: TextStyle(
                      fontSize: 14,
                      color: Colors.grey[600],
                      fontWeight: FontWeight.w400,
                      height: 1.4,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
