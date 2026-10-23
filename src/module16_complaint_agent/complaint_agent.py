"""Module 16: Complaint & Issue Resolution Agent - Core Agent

Processes guest complaints through a 6-stage operational pipeline:
Complaint Ingestion -> Classification & Severity Assessment -> Troubleshooting KB Retrieval ->
Resolution Suggestions -> Automated Service Request (SQLite) -> Managerial Escalation (if needed).
"""

import re
from typing import Optional, Dict, Any, List
from src.module16_complaint_agent.models import (
    ComplaintSeverity,
    ComplaintCategory,
    EscalationLevel,
    ComplaintAnalysis,
    ComplaintResolutionResult,
)
from src.module16_complaint_agent.troubleshooting_kb import get_troubleshooting_guide
from src.module13_service_agent.database import ServiceRequestDatabase, DB_PATH
from src.module13_service_agent.models import ServiceCategory, ServicePriority


class ComplaintResolutionAgent:
    """Enterprise AI agent specializing in guest defect resolution, empathy,
    self-troubleshooting guidance, ticket creation, and managerial escalations.
    """

    def __init__(self, db_path: Optional[Any] = None):
        self.db = ServiceRequestDatabase(db_path or DB_PATH)

    def analyze_complaint(
        self,
        query: str,
        room_number: Optional[str] = None,
        guest_name: Optional[str] = None,
    ) -> ComplaintAnalysis:
        """Classifies complaint category, severity, and escalation requirements."""
        q_lower = query.lower()

        # 1. Detect Room Number if not provided
        if not room_number:
            match = re.search(r'\b(?:room|suite)\s*#?\s*([0-9]{3,4})\b', q_lower)
            if match:
                room_number = match.group(1)
            else:
                match_num = re.search(r'\b([0-9]{3,4})\b', query)
                if match_num and 100 <= int(match_num.group(1)) <= 9999:
                    room_number = match_num.group(1)

        # 2. Category Detection
        category = ComplaintCategory.GENERAL
        if any(w in q_lower for w in ["ac", "air condition", "thermostat", "cooling", "too warm", "too hot", "heater", "temperature"]):
            category = ComplaintCategory.HVAC_AC
        elif any(w in q_lower for w in ["water", "shower", "leak", "plumbing", "toilet", "drain", "sink", "flood"]):
            category = ComplaintCategory.PLUMBING_WATER
        elif any(w in q_lower for w in ["wifi", "wi-fi", "internet", "tv", "television", "remote", "streaming", "portal"]):
            category = ComplaintCategory.WIFI_TECHNOLOGY
        elif any(w in q_lower for w in ["key", "card", "lock", "rfid", "door won't open", "locked out"]):
            category = ComplaintCategory.KEYCARD_ACCESS
        elif any(w in q_lower for w in ["noise", "loud", "party", "shouting", "neighbor", "barking", "music"]):
            category = ComplaintCategory.NOISE_DISTURBANCE
        elif any(w in q_lower for w in ["dirty", "stain", "hair", "smell", "dust", "cleaning", "trash", "towel"]):
            category = ComplaintCategory.CLEANLINESS_HOUSEKEEPING
        elif any(w in q_lower for w in ["bill", "charge", "charged", "fee", "deposit", "invoice", "price"]):
            category = ComplaintCategory.BILLING_SERVICE
        elif any(w in q_lower for w in ["rude", "attitude", "disrespectful", "staff", "waiter", "manager"]):
            category = ComplaintCategory.STAFF_INTERACTION

        # 3. Severity Assessment
        severity = ComplaintSeverity.MEDIUM
        if any(w in q_lower for w in ["flood", "flooding", "spark", "fire", "emergency", "danger", "fainted", "hurt", "bleeding"]):
            severity = ComplaintSeverity.CRITICAL
        elif any(w in q_lower for w in ["not working", "broken", "unbearable", "freezing", "sweltering", "leaking", "locked out", "nightmare", "furious"]):
            severity = ComplaintSeverity.HIGH
        elif any(w in q_lower for w in ["slow", "flickering", "minor", "noisy", "remote", "bulb"]):
            severity = ComplaintSeverity.MEDIUM
        elif any(w in q_lower for w in ["extra", "missing", "question", "slight"]):
            severity = ComplaintSeverity.LOW

        # 4. Self-Troubleshoot Eligibility
        can_troubleshoot = category in [
            ComplaintCategory.HVAC_AC,
            ComplaintCategory.WIFI_TECHNOLOGY,
            ComplaintCategory.PLUMBING_WATER,
            ComplaintCategory.KEYCARD_ACCESS,
        ] and severity != ComplaintSeverity.CRITICAL

        # 5. Escalation Decision
        escalation = EscalationLevel.NONE
        if severity == ComplaintSeverity.CRITICAL:
            escalation = EscalationLevel.GUEST_RELATIONS_MOD
        elif severity == ComplaintSeverity.HIGH:
            if category in [ComplaintCategory.HVAC_AC, ComplaintCategory.PLUMBING_WATER]:
                escalation = EscalationLevel.DUTY_ENGINEER
            elif category in [ComplaintCategory.NOISE_DISTURBANCE, ComplaintCategory.STAFF_INTERACTION]:
                escalation = EscalationLevel.GUEST_RELATIONS_MOD
        elif category == ComplaintCategory.CLEANLINESS_HOUSEKEEPING:
            escalation = EscalationLevel.HOUSEKEEPING_SUPERVISOR

        return ComplaintAnalysis(
            query=query,
            detected_category=category,
            detected_severity=severity,
            room_number=room_number or "Guest Suite",
            guest_name=guest_name or "Esteemed Guest",
            can_self_troubleshoot=can_troubleshoot,
            requires_immediate_dispatch=severity in [ComplaintSeverity.HIGH, ComplaintSeverity.CRITICAL],
            escalation_level=escalation,
            confidence=0.96,
        )

    def process_complaint(
        self,
        query: str,
        room_number: Optional[str] = None,
        guest_name: Optional[str] = None,
        auto_create_ticket: bool = True,
    ) -> ComplaintResolutionResult:
        """Executes the full complaint resolution pipeline."""
        analysis = self.analyze_complaint(query, room_number, guest_name)
        guide = get_troubleshooting_guide(analysis.detected_category)

        suggested_steps: List[str] = []
        if guide and analysis.can_self_troubleshoot:
            suggested_steps = [f"Step {s.step_number}: {s.instruction}" for s in guide.steps]

        # 1. Map to Module 13 Database Ticket
        service_category = ServiceCategory.MAINTENANCE
        if analysis.detected_category in [ComplaintCategory.CLEANLINESS_HOUSEKEEPING, ComplaintCategory.AMENITY_DEFECT]:
            service_category = ServiceCategory.HOUSEKEEPING
        elif analysis.detected_category in [ComplaintCategory.BILLING_SERVICE, ComplaintCategory.STAFF_INTERACTION]:
            service_category = ServiceCategory.FRONT_DESK

        priority = ServicePriority.HIGH if analysis.detected_severity == ComplaintSeverity.HIGH else ServicePriority.URGENT if analysis.detected_severity == ComplaintSeverity.CRITICAL else ServicePriority.NORMAL

        ticket_id = None
        ticket_created = False
        if auto_create_ticket:
            ticket = self.db.create_request(
                room_number=analysis.room_number,
                category=service_category,
                requested_items=[f"{analysis.detected_category.value}: {query[:50]}"],
                notes=f"Severity: {analysis.detected_severity.value.upper()} | Escalation: {analysis.escalation_level.value}",
                guest_name=analysis.guest_name,
                priority=priority,
                estimated_turnaround_minutes=15 if priority != ServicePriority.URGENT else 10
            )
            ticket_id = ticket.ticket_number
            ticket_created = True

        # 2. Escalation Details
        escalation_triggered = analysis.escalation_level != EscalationLevel.NONE
        escalation_details = None
        if escalation_triggered:
            escalation_details = {
                "level": analysis.escalation_level.value,
                "notified_role": "Duty Chief Engineer & MOD" if analysis.escalation_level == EscalationLevel.DUTY_ENGINEER else "Manager on Duty (MOD)",
                "action": "Immediate on-site inspection dispatched. Follow-up call logged.",
                "compensation_flag": analysis.detected_severity in [ComplaintSeverity.HIGH, ComplaintSeverity.CRITICAL],
            }

        # 3. Concierge Formulation
        apology = "Please accept my most sincere apologies for this unacceptable disruption to your comfort."
        if analysis.detected_severity == ComplaintSeverity.CRITICAL:
            apology = "I am deeply alarmed and offer our profoundest apologies for this urgent disturbance."

        steps_text = ""
        if suggested_steps:
            steps_text = "\n\n**Immediate In-Room Quick Check:**\n" + "\n".join(f"• {s}" for s in suggested_steps)

        dispatch_text = (
            f"\n\n**Action Taken:** I have immediately logged priority service ticket **{ticket_id}** "
            f"with our Engineering Department. A senior technician has been dispatched directly to {analysis.room_number} "
            f"with an arrival window within 10–15 minutes."
            if ticket_created else ""
        )

        escalation_text = ""
        if escalation_triggered:
            escalation_text = (
                f"\n\n**Leadership Oversight:** Our **Manager on Duty** has been formally notified of this incident "
                f"under case reference `{ticket_id}` to ensure your utmost satisfaction and personal follow-up."
            )

        concierge_response = (
            f"{apology} At The Grand Azure, your sanctuary of tranquility is our sacred duty.{steps_text}"
            f"{dispatch_text}{escalation_text}\n\n"
            f"Should you require anything further or prefer to be relocated to an adjacent suite while our team conducts repairs, "
            f"simply dial extension `0` for my personal line."
        )

        return ComplaintResolutionResult(
            analysis=analysis,
            troubleshooting_guide=guide,
            suggested_steps=suggested_steps,
            service_request_id=ticket_id,
            ticket_created=ticket_created,
            escalation_triggered=escalation_triggered,
            escalation_details=escalation_details,
            apology_statement=apology,
            concierge_response=concierge_response,
            follow_up_eta_minutes=15 if analysis.detected_severity == ComplaintSeverity.HIGH else 10,
        )
