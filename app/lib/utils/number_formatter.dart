class NumberFormatter {
  /// Formats a number to display in lakhs if it's >= 100000 (1 lakh)
  /// Examples:
  /// - 1900000 -> "19 Lakhs"
  /// - 500000 -> "5 Lakhs"
  /// - 50000 -> "50,000"
  /// - 1000 -> "1,000"
  static String formatToLakhs(dynamic value) {
    if (value == null) return '0';
    
    double number;
    if (value is String) {
      number = double.tryParse(value) ?? 0;
    } else if (value is num) {
      number = value.toDouble();
    } else {
      return '0';
    }
    
    // If number is >= 1 lakh (100,000), format as lakhs
    if (number >= 100000) {
      double lakhs = number / 100000;
      
      // If it's a whole number of lakhs, don't show decimal
      if (lakhs == lakhs.toInt()) {
        return '${lakhs.toInt()} Lakhs';
      } else {
        // Show one decimal place for partial lakhs
        return '${lakhs.toStringAsFixed(1)} Lakhs';
      }
    } else {
      // For numbers less than 1 lakh, show with comma separation
      return _addCommas(number.toInt());
    }
  }
  
  /// Formats a number with currency symbol and lakhs formatting
  /// Examples:
  /// - 1900000 -> "₹19 Lakhs"
  /// - 50000 -> "₹50,000"
  static String formatCurrency(dynamic value) {
    return '₹${formatToLakhs(value)}';
  }
  
  /// Adds comma separators to numbers
  /// Example: 50000 -> "50,000"
  static String _addCommas(int number) {
    return number.toString().replaceAllMapped(
      RegExp(r'(\d{1,3})(?=(\d{3})+(?!\d))'),
      (Match match) => '${match[1]},',
    );
  }
}
