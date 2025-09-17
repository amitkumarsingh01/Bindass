import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/contest_provider.dart';
import '../../providers/wallet_provider.dart';
import 'seat_selection_screen.dart';

class ContestDetailScreen extends StatefulWidget {
  final String contestId;

  const ContestDetailScreen({super.key, required this.contestId});

  @override
  State<ContestDetailScreen> createState() => _ContestDetailScreenState();
}

class _ContestDetailScreenState extends State<ContestDetailScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 5, vsync: this);
    _loadContestData();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _loadContestData() async {
    final contestProvider = Provider.of<ContestProvider>(
      context,
      listen: false,
    );
    await Future.wait([
      contestProvider.loadContest(widget.contestId),
      contestProvider.loadContestCategories(widget.contestId),
      contestProvider.loadContestLeaderboard(widget.contestId),
      contestProvider.loadContestWinners(widget.contestId),
      contestProvider.loadMyPurchases(widget.contestId),
    ]);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Contest Details'),
        backgroundColor: const Color(0xFF6A1B9A),
        foregroundColor: Colors.white,
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: Colors.white,
          labelColor: Colors.white,
          unselectedLabelColor: Colors.white70,
          tabs: const [
            Tab(text: 'Details'),
            Tab(text: 'Categories'),
            Tab(text: 'Leaderboard'),
            Tab(text: 'Winners'),
            Tab(text: 'My Purchases'),
          ],
        ),
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
                    onPressed: _loadContestData,
                    child: const Text('Retry'),
                  ),
                ],
              ),
            );
          }

          if (contestProvider.currentContest == null) {
            return const Center(child: Text('Contest not found'));
          }

          return TabBarView(
            controller: _tabController,
            children: [
              _DetailsTab(contest: contestProvider.currentContest!),
              _CategoriesTab(
                contestId: widget.contestId,
                contestName:
                    contestProvider.currentContest?['contestName'] ?? 'Contest',
                ticketPrice:
                    (contestProvider.currentContest?['ticketPrice'] ?? 0)
                        .toDouble(),
                categories:
                    contestProvider.contestCategories?['categories'] ?? [],
              ),
              _LeaderboardTab(leaderboard: contestProvider.contestLeaderboard),
              _WinnersTab(winners: contestProvider.contestWinners),
              _MyPurchasesTab(myPurchases: contestProvider.myPurchases),
            ],
          );
        },
      ),
    );
  }
}

class _DetailsTab extends StatelessWidget {
  final Map<String, dynamic> contest;

  const _DetailsTab({required this.contest});

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Contest Header
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    contest['contestName'] ?? 'Contest',
                    style: const TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      color: Color(0xFF6A1B9A),
                    ),
                  ),
                  const SizedBox(height: 16),

                  // Prize Money
                  _InfoRow(
                    icon: Icons.attach_money,
                    label: 'Total Prize Money',
                    value:
                        '₹${contest['totalPrizeMoney']?.toStringAsFixed(0) ?? '0'}',
                    valueColor: Colors.green,
                  ),

                  // Ticket Price
                  _InfoRow(
                    icon: Icons.confirmation_number,
                    label: 'Ticket Price',
                    value:
                        '₹${contest['ticketPrice']?.toStringAsFixed(0) ?? '0'}',
                    valueColor: Colors.orange,
                  ),

                  // Total Seats
                  _InfoRow(
                    icon: Icons.event_seat,
                    label: 'Total Seats',
                    value: '${contest['totalSeats'] ?? 0}',
                    valueColor: Colors.blue,
                  ),

                  // Available Seats
                  _InfoRow(
                    icon: Icons.event_available,
                    label: 'Available Seats',
                    value: '${contest['availableSeats'] ?? 0}',
                    valueColor: Colors.purple,
                  ),

                  // Total Winners
                  _InfoRow(
                    icon: Icons.emoji_events,
                    label: 'Total Winners',
                    value: '${contest['totalWinners'] ?? 0}',
                    valueColor: Colors.amber,
                  ),

                  // Status
                  _InfoRow(
                    icon: Icons.info,
                    label: 'Status',
                    value:
                        contest['status']?.toString().toUpperCase() ??
                        'UNKNOWN',
                    valueColor: _getStatusColor(contest['status']),
                  ),
                ],
              ),
            ),
          ),

          const SizedBox(height: 20),

          // Action Buttons
          Row(
            children: [
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: () {
                    Navigator.of(context).push(
                      MaterialPageRoute(
                        builder: (context) => SeatSelectionScreen(
                          contestId: contest['id'],
                          contestName: contest['contestName'],
                          ticketPrice:
                              contest['ticketPrice']?.toDouble() ?? 0.0,
                        ),
                      ),
                    );
                  },
                  icon: const Icon(Icons.shopping_cart),
                  label: const Text('Buy Seats'),
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 16),
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Color _getStatusColor(String? status) {
    switch (status?.toLowerCase()) {
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
}

class _CategoriesTab extends StatelessWidget {
  final String contestId;
  final String contestName;
  final double ticketPrice;
  final List<dynamic> categories;

  const _CategoriesTab({
    required this.contestId,
    required this.contestName,
    required this.ticketPrice,
    required this.categories,
  });

  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: categories.length,
      itemBuilder: (context, index) {
        final category = categories[index];
        return Card(
          margin: const EdgeInsets.only(bottom: 12),
          child: ListTile(
            leading: CircleAvatar(
              backgroundColor: const Color(0xFF6A1B9A),
              child: Text(
                '${category['categoryId'] ?? index + 1}',
                style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
            title: Text(
              category['categoryName'] ?? 'Category',
              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
            ),
            subtitle: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Seats: ${category['seatRangeStart'] ?? 0} - ${category['seatRangeEnd'] ?? 0}',
                ),
                Text(
                  'Available: ${category['availableSeats'] ?? 0} / ${category['totalSeats'] ?? 0}',
                ),
              ],
            ),
            trailing: ElevatedButton(
              onPressed: () {
                Navigator.of(context).push(
                  MaterialPageRoute(
                    builder: (context) => SeatSelectionScreen(
                      contestId: contestId,
                      contestName: contestName,
                      ticketPrice: ticketPrice,
                      categoryId: category['categoryId'],
                    ),
                  ),
                );
              },
              child: const Text('Select'),
            ),
            isThreeLine: true,
          ),
        );
      },
    );
  }
}

class _LeaderboardTab extends StatelessWidget {
  final Map<String, dynamic>? leaderboard;

  const _LeaderboardTab({this.leaderboard});

  @override
  Widget build(BuildContext context) {
    if (leaderboard == null || leaderboard!['leaderboard'] == null) {
      return const Center(child: Text('No leaderboard data available'));
    }

    final leaderboardData = leaderboard!['leaderboard'] as List<dynamic>;

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: leaderboardData.length,
      itemBuilder: (context, index) {
        final item = leaderboardData[index];
        return Card(
          margin: const EdgeInsets.only(bottom: 8),
          child: ListTile(
            leading: CircleAvatar(
              backgroundColor: _getRankColor(index + 1),
              child: Text(
                '${index + 1}',
                style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
            title: Text(
              item['userName'] ?? 'Unknown',
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
            subtitle: Text('${item['totalPurchases'] ?? 0} seats purchased'),
            trailing: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  '₹${item['totalAmount']?.toStringAsFixed(0) ?? '0'}',
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    color: Colors.green,
                  ),
                ),
                Text(
                  '${item['seatNumbers']?.length ?? 0} seats',
                  style: const TextStyle(fontSize: 12),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Color _getRankColor(int rank) {
    if (rank == 1) return Colors.amber;
    if (rank == 2) return Colors.grey;
    if (rank == 3) return Colors.brown;
    return const Color(0xFF6A1B9A);
  }
}

class _WinnersTab extends StatelessWidget {
  final Map<String, dynamic>? winners;

  const _WinnersTab({this.winners});

  @override
  Widget build(BuildContext context) {
    if (winners == null || winners!['winners'] == null) {
      return const Center(child: Text('No winners data available'));
    }

    final winnersData = winners!['winners'] as List<dynamic>;

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: winnersData.length,
      itemBuilder: (context, index) {
        final winner = winnersData[index];
        return Card(
          margin: const EdgeInsets.only(bottom: 8),
          child: ListTile(
            leading: CircleAvatar(
              backgroundColor: const Color(0xFF6A1B9A),
              child: Text(
                '${winner['prizeRank'] ?? index + 1}',
                style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
            title: Text(
              winner['userName'] ?? 'Unknown',
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
            subtitle: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Seat: ${winner['seatNumber'] ?? 'N/A'}'),
                Text('Category: ${winner['categoryName'] ?? 'N/A'}'),
                Text('City: ${winner['city'] ?? 'N/A'}'),
              ],
            ),
            trailing: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  '₹${winner['prizeAmount']?.toStringAsFixed(0) ?? '0'}',
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    color: Colors.green,
                    fontSize: 16,
                  ),
                ),
                Text(
                  winner['isPrizeClaimed'] == true ? 'Claimed' : 'Pending',
                  style: TextStyle(
                    color: winner['isPrizeClaimed'] == true
                        ? Colors.green
                        : Colors.orange,
                    fontSize: 12,
                  ),
                ),
              ],
            ),
            isThreeLine: true,
          ),
        );
      },
    );
  }
}

class _MyPurchasesTab extends StatelessWidget {
  final Map<String, dynamic>? myPurchases;

  const _MyPurchasesTab({this.myPurchases});

  @override
  Widget build(BuildContext context) {
    if (myPurchases == null || myPurchases!['purchases'] == null) {
      return const Center(child: Text('No purchases yet'));
    }

    final purchases = myPurchases!['purchases'] as List<dynamic>;

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: purchases.length,
      itemBuilder: (context, index) {
        final group = purchases[index];
        final seats = (group['seats'] as List<dynamic>? ?? []).cast<int>();
        return Card(
          margin: const EdgeInsets.only(bottom: 12),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      group['categoryName']?.toString() ?? 'Category',
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 16,
                      ),
                    ),
                    Text(
                      'Total: ${group['totalSeats'] ?? seats.length}',
                      style: const TextStyle(color: Colors.grey),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: seats.map((n) => Chip(label: Text('#$n'))).toList(),
                ),
                const SizedBox(height: 8),
                Align(
                  alignment: Alignment.centerRight,
                  child: Text(
                    'Amount: ₹${(group['totalAmount'] ?? 0).toString()}',
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                      color: Colors.green,
                    ),
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}

class _InfoRow extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;
  final Color valueColor;

  const _InfoRow({
    required this.icon,
    required this.label,
    required this.value,
    required this.valueColor,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          Icon(icon, size: 20, color: Colors.grey[600]),
          const SizedBox(width: 12),
          Text('$label: ', style: const TextStyle(fontSize: 16)),
          Text(
            value,
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: valueColor,
            ),
          ),
        ],
      ),
    );
  }
}
