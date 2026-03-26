from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, Date, Enum, JSON, DateTime, Text
from database import Base
import enum
from datetime import datetime


class CounterpartyType(str, enum.Enum):
    supplier = "supplier"
    utility = "utility"
    employee = "employee"
    rent = "rent"
    loan = "loan"
    government = "government"


class TransactionType(str, enum.Enum):
    inflow = "inflow"
    outflow = "outflow"


class Business(Base):
    __tablename__ = "businesses"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    gst_number = Column(String, nullable=True)
    currency = Column(String, default="INR")
    onboarding_completed = Column(Boolean, default=False)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"))
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)


class Obligation(Base):
    __tablename__ = "obligations"
    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"))
    counterparty = Column(String)
    counterparty_type = Column(String)
    amount = Column(Float)
    due_date = Column(Date)
    penalty_risk = Column(Float, default=0.0)
    flexibility = Column(Float, default=0.5)
    urgency = Column(Float, default=0.5)
    is_paid = Column(Boolean, default=False)


class Receivable(Base):
    __tablename__ = "receivables"
    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"))
    counterparty = Column(String)
    amount = Column(Float)
    expected_date = Column(Date)
    confidence = Column(Float, default=0.8)
    is_received = Column(Boolean, default=False)


class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"))
    date = Column(Date)
    amount = Column(Float)
    type = Column(String)
    description = Column(String)


class CashPosition(Base):
    __tablename__ = "cash_positions"
    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"))
    balance = Column(Float)
    as_of_date = Column(Date)


class GSTReminder(Base):
    __tablename__ = "gst_reminders"
    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"))
    form_name = Column(String)
    deadline_day = Column(Integer)
    notes = Column(String, nullable=True)


class HealthScore(Base):
    __tablename__ = "health_scores"
    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"))
    score = Column(Integer)
    level = Column(String)
    factors = Column(JSON, nullable=True)
    badge_unlocked = Column(Boolean, default=False)
    next_unlock_condition = Column(String, nullable=True)


class ForumPost(Base):
    __tablename__ = "forum_posts"
    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"))
    title = Column(String)
    content = Column(Text)
    category = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class ForumReply(Base):
    __tablename__ = "forum_replies"
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("forum_posts.id"))
    business_id = Column(Integer, ForeignKey("businesses.id"))
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
