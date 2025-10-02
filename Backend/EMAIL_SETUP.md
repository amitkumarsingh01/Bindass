# Email Setup for Forgot Password Feature

## Overview
The forgot password feature has been implemented with the following components:
- Email service for sending password reset emails
- Forgot password API endpoint
- Reset password API endpoint  
- Reset password webpage

## Email Configuration

### 1. Update Configuration
Edit `/root/Bindass/Backend/config.py` or create a `.env` file with the following settings:

```env
# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@gmail.com
FRONTEND_URL=http://localhost:8000
```

### 2. Gmail Setup (Recommended)

#### Step 1: Enable 2-Factor Authentication
1. Go to your Google Account settings
2. Navigate to Security
3. Enable 2-Step Verification

#### Step 2: Generate App Password
1. Go to Google Account > Security > 2-Step Verification
2. Scroll down to "App passwords"
3. Select "Mail" and your device
4. Copy the generated 16-character password
5. Use this password in `SMTP_PASSWORD`

#### Step 3: Update Configuration
Replace the placeholders in `config.py`:
```python
smtp_username: str = "your-actual-email@gmail.com"
smtp_password: str = "your-16-char-app-password"  
from_email: str = "your-actual-email@gmail.com"
frontend_url: str = "http://your-domain.com"  # or localhost:8000 for development
```

### 3. Other Email Providers

#### Outlook/Hotmail
```env
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
```

#### Yahoo Mail
```env
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
```

## API Endpoints

### 1. Forgot Password
**POST** `/api/auth/forgot-password`

Request:
```json
{
  "email": "user@example.com"
}
```

Response:
```json
{
  "message": "If an account with this email exists, you will receive a password reset link shortly.",
  "success": true
}
```

### 2. Reset Password
**POST** `/api/auth/reset-password`

Request:
```json
{
  "token": "reset-token-from-email",
  "new_password": "newpassword123",
  "confirm_password": "newpassword123"
}
```

Response:
```json
{
  "message": "Password reset successful. You can now login with your new password.",
  "success": true
}
```

### 3. Verify Reset Token
**GET** `/api/auth/verify-reset-token/{token}`

Response:
```json
{
  "valid": true,
  "email": "user@example.com",
  "userName": "John Doe"
}
```

## Reset Password Page

The reset password page is available at: `http://your-domain.com/reset-password?token=RESET_TOKEN`

Features:
- Token validation
- Password strength requirements (minimum 6 characters)
- Real-time password confirmation
- Responsive design
- Success/error messaging

## Security Features

1. **Token Expiration**: Reset tokens expire after 1 hour
2. **One-time Use**: Tokens can only be used once
3. **Secure Generation**: Tokens use cryptographically secure random generation
4. **Email Validation**: Only registered email addresses can request resets
5. **No Information Disclosure**: API doesn't reveal if email exists or not

## Database Collections

The system creates a new collection: `password_reset_tokens`

Structure:
```javascript
{
  _id: ObjectId(),
  userId: ObjectId(),  // Reference to users collection
  email: String,
  token: String,       // 32-character random token
  createdAt: Date,
  expiresAt: Date,     // 1 hour from creation
  used: Boolean,       // false initially, true after use
  usedAt: Date         // when token was used
}
```

## Installation

1. Install new dependencies:
```bash
pip install aiosmtplib==3.0.1 jinja2==3.1.2
```

2. Update your email configuration in `config.py`

3. Restart your FastAPI server

## Testing

1. **Test Forgot Password**:
```bash
curl -X POST "http://localhost:8000/api/auth/forgot-password" \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com"}'
```

2. **Check Email**: Look for the reset email in your inbox

3. **Test Reset**: Visit the reset link or use the API directly

## Troubleshooting

### Common Issues:

1. **Email not sending**:
   - Check SMTP credentials
   - Verify app password is correct
   - Check firewall/network settings

2. **Token invalid**:
   - Tokens expire after 1 hour
   - Tokens can only be used once
   - Check token format in URL

3. **Page not loading**:
   - Ensure static files are properly mounted
   - Check file path: `static/pages/reset-password.html`

### Logs
Check application logs for detailed error messages:
```bash
tail -f /path/to/your/logs
```

## Customization

### Email Template
Edit the HTML template in `/root/Bindass/Backend/services/email_service.py` in the `get_reset_email_template()` method.

### Reset Page
Modify `/root/Bindass/Backend/static/pages/reset-password.html` to match your branding.

### Password Requirements
Update validation in both:
- Backend: `/root/Bindass/Backend/routers/auth.py`
- Frontend: Reset password page JavaScript
