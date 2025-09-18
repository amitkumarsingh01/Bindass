import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/contest_provider.dart';
import 'seat_selection_screen.dart';

class ContestDetailScreen extends StatefulWidget {
  final String contestId;
  final int initialTabIndex;

  const ContestDetailScreen({
    super.key,
    required this.contestId,
    this.initialTabIndex = 0,
  });

  @override
  State<ContestDetailScreen> createState() => _ContestDetailScreenState();
}

class _ContestDetailScreenState extends State<ContestDetailScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(
      length: 6,
      vsync: this,
      initialIndex: widget.initialTabIndex,
    );
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
      contestProvider.loadPrizeStructure(widget.contestId),
    ]);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'Contest Details',
          style: TextStyle(color: Colors.black87, fontWeight: FontWeight.w600),
        ),
        backgroundColor: Colors.white,
        foregroundColor: Colors.black87,
        elevation: 0,
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(48),
          child: Container(
            color: Colors.white,
            child: TabBar(
              controller: _tabController,
              indicatorColor: const Color(0xFFdb9822),
              indicatorWeight: 3,
              labelColor: const Color(0xFFdb9822),
              unselectedLabelColor: Colors.grey[600],
              labelStyle: const TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w600,
              ),
              unselectedLabelStyle: const TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w500,
              ),
              isScrollable: true,
              tabAlignment: TabAlignment.start,
              tabs: const [
                Tab(text: 'Details'),
                Tab(text: 'Categories'),
                Tab(text: 'Leaderboard'),
                Tab(text: 'Winners'),
                Tab(text: 'Prize List'),
                Tab(text: 'My Purchases'),
              ],
            ),
          ),
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
              _LeaderboardTab(
                leaderboard: contestProvider.contestLeaderboard,
                cashbackforhighest:
                    contestProvider.currentContest?['cashbackforhighest'],
              ),
              _WinnersTab(winners: contestProvider.contestWinners),
              _PrizeListTab(prizeStructure: contestProvider.prizeStructure),
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
                      color: Color(0xFF2C3E50),
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
                    valueColor: const Color(0xFFdb9822),
                  ),

                  // Total Winners
                  _InfoRow(
                    icon: Icons.emoji_events,
                    label: 'Total Winners',
                    value: '${contest['totalWinners'] ?? 0}',
                    valueColor: Colors.amber,
                  ),

                  // Cashback for Highest Purchase (if configured)
                  if (contest['cashbackforhighest'] != null)
                    _InfoRow(
                      icon: Icons.trending_up,
                      label: 'Cashback for Highest Purchase',
                      value:
                          '₹${(contest['cashbackforhighest'] as num).toStringAsFixed(0)}',
                      valueColor: Colors.purple,
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
                child: Container(
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(
                      colors: [Color(0xFFdb9822), Color(0xFFffb32c)],
                      begin: Alignment.centerLeft,
                      end: Alignment.centerRight,
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
                    icon: const Icon(Icons.shopping_cart, color: Colors.white),
                    label: const Text(
                      'Buy Seats',
                      style: TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.w600,
                        fontSize: 16,
                      ),
                    ),
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      backgroundColor: Colors.transparent,
                      shadowColor: Colors.transparent,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
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
    return GridView.builder(
      padding: const EdgeInsets.all(16),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        childAspectRatio: 0.8,
        crossAxisSpacing: 16,
        mainAxisSpacing: 16,
      ),
      itemCount: categories.length,
      itemBuilder: (context, index) {
        final category = categories[index];
        return _CategoryCard(
          category: category,
          contestId: contestId,
          contestName: contestName,
          ticketPrice: ticketPrice,
        );
      },
    );
  }
}

class _CategoryCard extends StatelessWidget {
  final Map<String, dynamic> category;
  final String contestId;
  final String contestName;
  final double ticketPrice;

  const _CategoryCard({
    required this.category,
    required this.contestId,
    required this.contestName,
    required this.ticketPrice,
  });

  @override
  Widget build(BuildContext context) {
    final categoryName = category['categoryName'] ?? 'Category';
    final imagePath = _getCategoryImagePath(categoryName);

    return GestureDetector(
      onTap: () {
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
      child: Container(
        decoration: BoxDecoration(
          color: Colors.transparent,
          borderRadius: BorderRadius.circular(16),
          // boxShadow: [
          //   BoxShadow(
          //     color: Colors.grey.withOpacity(0.1),
          //     spreadRadius: 1,
          //     blurRadius: 8,
          //     offset: const Offset(0, 2),
          //   ),
          // ],
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Circular image container
            Container(
              width: 100,
              height: 100,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                border: Border.all(color: const Color(0xFFdb9822), width: 3),
              ),
              child: Padding(
                padding: const EdgeInsets.all(7.0),
                child: ClipOval(
                  child: Image.asset(
                    imagePath,
                    width: 80,
                    height: 80,
                    fit: BoxFit.cover,
                    errorBuilder: (context, error, stackTrace) {
                      return Container(
                        color: const Color(0xFFdb9822).withOpacity(0.1),
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(
                              Icons.category,
                              color: const Color(0xFFdb9822),
                              size: 30,
                            ),
                            Text(
                              categoryName.substring(0, 1).toUpperCase(),
                              style: const TextStyle(
                                color: Color(0xFFdb9822),
                                fontWeight: FontWeight.bold,
                                fontSize: 16,
                              ),
                            ),
                          ],
                        ),
                      );
                    },
                  ),
                ),
              ),
            ),

            const SizedBox(height: 12),

            // Category name
            Text(
              categoryName.toUpperCase(),
              style: const TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: Color(0xFFdb9822),
              ),
              textAlign: TextAlign.center,
            ),

            const SizedBox(height: 8),

            // Seats range
            Text(
              'SEATS : ${category['seatRangeStart'] ?? 0}-${category['seatRangeEnd'] ?? 0}',
              style: const TextStyle(
                fontSize: 12,
                color: Color(0xFFdb9822),
                fontWeight: FontWeight.w500,
              ),
              textAlign: TextAlign.center,
            ),

            const SizedBox(height: 4),

            // Available seats
            Text(
              'Available : ${category['availableSeats'] ?? 0} / ${category['totalSeats'] ?? 0}',
              style: const TextStyle(
                fontSize: 12,
                color: Color(0xFFdb9822),
                fontWeight: FontWeight.w500,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  String _getCategoryImagePath(String categoryName) {
    switch (categoryName.toLowerCase()) {
      case 'bike':
        return 'assets/Bike.png';
      case 'auto':
        return 'assets/Auto.png';
      case 'car':
        return 'assets/Car.png';
      case 'jeep':
        return 'assets/Jeep.png';
      case 'van':
        return 'assets/Van.png';
      case 'bus':
        return 'assets/Bus.png';
      case 'lorry':
        return 'assets/Lorry.png';
      case 'train':
        return 'assets/Train.png';
      case 'helicopter':
        return 'assets/Helicopter.png';
      case 'airplane':
        return 'assets/Airplane.png';
      default:
        return 'assets/logo.png'; // fallback image
    }
  }
}

class _LeaderboardTab extends StatelessWidget {
  final Map<String, dynamic>? leaderboard;
  final dynamic cashbackforhighest;

  const _LeaderboardTab({this.leaderboard, this.cashbackforhighest});

  @override
  Widget build(BuildContext context) {
    if (leaderboard == null || leaderboard!['leaderboard'] == null) {
      return const Center(child: Text('No leaderboard data available'));
    }

    final leaderboardData = leaderboard!['leaderboard'] as List<dynamic>;

    final bool showCashbackHeader = cashbackforhighest != null;

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: leaderboardData.length + (showCashbackHeader ? 1 : 0),
      itemBuilder: (context, index) {
        if (showCashbackHeader && index == 0) {
          final amount = (cashbackforhighest is num)
              ? (cashbackforhighest as num).toStringAsFixed(0)
              : cashbackforhighest.toString();
          return Card(
            margin: const EdgeInsets.only(bottom: 12),
            color: Colors.purple.shade50,
            child: ListTile(
              leading: const Icon(Icons.local_atm, color: Colors.purple),
              title: const Text(
                'Cashback for Highest Purchase',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              subtitle: Text('₹$amount will be awarded'),
            ),
          );
        }

        final adjustedIndex = showCashbackHeader ? index - 1 : index;
        final item = leaderboardData[adjustedIndex];
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
    return const Color(0xFFdb9822);
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
          margin: const EdgeInsets.only(bottom: 12),
          elevation: 4,
          shadowColor: Colors.black.withOpacity(0.1),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
          child: Container(
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: Colors.grey.shade200, width: 1),
            ),
            padding: const EdgeInsets.all(20),
            child: Row(
              children: [
                // Left side - Rank and Profile Circle
                Row(
                  children: [
                    // Yellow rank number
                    Center(
                      child: Text(
                        '${winner['prizeRank'] ?? index + 1}',
                        style: const TextStyle(
                          color: Colors.amber,
                          fontWeight: FontWeight.bold,
                          fontSize: 18,
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    // Red circle for profile pic (placeholder)
                    Container(
                      width: 50,
                      height: 50,
                      decoration: BoxDecoration(
                        color: Colors.red.shade100,
                        shape: BoxShape.circle,
                        border: Border.all(
                          color: Colors.red.shade300,
                          width: 2,
                        ),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.red.withOpacity(0.2),
                            blurRadius: 8,
                            offset: const Offset(0, 2),
                          ),
                        ],
                      ),
                      child: Center(
                        child: Icon(
                          Icons.person,
                          color: Colors.red.shade600,
                          size: 24,
                        ),
                      ),
                    ),
                  ],
                ),

                const SizedBox(width: 16),

                // Middle section - Winner details (left aligned)
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        winner['userName'] ?? 'Unknown',
                        style: const TextStyle(
                          fontWeight: FontWeight.w700,
                          fontSize: 17,
                          color: Color(0xFF2C3E50),
                          letterSpacing: 0.3,
                        ),
                      ),
                      const SizedBox(height: 6),
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 8,
                          vertical: 3,
                        ),
                        decoration: BoxDecoration(
                          color: const Color(0xFFdb9822).withOpacity(0.1),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Text(
                          winner['categoryName'] ?? 'N/A',
                          style: const TextStyle(
                            fontSize: 13,
                            color: Color(0xFFdb9822),
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ),
                      const SizedBox(height: 4),
                      Row(
                        children: [
                          Icon(
                            Icons.location_on,
                            size: 14,
                            color: Colors.grey.shade600,
                          ),
                          const SizedBox(width: 4),
                          Text(
                            winner['city'] ?? 'N/A',
                            style: TextStyle(
                              fontSize: 13,
                              color: Colors.grey.shade600,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),

                // Right side - Prize amount and seat info (right aligned)
                Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      '₹${winner['prizeAmount']?.toStringAsFixed(0) ?? '0'}',
                      style: const TextStyle(
                        fontWeight: FontWeight.w800,
                        color: Colors.black87,
                        fontSize: 17,
                        letterSpacing: 0.5,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 8,
                        vertical: 4,
                      ),
                      decoration: BoxDecoration(
                        color: Colors.blue.shade50,
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(
                          color: Colors.blue.shade200,
                          width: 1,
                        ),
                      ),
                      child: Text(
                        'Seat : ${winner['seatNumber'] ?? 'N/A'}',
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.blue.shade700,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                    const SizedBox(height: 6),
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 8,
                        vertical: 3,
                      ),
                      decoration: BoxDecoration(
                        color: winner['isPrizeClaimed'] == true
                            ? Colors.green.shade50
                            : Colors.orange.shade50,
                        borderRadius: BorderRadius.circular(6),
                        border: Border.all(
                          color: winner['isPrizeClaimed'] == true
                              ? Colors.green.shade300
                              : Colors.orange.shade300,
                          width: 1,
                        ),
                      ),
                      child: Text(
                        winner['isPrizeClaimed'] == true
                            ? '✓ Claimed'
                            : '⏳ Pending',
                        style: TextStyle(
                          color: winner['isPrizeClaimed'] == true
                              ? Colors.green.shade700
                              : Colors.orange.shade700,
                          fontSize: 11,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}

class _PrizeListTab extends StatelessWidget {
  final Map<String, dynamic>? prizeStructure;

  const _PrizeListTab({this.prizeStructure});

  @override
  Widget build(BuildContext context) {
    if (prizeStructure == null || prizeStructure!['items'] == null) {
      return const Center(child: Text('No prize structure available'));
    }

    final prizeItems = prizeStructure!['items'] as List<dynamic>;

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: prizeItems.length,
      itemBuilder: (context, index) {
        final prize = prizeItems[index];
        return Card(
          margin: const EdgeInsets.only(bottom: 12),
          elevation: 2,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          child: Container(
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(12),
              gradient: _getPrizeGradient(prize['prizeRank']),
            ),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 12,
                          vertical: 6,
                        ),
                        decoration: BoxDecoration(
                          color: Colors.white.withOpacity(0.2),
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: Text(
                          'Rank ${prize['prizeRank'] ?? index + 1}',
                          style: const TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                            fontSize: 14,
                          ),
                        ),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 12,
                          vertical: 6,
                        ),
                        decoration: BoxDecoration(
                          color: Colors.white.withOpacity(0.2),
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: Text(
                          '${prize['numberOfWinners'] ?? 1} Winner${(prize['numberOfWinners'] ?? 1) > 1 ? 's' : ''}',
                          style: const TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.w600,
                            fontSize: 12,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Prize Amount',
                            style: TextStyle(
                              color: Colors.white.withOpacity(0.8),
                              fontSize: 14,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            '₹${prize['prizeAmount']?.toStringAsFixed(0) ?? '0'}',
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 24,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                      if (prize['prizeDescription'] != null &&
                          prize['prizeDescription'].toString().isNotEmpty)
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.end,
                            children: [
                              Text(
                                'Description',
                                style: TextStyle(
                                  color: Colors.white.withOpacity(0.8),
                                  fontSize: 14,
                                  fontWeight: FontWeight.w500,
                                ),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                prize['prizeDescription'],
                                style: const TextStyle(
                                  color: Colors.white,
                                  fontSize: 14,
                                  fontWeight: FontWeight.w600,
                                ),
                                textAlign: TextAlign.right,
                              ),
                            ],
                          ),
                        ),
                    ],
                  ),
                  if (prize['winnersSeatNumbers'] != null &&
                      (prize['winnersSeatNumbers'] as List).isNotEmpty) ...[
                    const SizedBox(height: 12),
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: Colors.white.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Winning Seat Numbers',
                            style: TextStyle(
                              color: Colors.white.withOpacity(0.8),
                              fontSize: 12,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                          const SizedBox(height: 8),
                          Wrap(
                            spacing: 6,
                            runSpacing: 6,
                            children:
                                (prize['winnersSeatNumbers'] as List<dynamic>)
                                    .map(
                                      (seatNumber) => Container(
                                        padding: const EdgeInsets.symmetric(
                                          horizontal: 8,
                                          vertical: 4,
                                        ),
                                        decoration: BoxDecoration(
                                          color: Colors.white.withOpacity(0.2),
                                          borderRadius: BorderRadius.circular(
                                            12,
                                          ),
                                        ),
                                        child: Text(
                                          '#$seatNumber',
                                          style: const TextStyle(
                                            color: Colors.white,
                                            fontSize: 12,
                                            fontWeight: FontWeight.w600,
                                          ),
                                        ),
                                      ),
                                    )
                                    .toList(),
                          ),
                        ],
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  LinearGradient _getPrizeGradient(int? rank) {
    switch (rank) {
      case 1:
        return const LinearGradient(
          colors: [Color(0xFF6A5ACD), Color(0xFF9370DB)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        );
      case 2:
        return const LinearGradient(
          colors: [Color(0xFF20B2AA), Color(0xFF00CED1)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        );
      case 3:
        return const LinearGradient(
          colors: [Color(0xFFFF69B4), Color(0xFFFFB6C1)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        );
      case 4:
        return const LinearGradient(
          colors: [Color(0xFFFF6347), Color(0xFFFF7F50)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        );
      case 5:
        return const LinearGradient(
          colors: [Color(0xFF4169E1), Color(0xFF6495ED)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        );
      default:
        return const LinearGradient(
          colors: [Color(0xFFdb9822), Color(0xFFffb32c)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        );
    }
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
