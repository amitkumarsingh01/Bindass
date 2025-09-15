# BINDASS GRAND Lottery Backend API

A comprehensive FastAPI backend for the BINDASS GRAND lottery system with MongoDB database.

## Features

- **User Management**: Registration, login, profile management
- **Contest Management**: Create and manage lottery contests
- **Seat Purchasing**: Buy lottery seats with real-time availability
- **Wallet System**: Digital wallet with transactions and withdrawals
- **Lottery Draw**: Automated winner selection and prize distribution
- **Admin Panel**: Complete admin functionality for managing the system
- **Notifications**: Real-time notifications for users
- **Bank Details**: Secure bank account management

## Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **MongoDB**: NoSQL database with Motor async driver
- **JWT**: JSON Web Tokens for authentication
- **Bcrypt**: Password hashing
- **Pydantic**: Data validation and serialization

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up MongoDB**
   - Install MongoDB locally or use MongoDB Atlas
   - Start MongoDB service
   - Default connection: `mongodb://localhost:27017`

5. **Configure environment variables**
   Create a `.env` file in the Backend directory:
   ```env
   MONGODB_URL=mongodb://localhost:27017
   DATABASE_NAME=bindass_grand
   SECRET_KEY=your-secret-key-here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

6. **Run the application**
   ```bash
   python main.py
   ```

   Or using uvicorn directly:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Database Structure

The system uses the following MongoDB collections:

1. **users**: User accounts and profiles
2. **bank_details**: User bank account information
3. **contests**: Lottery contests and configurations
4. **purchased_seats**: Seat purchases and transactions
5. **prize_structure**: Prize distribution for contests
6. **winners**: Winner records and prize details
7. **wallet_transactions**: Wallet transaction history
8. **withdrawals**: Withdrawal requests and processing
9. **cashback**: Cashback offers and tracking
10. **home_sliders**: Homepage slider content
11. **notifications**: User notifications

## API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user info

### Users
- `GET /api/users/profile` - Get user profile
- `PUT /api/users/profile` - Update user profile
- `POST /api/users/bank-details` - Add bank details
- `GET /api/users/bank-details` - Get bank details
- `DELETE /api/users/bank-details` - Delete bank details

### Contests
- `GET /api/contests/` - List all contests
- `GET /api/contests/{contest_id}` - Get contest details
- `GET /api/contests/{contest_id}/categories` - Get contest categories
- `GET /api/contests/{contest_id}/leaderboard` - Get contest leaderboard
- `GET /api/contests/{contest_id}/winners` - Get contest winners
- `GET /api/contests/{contest_id}/my-purchases` - Get user's purchases

### Seats
- `GET /api/seats/{contest_id}/available` - Get available seats
- `POST /api/seats/purchase` - Purchase seats
- `GET /api/seats/{contest_id}/purchased` - Get purchased seats
- `GET /api/seats/{contest_id}/category/{category_id}` - Get category seats

### Wallet
- `GET /api/wallet/balance` - Get wallet balance
- `GET /api/wallet/transactions` - Get transaction history
- `POST /api/wallet/add-money` - Add money to wallet
- `POST /api/wallet/withdraw` - Request withdrawal
- `GET /api/wallet/withdrawals` - Get withdrawal history

### Admin
- `POST /api/admin/contests` - Create contest
- `POST /api/admin/contests/{contest_id}/prize-structure` - Add prize structure
- `POST /api/admin/contests/{contest_id}/draw` - Conduct lottery draw
- `GET /api/admin/withdrawals` - Get all withdrawals
- `PUT /api/admin/withdrawals/{withdrawal_id}/status` - Update withdrawal status

### Notifications
- `GET /api/notifications/` - Get user notifications
- `PUT /api/notifications/{notification_id}/read` - Mark as read
- `POST /api/notifications/send-broadcast` - Send broadcast notification

## Contest Categories

The system supports 10 predefined categories with 1000 seats each:

1. **Bike**: Seats 1-1000
2. **Auto**: Seats 1001-2000
3. **Car**: Seats 2001-3000
4. **Jeep**: Seats 3001-4000
5. **Van**: Seats 4001-5000
6. **Bus**: Seats 5001-6000
7. **Lorry**: Seats 6001-7000
8. **Train**: Seats 7001-8000
9. **Helicopter**: Seats 8001-9000
10. **Airplane**: Seats 9001-10000

## Lottery Draw Process

1. **Prize Structure Setup**: Admin defines prize ranks and amounts
2. **Seat Purchasing**: Users buy seats until contest ends
3. **Draw Conduct**: Admin triggers lottery draw
4. **Winner Selection**: Random selection based on prize structure
5. **Prize Distribution**: Automatic crediting to winners' wallets
6. **Notifications**: Winners receive notifications

## Security Features

- JWT-based authentication
- Password hashing with bcrypt
- Input validation with Pydantic
- CORS middleware for cross-origin requests
- Admin role-based access control

## Development

### Running in Development Mode
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Database Indexes
The system automatically creates necessary indexes for performance optimization.

### Error Handling
Comprehensive error handling with appropriate HTTP status codes and error messages.

## Production Deployment

1. **Environment Variables**: Set production environment variables
2. **Database**: Use MongoDB Atlas or production MongoDB instance
3. **Security**: Change default secret keys and implement proper security measures
4. **Monitoring**: Add logging and monitoring
5. **Scaling**: Consider horizontal scaling for high traffic

## License

This project is proprietary software for BINDASS GRAND lottery system.
