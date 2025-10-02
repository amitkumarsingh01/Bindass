import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/contest_provider.dart';
import '../../utils/number_formatter.dart';
import 'contest_detail_screen.dart';

class ContestListScreen extends StatefulWidget {
  const ContestListScreen({super.key});

  @override
  State<ContestListScreen> createState() => _ContestListScreenState();
}

class _ContestListScreenState extends State<ContestListScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      Provider.of<ContestProvider>(context, listen: false).loadContests();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        centerTitle: true,
        // title: Text('All Contests', style: TextStyle(color: Color(0xFFdb9822))),
        title: Text(
          'All Contests',
          style: TextStyle(color: Colors.black, fontWeight: FontWeight.w500),
        ),
        backgroundColor: Colors.white,
        foregroundColor: Colors.white,
      ),
      body: Consumer<ContestProvider>(
        builder: (context, contestProvider, child) {
          if (contestProvider.isLoading) {
            return const Center(child: CircularProgressIndicator());
          }

          if (contestProvider.error != null) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.error_outline, size: 64, color: Colors.red),
                  const SizedBox(height: 16),
                  Text(
                    'Error: ${contestProvider.error}',
                    style: const TextStyle(fontSize: 16),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 16),
                  ElevatedButton(
                    onPressed: () {
                      contestProvider.loadContests();
                    },
                    child: const Text('Retry'),
                  ),
                ],
              ),
            );
          }

          if (contestProvider.contests.isEmpty) {
            return const Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.casino_outlined, size: 64, color: Colors.grey),
                  SizedBox(height: 16),
                  Text(
                    'No contests available',
                    style: TextStyle(fontSize: 18, color: Colors.grey),
                  ),
                ],
              ),
            );
          }

          return RefreshIndicator(
            onRefresh: () async {
              await contestProvider.loadContests();
            },
            child: ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: contestProvider.contests.length,
              itemBuilder: (context, index) {
                // Sort contests to move completed ones to the end
                final sortedContests = List<Map<String, dynamic>>.from(
                  contestProvider.contests,
                );
                sortedContests.sort((a, b) {
                  final aStatus = a['status']?.toString().toLowerCase() ?? '';
                  final bStatus = b['status']?.toString().toLowerCase() ?? '';

                  // If one is completed and the other is not, completed goes to end
                  if (aStatus == 'completed' && bStatus != 'completed') {
                    return 1; // a goes after b
                  } else if (aStatus != 'completed' && bStatus == 'completed') {
                    return -1; // a goes before b
                  } else {
                    return 0; // maintain original order for same status
                  }
                });

                final contest = sortedContests[index];
                return _ContestCard(
                  contest: contest,
                  index: index, // Use original index for gradient colors
                  onTap: () {
                    Navigator.of(context).push(
                      MaterialPageRoute(
                        builder: (context) => ContestDetailScreen(
                          contestId: contest['id'],
                          initialTabIndex: 1, // Navigate to Categories tab
                        ),
                      ),
                    );
                  },
                );
              },
            ),
          );
        },
      ),
    );
  }
}

class _ContestCard extends StatelessWidget {
  final Map<String, dynamic> contest;
  final VoidCallback onTap;
  final int index;

  const _ContestCard({
    required this.contest,
    required this.onTap,
    required this.index,
  });

  @override
  Widget build(BuildContext context) {
    final status = contest['status'] ?? 'unknown';
    final statusColor = _getStatusColor(status);
    final statusText = _getStatusText(status);
    final gradientColors = _getGradientColors(index);
    final buttonColor = _getButtonColor(index);

    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      height: 200,
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: gradientColors,
        ),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 8,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(16),
          child: Stack(
            children: [
              Padding(
                padding: const EdgeInsets.all(16),
                child: Row(
                  children: [
                    // Left Section - Contest Details
                    Expanded(
                      flex: 3,
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              // Prize Amount
                              Text(
                                'Win ${NumberFormatter.formatCurrency(contest['totalPrizeMoney'])}',
                                style: const TextStyle(
                                  fontSize: 22,
                                  fontWeight: FontWeight.bold,
                                  color: Colors.white,
                                ),
                              ),
                              const SizedBox(height: 6),

                              // Total Seats
                              Row(
                                children: [
                                  const Icon(
                                    Icons.event_seat,
                                    size: 16,
                                    color: Colors.white,
                                  ),
                                  const SizedBox(width: 6),
                                  Text(
                                    'Total Seats : ${contest['totalSeats'] ?? 0}',
                                    style: const TextStyle(
                                      fontSize: 15,
                                      color: Colors.white,
                                    ),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 2),

                              // Available Seats
                              Row(
                                children: [
                                  const Icon(
                                    Icons.chair_alt,
                                    size: 16,
                                    color: Colors.white,
                                  ),
                                  const SizedBox(width: 6),
                                  Text(
                                    'Available : ${contest['availableSeats'] ?? 0}',
                                    style: const TextStyle(
                                      fontSize: 15,
                                      color: Colors.white,
                                    ),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 2),

                              // Highest Purchase Info
                              Row(
                                children: [
                                  const Icon(
                                    Icons.trending_up,
                                    size: 14,
                                    color: Colors.white,
                                  ),
                                  const SizedBox(width: 6),
                                  Expanded(
                                    child: Text(
                                      contest['cashbackforhighest'] != null
                                          ? 'Cashback for highest purchase ${NumberFormatter.formatCurrency(contest['cashbackforhighest'])}'
                                          : 'Highest number purchase person ${NumberFormatter.formatCurrency(contest['ticketPrice'])}/-',
                                      style: const TextStyle(
                                        fontSize: 13,
                                        color: Colors.white,
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 4),

                              // Progress Bar
                              LinearProgressIndicator(
                                value:
                                    (contest['totalSeats'] != null &&
                                        contest['totalSeats'] > 0)
                                    ? (contest['purchasedSeats'] ?? 0) /
                                          contest['totalSeats']
                                    : 0,
                                backgroundColor: Colors.white.withOpacity(0.3),
                                valueColor: const AlwaysStoppedAnimation<Color>(
                                  Colors.white,
                                ),
                                minHeight: 3,
                              ),
                              const SizedBox(height: 2),

                              // Progress Text
                              Text(
                                '${contest['purchasedSeats'] ?? 0}/${contest['totalSeats'] ?? 0}',
                                style: const TextStyle(
                                  fontSize: 11,
                                  color: Colors.white,
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),

                    // Right Section - Price and Action
                    Expanded(
                      flex: 2,
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.end,
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          // Spacer to push content down and avoid overlap with status badge
                          const SizedBox(height: 20),

                          Column(
                            crossAxisAlignment: CrossAxisAlignment.end,
                            children: [
                              // Winners Count
                              Text(
                                'Winners : ${contest['totalWinners'] ?? 0}',
                                style: const TextStyle(
                                  fontSize: 13,
                                  color: Colors.white,
                                ),
                              ),
                              const SizedBox(height: 8),

                              // Ticket Price Label
                              const Text(
                                'TICKET PRICE',
                                style: TextStyle(
                                  fontSize: 11,
                                  color: Colors.white,
                                ),
                              ),
                              const SizedBox(height: 4),

                              // Ticket Price Amount
                              Text(
                                NumberFormatter.formatCurrency(contest['ticketPrice']),
                                style: const TextStyle(
                                  fontSize: 24,
                                  fontWeight: FontWeight.bold,
                                  color: Colors.white,
                                ),
                              ),
                            ],
                          ),

                          Column(
                            children: [
                              // Buy Now Button
                              Container(
                                width: 100,
                                height: 40,
                                decoration: BoxDecoration(
                                  color: Colors.white,
                                  borderRadius: BorderRadius.circular(20),
                                  border: Border.all(
                                    color: buttonColor,
                                    width: 1.5,
                                  ),
                                ),
                                child: Material(
                                  color: Colors.transparent,
                                  child: InkWell(
                                    onTap: onTap,
                                    borderRadius: BorderRadius.circular(20),
                                    child: Center(
                                      child: Text(
                                        'BUY NOW',
                                        style: TextStyle(
                                          color: buttonColor,
                                          fontWeight: FontWeight.bold,
                                          fontSize: 14,
                                        ),
                                      ),
                                    ),
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),

              // Status Badge - Positioned at top right corner
              Positioned(
                top: 12,
                right: 12,
                child: Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 8,
                    vertical: 4,
                  ),
                  decoration: BoxDecoration(
                    color: statusColor.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: Colors.white),
                  ),
                  child: Text(
                    statusText,
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                      fontSize: 10,
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  List<Color> _getGradientColors(int index) {
    final cycleIndex = index % 3;
    if (cycleIndex == 0) {
      // 1st, 4th, 7th, 10th... cards - Orange gradient
      return [const Color(0xFFff8123), const Color(0xFFcd4400)];
    } else if (cycleIndex == 1) {
      // 2nd, 5th, 8th, 11th... cards - Blue gradient
      return [const Color(0xFF2388ff), const Color(0xFF0058cd)];
    } else {
      // 3rd, 6th, 9th, 12th... cards - Yellow gradient
      return [const Color(0xFFffc123), const Color(0xFFcd9400)];
    }
  }

  Color _getButtonColor(int index) {
    final cycleIndex = index % 3;
    if (cycleIndex == 0) {
      // Orange button
      return const Color(0xFFffa726);
    } else if (cycleIndex == 1) {
      // Blue button
      return const Color(0xFF42a5f5);
    } else {
      // Yellow button
      return const Color(0xFFffca28);
    }
  }

  Color _getStatusColor(String status) {
    switch (status.toLowerCase()) {
      case 'active':
        return Colors.green;
      case 'upcoming':
        return Colors.blue;
      case 'completed':
        return Colors.grey;
      case 'cancelled':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  String _getStatusText(String status) {
    switch (status.toLowerCase()) {
      case 'active':
        return 'ACTIVE';
      case 'upcoming':
        return 'UPCOMING';
      case 'completed':
        return 'COMPLETED';
      case 'cancelled':
        return 'CANCELLED';
      default:
        return 'UNKNOWN';
    }
  }
}
