class ContactModel {
  final String contactNo;
  final String email;
  final String website;

  ContactModel({
    required this.contactNo,
    required this.email,
    required this.website,
  });

  factory ContactModel.fromJson(Map<String, dynamic> json) {
    return ContactModel(
      contactNo: json['contactNo'] ?? '',
      email: json['email'] ?? '',
      website: json['website'] ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {'contactNo': contactNo, 'email': email, 'website': website};
  }
}
