from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.models.models import ItemCondition, CheckoutStatus


# InventoryItem Schemas
class ItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    sku: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    category: str = Field(..., min_length=1, max_length=100)
    quantity_total: int = Field(1, ge=0)
    quantity_available: int = Field(1, ge=0)
    low_stock_threshold: int = Field(1, ge=0)
    condition: ItemCondition = ItemCondition.GOOD
    location: Optional[str] = None

    @field_validator("quantity_available")
    @classmethod
    def validate_available_le_total(cls, v, info):
        total = info.data.get("quantity_total")
        if total is not None and v > total:
            raise ValueError("quantity_available cannot exceed quantity_total")
        return v


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    quantity_total: Optional[int] = Field(None, ge=0)
    quantity_available: Optional[int] = Field(None, ge=0)
    low_stock_threshold: Optional[int] = Field(None, ge=0)
    condition: Optional[ItemCondition] = None
    location: Optional[str] = None


class ItemResponse(ItemBase):
    id: int
    created_at: datetime
    updated_at: datetime
    is_low_stock: bool = False

    model_config = ConfigDict(from_attributes=True)


# Checkout Schemas
class CheckoutCreate(BaseModel):
    borrower_name: str = Field(..., min_length=1, max_length=255)
    borrower_contact: Optional[str] = Field(None, max_length=255)
    quantity: int = Field(1, gt=0)
    due_at: Optional[datetime] = None


class CheckoutResponse(BaseModel):
    id: int
    item_id: int
    borrower_name: str
    borrower_contact: Optional[str] = None
    quantity: int
    checked_out_at: datetime
    due_at: Optional[datetime] = None
    returned_at: Optional[datetime] = None
    status: CheckoutStatus
    item_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# Activity Schemas
class ActivityEventResponse(BaseModel):
    id: int
    event_type: str
    item_id: Optional[int] = None
    summary: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Dashboard Schemas
class DashboardStats(BaseModel):
    total_distinct_items: int
    total_units_owned: int
    total_units_available: int
    active_checkouts_count: int
    low_stock_items_count: int
    items_needing_repair_count: int
