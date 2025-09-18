import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/wallet_provider.dart';

class BankDetailsScreen extends StatefulWidget {
  const BankDetailsScreen({super.key});

  @override
  State<BankDetailsScreen> createState() => _BankDetailsScreenState();
}

class _BankDetailsScreenState extends State<BankDetailsScreen> {
  final _formKey = GlobalKey<FormState>();
  final _accountNumberController = TextEditingController();
  final _ifscCodeController = TextEditingController();
  final _bankNameController = TextEditingController();
  final _accountHolderNameController = TextEditingController();
  final _placeController = TextEditingController();
  final _upiIdController = TextEditingController();
  final _extraParameterController = TextEditingController();

  bool _isEditing = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadBankDetails();
    });
  }

  Future<void> _loadBankDetails() async {
    final walletProvider = Provider.of<WalletProvider>(context, listen: false);
    await walletProvider.loadBankDetails();

    if (walletProvider.bankDetails != null) {
      _initializeFields(walletProvider.bankDetails!);
    }
  }

  void _initializeFields(Map<String, dynamic> bankDetails) {
    _accountNumberController.text = bankDetails['accountNumber'] ?? '';
    _ifscCodeController.text = bankDetails['ifscCode'] ?? '';
    _bankNameController.text = bankDetails['bankName'] ?? '';
    _accountHolderNameController.text = bankDetails['accountHolderName'] ?? '';
    _placeController.text = bankDetails['place'] ?? '';
    _upiIdController.text = bankDetails['upiId'] ?? '';
    _extraParameterController.text = bankDetails['extraParameter1'] ?? '';
  }

  @override
  void dispose() {
    _accountNumberController.dispose();
    _ifscCodeController.dispose();
    _bankNameController.dispose();
    _accountHolderNameController.dispose();
    _placeController.dispose();
    _upiIdController.dispose();
    _extraParameterController.dispose();
    super.dispose();
  }

  void _toggleEdit() {
    setState(() {
      _isEditing = !_isEditing;
    });
  }

  Future<void> _saveBankDetails() async {
    if (_formKey.currentState!.validate()) {
      final walletProvider = Provider.of<WalletProvider>(
        context,
        listen: false,
      );

      final bankData = {
        'accountNumber': _accountNumberController.text.trim(),
        'ifscCode': _ifscCodeController.text.trim().toUpperCase(),
        'bankName': _bankNameController.text.trim(),
        'accountHolderName': _accountHolderNameController.text.trim(),
        'place': _placeController.text.trim(),
        'upiId': _upiIdController.text.trim(),
        'extraParameter1': _extraParameterController.text.trim(),
      };

      final success = await walletProvider.addBankDetails(bankData);

      if (success && mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Bank details saved successfully!'),
            backgroundColor: Colors.green,
          ),
        );
        setState(() {
          _isEditing = false;
        });
      } else if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              walletProvider.error ?? 'Failed to save bank details',
            ),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'Bank Details',
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
          Consumer<WalletProvider>(
            builder: (context, walletProvider, child) {
              if (walletProvider.bankDetails == null) {
                return const SizedBox.shrink();
              }

              return TextButton(
                onPressed: walletProvider.isLoading ? null : _toggleEdit,
                child: ShaderMask(
                  shaderCallback: (bounds) => const LinearGradient(
                    colors: [Color(0xFFdb9822), Color(0xFFffb32c)],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ).createShader(bounds),
                  child: Text(
                    _isEditing ? 'Cancel' : 'Edit',
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                    ),
                  ),
                ),
              );
            },
          ),
        ],
      ),
      body: Consumer<WalletProvider>(
        builder: (context, walletProvider, child) {
          if (walletProvider.isLoading) {
            return const Center(child: CircularProgressIndicator());
          }

          if (walletProvider.bankDetails == null && !_isEditing) {
            return _buildEmptyState();
          }

          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Form(
              key: _formKey,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
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
                    child: Column(
                      children: [
                        const Icon(
                          Icons.account_balance_rounded,
                          size: 48,
                          color: Colors.white,
                        ),
                        const SizedBox(height: 12),
                        Text(
                          _isEditing ? 'Edit Bank Details' : 'Bank Details',
                          style: const TextStyle(
                            fontSize: 22,
                            fontWeight: FontWeight.bold,
                            color: Colors.white,
                            letterSpacing: 0.5,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          _isEditing
                              ? 'Update your bank account information'
                              : 'Your bank account information for withdrawals',
                          style: const TextStyle(
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

                  // Bank Details Form
                  if (_isEditing) ...[
                    _buildFormFields(),
                    const SizedBox(height: 32),
                    SizedBox(
                      width: double.infinity,
                      child: Container(
                        width: double.infinity,
                        decoration: BoxDecoration(
                          gradient: const LinearGradient(
                            colors: [Color(0xFFdb9822), Color(0xFFffb32c)],
                            begin: Alignment.topLeft,
                            end: Alignment.bottomRight,
                          ),
                          borderRadius: BorderRadius.circular(12),
                          boxShadow: [
                            BoxShadow(
                              color: const Color(0xFFdb9822).withOpacity(0.3),
                              blurRadius: 8,
                              offset: const Offset(0, 4),
                            ),
                          ],
                        ),
                        child: ElevatedButton(
                          onPressed: walletProvider.isLoading
                              ? null
                              : _saveBankDetails,
                          style: ElevatedButton.styleFrom(
                            padding: const EdgeInsets.symmetric(vertical: 16),
                            backgroundColor: Colors.transparent,
                            shadowColor: Colors.transparent,
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(12),
                            ),
                          ),
                          child: walletProvider.isLoading
                              ? const CircularProgressIndicator(
                                  color: Colors.white,
                                )
                              : const Text(
                                  'Save Bank Details',
                                  style: TextStyle(
                                    fontSize: 16,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                        ),
                      ),
                    ),
                  ] else ...[
                    _buildBankDetailsDisplay(walletProvider.bankDetails!),
                  ],

                  const SizedBox(height: 16),

                  // Info Card
                  Container(
                    padding: const EdgeInsets.all(20),
                    decoration: BoxDecoration(
                      color: const Color(0xFFdb9822).withOpacity(0.1),
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(
                        color: const Color(0xFFdb9822).withOpacity(0.3),
                        width: 1,
                      ),
                    ),
                    child: const Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Icon(
                              Icons.info_rounded,
                              color: Color(0xFFdb9822),
                              size: 20,
                            ),
                            SizedBox(width: 8),
                            Text(
                              'Important',
                              style: TextStyle(
                                fontWeight: FontWeight.bold,
                                color: Color(0xFFdb9822),
                                fontSize: 16,
                              ),
                            ),
                          ],
                        ),
                        SizedBox(height: 12),
                        Text(
                          '• Bank details are required for withdrawals\n• Ensure all information is accurate\n• Withdrawals will be processed to this account\n• Contact support if you need to change bank details',
                          style: TextStyle(
                            fontSize: 14,
                            color: Color(0xFFdb9822),
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
        },
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.account_balance, size: 80, color: Colors.grey),
            const SizedBox(height: 24),
            const Text(
              'No Bank Details',
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: Colors.grey,
              ),
            ),
            const SizedBox(height: 12),
            const Text(
              'Add your bank details to enable withdrawals',
              style: TextStyle(fontSize: 16, color: Colors.grey),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 32),
            Container(
              width: double.infinity,
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [Color(0xFFdb9822), Color(0xFFffb32c)],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(12),
                boxShadow: [
                  BoxShadow(
                    color: const Color(0xFFdb9822).withOpacity(0.3),
                    blurRadius: 8,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              child: ElevatedButton.icon(
                onPressed: () {
                  setState(() {
                    _isEditing = true;
                  });
                },
                icon: const Icon(Icons.add_rounded, color: Colors.white),
                label: const Text(
                  'Add Bank Details',
                  style: TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 32,
                    vertical: 16,
                  ),
                  backgroundColor: Colors.transparent,
                  shadowColor: Colors.transparent,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFormFields() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Bank Information',
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
            color: Color(0xFFdb9822),
            letterSpacing: 0.5,
          ),
        ),
        const SizedBox(height: 16),

        // Bank Name
        TextFormField(
          controller: _bankNameController,
          decoration: InputDecoration(
            labelText: 'Bank Name',
            prefixIcon: const Icon(
              Icons.account_balance_rounded,
              color: Color(0xFFdb9822),
            ),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide(color: Colors.grey[300]!),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: Color(0xFFdb9822), width: 2),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide(color: Colors.grey[300]!),
            ),
            filled: true,
            fillColor: Colors.grey[50],
          ),
          validator: (value) {
            if (value == null || value.trim().isEmpty) {
              return 'Please enter bank name';
            }
            return null;
          },
        ),
        const SizedBox(height: 16),

        // Account Number
        TextFormField(
          controller: _accountNumberController,
          keyboardType: TextInputType.number,
          decoration: InputDecoration(
            labelText: 'Account Number',
            prefixIcon: const Icon(
              Icons.credit_card_rounded,
              color: Color(0xFFdb9822),
            ),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide(color: Colors.grey[300]!),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: Color(0xFFdb9822), width: 2),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide(color: Colors.grey[300]!),
            ),
            filled: true,
            fillColor: Colors.grey[50],
          ),
          validator: (value) {
            if (value == null || value.trim().isEmpty) {
              return 'Please enter account number';
            }
            if (value.length < 9) {
              return 'Account number must be at least 9 digits';
            }
            return null;
          },
        ),
        const SizedBox(height: 16),

        // IFSC Code
        TextFormField(
          controller: _ifscCodeController,
          textCapitalization: TextCapitalization.characters,
          decoration: InputDecoration(
            labelText: 'IFSC Code',
            prefixIcon: const Icon(
              Icons.code_rounded,
              color: Color(0xFFdb9822),
            ),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide(color: Colors.grey[300]!),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: Color(0xFFdb9822), width: 2),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide(color: Colors.grey[300]!),
            ),
            filled: true,
            fillColor: Colors.grey[50],
          ),
          validator: (value) {
            if (value == null || value.trim().isEmpty) {
              return 'Please enter IFSC code';
            }
            if (value.length != 11) {
              return 'IFSC code must be 11 characters';
            }
            return null;
          },
        ),
        const SizedBox(height: 16),

        // Account Holder Name
        TextFormField(
          controller: _accountHolderNameController,
          decoration: InputDecoration(
            labelText: 'Account Holder Name',
            prefixIcon: const Icon(
              Icons.person_rounded,
              color: Color(0xFFdb9822),
            ),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide(color: Colors.grey[300]!),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: Color(0xFFdb9822), width: 2),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide(color: Colors.grey[300]!),
            ),
            filled: true,
            fillColor: Colors.grey[50],
          ),
          validator: (value) {
            if (value == null || value.trim().isEmpty) {
              return 'Please enter account holder name';
            }
            return null;
          },
        ),
        const SizedBox(height: 16),

        // Place
        TextFormField(
          controller: _placeController,
          decoration: InputDecoration(
            labelText: 'Place',
            prefixIcon: const Icon(
              Icons.location_on_rounded,
              color: Color(0xFFdb9822),
            ),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide(color: Colors.grey[300]!),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: Color(0xFFdb9822), width: 2),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide(color: Colors.grey[300]!),
            ),
            filled: true,
            fillColor: Colors.grey[50],
          ),
          validator: (value) {
            if (value == null || value.trim().isEmpty) {
              return 'Please enter place';
            }
            return null;
          },
        ),
        const SizedBox(height: 16),

        // UPI ID (Optional)
        TextFormField(
          controller: _upiIdController,
          decoration: InputDecoration(
            labelText: 'UPI ID (Optional)',
            prefixIcon: const Icon(
              Icons.payment_rounded,
              color: Color(0xFFdb9822),
            ),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide(color: Colors.grey[300]!),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: Color(0xFFdb9822), width: 2),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide(color: Colors.grey[300]!),
            ),
            filled: true,
            fillColor: Colors.grey[50],
          ),
        ),
        const SizedBox(height: 16),

        // Extra Parameter (Optional)
        TextFormField(
          controller: _extraParameterController,
          decoration: InputDecoration(
            labelText: 'Additional Information (Optional)',
            prefixIcon: const Icon(
              Icons.info_rounded,
              color: Color(0xFFdb9822),
            ),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide(color: Colors.grey[300]!),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: Color(0xFFdb9822), width: 2),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide(color: Colors.grey[300]!),
            ),
            filled: true,
            fillColor: Colors.grey[50],
          ),
        ),
      ],
    );
  }

  Widget _buildBankDetailsDisplay(Map<String, dynamic> bankDetails) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(
                  Icons.account_balance_rounded,
                  color: Color(0xFFdb9822),
                ),
                const SizedBox(width: 8),
                const Text(
                  'Bank Details',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFFdb9822),
                  ),
                ),
                const Spacer(),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 8,
                    vertical: 4,
                  ),
                  decoration: BoxDecoration(
                    color: bankDetails['isVerified'] == true
                        ? Colors.green.withOpacity(0.1)
                        : Colors.orange.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(
                      color: bankDetails['isVerified'] == true
                          ? Colors.green
                          : Colors.orange,
                    ),
                  ),
                  child: Text(
                    bankDetails['isVerified'] == true ? 'Verified' : 'Pending',
                    style: TextStyle(
                      color: bankDetails['isVerified'] == true
                          ? Colors.green
                          : Colors.orange,
                      fontWeight: FontWeight.bold,
                      fontSize: 12,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            _buildDetailRow('Bank Name', bankDetails['bankName'] ?? 'N/A'),
            _buildDetailRow(
              'Account Number',
              _maskAccountNumber(bankDetails['accountNumber']),
            ),
            _buildDetailRow('IFSC Code', bankDetails['ifscCode'] ?? 'N/A'),
            _buildDetailRow(
              'Account Holder',
              bankDetails['accountHolderName'] ?? 'N/A',
            ),
            _buildDetailRow('Place', bankDetails['place'] ?? 'N/A'),
            if (bankDetails['upiId'] != null && bankDetails['upiId'].isNotEmpty)
              _buildDetailRow('UPI ID', bankDetails['upiId']),
            if (bankDetails['extraParameter1'] != null &&
                bankDetails['extraParameter1'].isNotEmpty)
              _buildDetailRow(
                'Additional Info',
                bankDetails['extraParameter1'],
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildDetailRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 120,
            child: Text(
              '$label:',
              style: const TextStyle(
                fontWeight: FontWeight.bold,
                color: Colors.grey,
              ),
            ),
          ),
          Expanded(child: Text(value, style: const TextStyle(fontSize: 16))),
        ],
      ),
    );
  }

  String _maskAccountNumber(String? accountNumber) {
    if (accountNumber == null || accountNumber.isEmpty) {
      return 'N/A';
    }
    if (accountNumber.length <= 4) {
      return accountNumber;
    }
    return '****${accountNumber.substring(accountNumber.length - 4)}';
  }
}
