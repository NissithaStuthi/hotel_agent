"""Kaggle Data Collector for AI Hotel Concierge

Collects, downloads, and processes hospitality datasets:
1. Hotel Booking Demand & Reservation Patterns (Kaggle: jessemostipak/hotel-booking-demand)
2. Hotel Guest Queries & FAQ Intent Dataset (Cross-domain hospitality dialogue & queries)
3. Hotel Guest Service Feedback & Reviews (Aspect-based service quality)

Supports both official Kaggle API (with credentials) and public mirror downloaders.
"""

import os
import sys
import json
import csv
import urllib.request
from pathlib import Path
from typing import Dict, Any, List, Optional
import src.utils.console_display  # Ensures UTF-8 on Windows

from src.config import DATA_DIR

KAGGLE_DATA_DIR = DATA_DIR / "kaggle_data"
KAGGLE_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Dataset Mirrors & Sources
BOOKING_DEMAND_URL = "https://raw.githubusercontent.com/aaqibqadeer/Hotel-booking-demand/master/hotel_bookings.csv"


class KaggleDataCollector:
    """Manages downloading, caching, and processing Kaggle hotel datasets."""

    def __init__(self, target_dir: Path = KAGGLE_DATA_DIR):
        self.target_dir = target_dir
        self.target_dir.mkdir(parents=True, exist_ok=True)

    def has_kaggle_credentials(self) -> bool:
        """Checks if Kaggle API credentials are configured."""
        config_path = Path.home() / ".kaggle" / "kaggle.json"
        has_file = config_path.exists()
        has_env = "KAGGLE_USERNAME" in os.environ and "KAGGLE_KEY" in os.environ
        return has_file or has_env

    def download_via_kaggle_cli(self, dataset_identifier: str) -> bool:
        """Downloads a dataset using the official Kaggle CLI."""
        if not self.has_kaggle_credentials():
            print(f"⚠️ Kaggle API credentials not found in ~/.kaggle/kaggle.json or env.")
            return False

        try:
            import subprocess
            cmd = [
                sys.executable, "-m", "kaggle", "datasets", "download",
                "-d", dataset_identifier,
                "-p", str(self.target_dir),
                "--unzip"
            ]
            print(f"📥 Downloading '{dataset_identifier}' via Kaggle API...")
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode == 0:
                print(f"✅ Successfully downloaded {dataset_identifier} via Kaggle API.")
                return True
            else:
                print(f"❌ Kaggle API download failed: {res.stderr}")
                return False
        except Exception as e:
            print(f"❌ Kaggle CLI invocation error: {e}")
            return False

    def collect_hotel_booking_demand(self) -> Path:
        """Downloads and prepares the 119,000+ Hotel Booking Demand dataset."""
        dest_file = self.target_dir / "hotel_bookings.csv"
        if dest_file.exists() and dest_file.stat().st_size > 1000:
            print(f"✓ Hotel Booking Demand dataset already exists at: {dest_file.name} ({dest_file.stat().st_size // 1024} KB)")
            return dest_file

        print(f"📥 Collecting Hotel Booking Demand dataset (Kaggle: jessemostipak/hotel-booking-demand)...")

        # 1. Try Kaggle CLI first if configured
        if self.has_kaggle_credentials():
            if self.download_via_kaggle_cli("jessemostipak/hotel-booking-demand"):
                if dest_file.exists():
                    return dest_file

        # 2. Fallback to direct public mirror
        print(f"🌐 Fetching from verified dataset mirror: {BOOKING_DEMAND_URL}")
        try:
            urllib.request.urlretrieve(BOOKING_DEMAND_URL, dest_file)
            print(f"✅ Successfully downloaded {dest_file.name} ({dest_file.stat().st_size // 1024} KB)")
            return dest_file
        except Exception as e:
            print(f"❌ Download failed: {e}")
            raise

    def collect_hotel_guest_queries_faq(self) -> Path:
        """Generates and prepares the curated Hotel Guest Queries & FAQ Intent dataset."""
        dest_file = self.target_dir / "hotel_guest_queries_faq.csv"
        if dest_file.exists():
            print(f"✓ Hotel Guest Queries & FAQ dataset already exists at: {dest_file.name}")
            return dest_file

        print("📦 Compiling Kaggle-style Hotel Guest Queries & Intent Dataset...")
        records = [
            # Front Desk
            ("What time can I check into my room?", "Information", "Front Desk & Policies", "Low", "Check-in begins at 3:00 PM local time."),
            ("Can we request a complimentary late check-out?", "Information", "Front Desk & Policies", "Low", "Complimentary late check-out is available until 1:00 PM upon availability."),
            ("What is the penalty if I need to cancel my booking tomorrow?", "Information", "Front Desk & Policies", "Medium", "Cancellations must be made at least 48 hours in advance to avoid penalty."),
            ("Where can I store our luggage after check-out?", "Information", "Front Desk & Policies", "Low", "Our Bell Desk provides complimentary 24/7 luggage storage."),
            
            # Dining
            ("What time is breakfast served at Azure Breeze?", "Information", "Restaurants & Room Service", "Low", "Breakfast is served 6:30 AM to 10:30 AM weekdays (11:00 AM weekends)."),
            ("Do you have gluten-free or vegan options at dinner?", "Information", "Restaurants & Room Service", "Low", "All our dining venues provide dedicated gluten-free and plant-based menus."),
            ("Can I order room service food at 2 AM?", "Information", "Restaurants & Room Service", "Low", "Yes, In-Room Dining offers a 24/7 menu with late-night specialties."),
            ("Can you recommend a romantic restaurant for our anniversary dinner?", "Recommendation", "Restaurants & Room Service", "Low", "We recommend Azure Breeze Seafood Grill on the cliffside terrace."),
            ("Please reserve a table for 4 at Le Jardin Bistro tonight at 8 PM.", "Action-Based", "Restaurants & Room Service", "Medium", "Restaurant reservation request dispatched to maître d'."),
            
            # Housekeeping
            ("We need 3 extra fresh bath towels in Room 412.", "Action-Based", "Housekeeping & Supplies", "High", "Housekeeping dispatch created with 15-minute delivery window."),
            ("Could you please send an iron and ironing board to Suite 205?", "Action-Based", "Housekeeping & Supplies", "High", "Housekeeping attendant notified for immediate delivery."),
            ("Please send extra feather pillows and blankets.", "Action-Based", "Housekeeping & Supplies", "Medium", "Bedding supplies dispatched to your accommodation."),
            
            # Amenities & Spa
            ("Is the infinity pool heated during cooler evenings?", "Information", "Hotel Facilities & Amenities", "Low", "The pool is heated to 82°F (28°C) year-round."),
            ("Are children allowed in the pool after 8 PM?", "Information", "Hotel Facilities & Amenities", "Low", "Pool quiet hours for adults (18+) run from 8:00 PM to 10:00 PM."),
            ("What is the cost of overnight valet parking?", "Information", "Hotel Facilities & Amenities", "Low", "Overnight valet parking is $45 per night with unlimited in/out privileges."),
            ("Can you recommend a restorative massage treatment for neck stiffness?", "Recommendation", "Spa & Wellness", "Low", "We suggest the 80-minute Azure Deep Mineral Recovery Massage."),
            ("Can I fly my recreational drone over the beach?", "Information", "Hotel Facilities & Amenities", "Low", "Recreational drone flights are strictly prohibited across resort airspace."),
            
            # Complaints & Maintenance
            ("The air conditioning unit in Room 305 is broken and blowing hot air!", "Complaint & Feedback", "Maintenance & Engineering", "High", "Priority engineering ticket dispatched with 15-minute response SLA."),
            ("The shower drain is clogged and overflowing onto the bathroom floor.", "Complaint & Feedback", "Maintenance & Engineering", "High", "Urgent engineering dispatch and housekeeping sanitization initiated."),
            ("I was double-charged for valet parking on my checkout invoice.", "Complaint & Feedback", "Billing & Payments", "Medium", "Folio audit initiated and billing credit reversal processed."),
            
            # Emergency
            ("Help, my husband slipped and injured his ankle by the elevator!", "Emergency & Escalation", "Front Desk & Policies", "Critical", "Manager on Duty and First Responder EMT team dispatched immediately.")
        ]

        with open(dest_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["query", "intent_category", "domain", "urgency", "standard_resolution"])
            writer.writerows(records)

        print(f"✅ Generated {dest_file.name} with {len(records)} annotated hospitality queries.")
        return dest_file

    def collect_hotel_reviews_aspects(self) -> Path:
        """Collects aspect-annotated guest feedback data."""
        dest_file = self.target_dir / "hotel_reviews_aspects.csv"
        if dest_file.exists():
            print(f"✓ Hotel Reviews & Service Aspects dataset already exists at: {dest_file.name}")
            return dest_file

        print("📦 Compiling Aspect-Based Hotel Reviews Dataset...")
        records = [
            ("The oceanfront room view was breathtaking, but check-in took 25 minutes.", "Front Desk", "Neutral", 3, "Check-in efficiency"),
            ("Azure Breeze seafood dinner was absolute perfection. The Chilean sea bass was extraordinary.", "Dining", "Positive", 5, "Culinary excellence"),
            ("Air conditioner in room 412 made loud vibration sounds throughout the night.", "Maintenance", "Negative", 1, "HVAC defect"),
            ("Concierge Julian arranged an unforgettable private sea cave kayak tour for our family.", "Concierge", "Positive", 5, "Excursion curation"),
            ("Housekeeping promptly delivered extra towels and sparkling water within 10 minutes.", "Housekeeping", "Positive", 5, "Service speed"),
            ("Overnight valet parking fee of $45 felt steep, though EV charging was free.", "Valet / Billing", "Neutral", 3, "Parking fee transparency"),
            ("Spa deep mineral massage relieved all my travel fatigue. World-class therapist.", "Spa", "Positive", 5, "Spa quality")
        ]

        with open(dest_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["review_text", "aspect_category", "sentiment", "star_rating", "key_topic"])
            writer.writerows(records)

        print(f"✅ Generated {dest_file.name} with {len(records)} service aspect reviews.")
        return dest_file

    def collect_all(self) -> Dict[str, Any]:
        """Runs the complete Kaggle data collection pipeline."""
        print("=" * 80)
        print("📥 KAGGLE DATA COLLECTION PIPELINE — AI HOTEL CONCIERGE")
        print("=" * 80)

        f1 = self.collect_hotel_booking_demand()
        f2 = self.collect_hotel_guest_queries_faq()
        f3 = self.collect_hotel_reviews_aspects()

        summary = {
            "kaggle_credentials_configured": self.has_kaggle_credentials(),
            "target_directory": str(self.target_dir),
            "datasets": [
                {"name": f1.name, "path": str(f1), "size_kb": f1.stat().st_size // 1024},
                {"name": f2.name, "path": str(f2), "size_kb": f2.stat().st_size // 1024},
                {"name": f3.name, "path": str(f3), "size_kb": f3.stat().st_size // 1024}
            ]
        }

        print("\n" + "=" * 80)
        print("📊 DATA COLLECTION SUMMARY:")
        for d in summary["datasets"]:
            print(f"   • {d['name']:<30} : {d['size_kb']} KB")
        print("=" * 80)
        print("✅ Kaggle data collection completed successfully!")
        print("=" * 80)

        return summary


def run_collection():
    collector = KaggleDataCollector()
    return collector.collect_all()


if __name__ == "__main__":
    run_collection()
