import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template
from config import settings
import logging
import secrets
import string
from datetime import datetime, timedelta
from database import get_database
from bson import ObjectId

logger = logging.getLogger(__name__)

class EmailService:
    @staticmethod
    async def send_email(to_email: str, subject: str, html_content: str, text_content: str = None):
        """Send an email using SMTP"""
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = settings.from_email
            message["To"] = to_email

            # Add text part if provided
            if text_content:
                text_part = MIMEText(text_content, "plain")
                message.attach(text_part)

            # Add HTML part
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)

            # Send email
            await aiosmtplib.send(
                message,
                hostname=settings.smtp_server,
                port=settings.smtp_port,
                start_tls=True,
                username=settings.smtp_username,
                password=settings.smtp_password,
            )
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False

    @staticmethod
    def generate_reset_token() -> str:
        """Generate a secure random token for password reset"""
        return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))

    @staticmethod
    async def create_password_reset_token(email: str) -> str:
        """Create and store a password reset token for the user"""
        database = get_database()
        
        # Find user by email
        user = await database.users.find_one({"email": email.lower().strip()})
        if not user:
            raise ValueError("User not found")

        # Generate token
        token = EmailService.generate_reset_token()
        
        # Store token in database with expiration (1 hour)
        reset_record = {
            "userId": user["_id"],
            "email": email.lower().strip(),
            "token": token,
            "createdAt": datetime.now(),
            "expiresAt": datetime.now() + timedelta(hours=1),
            "used": False
        }
        
        # Remove any existing tokens for this user
        await database.password_reset_tokens.delete_many({"userId": user["_id"]})
        
        # Insert new token
        await database.password_reset_tokens.insert_one(reset_record)
        
        return token

    @staticmethod
    async def verify_reset_token(token: str) -> dict:
        """Verify a password reset token and return user info"""
        database = get_database()
        
        # Find token
        reset_record = await database.password_reset_tokens.find_one({
            "token": token,
            "used": False,
            "expiresAt": {"$gt": datetime.now()}
        })
        
        if not reset_record:
            raise ValueError("Invalid or expired token")
        
        # Get user info
        user = await database.users.find_one({"_id": reset_record["userId"]})
        if not user:
            raise ValueError("User not found")
        
        return {
            "userId": str(user["_id"]),
            "email": user["email"],
            "userName": user["userName"]
        }

    @staticmethod
    async def use_reset_token(token: str) -> bool:
        """Mark a reset token as used"""
        database = get_database()
        
        result = await database.password_reset_tokens.update_one(
            {"token": token, "used": False},
            {"$set": {"used": True, "usedAt": datetime.now()}}
        )
        
        return result.modified_count > 0

    @staticmethod
    def get_reset_email_template() -> str:
        """Get the HTML template for password reset email"""
        return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reset Your Password - BINDASS GRAND</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
            border-radius: 10px 10px 0 0;
        }
        .content {
            background: #f9f9f9;
            padding: 30px;
            border-radius: 0 0 10px 10px;
        }
        .button {
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 30px;
            text-decoration: none;
            border-radius: 5px;
            margin: 20px 0;
            font-weight: bold;
        }
        .footer {
            text-align: center;
            margin-top: 30px;
            color: #666;
            font-size: 14px;
        }
        .warning {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            color: #856404;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎲 BINDASS GRAND</h1>
        <h2>Password Reset Request</h2>
    </div>
    
    <div class="content">
        <p>Hello <strong>{{ user_name }}</strong>,</p>
        
        <p>We received a request to reset your password for your BINDASS GRAND account associated with <strong>{{ email }}</strong>.</p>
        
        <p>Click the button below to reset your password:</p>
        
        <div style="text-align: center;">
            <a href="{{ reset_link }}" class="button">Reset My Password</a>
        </div>
        
        <p>Or copy and paste this link into your browser:</p>
        <p style="word-break: break-all; background: #e9ecef; padding: 10px; border-radius: 5px;">{{ reset_link }}</p>
        
        <div class="warning">
            <strong>⚠️ Important:</strong>
            <ul>
                <li>This link will expire in <strong>1 hour</strong></li>
                <li>If you didn't request this reset, please ignore this email</li>
                <li>For security, never share this link with anyone</li>
            </ul>
        </div>
        
        <p>If you have any questions, please contact our support team.</p>
        
        <p>Best regards,<br>
        The BINDASS GRAND Team</p>
    </div>
    
    <div class="footer">
        <p>This is an automated email. Please do not reply to this message.</p>
        <p>&copy; {{ current_year }} BINDASS GRAND. All rights reserved.</p>
    </div>
</body>
</html>
        """

    @staticmethod
    async def send_password_reset_email(email: str) -> bool:
        """Send password reset email to user"""
        try:
            # Create reset token
            token = await EmailService.create_password_reset_token(email)
            
            # Get user info
            database = get_database()
            user = await database.users.find_one({"email": email.lower().strip()})
            
            # Create reset link
            reset_link = f"{settings.frontend_url}/reset-password?token={token}"
            
            # Prepare email content
            template = Template(EmailService.get_reset_email_template())
            html_content = template.render(
                user_name=user["userName"],
                email=email,
                reset_link=reset_link,
                current_year=datetime.now().year
            )
            
            # Text version
            text_content = f"""
Hello {user["userName"]},

We received a request to reset your password for your BINDASS GRAND account.

Reset your password by clicking this link: {reset_link}

This link will expire in 1 hour.

If you didn't request this reset, please ignore this email.

Best regards,
The BINDASS GRAND Team
            """
            
            # Send email
            success = await EmailService.send_email(
                to_email=email,
                subject="Reset Your BINDASS GRAND Password",
                html_content=html_content,
                text_content=text_content
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to send password reset email: {e}")
            return False
