from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from bson import ObjectId
from enum import Enum

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type, _handler):
        from pydantic_core import core_schema
        return core_schema.no_info_plain_validator_function(cls.validate)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")
        return field_schema

class User(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    userName: str
    userId: str = Field(..., unique=True)
    email: EmailStr
    phoneNumber: str
    password: str
    profilePicture: Optional[str] = None
    city: str
    state: str
    walletBalance: float = 0.0
    isActive: bool = True
    extraParameter1: Optional[str] = None
    createdAt: datetime = Field(default_factory=datetime.now)
    updatedAt: datetime = Field(default_factory=datetime.now)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class BankDetails(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    userId: PyObjectId
    accountNumber: str
    ifscCode: str
    bankName: str
    accountHolderName: str
    place: str
    upiId: Optional[str] = None
    extraParameter1: Optional[str] = None
    isVerified: bool = False
    createdAt: datetime = Field(default_factory=datetime.now)
    updatedAt: datetime = Field(default_factory=datetime.now)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class Category(BaseModel):
    categoryId: int
    categoryName: str
    seatRangeStart: int
    seatRangeEnd: int
    totalSeats: int
    availableSeats: int
    purchasedSeats: int = 0

class ContestStatus(str, Enum):
    ACTIVE = "active"
    UPCOMING = "upcoming"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Contest(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    contestName: str
    totalPrizeMoney: float
    ticketPrice: float
    totalSeats: int = 10000
    availableSeats: int = 10000
    purchasedSeats: int = 0
    totalWinners: int
    cashbackforhighest: Optional[float] = None
    status: ContestStatus = ContestStatus.ACTIVE
    contestStartDate: datetime
    contestEndDate: datetime
    drawDate: datetime
    isDrawCompleted: bool = False
    categories: List[Category] = []
    createdAt: datetime = Field(default_factory=datetime.now)
    updatedAt: datetime = Field(default_factory=datetime.now)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class PaymentMethod(str, Enum):
    WALLET = "wallet"
    UPI = "upi"
    CARD = "card"
    NETBANKING = "netbanking"

class PurchaseStatus(str, Enum):
    PURCHASED = "purchased"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"

class PurchasedSeat(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    contestId: PyObjectId
    userId: PyObjectId
    seatNumber: int = Field(..., ge=1, le=10000)
    categoryId: int
    categoryName: str
    ticketPrice: float
    purchaseDate: datetime = Field(default_factory=datetime.now)
    transactionId: str
    paymentMethod: PaymentMethod = PaymentMethod.WALLET
    status: PurchaseStatus = PurchaseStatus.PURCHASED
    isWinner: bool = False
    prizeAmount: float = 0.0
    createdAt: datetime = Field(default_factory=datetime.now)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class PrizeStructure(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    contestId: PyObjectId
    prizeRank: int
    prizeAmount: float
    numberOfWinners: int
    prizeDescription: Optional[str] = None
    winnersSeatNumbers: Optional[List[int]] = None
    createdAt: datetime = Field(default_factory=datetime.now)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class Winner(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    contestId: PyObjectId
    userId: PyObjectId
    seatNumber: int
    categoryName: str
    prizeRank: int
    prizeAmount: float
    prizeDescription: Optional[str] = None
    drawDate: datetime
    isPrizeClaimed: bool = False
    prizeClaimedDate: Optional[datetime] = None
    createdAt: datetime = Field(default_factory=datetime.now)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class TransactionType(str, Enum):
    CREDIT = "credit"
    DEBIT = "debit"

class TransactionCategory(str, Enum):
    TICKET_PURCHASE = "ticket_purchase"
    PRIZE_CREDIT = "prize_credit"
    REFUND = "refund"
    CASHBACK = "cashback"
    WITHDRAWAL = "withdrawal"
    DEPOSIT = "deposit"

class TransactionStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class WalletTransaction(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    userId: PyObjectId
    transactionId: str
    transactionType: TransactionType
    amount: float
    description: str
    category: TransactionCategory
    balanceBefore: float
    balanceAfter: float
    status: TransactionStatus = TransactionStatus.COMPLETED
    referenceId: Optional[str] = None
    paymentGatewayResponse: dict = {}
    createdAt: datetime = Field(default_factory=datetime.now)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class WithdrawalMethod(str, Enum):
    BANK_TRANSFER = "bank_transfer"
    UPI = "upi"

class WithdrawalStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"

class Withdrawal(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    userId: PyObjectId
    amount: float
    bankDetailsId: PyObjectId
    withdrawalMethod: WithdrawalMethod
    status: WithdrawalStatus = WithdrawalStatus.PENDING
    requestDate: datetime = Field(default_factory=datetime.now)
    processedDate: Optional[datetime] = None
    transactionId: Optional[str] = None
    bankTransactionId: Optional[str] = None
    rejectionReason: Optional[str] = None
    adminNotes: Optional[str] = None
    createdAt: datetime = Field(default_factory=datetime.now)
    updatedAt: datetime = Field(default_factory=datetime.now)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class CashbackType(str, Enum):
    HIGHEST_PURCHASE = "highest_purchase"
    SPECIAL_OFFER = "special_offer"
    REFERRAL = "referral"

class Cashback(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    contestId: PyObjectId
    userId: PyObjectId
    cashbackType: CashbackType
    cashbackAmount: float
    eligibilityCriteria: str
    totalPurchases: int = 0
    isCredited: bool = False
    creditedDate: Optional[datetime] = None
    createdAt: datetime = Field(default_factory=datetime.now)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class HomeSlider(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    title: str
    imageUrl: str
    linkUrl: Optional[str] = None
    description: Optional[str] = None
    order: int = 0
    isActive: bool = True
    createdAt: datetime = Field(default_factory=datetime.now)
    updatedAt: datetime = Field(default_factory=datetime.now)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class NotificationType(str, Enum):
    GENERAL = "general"
    CONTEST = "contest"
    WINNER = "winner"
    PAYMENT = "payment"
    WITHDRAWAL = "withdrawal"

class Notification(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    userId: Optional[PyObjectId] = None  # null for broadcast notifications
    title: str
    message: str
    type: NotificationType = NotificationType.GENERAL
    isRead: bool = False
    readAt: Optional[datetime] = None
    createdAt: datetime = Field(default_factory=datetime.now)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# Request/Response Models
class UserCreate(BaseModel):
    userName: str
    userId: str
    email: EmailStr
    phoneNumber: str
    password: str
    profilePicture: Optional[str] = None
    city: str
    state: str
    extraParameter1: Optional[str] = None

class UserRegisterSimple(BaseModel):
    # Complete registration with all user parameters
    userName: str
    userId: str
    email: EmailStr
    phoneNumber: str
    password: str
    profilePicture: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    extraParameter1: Optional[str] = None

class UserLogin(BaseModel):
    # Accept any identifier: email, phoneNumber, or userId
    identifier: str
    password: str

class UserResponse(BaseModel):
    id: str
    userName: str
    userId: str
    email: str
    phoneNumber: str
    profilePicture: Optional[str] = None
    city: str
    state: str
    walletBalance: float
    isActive: bool
    extraParameter1: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime

class BankDetailsCreate(BaseModel):
    accountNumber: str
    ifscCode: str
    bankName: str
    accountHolderName: str
    place: str
    upiId: Optional[str] = None
    extraParameter1: Optional[str] = None

class ContestCreate(BaseModel):
    contestName: str
    totalPrizeMoney: float
    ticketPrice: float
    totalWinners: int
    contestStartDate: datetime
    contestEndDate: datetime
    drawDate: datetime

class SeatPurchase(BaseModel):
    contestId: str
    seatNumbers: List[int]
    paymentMethod: PaymentMethod = PaymentMethod.WALLET

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    userId: Optional[str] = None

class WithdrawalCreate(BaseModel):
    amount: float
    bank_details_id: str
    withdrawal_method: WithdrawalMethod = WithdrawalMethod.BANK_TRANSFER
