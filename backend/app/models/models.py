from datetime import datetime, timezone
import enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    CheckConstraint,
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship
from app.db.session import Base


def utcnow():
    return datetime.now(timezone.utc)


class ItemCondition(str, enum.Enum):
    GOOD = "good"
    NEEDS_REPAIR = "needs_repair"
    RETIRED = "retired"


class CheckoutStatus(str, enum.Enum):
    CHECKED_OUT = "checked_out"
    RETURNED = "returned"


class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    sku = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=False, index=True)
    quantity_total = Column(Integer, nullable=False, default=1)
    quantity_available = Column(Integer, nullable=False, default=1)
    low_stock_threshold = Column(Integer, nullable=False, default=1)
    condition = Column(
        SQLEnum(ItemCondition, native_enum=False, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        default=ItemCondition.GOOD,
    )
    location = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    checkouts = relationship("Checkout", back_populates="item", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("quantity_total >= 0", name="check_positive_total"),
        CheckConstraint("quantity_available >= 0", name="check_positive_available"),
        CheckConstraint(
            "quantity_available <= quantity_total",
            name="check_available_le_total",
        ),
        CheckConstraint("low_stock_threshold >= 0", name="check_positive_low_stock"),
    )


class Checkout(Base):
    __tablename__ = "checkouts"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("inventory_items.id", ondelete="RESTRICT"), nullable=False, index=True)
    borrower_name = Column(String(255), nullable=False)
    borrower_contact = Column(String(255), nullable=True)
    quantity = Column(Integer, nullable=False, default=1)
    checked_out_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    due_at = Column(DateTime(timezone=True), nullable=True)
    returned_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(
        SQLEnum(CheckoutStatus, native_enum=False, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        default=CheckoutStatus.CHECKED_OUT,
        index=True,
    )

    item = relationship("InventoryItem", back_populates="checkouts")

    __table_args__ = (
        CheckConstraint("quantity > 0", name="check_positive_checkout_quantity"),
    )


class ActivityEvent(Base):
    __tablename__ = "activity_events"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(50), nullable=False, index=True)
    item_id = Column(Integer, nullable=True, index=True)
    summary = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
