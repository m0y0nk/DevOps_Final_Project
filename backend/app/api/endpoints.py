from fastapi import APIRouter, Depends, Query, status
from typing import List, Optional
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.schemas import (
    ItemCreate,
    ItemUpdate,
    ItemResponse,
    CheckoutCreate,
    CheckoutResponse,
    ActivityEventResponse,
    DashboardStats,
)
from app.models.models import CheckoutStatus
from app.services import services

router = APIRouter()


# Dashboard stats
@router.get("/dashboard/stats", response_model=DashboardStats)
def get_stats(db: Session = Depends(get_db)):
    return services.get_dashboard_stats(db)


# Inventory Items
@router.get("/items", response_model=List[ItemResponse])
def list_items(
    search: Optional[str] = Query(None, description="Search by name, sku, or description"),
    category: Optional[str] = Query(None, description="Filter by category"),
    condition: Optional[str] = Query(None, description="Filter by condition"),
    low_stock: Optional[bool] = Query(None, description="Filter low-stock items"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db),
):
    items = services.get_items(
        db,
        search=search,
        category=category,
        condition=condition,
        low_stock=low_stock,
        skip=skip,
        limit=limit,
    )
    # Enrich with is_low_stock flag
    results = []
    for item in items:
        item_dict = ItemResponse.model_validate(item).model_dump()
        item_dict["is_low_stock"] = item.quantity_available <= item.low_stock_threshold
        results.append(ItemResponse(**item_dict))
    return results


@router.post("/items", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(item_in: ItemCreate, db: Session = Depends(get_db)):
    item = services.create_item(db, item_in)
    item_dict = ItemResponse.model_validate(item).model_dump()
    item_dict["is_low_stock"] = item.quantity_available <= item.low_stock_threshold
    return ItemResponse(**item_dict)


@router.get("/items/{item_id}", response_model=ItemResponse)
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = services.get_item_by_id(db, item_id)
    item_dict = ItemResponse.model_validate(item).model_dump()
    item_dict["is_low_stock"] = item.quantity_available <= item.low_stock_threshold
    return ItemResponse(**item_dict)


@router.put("/items/{item_id}", response_model=ItemResponse)
def update_item(item_id: int, item_in: ItemUpdate, db: Session = Depends(get_db)):
    item = services.update_item(db, item_id, item_in)
    item_dict = ItemResponse.model_validate(item).model_dump()
    item_dict["is_low_stock"] = item.quantity_available <= item.low_stock_threshold
    return ItemResponse(**item_dict)


@router.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    return services.delete_item(db, item_id)


# Checkouts
@router.post("/items/{item_id}/checkouts", response_model=CheckoutResponse, status_code=status.HTTP_201_CREATED)
def checkout_item(item_id: int, checkout_in: CheckoutCreate, db: Session = Depends(get_db)):
    checkout = services.checkout_item(db, item_id, checkout_in)
    res = CheckoutResponse.model_validate(checkout)
    res.item_name = checkout.item.name if checkout.item else None
    return res


@router.post("/checkouts/{checkout_id}/return", response_model=CheckoutResponse)
def return_checkout(checkout_id: int, db: Session = Depends(get_db)):
    checkout = services.return_checkout(db, checkout_id)
    res = CheckoutResponse.model_validate(checkout)
    res.item_name = checkout.item.name if checkout.item else None
    return res


@router.get("/checkouts", response_model=List[CheckoutResponse])
def list_checkouts(
    status_filter: Optional[CheckoutStatus] = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db),
):
    checkouts = services.get_checkouts(db, status_filter=status_filter, skip=skip, limit=limit)
    res = []
    for c in checkouts:
        c_res = CheckoutResponse.model_validate(c)
        c_res.item_name = c.item.name if c.item else None
        res.append(c_res)
    return res


# Activity Feed
@router.get("/activity", response_model=List[ActivityEventResponse])
def get_activity(
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return services.get_activities(db, limit=limit)
