import os
import sys
from datetime import datetime, timezone, timedelta

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/backend")

from app.db.session import SessionLocal
from app.models.models import InventoryItem, Checkout, ActivityEvent, ItemCondition, CheckoutStatus


def seed():
    db = SessionLocal()
    try:
        print("🌱 Seeding demo data for LabTrack...")

        # Clear existing demo data
        db.query(ActivityEvent).delete()
        db.query(Checkout).delete()
        db.query(InventoryItem).delete()
        db.commit()

        # Seed items
        items_data = [
            {
                "name": "Digital Storage Oscilloscope 100MHz",
                "sku": "OSC-RIGOL-1054Z",
                "description": "Rigol DS1054Z 4-channel 50MHz-100MHz digital oscilloscope with probes.",
                "category": "Test & Measurement",
                "quantity_total": 4,
                "quantity_available": 3,
                "low_stock_threshold": 1,
                "condition": ItemCondition.GOOD,
                "location": "Bench 2, Rack A",
            },
            {
                "name": "Precision Soldering Station 65W",
                "sku": "SLD-HAKKO-FX888D",
                "description": "Hakko FX-888D ESD-safe digital soldering station with chisel tip.",
                "category": "Tools",
                "quantity_total": 6,
                "quantity_available": 4,
                "low_stock_threshold": 2,
                "condition": ItemCondition.GOOD,
                "location": "Solder Bench 1",
            },
            {
                "name": "Binocular Stereo Zoom Microscope",
                "sku": "MIC-AMSOPE-SM4T",
                "description": "AmScope 7X-45X continuous zoom stereo microscope with LED ring light.",
                "category": "Optics",
                "quantity_total": 2,
                "quantity_available": 2,
                "low_stock_threshold": 1,
                "condition": ItemCondition.GOOD,
                "location": "Optics Room 104",
            },
            {
                "name": "Variable Triple DC Power Supply 30V 5A",
                "sku": "PSU-KORAD-KA3005D",
                "description": "Korad programmable linear DC bench power supply with digital display.",
                "category": "Power Supplies",
                "quantity_total": 5,
                "quantity_available": 1,  # Low stock indicator triggered
                "low_stock_threshold": 2,
                "condition": ItemCondition.GOOD,
                "location": "Bench 4, Shelf 1",
            },
            {
                "name": "Prusa MK4 3D Printer (Heated Bed)",
                "sku": "3DP-PRUSA-MK4",
                "description": "High-reliability FDM 3D printer with 0.4mm Nextruder nozzle.",
                "category": "Rapid Prototyping",
                "quantity_total": 3,
                "quantity_available": 2,
                "low_stock_threshold": 1,
                "condition": ItemCondition.NEEDS_REPAIR,  # Demonstrates needs repair metric
                "location": "Fabrication Bay 3",
            },
            {
                "name": "Arbitrary Waveform Generator 25MHz",
                "sku": "GEN-SIGLENT-1025",
                "description": "Dual-channel 25MHz DDS function and arbitrary waveform generator.",
                "category": "Test & Measurement",
                "quantity_total": 3,
                "quantity_available": 3,
                "low_stock_threshold": 1,
                "condition": ItemCondition.GOOD,
                "location": "Bench 3, Rack B",
            },
            {
                "name": "High-Performance Logic Analyzer 16ch",
                "sku": "LOGIC-SALEAE-16",
                "description": "Saleae Logic Pro 16 USB logic analyzer and protocol decoder.",
                "category": "Digital Tools",
                "quantity_total": 2,
                "quantity_available": 0,  # Zero available / active checkout
                "low_stock_threshold": 1,
                "condition": ItemCondition.GOOD,
                "location": "Cabinet A, Drawer 3",
            },
        ]

        items = []
        for d in items_data:
            item = InventoryItem(**d)
            db.add(item)
            items.append(item)
        db.flush()

        now = datetime.now(timezone.utc)

        # Seed Checkouts
        co1 = Checkout(
            item_id=items[0].id,
            borrower_name="Elena Rostova",
            borrower_contact="elena.r@university.edu",
            quantity=1,
            checked_out_at=now - timedelta(days=2),
            due_at=now + timedelta(days=5),
            status=CheckoutStatus.CHECKED_OUT,
        )
        co2 = Checkout(
            item_id=items[1].id,
            borrower_name="Marcus Vance",
            borrower_contact="m.vance@robotics-club.org",
            quantity=2,
            checked_out_at=now - timedelta(days=1),
            due_at=now + timedelta(days=3),
            status=CheckoutStatus.CHECKED_OUT,
        )
        co3 = Checkout(
            item_id=items[6].id,
            borrower_name="Dr. Aris Thorne",
            borrower_contact="thorne@lab.edu",
            quantity=2,
            checked_out_at=now - timedelta(days=4),
            due_at=now + timedelta(days=1),
            status=CheckoutStatus.CHECKED_OUT,
        )
        # Returned checkout history
        co4 = Checkout(
            item_id=items[2].id,
            borrower_name="Sarah Chen",
            borrower_contact="schen@bio-eng.edu",
            quantity=1,
            checked_out_at=now - timedelta(days=7),
            due_at=now - timedelta(days=2),
            returned_at=now - timedelta(days=2),
            status=CheckoutStatus.RETURNED,
        )
        db.add_all([co1, co2, co3, co4])
        db.flush()

        # Seed Activity Events
        events = [
            ActivityEvent(
                event_type="item_created",
                item_id=items[0].id,
                summary="Initial inventory setup: 4x Digital Storage Oscilloscope 100MHz added",
                created_at=now - timedelta(days=10),
            ),
            ActivityEvent(
                event_type="checked_out",
                item_id=items[6].id,
                summary="Checked out 2x High-Performance Logic Analyzer 16ch to Dr. Aris Thorne",
                created_at=now - timedelta(days=4),
            ),
            ActivityEvent(
                event_type="returned",
                item_id=items[2].id,
                summary="Returned 1x Binocular Stereo Zoom Microscope from Sarah Chen",
                created_at=now - timedelta(days=2),
            ),
            ActivityEvent(
                event_type="checked_out",
                item_id=items[0].id,
                summary="Checked out 1x Digital Storage Oscilloscope 100MHz to Elena Rostova",
                created_at=now - timedelta(days=2),
            ),
            ActivityEvent(
                event_type="checked_out",
                item_id=items[1].id,
                summary="Checked out 2x Precision Soldering Station 65W to Marcus Vance",
                created_at=now - timedelta(days=1),
            ),
            ActivityEvent(
                event_type="item_updated",
                item_id=items[4].id,
                summary="Marked Prusa MK4 3D Printer condition as 'needs_repair' (hotend clog)",
                created_at=now - timedelta(hours=3),
            ),
        ]
        db.add_all(events)
        db.commit()

        print(f"✅ Successfully seeded {len(items)} items, 4 checkouts, and {len(events)} activity events.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
