"""
Payment and Milestone Models - For smart contract-based payments
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class PaymentStatus(str, enum.Enum):
    """Payment status enumeration"""
    PENDING = "pending"
    ESCROWED = "escrowed"
    RELEASED = "released"
    REFUNDED = "refunded"
    DISPUTED = "disputed"


class MilestoneStatus(str, enum.Enum):
    """Milestone status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    APPROVED = "approved"
    REJECTED = "rejected"


class Payment(Base):
    """Payment model for campaign payments"""
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    
    # Smart Contract Details (for future blockchain integration)
    contract_address = Column(String)  # Smart contract address
    transaction_hash = Column(String)  # Blockchain transaction hash
    
    # Payment Details
    payment_method = Column(String)  # "smart_contract", "escrow", "direct"
    paid_at = Column(DateTime(timezone=True))
    
    extra_data = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    campaign = relationship("Campaign", back_populates="payments")


class Milestone(Base):
    """Milestone model for milestone-based payments - Phase 1"""
    __tablename__ = "milestones"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    influencer_id = Column(Integer, ForeignKey("influencers.id"), nullable=False)  # Who completes it
    
    title = Column(String, nullable=False)
    description = Column(Text)
    amount = Column(Float, nullable=False)
    payout_percentage = Column(Float, nullable=True)  # Percentage of total budget
    status = Column(Enum(MilestoneStatus), default=MilestoneStatus.PENDING)
    
    # Milestone Details
    due_date = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    approved_at = Column(DateTime(timezone=True))
    
    # Proof/Submission (Phase 1)
    proof_urls = Column(JSON, default=[])  # Array of proof URLs (images, links, files)
    proof_description = Column(Text)  # Description of proof submitted
    submission_notes = Column(Text)  # Notes from influencer
    
    # Approval
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    rejection_reason = Column(Text)
    review_notes = Column(Text)  # Notes from brand reviewer
    
    # Payment tracking (Phase 1 - manual confirmation)
    payment_confirmed = Column(String, default="false")  # "true", "false", "pending"
    payment_confirmed_at = Column(DateTime(timezone=True), nullable=True)
    payment_confirmed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Smart Contract (Phase 2)
    contract_address = Column(String)
    transaction_hash = Column(String)
    
    extra_data = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    campaign = relationship("Campaign", back_populates="milestones")
    influencer = relationship("Influencer", foreign_keys=[influencer_id])

