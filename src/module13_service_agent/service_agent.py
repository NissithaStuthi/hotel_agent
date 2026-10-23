"""Module 13: Guest Service Request Agent

Implements the complete 6-stage service request pipeline:
Guest Request -> Intent Detection -> Required Information -> Tool Call -> Structured Request -> Confirmation
"""

import re
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

from src.module13_service_agent.models import (
    ServiceRequest,
    ServiceCategory,
    ServicePriority,
    ServiceRequestStatus,
    RequestAnalysis
)
from src.module13_service_agent.database import ServiceRequestDatabase


class GuestServiceRequestAgent:
    """Specialized autonomous agent for guest hospitality service requests."""

    def __init__(self, db: Optional[ServiceRequestDatabase] = None):
        self.db = db or ServiceRequestDatabase()

    def analyze_request(self, message: str, current_room: Optional[str] = None) -> RequestAnalysis:
        """Stage 1 & 2: Intent detection, item extraction, and required information check."""
        text = message.strip()
        tl = text.lower()

        # 1. Extract Room Number
        room_number = current_room
        room_match = re.search(r'\b(?:room|villa|suite)\s*#?\s*([0-9]{3,4})\b', tl)
        if room_match:
            room_number = room_match.group(1).upper()
        elif not room_number:
            # Standalone digits if user is just responding with their room number (e.g. "412" or "Room 412")
            digit_match = re.search(r'^\s*([0-9]{3,4})\s*$', text)
            if digit_match:
                room_number = digit_match.group(1)

        # 2. Determine Category, Items & Turnaround
        category = ServiceCategory.HOUSEKEEPING
        requested_items: List[str] = []
        turnaround = 15
        priority = ServicePriority.NORMAL

        if any(w in tl for w in ["towel", "towels"]):
            category = ServiceCategory.HOUSEKEEPING
            qty_match = re.search(r'\b(one|two|three|four|five|six|1|2|3|4|5|6)\b\s*(?:extra\s*)?(?:bath\s*|pool\s*)?towels?', tl)
            qty = qty_match.group(1) if qty_match else "2"
            requested_items.append(f"{qty} extra plush towels")
            turnaround = 15

        elif any(w in tl for w in ["housekeeping", "clean my room", "make up room", "turndown", "tidy up"]):
            category = ServiceCategory.HOUSEKEEPING
            requested_items.append("Full Housekeeping Refresh & Turndown Service")
            turnaround = 30

        elif any(w in tl for w in ["late checkout", "late check-out", "checkout late", "stay longer", "extend checkout"]):
            category = ServiceCategory.FRONT_DESK
            requested_items.append("Late Check-out Request (Standard extension until 1:00 PM)")
            turnaround = 5

        elif any(w in tl for w in ["pillow", "blanket", "duvet", "slippers", "robe", "shampoo", "dental"]):
            category = ServiceCategory.HOUSEKEEPING
            item_desc = "Bedding / Bath Comfort Amenities"
            if "pillow" in tl:
                item_desc = "Feather & Memory Foam Pillows"
            elif "robe" in tl or "slipper" in tl:
                item_desc = "Plush Bathrobes & Slippers"
            requested_items.append(item_desc)
            turnaround = 15

        elif any(w in tl for w in ["ac", "air condition", "leak", "broken", "light", "toilet", "plumbing", "safe", "tv", "remote"]):
            category = ServiceCategory.MAINTENANCE
            priority = ServicePriority.HIGH
            requested_items.append(f"Urgent Engineering Inspection: {text}")
            turnaround = 15

        elif any(w in tl for w in ["laundry", "dry clean", "press", "iron"]):
            category = ServiceCategory.LAUNDRY
            requested_items.append("Express Garment Laundry / Valet Pressing")
            turnaround = 45

        elif any(w in tl for w in ["luggage", "bags", "bellhop", "porter"]):
            category = ServiceCategory.BELL_DESK
            requested_items.append("Bell Desk Luggage Assistance")
            turnaround = 10

        elif any(w in tl for w in ["food", "room service", "dinner in room", "order burger", "breakfast in bed"]):
            category = ServiceCategory.ROOM_SERVICE
            requested_items.append("In-Room Dining Order Dispatch")
            turnaround = 30

        else:
            requested_items.append(text)

        # 3. Check Required Information
        missing_info = []
        if not room_number:
            missing_info.append("room_number")

        is_complete = len(missing_info) == 0

        return RequestAnalysis(
            category=category,
            requested_items=requested_items,
            room_number=room_number,
            priority=priority,
            missing_information=missing_info,
            is_complete=is_complete,
            turnaround_estimate_mins=turnaround,
            special_instructions=text
        )

    def process_request(
        self,
        message: str,
        guest_name: str = "Esteemed Guest",
        current_room: Optional[str] = None,
        pending_items: Optional[List[str]] = None,
        pending_category: Optional[ServiceCategory] = None
    ) -> Dict[str, Any]:
        """Executes the full pipeline: analysis, validation, tool call, and confirmation."""
        # Check if user is supplying previously missing room number
        if pending_items and pending_category and not current_room:
            # Try to extract room number from current message
            room_match = re.search(r'\b(?:room|villa|suite)?\s*([0-9a-zA-Z]+)\b', message.lower())
            if room_match:
                room = room_match.group(1).upper()
                # Create the request now!
                req = self.db.create_request(
                    room_number=room,
                    category=pending_category,
                    requested_items=pending_items,
                    notes=f"Follow-up room number confirmation for: {', '.join(pending_items)}",
                    guest_name=guest_name,
                    estimated_turnaround_minutes=15
                )
                return {
                    "status": "confirmed",
                    "request": req,
                    "reply": self._generate_confirmation_message(req),
                    "pending_slot": None
                }

        # Regular analysis
        analysis = self.analyze_request(message, current_room=current_room)

        # If required information is missing, ask polite clarification
        if not analysis.is_complete:
            return {
                "status": "awaiting_information",
                "request": None,
                "missing_information": analysis.missing_information,
                "analysis": analysis,
                "pending_slot": "room_number",
                "pending_items": analysis.requested_items,
                "pending_category": analysis.category,
                "reply": (
                    f"Certainly, I would be delighted to arrange that for you right away. "
                    f"May I kindly have your **Room or Villa Number** so our attendants can deliver your "
                    f"{', '.join(analysis.requested_items)} promptly?"
                )
            }

        # Stage 4 & 5: Tool Call & Structured Request in SQLite
        req = self.db.create_request(
            room_number=analysis.room_number,
            category=analysis.category,
            requested_items=analysis.requested_items,
            notes=analysis.special_instructions or "",
            guest_name=guest_name,
            priority=analysis.priority,
            estimated_turnaround_minutes=analysis.turnaround_estimate_mins
        )

        # Stage 6: Confirmation
        return {
            "status": "confirmed",
            "request": req,
            "reply": self._generate_confirmation_message(req),
            "pending_slot": None
        }

    def check_status(self, ticket_number: str) -> Dict[str, Any]:
        """Queries status of an existing ticket."""
        req = self.db.get_request(ticket_number)
        if not req:
            return {
                "found": False,
                "reply": f"I was unable to locate a service ticket with reference **{ticket_number}**. Please verify the reference number or contact Concierge directly."
            }

        status_text = req.status.value.replace("_", " ").title()
        return {
            "found": True,
            "request": req,
            "reply": (
                f"Status update for Ticket **{req.ticket_number}**:\n"
                f"• **Room:** {req.room_number}\n"
                f"• **Service Category:** {req.category.value.title()}\n"
                f"• **Items:** {', '.join(req.requested_items)}\n"
                f"• **Current Status:** `{status_text}`\n"
                f"• **Created:** {req.created_at}\n"
                f"• **Estimated Delivery / Completion:** {req.estimated_completion_time}\n\n"
                "Our team is actively overseeing this request to ensure your absolute comfort."
            )
        }

    def _generate_confirmation_message(self, req: ServiceRequest) -> str:
        dept_names = {
            ServiceCategory.HOUSEKEEPING: "Floor Housekeeping",
            ServiceCategory.LAUNDRY: "Valet Laundry & Garment Care",
            ServiceCategory.FRONT_DESK: "Front Desk & Guest Services",
            ServiceCategory.MAINTENANCE: "Duty Engineering Team",
            ServiceCategory.ROOM_SERVICE: "In-Room Dining Kitchen",
            ServiceCategory.BELL_DESK: "Porte-Cochère Bell Captain"
        }
        dept = dept_names.get(req.category, "Resort Guest Operations")
        items_str = ", ".join(req.requested_items)

        if req.category == ServiceCategory.FRONT_DESK and "late check-out" in items_str.lower():
            return (
                f"Delighted to assist, {req.guest_name}. Your late check-out request for **Room {req.room_number}** "
                f"has been approved until **1:00 PM** complimentary. (Ticket Reference: `{req.ticket_number}`). "
                f"Your keycards have been updated in our system. Please let us know if you require luggage assistance at departure."
            )

        return (
            f"Consider it done right away, {req.guest_name}. I have registered your request for **Room {req.room_number}** "
            f"and dispatched a priority work order to **{dept}**.\n\n"
            f"• **Ticket Reference:** `{req.ticket_number}`\n"
            f"• **Requested Services:** {items_str}\n"
            f"• **Estimated Delivery:** ~{req.estimated_turnaround_minutes} minutes (by {req.estimated_completion_time.split()[-1]})\n\n"
            f"Should you require any additional comforts in the meantime, please feel free to ask!"
        )
