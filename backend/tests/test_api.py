import pytest
from fastapi import status


def test_health_endpoint(client):
    """1. Test health check liveness."""
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "LabTrack"


def test_ready_endpoint(client):
    """2. Test readiness check with connected database."""
    response = client.get("/ready")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "ready"


def test_create_item_success(client):
    """3. Test creating a valid inventory item."""
    payload = {
        "name": "Oscilloscope 100MHz",
        "sku": "OSC-100-01",
        "description": "Rigol DS1054Z Digital Oscilloscope",
        "category": "Electronics",
        "quantity_total": 5,
        "quantity_available": 5,
        "low_stock_threshold": 2,
        "condition": "good",
        "location": "Shelf B3",
    }
    response = client.post("/api/items", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["id"] is not None
    assert data["name"] == payload["name"]
    assert data["sku"] == payload["sku"]
    assert data["is_low_stock"] is False


def test_create_item_validation_failure(client):
    """4. Test validation failure: available quantity exceeds total quantity."""
    payload = {
        "name": "Soldering Station",
        "sku": "SLD-001",
        "category": "Electronics",
        "quantity_total": 2,
        "quantity_available": 5,  # Invalid: > total
        "low_stock_threshold": 1,
    }
    response = client.post("/api/items", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_nonexistent_item_returns_404(client):
    """5. Test requesting a nonexistent item returns 404."""
    response = client.get("/api/items/99999")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_list_items_and_filters(client):
    """6. Test listing items and filtering by category."""
    client.post(
        "/api/items",
        json={
            "name": "Digital Multimeter",
            "sku": "DMM-001",
            "category": "Test Equipment",
            "quantity_total": 10,
            "quantity_available": 10,
            "low_stock_threshold": 3,
        },
    )
    client.post(
        "/api/items",
        json={
            "name": "3D Printer Filament Black",
            "sku": "FIL-BLK-01",
            "category": "Materials",
            "quantity_total": 20,
            "quantity_available": 20,
            "low_stock_threshold": 5,
        },
    )

    response = client.get("/api/items?category=Materials")
    assert response.status_code == status.HTTP_200_OK
    items = response.json()
    assert len(items) == 1
    assert items[0]["sku"] == "FIL-BLK-01"


def test_update_item(client):
    """7. Test updating an existing inventory item."""
    create_res = client.post(
        "/api/items",
        json={
            "name": "Power Supply DC",
            "sku": "PSU-001",
            "category": "Power",
            "quantity_total": 4,
            "quantity_available": 4,
            "low_stock_threshold": 1,
        },
    )
    item_id = create_res.json()["id"]

    update_res = client.put(
        f"/api/items/{item_id}",
        json={"location": "Cabinet A1", "condition": "needs_repair"},
    )
    assert update_res.status_code == status.HTTP_200_OK
    data = update_res.json()
    assert data["location"] == "Cabinet A1"
    assert data["condition"] == "needs_repair"


def test_checkout_reduces_available_quantity(client):
    """8. Test checking out an item successfully reduces quantity_available."""
    create_res = client.post(
        "/api/items",
        json={
            "name": "Function Generator",
            "sku": "FGEN-001",
            "category": "Instruments",
            "quantity_total": 3,
            "quantity_available": 3,
            "low_stock_threshold": 1,
        },
    )
    item_id = create_res.json()["id"]

    checkout_payload = {
        "borrower_name": "Alice Researcher",
        "borrower_contact": "alice@lab.edu",
        "quantity": 2,
    }
    co_res = client.post(f"/api/items/{item_id}/checkouts", json=checkout_payload)
    assert co_res.status_code == status.HTTP_201_CREATED
    co_data = co_res.json()
    assert co_data["status"] == "checked_out"
    assert co_data["quantity"] == 2

    # Check that item quantity_available is now 1
    item_res = client.get(f"/api/items/{item_id}")
    assert item_res.json()["quantity_available"] == 1


def test_checkout_exceeding_availability_fails(client):
    """9. Test checkout fails when requested quantity exceeds available quantity."""
    create_res = client.post(
        "/api/items",
        json={
            "name": "Laser Cutter Glasses",
            "sku": "LCG-001",
            "category": "Safety",
            "quantity_total": 2,
            "quantity_available": 1,
            "low_stock_threshold": 1,
        },
    )
    item_id = create_res.json()["id"]

    checkout_payload = {
        "borrower_name": "Bob Maker",
        "quantity": 3,  # Only 1 available
    }
    co_res = client.post(f"/api/items/{item_id}/checkouts", json=checkout_payload)
    assert co_res.status_code == status.HTTP_400_BAD_REQUEST
    assert "Only 1 units available" in co_res.json()["detail"]


def test_return_item_restores_availability(client):
    """10. Test returning a checked-out item restores quantity_available."""
    create_res = client.post(
        "/api/items",
        json={
            "name": "Logic Analyzer",
            "sku": "LOGIC-001",
            "category": "Instruments",
            "quantity_total": 2,
            "quantity_available": 2,
            "low_stock_threshold": 1,
        },
    )
    item_id = create_res.json()["id"]

    # Checkout 1
    co_res = client.post(
        f"/api/items/{item_id}/checkouts",
        json={"borrower_name": "Charlie", "quantity": 1},
    )
    checkout_id = co_res.json()["id"]

    # Return it
    return_res = client.post(f"/api/checkouts/{checkout_id}/return")
    assert return_res.status_code == status.HTTP_200_OK
    assert return_res.json()["status"] == "returned"

    # Verify availability is back to 2
    item_res = client.get(f"/api/items/{item_id}")
    assert item_res.json()["quantity_available"] == 2


def test_delete_item_with_active_checkout_fails(client):
    """11. Test deleting an item with an active checkout fails with 409 conflict."""
    create_res = client.post(
        "/api/items",
        json={
            "name": "Microscope HD",
            "sku": "MIC-001",
            "category": "Optics",
            "quantity_total": 1,
            "quantity_available": 1,
            "low_stock_threshold": 1,
        },
    )
    item_id = create_res.json()["id"]

    # Check out the item
    client.post(
        f"/api/items/{item_id}/checkouts",
        json={"borrower_name": "Dr. Davis", "quantity": 1},
    )

    # Attempt delete
    del_res = client.delete(f"/api/items/{item_id}")
    assert del_res.status_code == status.HTTP_409_CONFLICT
    assert "active checkout" in del_res.json()["detail"]


def test_dashboard_stats(client):
    """12. Test dashboard KPIs accurately calculate counts and thresholds."""
    # Create low stock item
    client.post(
        "/api/items",
        json={
            "name": "Resistor Pack 1k",
            "sku": "RES-1K",
            "category": "Components",
            "quantity_total": 10,
            "quantity_available": 1,  # <= low_stock_threshold 2
            "low_stock_threshold": 2,
            "condition": "good",
        },
    )
    # Create item needing repair
    client.post(
        "/api/items",
        json={
            "name": "Broken Solder Fan",
            "sku": "FAN-002",
            "category": "Safety",
            "quantity_total": 1,
            "quantity_available": 1,
            "low_stock_threshold": 0,
            "condition": "needs_repair",
        },
    )

    stats_res = client.get("/api/dashboard/stats")
    assert stats_res.status_code == status.HTTP_200_OK
    stats = stats_res.json()
    assert stats["total_distinct_items"] >= 2
    assert stats["low_stock_items_count"] >= 1
    assert stats["items_needing_repair_count"] >= 1
