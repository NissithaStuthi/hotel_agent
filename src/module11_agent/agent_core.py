"""Module 11: Concierge Agent Architecture — Master Orchestrator

Implements the central autonomous Concierge Agent:
- Planning & Dynamic Goal Decomposition
- Subsystem Tool Selection (Hotel KB, Hotel Services, Local Info, Actions)
- Multi-Turn Agent State Tracking
- Deliberation & Decision Making Loop
- Clefs d'Or Grounded Synthesis
"""

import uuid
from typing import Dict, Any, Optional, List

from src.module11_agent.models import (
    AgentState,
    AgentPlan,
    PlanStep,
    AgentDecision,
    ActionType,
    AgentStepStatus
)
from src.module11_agent.planner import AgentPlanner
from src.module12_tool_calling.tools import ToolRegistry
from src.module12_tool_calling.models import ToolResult
from src.module4_concierge.llm_backend import LLMBackend
from src.module4_concierge.persona import PersonaStyle, get_system_prompt
from src.module4_concierge.memory import ChatMessage


class ConciergeAgent:
    """Master Autonomous Concierge Agent orchestrating Hotel KB, Services, and Local Info."""

    def __init__(
        self,
        session_id: Optional[str] = None,
        tool_registry: Optional[ToolRegistry] = None,
        planner: Optional[AgentPlanner] = None,
        persona_style: PersonaStyle = PersonaStyle.LUXURY_CLEFS_D_OR,
        provider: str = "auto"
    ):
        self.session_id = session_id or str(uuid.uuid4())
        self.state = AgentState(session_id=self.session_id)
        self.planner = planner or AgentPlanner()
        self.tools = tool_registry or ToolRegistry()
        self.llm = LLMBackend(provider=provider)
        self.system_prompt = get_system_prompt(persona_style)

    def process_turn(self, user_message: str) -> Dict[str, Any]:
        """Executes a single conversational agent turn with planning and tool deliberation."""
        # 1. Update State with User Input
        self.state.add_user_message(user_message)
        self.state.log_thought(f"Received guest message: '{user_message}'")

        # Check if user message reveals room number
        import re
        r_match = re.search(r'\b(?:room|villa)\s*([0-9a-zA-Z]+)\b', user_message.lower())
        if r_match:
            self.state.room_number = r_match.group(1).upper()
            if self.state.pending_slot == "room_number":
                self.state.pending_slot = None

        # 2. Planning: Create or update execution plan
        plan = self.planner.create_plan(user_message, self.state)
        self.state.active_plan = plan
        self.state.log_thought(
            f"Formulated plan: '{plan.goal}' ({plan.complexity}) with {len(plan.steps)} step(s)"
        )

        executed_tools: List[Dict[str, Any]] = []

        # 3. Deliberation & Execution Loop
        while not plan.completed:
            decision = self.planner.decide_next_action(self.state)

            if decision.action_type == ActionType.ASK_CLARIFICATION:
                self.state.log_thought(f"Decision: Ask Clarification — {decision.reasoning}")
                clarif = decision.clarification_question or "Could you please specify?"
                self.state.add_assistant_message(clarif)
                return {
                    "reply": clarif,
                    "action": "ask_clarification",
                    "plan": plan.model_dump(),
                    "state": self.state.model_dump(),
                    "executed_tools": executed_tools
                }

            elif decision.action_type == ActionType.CALL_TOOL:
                step = plan.get_current_step()
                tool_name = decision.tool_name or (step.tool_name if step else "get_hotel_policy")
                args = decision.tool_args or (step.parameters if step else {})

                # Ensure room number is passed if tool needs it
                if tool_name == "create_service_request" and "room_number" not in args:
                    if self.state.room_number:
                        args["room_number"] = self.state.room_number
                    else:
                        # Need room number from guest
                        self.state.pending_slot = "room_number"
                        clarif = "Certainly! May I kindly have your **Room or Villa Number** so our team may fulfill this request?"
                        self.state.add_assistant_message(clarif)
                        return {
                            "reply": clarif,
                            "action": "ask_clarification",
                            "plan": plan.model_dump(),
                            "state": self.state.model_dump(),
                            "executed_tools": executed_tools
                        }

                self.state.log_thought(f"Invoking tool '{tool_name}' with args {args}")
                tool_res: ToolResult = self.tools.execute(tool_name, args)
                self.state.total_tool_calls += 1

                tool_record = {
                    "tool": tool_name,
                    "args": args,
                    "success": tool_res.success,
                    "summary": tool_res.summary(),
                    "data": tool_res.data
                }
                executed_tools.append(tool_record)
                self.state.intermediate_tool_outputs.append(tool_record)

                if step:
                    step.status = AgentStepStatus.COMPLETED if tool_res.success else AgentStepStatus.FAILED
                    step.result = tool_res.data

                # Advance plan
                plan.advance()

            elif decision.action_type == ActionType.RESPOND:
                break

        # 4. Final Response Synthesis (LLM with Julian Persona)
        synthesis = self._synthesize_response(user_message, executed_tools)
        self.state.add_assistant_message(synthesis)
        self.state.log_thought("Response synthesized and returned to guest.")

        return {
            "reply": synthesis,
            "action": "respond",
            "plan": plan.model_dump(),
            "state": self.state.model_dump(),
            "executed_tools": executed_tools
        }

    def _synthesize_response(self, user_query: str, executed_tools: List[Dict[str, Any]]) -> str:
        """Grounds LLM synthesis in tool observations while maintaining Julian's etiquette."""
        if not executed_tools:
            # Fallback to persona conversational response
            history = [ChatMessage(role=t["role"], content=t["content"]) for t in self.state.conversation_turns]
            return self.llm.generate_response(self.system_prompt, history)

        last_tool = executed_tools[-1]
        t_name = last_tool["tool"]
        data = last_tool["data"]

        # Tool-specific grounded synthesis templates matching Julian's voice:
        if t_name == "create_service_request":
            if isinstance(data, dict) and "ticket_number" in data:
                return (
                    f"Consider it done right away, esteemed guest. I have registered your request for **Room {data.get('room_number', '')}** "
                    f"and dispatched work order `{data['ticket_number']}` to our hospitality floor team.\n\n"
                    f"• **Service Ticket:** `{data['ticket_number']}`\n"
                    f"• **Estimated Completion:** {data.get('estimated_completion_time', '15-20 minutes')}\n\n"
                    "Our attendants will deliver your items with utmost care. Please let me know if you desire anything further."
                )

        if t_name == "calculate_distance":
            if isinstance(data, dict):
                return (
                    f"It is my absolute pleasure to provide travel details to **{data.get('destination')}**.\n\n"
                    f"• **Distance:** {data.get('distance_km')} km from our resort gates\n"
                    f"• **Estimated Transit Time:** ~{data.get('travel_time_minutes')} minutes\n"
                    f"• **Recommended Transit:** {', '.join(data.get('recommended_transit', []))}\n\n"
                    f"💡 *Concierge Recommendation:* {data.get('concierge_note', 'Our house shuttle departs from the porte-cochère hourly.')}"
                )

        if t_name == "get_room_info":
            if isinstance(data, list) and data:
                lines = [f"Allow me to present our distinguished accommodations matching your preference:\n"]
                for r in data[:3]:
                    lines.append(f"• **{r.get('name')}** (${r.get('base_rate_usd')}/night) — {r.get('view_type')} view, {r.get('bed_configuration')}, up to {r.get('max_occupancy')} guests.")
                lines.append("\nMay I arrange an upgrade or reserve one of these exquisite sanctuaries for your stay?")
                return "\n".join(lines)

        if t_name == "get_restaurant_info":
            if isinstance(data, list) and data:
                lines = [f"Delighted to share our culinary offerings, esteemed guest:\n"]
                for v in data[:3]:
                    lines.append(f"• **{v.get('name')}** ({v.get('cuisine_type')}) — {v.get('location')}. Hours: {list(v.get('hours', {}).values())[0] if v.get('hours') else 'Open Daily'}.")
                    if v.get("signature_dishes"):
                        lines.append(f"  *Signature:* {v['signature_dishes'][0]}")
                lines.append("\nShall I reserve a premier table or arrange an in-room dining delivery for you this evening?")
                return "\n".join(lines)

        if t_name == "get_hotel_policy":
            if isinstance(data, list) and data:
                p = data[0]
                return (
                    f"Certainly, esteemed guest. Here are the official terms regarding **{p.get('title')}**:\n\n"
                    f"{p.get('summary')}\n\n"
                    f"*{p.get('details')}*\n\n"
                    "Please let me know if you would like me to assist with any special accommodations or exemptions."
                )

        if t_name == "search_attractions":
            if isinstance(data, list) and data:
                lines = [f"I would be thrilled to recommend these regional highlights, esteemed guest:\n"]
                for a in data[:3]:
                    lines.append(f"• **{a.get('name')}** ({a.get('distance_km')} km away) — {a.get('sub_category')}. Highlights: {', '.join(a.get('highlights', [])[:3])}.")
                    if a.get("concierge_tips"):
                        lines.append(f"  💡 *Insider Tip:* {a['concierge_tips']}")
                lines.append("\nOur resort chauffeur or house shuttle is readily at your disposal whenever you wish to venture out.")
        if t_name == "synthesize_itinerary" and isinstance(data, dict):
            title = data.get("title", "Curated Day Itinerary")
            stops = data.get("stops", [])
            lines = [f"It is my absolute honor to present **{title}**:\n"]
            lines.append(f"{data.get('summary', '')}\n")
            for s in stops:
                lines.append(f"• **{s.get('time_slot')} — {s.get('venue_name')}** ({s.get('category', '').title()})")
                lines.append(f"  {s.get('activity_description')}")
                if s.get("curator_tip"):
                    lines.append(f"  💡 *Insider Tip:* {s.get('curator_tip')}")
            lines.append(f"\n🚗 *Transit Logistics:* {data.get('transit_advice', 'Complimentary shuttle and private sedans available.')}")
            lines.append(f"🎫 *Bookings:* {data.get('booking_instructions', 'All table reservations are confirmed.')}")
            return "\n".join(lines)

        # Fallback to LLM backend
        history = [ChatMessage(role=t["role"], content=t["content"]) for t in self.state.conversation_turns]
        return self.llm.generate_response(self.system_prompt, history)
