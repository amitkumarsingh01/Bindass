import 'lib/utils/number_formatter.dart';

void main() {
  print('Testing NumberFormatter...');
  
  // Test cases
  final testCases = [
    1900000,    // Should be "19 Lakhs"
    500000,     // Should be "5 Lakhs"
    150000,     // Should be "1.5 Lakhs"
    50000,      // Should be "50,000"
    1000,       // Should be "1,000"
    100,        // Should be "100"
    1234567,    // Should be "12.3 Lakhs"
    10000000,   // Should be "100 Lakhs"
  ];
  
  for (final testCase in testCases) {
    final formatted = NumberFormatter.formatToLakhs(testCase);
    final currency = NumberFormatter.formatCurrency(testCase);
    print('$testCase -> $formatted (Currency: $currency)');
  }
  
  print('Testing completed!');
}
