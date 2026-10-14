from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from fastapi import HTTPException, status
from app.models.models import InventoryItem, Checkout, ActivityEvent, CheckoutStatus, ItemCondition
from app.schemas.schemas import ItemCreate, ItemUpdate, CheckoutCreate, DashboardStats


def log_activity(db: Session, event_type: str, item_id: Optional[int], summary: str):
    event = ActivityEvent(event_type=event_type, item_id=item_id, summary=summary)
    db.add(event)


# Inventory Service
def get_items(
    db: Session,
    search: Optional[str] = None,
    category: Optional[str] = None,
    condition: Optional[str] = None,
    low_stock: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[InventoryItem]:
    query = db.query(InventoryItem)

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                InventoryItem.name.ilike(search_filter),
                InventoryItem.sku.ilike(search_filter),
                InventoryItem.description.ilike(search_filter),
            )
        )
    if category:
        query = query.filter(InventoryItem.category.ilike(category))
    if condition:
        query = query.filter(InventoryItem.condition == condition)
    if low_stock is True:
        query = query.filter(InventoryItem.quantity_available <= InventoryItem.low_stock_threshold)

    return query.order_by(InventoryItem.created_at.desc()).offset(skip).limit(limit).all()


def get_item_by_id(db: Session, item_id: int) -> InventoryItem:
    item = db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found",
        )
    return item


def create_item(db: Session, item_in: ItemCreate) -> InventoryItem:
    existing = db.query(InventoryItem).filter(InventoryItem.sku == item_in.sku).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Item with SKU '{item_in.sku}' already exists",
        )

    item = InventoryItem(**item_in.model_dump())
    db.add(item)
    db.flush()

    log_activity(
        db,
        event_type="item_created",
        item_id=item.id,
        summary=f"Created item '{item.name}' (SKU: {item.sku}) with quantity {item.quantity_total}",
    )
    db.commit()
    db.refresh(item)
    return item


def update_item(db: Session, item_id: int, item_in: ItemUpdate) -> InventoryItem:
    item = get_item_by_id(db, item_id)
    update_data = item_in.model_dump(exclude_unset=True)

    # Invariant checks if quantities are updated
    new_total = update_data.get("quantity_total", item.quantity_total)
    new_avail = update_data.get("quantity_available", item.quantity_available)

    if new_avail > new_total:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Available quantity cannot exceed total quantity",
        )

    for field, val in update_data.items():
        setattr(item, field, val)

    log_activity(
        db,
        event_type="item_updated",
        item_id=item.id,
        summary=f"Updated details for '{item.name}'",
    )
    db.commit()
    db.refresh(item)
    return item


def delete_item(db: Session, item_id: int) -> dict:
    item = get_item_by_id(db, item_id)

    # Check for active checkouts
    active_checkouts = (
        db.query(Checkout)
        .filter(Checkout.item_id == item_id, Checkout.status == CheckoutStatus.CHECKED_OUT)
        .count()
    )
    if active_checkouts > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot delete item '{item.name}'. There are {active_checkouts} active checkout(s).",
        )

    item_name = item.name
    db.delete(item)
    log_activity(
        db,
        event_type="item_deleted",
        item_id=item_id,
        summary=f"Deleted item '{item_name}' (ID: {item_id})",
    )
    db.commit()
    return {"message": f"Item '{item_name}' deleted successfully", "id": item_id}


# Checkout Service
def checkout_item(db: Session, item_id: int, checkout_in: CheckoutCreate) -> Checkout:
    item = get_item_by_id(db, item_id)

    if checkout_in.quantity > item.quantity_available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot checkout {checkout_in.quantity} units. Only {item.quantity_available} units available.",
        )

    # Atomically deduct available quantity
    item.quantity_available -= checkout_in.quantity

    checkout = Checkout(
        item_id=item.id,
        borrower_name=checkout_in.borrower_name,
        borrower_contact=checkout_in.borrower_contact,
        quantity=checkout_in.quantity,
        due_at=checkout_in.due_at,
        status=CheckoutStatus.CHECKED_OUT,
    )
    db.add(checkout)
    db.flush()

    log_activity(
        db,
        event_type="checked_out",
        item_id=item.id,
        summary=f"Checked out {checkout.quantity}x '{item.name}' to {checkout.borrower_name}",
    )
    db.commit()
    db.refresh(checkout)
    return checkout


def return_checkout(db: Session, checkout_id: int) -> Checkout:
    checkout = db.query(Checkout).filter(Checkout.id == checkout_id).first()
    if not checkout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Checkout with id {checkout_id} not found",
        )

    if checkout.status == CheckoutStatus.RETURNED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Item has already been returned",
        )

    item = get_item_by_id(db, checkout.item_id)

    # Invariant: available cannot exceed total
    new_avail = item.quantity_available + checkout.quantity
    if new_avail > item.quantity_total:
        item.quantity_available = item.quantity_total
    else:
        item.quantity_available = new_avail

    checkout.status = CheckoutStatus.RETURNED
    checkout.returned_at = datetime.now(timezone.utc)

    log_activity(
        db,
        event_type="returned",
        item_id=item.id,
        summary=f"Returned {checkout.quantity}x '{item.name}' from {checkout.borrower_name}",
    )
    db.commit()
    db.refresh(checkout)
    return checkout


def get_checkouts(
    db: Session,
    status_filter: Optional[CheckoutStatus] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[Checkout]:
    query = db.query(Checkout)
    if status_filter:
        query = query.filter(Checkout.status == status_filter)
    return query.order_by(Checkout.checked_out_at.desc()).offset(skip).limit(limit).all()


# Activity Service
def get_activities(db: Session, limit: int = 50) -> List[ActivityEvent]:
    return (
        db.query(ActivityEvent)
        .order_by(ActivityEvent.created_at.desc())
        .limit(limit)
        .all()
    )


# Dashboard Stats
def get_dashboard_stats(db: Session) -> DashboardStats:
    total_distinct = db.query(func.count(InventoryItem.id)).scalar() or 0
    total_owned = db.query(func.sum(InventoryItem.quantity_total)).scalar() or 0
    total_avail = db.query(func.sum(InventoryItem.quantity_available)).scalar() or 0
    active_checkouts = (
        db.query(func.count(Checkout.id))
        .filter(Checkout.status == CheckoutStatus.CHECKED_OUT)
        .scalar()
        or 0
    )
    low_stock_items = (
        db.query(func.count(InventoryItem.id))
        .filter(InventoryItem.quantity_available <= InventoryItem.low_stock_threshold)
        .scalar()
        or 0
    )
    needing_repair = (
        db.query(func.count(InventoryItem.id))
        .filter(InventoryItem.condition == ItemCondition.NEEDS_REPAIR)
        .scalar()
        or 0
    )

    return DashboardStats(
        total_distinct_items=total_distinct,
        total_units_owned=int(total_owned),
        total_units_available=int(total_avail),
        active_checkouts_count=active_checkouts,
        low_stock_items_count=low_stock_items,
        items_needing_repair_count=needing_repair,
    )
