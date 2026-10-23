"""Module 20: Final AI Hotel Concierge Agent - Master Orchestrator

The culmination of Modules 1 through 19:
Unifies Natural Language RAG, Conversation Memory, Semantic Search,
Personalized Recommendations, Autonomous Tool Calling, Transactional Service Requests,
Specialized Dining Intelligence, Travel Itineraries, Complaint Triage,
Multi-Agent Collaboration, Multimodal Vision, and Safety/Hallucination Control.
"""

import time
import re
from pathlib import Path
from typing import Optional, Dict, Any, List, Union
from PIL import Image

from src.module3_classifier.hybrid_classifier import HybridIntentClassifier
from src.module4_concierge.memory import ConversationalMemory
from src.module5_rag.retriever import HotelRetriever
from src.module8_context_memory.context_resolver import ShortTermContextResolver
from src.module8_context_memory.session_state import SessionState
from src.module11_agent.models import AgentState
from src.module11_agent.planner import AgentPlanner
from src.module12_tool_calling.tool_caller import LLMToolDispatcher
from src.module17_multi_agent.supervisor import MultiAgentConciergeSupervisor
from src.module18_multimodal.vision_engine import MultimodalVisionEngine
from src.module19_safety_grounding.guardrails import ConciergeSafetyGuardrail
from src.module20_final_concierge.models import (
    FinalSystemTelemetry,
    FinalConciergeResult,
)


class TheGrandAzureMasterAgent:
    """The complete, autonomous AI Hotel Concierge Agent for The Grand Azure Resort & Spa."""

    def __init__(self):
        # 1. Linguistic & Memory Layers (Modules 3, 4, 8)
        self.classifier = HybridIntentClassifier()
        self.memory = ConversationalMemory()
        self.sessions: Dict[str, SessionState] = {}
        self.resolver = ShortTermContextResolver()

        # 2. Knowledge Retrieval Layers (Modules 5, 7, 10)
        self.retriever = HotelRetriever()

        # 3. Agent Planning & Tool Calling (Modules 11, 12)
        self.planner = AgentPlanner()
        self.tool_dispatcher = LLMToolDispatcher()

        # 4. Multi-Agent Collaboration (Module 17 with 13, 14, 15, 16)
        self.supervisor = MultiAgentConciergeSupervisor()

        # 5. Multimodal Vision Layer (Module 18)
        self.vision = MultimodalVisionEngine()

        # 6. Safety & Grounding Guardrail (Module 19)
        self.guardrail = ConciergeSafetyGuardrail(retriever=self.retriever)

    def process_guest_interaction(
        self,
        query: str,
        image_input: Optional[Union[str, Path, Image.Image]] = None,
        room_number: Optional[str] = None,
        guest_name: str = "Esteemed Guest",
        session_id: str = "default_session",
    ) -> FinalConciergeResult:
        """Executes the complete 8-stage end-to-end concierge pipeline."""
        start_time = time.time()
        stages_completed = []
        tools_executed = []
        tickets_created = []
        reservations_made = []

        # STAGE 1: CONVERSATION MEMORY & INTENT UNDERSTANDING
        # Resolve coreferences if short query
        session = self.sessions.setdefault(session_id, SessionState(session_id))
        resolved_query, _, _ = self.resolver.resolve(query, session)
        classification = self.classifier.classify(resolved_query)
        stages_completed.append("Stage 1: Intent Understanding & Coreference Resolution")

        # Check for Room Number
        if not room_number:
            rm_match = re.search(r'\b(?:room|suite|villa)\s*#?\s*([0-9]{3,4})\b', resolved_query.lower())
            if rm_match:
                room_number = rm_match.group(1).upper()
            elif session.preferences.room_number:
                room_number = session.preferences.room_number

        # Check for Multimodal Vision Ingestion if image provided
        visual_analysis = None
        if image_input:
            visual_analysis = self.vision.analyze_image(image_input, user_prompt=resolved_query)
            stages_completed.append("Stage 1B: Multimodal Visual Feature Understanding")

        # STAGE 2: AGENT PLANNING & GOAL DECOMPOSITION
        agent_state = AgentState(session_id=session_id, guest_name=guest_name, room_number=room_number)
        agent_plan = self.planner.create_plan(resolved_query, state=agent_state)
        stages_completed.append("Stage 2: Agent Planning & Step Decomposition")

        # STAGE 3 & 4: AUTONOMOUS TOOL DISPATCH
        tool_call, tool_res = self.tool_dispatcher.execute_query(
            resolved_query,
            context={"room_number": room_number, "guest_name": guest_name}
        )
        if tool_call and tool_res and tool_res.success:
            tools_executed.append(f"{tool_call.tool_name}() -> Executed")
            stages_completed.append(f"Stage 4: Autonomous Tool Execution ({tool_call.tool_name})")

        # STAGE 5: SPECIALIZED MULTI-AGENT COLLABORATION
        # Pass query to supervisor which routes to Hotel, Dining, Travel, Service, Local, or Complaint
        multi_agent_resp = self.supervisor.process_query(
            resolved_query,
            room_number=room_number,
            guest_name=guest_name
        )
        stages_completed.append(f"Stage 5: Multi-Agent Collaboration ({multi_agent_resp.routing_decision.primary_role.value})")

        # Harvest any tickets / reservations created by sub-agents
        for act in multi_agent_resp.all_tickets_and_bookings:
            if "ticket" in act.lower():
                tickets_created.append(act)
            if "reservation" in act.lower():
                reservations_made.append(act)

        candidate_answer = multi_agent_resp.unified_response

        # If visual analysis occurred, blend visual findings with candidate answer
        if visual_analysis:
            candidate_answer = (
                f"**[Visual Analysis: {visual_analysis.scene_description}]**\n\n"
                f"{candidate_answer}"
            )

        # STAGE 6 & 7: SAFETY, GROUNDING & HALLUCINATION CHECK
        grounding_audit = self.guardrail.validate_and_guard(
            query=resolved_query,
            candidate_answer=candidate_answer,
            domain_hint=classification.domain
        )
        stages_completed.append(f"Stage 7: Grounding Verification ({grounding_audit.verdict.value})")

        final_response = grounding_audit.final_grounded_answer

        # Update Session State & Memory
        if room_number:
            session.preferences.room_number = room_number
        session.add_turn(
            user_msg=query,
            assistant_msg=final_response,
            resolved_query=resolved_query,
            intent=classification.intent_category.value if hasattr(classification.intent_category, "value") else str(classification.intent_category)
        )
        self.memory.add_user_message(resolved_query)
        self.memory.add_assistant_message(final_response)

        duration_ms = (time.time() - start_time) * 1000

        telemetry = FinalSystemTelemetry(
            pipeline_duration_ms=round(duration_ms, 2),
            stages_completed=stages_completed,
            specialized_agents_engaged=[s.agent_name for s in multi_agent_resp.sub_agent_results],
            tools_called=tools_executed,
            grounding_verdict=grounding_audit.verdict,
            confidence_score=grounding_audit.confidence_score,
        )

        return FinalConciergeResult(
            guest_name=guest_name,
            room_number=room_number,
            original_query=query,
            image_attached=Path(image_input).name if isinstance(image_input, (str, Path)) else None,
            intent_understanding=classification,
            visual_analysis=visual_analysis,
            agent_plan=agent_plan,
            routing_decision=multi_agent_resp.routing_decision,
            sub_agent_results=multi_agent_resp.sub_agent_results,
            tools_executed=tools_executed,
            service_tickets_created=tickets_created,
            dining_reservations_made=reservations_made,
            grounding_audit=grounding_audit,
            final_response=final_response,
            telemetry=telemetry,
        )
