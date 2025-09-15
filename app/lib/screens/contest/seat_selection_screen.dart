import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/contest_provider.dart';
import '../../providers/wallet_provider.dart';

class SeatSelectionScreen extends StatefulWidget {
  final String contestId;
  final String contestName;
  final double ticketPrice;
  final int? categoryId;

  const SeatSelectionScreen({
    super.key,
    required this.contestId,
    required this.contestName,
    required this.ticketPrice,
    this.categoryId,
  });

  @override
  State<SeatSelectionScreen> createState() => _SeatSelectionScreenState();
}

class _SeatSelectionScreenState extends State<SeatSelectionScreen> {
  Set<int> _selectedSeats = {};
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _loadSeatData();
  }

  Future<void> _loadSeatData() async {
    final contestProvider = Provider.of<ContestProvider>(context, listen: false);
    
    if (widget.categoryId != null) {
      await contestProvider.loadCategorySeats(widget.contestId, widget.categoryId!);
    } else {
      // Load all categories if no specific category
      await contestProvider.loadContestCategories(widget.contestId);
    }
  }

  void _toggleSeat(int seatNumber) {
    setState(() {
      if (_selectedSeats.contains(seatNumber)) {
        _selectedSeats.remove(seatNumber);
      } else {
        _selectedSeats.add(seatNumber);
      }
    });
  }

  Future<void> _purchaseSeats() async {
    if (_selectedSeats.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please select at least one seat'),
          backgroundColor: Colors.red,
        ),
      );
      return;
    }

    setState(() {
      _isLoading = true;
    });

    final contestProvider = Provider.of<ContestProvider>(context, listen: false);
    final walletProvider = Provider.of<WalletProvider>(context, listen: false);

    // Check wallet balance
    final walletBalance = walletProvider.walletBalance?['walletBalance'] ?? 0.0;
    final totalAmount = _selectedSeats.length * widget.ticketPrice;

    if (walletBalance < totalAmount) {
      setState(() {
        _isLoading = false;
      });
      
      showDialog(
        context: context,
        builder: (context) => AlertDialog(
          title: const Text('Insufficient Balance'),
          content: Text(
            'You need ₹${totalAmount.toStringAsFixed(2)} but only have ₹${walletBalance.toStringAsFixed(2)} in your wallet.',
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('Cancel'),
            ),
            ElevatedButton(
              onPressed: () {
                Navigator.of(context).pop();
                // Navigate to add money screen
              },
              child: const Text('Add Money'),
            ),
          ],
        ),
      );
      return;
    }

    // Purchase seats
    final success = await contestProvider.purchaseSeats(
      widget.contestId,
      _selectedSeats.toList(),
      'wallet',
    );

    setState(() {
      _isLoading = false;
    });

    if (success) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Seats purchased successfully!'),
          backgroundColor: Colors.green,
        ),
      );
      
      // Refresh wallet balance
      await walletProvider.loadWalletBalance();
      
      // Clear selected seats
      setState(() {
        _selectedSeats.clear();
      });
      
      // Refresh seat data
      await _loadSeatData();
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(contestProvider.error ?? 'Purchase failed'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.contestName),
        backgroundColor: const Color(0xFF6A1B9A),
        foregroundColor: Colors.white,
      ),
      body: Consumer<ContestProvider>(
        builder: (context, contestProvider, child) {
          if (contestProvider.isLoading) {
            return const Center(
              child: CircularProgressIndicator(),
            );
          }

          if (contestProvider.error != null) {
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
                    'Error: ${contestProvider.error}',
                    style: const TextStyle(fontSize: 16),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 16),
                  ElevatedButton(
                    onPressed: _loadSeatData,
                    child: const Text('Retry'),
                  ),
                ],
              ),
            );
          }

          final seatData = contestProvider.categorySeats;
          if (seatData == null) {
            return const Center(
              child: Text('No seat data available'),
            );
          }

          final seatStatus = seatData['seatStatus'] as List<dynamic>? ?? [];
          final categoryName = seatData['categoryName'] ?? 'Category';
          final totalSeats = seatData['totalSeats'] ?? 0;
          final availableSeats = seatData['availableSeats'] ?? 0;
          final purchasedSeats = seatData['purchasedSeats'] ?? 0;

          return Column(
            children: [
              // Header Info
              Container(
                padding: const EdgeInsets.all(16),
                color: const Color(0xFF6A1B9A),
                child: Column(
                  children: [
                    Text(
                      categoryName,
                      style: const TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceAround,
                      children: [
                        _InfoChip(
                          icon: Icons.event_seat,
                          label: 'Total',
                          value: totalSeats.toString(),
                          color: Colors.blue,
                        ),
                        _InfoChip(
                          icon: Icons.check_circle,
                          label: 'Available',
                          value: availableSeats.toString(),
                          color: Colors.green,
                        ),
                        _InfoChip(
                          icon: Icons.shopping_cart,
                          label: 'Purchased',
                          value: purchasedSeats.toString(),
                          color: Colors.orange,
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              
              // Selected Seats Info
              if (_selectedSeats.isNotEmpty)
                Container(
                  padding: const EdgeInsets.all(16),
                  color: Colors.blue[50],
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'Selected: ${_selectedSeats.length} seats',
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                      Text(
                        'Total: ₹${(_selectedSeats.length * widget.ticketPrice).toStringAsFixed(2)}',
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                          color: Colors.green,
                        ),
                      ),
                    ],
                  ),
                ),
              
              // Seat Grid
              Expanded(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: GridView.builder(
                    gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                      crossAxisCount: 10,
                      childAspectRatio: 1,
                      crossAxisSpacing: 4,
                      mainAxisSpacing: 4,
                    ),
                    itemCount: seatStatus.length,
                    itemBuilder: (context, index) {
                      final seat = seatStatus[index];
                      final seatNumber = seat['seatNumber'] as int;
                      final isPurchased = seat['isPurchased'] as bool;
                      final isSelected = _selectedSeats.contains(seatNumber);

                      return GestureDetector(
                        onTap: isPurchased ? null : () => _toggleSeat(seatNumber),
                        child: Container(
                          decoration: BoxDecoration(
                            color: isPurchased
                                ? Colors.grey[400]
                                : isSelected
                                    ? const Color(0xFF6A1B9A)
                                    : Colors.green[100],
                            borderRadius: BorderRadius.circular(4),
                            border: Border.all(
                              color: isPurchased
                                  ? Colors.grey[600]!
                                  : isSelected
                                      ? const Color(0xFF6A1B9A)
                                      : Colors.green,
                              width: 1,
                            ),
                          ),
                          child: Center(
                            child: Text(
                              seatNumber.toString(),
                              style: TextStyle(
                                fontSize: 12,
                                fontWeight: FontWeight.bold,
                                color: isPurchased
                                    ? Colors.grey[600]
                                    : isSelected
                                        ? Colors.white
                                        : Colors.green[800],
                              ),
                            ),
                          ),
                        ),
                      );
                    },
                  ),
                ),
              ),
              
              // Purchase Button
              Container(
                padding: const EdgeInsets.all(16),
                child: SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: _isLoading || _selectedSeats.isEmpty ? null : _purchaseSeats,
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      backgroundColor: const Color(0xFF6A1B9A),
                    ),
                    child: _isLoading
                        ? const CircularProgressIndicator(color: Colors.white)
                        : Text(
                            _selectedSeats.isEmpty
                                ? 'Select Seats to Purchase'
                                : 'Purchase ${_selectedSeats.length} Seats - ₹${(_selectedSeats.length * widget.ticketPrice).toStringAsFixed(2)}',
                            style: const TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                  ),
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}

class _InfoChip extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;
  final Color color;

  const _InfoChip({
    required this.icon,
    required this.label,
    required this.value,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Icon(icon, color: Colors.white, size: 20),
        const SizedBox(height: 4),
        Text(
          value,
          style: const TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.bold,
            fontSize: 16,
          ),
        ),
        Text(
          label,
          style: const TextStyle(
            color: Colors.white70,
            fontSize: 12,
          ),
        ),
      ],
    );
  }
}
