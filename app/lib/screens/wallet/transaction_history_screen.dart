import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/wallet_provider.dart';

class TransactionHistoryScreen extends StatefulWidget {
  const TransactionHistoryScreen({super.key});

  @override
  State<TransactionHistoryScreen> createState() =>
      _TransactionHistoryScreenState();
}

class _TransactionHistoryScreenState extends State<TransactionHistoryScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      Provider.of<WalletProvider>(context, listen: false).loadTransactions();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Theme(
      data: Theme.of(context).copyWith(
        primaryColor: const Color(0xFFdb9822),
        colorScheme: Theme.of(context).colorScheme.copyWith(
          primary: const Color(0xFFdb9822),
          secondary: const Color(0xFFffb32c),
        ),
        textTheme: Theme.of(context).textTheme.copyWith(
          bodyLarge: const TextStyle(color: Colors.black87),
          bodyMedium: const TextStyle(color: Colors.black87),
          bodySmall: const TextStyle(color: Colors.black87),
        ),
      ),
      child: Scaffold(
        appBar: AppBar(
          title: const Text(
            'Transaction History',
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
                  Icons.refresh_rounded,
                  color: Color(0xFFdb9822),
                  size: 22,
                ),
                onPressed: () {
                  Provider.of<WalletProvider>(
                    context,
                    listen: false,
                  ).loadTransactions();
                },
              ),
            ),
          ],
        ),
        body: Consumer<WalletProvider>(
          builder: (context, walletProvider, child) {
            if (walletProvider.isLoading) {
              return const Center(child: CircularProgressIndicator());
            }

            if (walletProvider.error != null) {
              return Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Icon(
                      Icons.error_outline,
                      size: 64,
                      color: Colors.red,
                    ),
                    const SizedBox(height: 16),
                    Text(
                      'Error: ${walletProvider.error}',
                      style: const TextStyle(fontSize: 16),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 16),
                    Container(
                      decoration: BoxDecoration(
                        gradient: const LinearGradient(
                          colors: [Color(0xFFdb9822), Color(0xFFffb32c)],
                          begin: Alignment.topLeft,
                          end: Alignment.bottomRight,
                        ),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: ElevatedButton(
                        onPressed: () {
                          walletProvider.loadTransactions();
                        },
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.transparent,
                          shadowColor: Colors.transparent,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                        ),
                        child: const Text(
                          'Retry',
                          style: TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              );
            }

            if (walletProvider.transactions.isEmpty) {
              return Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    ShaderMask(
                      shaderCallback: (bounds) => const LinearGradient(
                        colors: [Color(0xFFdb9822), Color(0xFFffb32c)],
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                      ).createShader(bounds),
                      child: const Icon(
                        Icons.receipt_long_rounded,
                        size: 64,
                        color: Colors.white,
                      ),
                    ),
                    const SizedBox(height: 16),
                    const Text(
                      'No transactions found',
                      style: TextStyle(
                        fontSize: 18,
                        color: Color(0xFFdb9822),
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ),
              );
            }

            return RefreshIndicator(
              onRefresh: () async {
                await walletProvider.loadTransactions();
              },
              child: ListView.builder(
                padding: const EdgeInsets.all(16),
                itemCount: walletProvider.transactions.length,
                itemBuilder: (context, index) {
                  final transaction = walletProvider.transactions[index];
                  return _TransactionCard(transaction: transaction);
                },
              ),
            );
          },
        ),
      ),
    );
  }
}

class _TransactionCard extends StatelessWidget {
  final Map<String, dynamic> transaction;

  const _TransactionCard({required this.transaction});

  @override
  Widget build(BuildContext context) {
    final type = transaction['transactionType'] as String? ?? '';
    final amount = (transaction['amount'] as num?)?.toDouble() ?? 0.0;
    final description = transaction['description'] as String? ?? '';
    final category = transaction['category'] as String? ?? '';
    final createdAt = transaction['createdAt'] as String? ?? '';
    final status = transaction['status'] as String? ?? '';
    final balanceAfter =
        (transaction['balanceAfter'] as num?)?.toDouble() ?? 0.0;

    final isCredit = type.toLowerCase() == 'credit';
    final amountPrefix = isCredit ? '+' : '-';

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      elevation: 2,
      shadowColor: Colors.grey.withOpacity(0.1),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: ExpansionTile(
        leading: Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [
                const Color(0xFFdb9822).withOpacity(0.1),
                const Color(0xFFffb32c).withOpacity(0.1),
              ],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            borderRadius: BorderRadius.circular(20),
          ),
          child: CircleAvatar(
            backgroundColor: Colors.transparent,
            child: ShaderMask(
              shaderCallback: (bounds) => LinearGradient(
                colors: isCredit
                    ? [Colors.green, Colors.green.shade600]
                    : [const Color(0xFFdb9822), const Color(0xFFffb32c)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ).createShader(bounds),
              child: Icon(_getCategoryIcon(category), color: Colors.white),
            ),
          ),
        ),
        title: Text(
          description,
          style: const TextStyle(
            fontWeight: FontWeight.bold,
            color: Colors.black87,
          ),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              _formatCategory(category),
              style: const TextStyle(
                color: Color(0xFFdb9822),
                fontWeight: FontWeight.w500,
              ),
            ),
            Text(
              _formatDate(createdAt),
              style: TextStyle(color: Colors.grey[600], fontSize: 12),
            ),
          ],
        ),
        trailing: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.end,
          children: [
            Text(
              '$amountPrefix₹${amount.toStringAsFixed(2)}',
              style: TextStyle(
                fontWeight: FontWeight.bold,
                color: isCredit ? Colors.green : const Color(0xFFdb9822),
                fontSize: 16,
              ),
            ),
            Text(
              _formatStatus(status),
              style: TextStyle(fontSize: 12, color: _getStatusColor(status)),
            ),
          ],
        ),
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                Divider(color: Colors.grey[300], thickness: 1),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text(
                      'Transaction ID:',
                      style: TextStyle(
                        color: Colors.grey,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    Text(
                      transaction['transactionId'] ??
                          transaction['id'] ??
                          'N/A',
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        color: Colors.black87,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text(
                      'Balance Before:',
                      style: TextStyle(
                        color: Colors.grey,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    Text(
                      '₹${((transaction['balanceBefore'] as num?)?.toDouble() ?? 0.0).toStringAsFixed(2)}',
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        color: Colors.black87,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text(
                      'Balance After:',
                      style: TextStyle(
                        color: Colors.grey,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    Text(
                      '₹${balanceAfter.toStringAsFixed(2)}',
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        color: Color(0xFFdb9822),
                      ),
                    ),
                  ],
                ),
                if (transaction['referenceId'] != null) ...[
                  const SizedBox(height: 8),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text(
                        'Reference ID:',
                        style: TextStyle(
                          color: Colors.grey,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                      Text(
                        transaction['referenceId'],
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          color: Colors.black87,
                        ),
                      ),
                    ],
                  ),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }

  IconData _getCategoryIcon(String category) {
    switch (category.toLowerCase()) {
      case 'ticket_purchase':
        return Icons.confirmation_number;
      case 'prize_credit':
        return Icons.emoji_events;
      case 'refund':
        return Icons.refresh;
      case 'cashback':
        return Icons.monetization_on;
      case 'withdrawal':
        return Icons.money_off;
      case 'deposit':
        return Icons.add_circle;
      default:
        return Icons.account_balance_wallet;
    }
  }

  String _formatCategory(String category) {
    switch (category.toLowerCase()) {
      case 'ticket_purchase':
        return 'Ticket Purchase';
      case 'prize_credit':
        return 'Prize Credit';
      case 'refund':
        return 'Refund';
      case 'cashback':
        return 'Cashback';
      case 'withdrawal':
        return 'Withdrawal';
      case 'deposit':
        return 'Deposit';
      default:
        return category;
    }
  }

  String _formatStatus(String status) {
    switch (status.toLowerCase()) {
      case 'completed':
        return 'Completed';
      case 'pending':
        return 'Pending';
      case 'failed':
        return 'Failed';
      case 'cancelled':
        return 'Cancelled';
      default:
        return status;
    }
  }

  Color _getStatusColor(String status) {
    switch (status.toLowerCase()) {
      case 'completed':
        return Colors.green;
      case 'pending':
        return Colors.orange;
      case 'failed':
        return Colors.red;
      case 'cancelled':
        return Colors.grey;
      default:
        return Colors.grey;
    }
  }

  String _formatDate(String dateString) {
    try {
      final date = DateTime.parse(dateString);
      return '${date.day}/${date.month}/${date.year} ${date.hour}:${date.minute.toString().padLeft(2, '0')}';
    } catch (e) {
      return dateString;
    }
  }
}
