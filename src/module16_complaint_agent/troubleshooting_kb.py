"""Module 16: Complaint & Issue Resolution Agent - Troubleshooting Knowledge Base

Curated hotel troubleshooting procedures for in-room appliances, HVAC,
Wi-Fi connectivity, plumbing, and keycard locks.
"""

from typing import Dict, List, Optional
from src.module16_complaint_agent.models import (
    ComplaintCategory,
    TroubleshootingGuide,
    TroubleshootingStep,
)

TROUBLESHOOTING_GUIDES: Dict[ComplaintCategory, TroubleshootingGuide] = {
    ComplaintCategory.HVAC_AC: TroubleshootingGuide(
        category=ComplaintCategory.HVAC_AC,
        issue_title="In-Room Climate Control & Air Conditioning Diagnostic",
        symptoms=[
            "ac not cooling", "ac not working", "air conditioning warm",
            "thermostat blank", "fan not blowing", "room too hot", "too cold"
        ],
        steps=[
            TroubleshootingStep(
                step_number=1,
                instruction="Inspect the balcony terrace sliding glass door handle to verify it is firmly closed and locked.",
                rationale="For energy conservation and humidity control, all suites feature a magnetic interlock sensor that automatically deactivates the compressor when the terrace door is ajar.",
                estimated_seconds=20,
            ),
            TroubleshootingStep(
                step_number=2,
                instruction="Check the digital wall thermostat beside the bedroom entry: press the central 'Power' button once to ensure the blue backlight illuminates.",
                rationale="Wakes the microprocessor from standby mode if accidentally switched off.",
                estimated_seconds=15,
            ),
            TroubleshootingStep(
                step_number=3,
                instruction="Toggle the mode button to 'COOL' (snowflake icon) and tap the down arrow to set the temperature to 68°F (20°C).",
                rationale="Forces the chilled-water valve actuator to open fully within 90 seconds.",
                estimated_seconds=15,
            ),
        ],
        success_criteria="Cool airflow begins circulating from the acoustic ceiling louvers within 2 minutes.",
        auto_dispatch_on_failure=True,
        estimated_fix_time_mins=15,
    ),
    ComplaintCategory.WIFI_TECHNOLOGY: TroubleshootingGuide(
        category=ComplaintCategory.WIFI_TECHNOLOGY,
        issue_title="High-Speed Wi-Fi & Smart TV Connectivity",
        symptoms=[
            "wifi not working", "slow internet", "cannot connect to wifi",
            "tv no signal", "streaming disconnected", "login page not opening"
        ],
        steps=[
            TroubleshootingStep(
                step_number=1,
                instruction="Disconnect from 'GrandAzure_Guest', wait 10 seconds, and reconnect to the 5 GHz band named 'GrandAzure_Guest_5G'.",
                rationale="Clears cached DHCP lease and switches to low-latency channel.",
                estimated_seconds=20,
            ),
            TroubleshootingStep(
                step_number=2,
                instruction="Open a browser and navigate to 'http://portal.grandazure.local' (or '1.1.1.1') to re-trigger the guest authentication screen.",
                rationale="Bypasses HTTPS captive portal traps.",
                estimated_seconds=25,
            ),
            TroubleshootingStep(
                step_number=3,
                instruction="Enter your Room Number and Guest Last Name to validate your complimentary 150 Mbps tier.",
                rationale="Authenticates session on the hotel central gateway.",
                estimated_seconds=20,
            ),
        ],
        success_criteria="Portal displays 'Connected' and streaming video loads smoothly.",
        auto_dispatch_on_failure=True,
        estimated_fix_time_mins=10,
    ),
    ComplaintCategory.PLUMBING_WATER: TroubleshootingGuide(
        category=ComplaintCategory.PLUMBING_WATER,
        issue_title="Water Temperature & Shower Pressure Diagnostic",
        symptoms=[
            "no hot water", "low water pressure", "water drain clogged",
            "shower handle stiff", "leaking sink", "toilet running"
        ],
        steps=[
            TroubleshootingStep(
                step_number=1,
                instruction="Allow the rainfall shower fixture or faucet to run on full hot position for 60 to 90 seconds.",
                rationale="In high-floor suites, recirculating hot water loops can take up to 90 seconds to purge residual line coolant.",
                estimated_seconds=75,
            ),
            TroubleshootingStep(
                step_number=2,
                instruction="Verify the thermostatic dial button on the Hansgrohe shower valve is depressed past the 38°C (100°F) child safety stop.",
                rationale="The scald-prevention lock restricts temperature unless manually overridden.",
                estimated_seconds=15,
            ),
        ],
        success_criteria="Consistent therapeutic hot water (104°F–110°F) flows steadily.",
        auto_dispatch_on_failure=True,
        estimated_fix_time_mins=20,
    ),
    ComplaintCategory.KEYCARD_ACCESS: TroubleshootingGuide(
        category=ComplaintCategory.KEYCARD_ACCESS,
        issue_title="RFID Keycard & Electronic Suite Entry",
        symptoms=[
            "keycard not opening door", "door lock flashing red", "locked out",
            "rfid card invalid", "keycard demagnetized"
        ],
        steps=[
            TroubleshootingStep(
                step_number=1,
                instruction="Hold the RFID card flat and motionless against the black reader circle for 3 uninterrupted seconds.",
                rationale="Rapid tapping can cause the reader's low-energy battery cycle to time out.",
                estimated_seconds=10,
            ),
            TroubleshootingStep(
                step_number=2,
                instruction="Keep the card separated from wireless smartphone charging coils or MagSafe magnetic wallets.",
                rationale="High-intensity electromagnetic fields can temporarily desynchronize RFID transponders.",
                estimated_seconds=10,
            ),
        ],
        success_criteria="Lock flashes green with a gentle chime and the lever unlatches.",
        auto_dispatch_on_failure=True,
        estimated_fix_time_mins=10,
    ),
    ComplaintCategory.NOISE_DISTURBANCE: TroubleshootingGuide(
        category=ComplaintCategory.NOISE_DISTURBANCE,
        issue_title="Acoustic Privacy & Exterior Noise Disturbance",
        symptoms=[
            "loud neighbors", "party next door", "music too loud",
            "construction noise", "hallway shouting", "barking dog"
        ],
        steps=[
            TroubleshootingStep(
                step_number=1,
                instruction="Ensure double-glazed acoustic patio doors are fully latched in the upright compression position.",
                rationale="Engages the secondary acoustic perimeter gasket rated at STC 48 noise reduction.",
                estimated_seconds=20,
            ),
        ],
        success_criteria="Exterior environmental noise is dampened by at least 85%.",
        auto_dispatch_on_failure=True,
        estimated_fix_time_mins=10,
    ),
}


def get_troubleshooting_guide(category: ComplaintCategory) -> Optional[TroubleshootingGuide]:
    """Retrieves standard troubleshooting procedure for a complaint category."""
    return TROUBLESHOOTING_GUIDES.get(category)
