
import streamlit as st
from datetime import datetime
from src.module20_final_concierge.final_agent import TheGrandAzureMasterAgent

# ======================== PAGE CONFIGURATION ========================

st.set_page_config(
    page_title="The Grand Azure | Guest Concierge",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ======================== PROFESSIONAL DESIGN ========================

st.markdown("""
<style>
:root {
    --navy: #172F43;
    --navy-light: #24465D;
    --teal: #397C78;
    --teal-dark: #2D6865;
    --ivory: #F5F3EE;
    --gold: #C5A878;
    --ink: #243444;
    --muted: #71808C;
    --line: #DFE5E6;
    --soft-teal: #E8F1EF;
}

.stApp {
    background: var(--ivory);
    color: var(--ink);
}

.block-container {
    max-width: 1180px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #172F43 0%, #203E52 100%);
    border-right: 1px solid #2C4B60;
}

[data-testid="stSidebar"] > div:first-child {
    padding-top: 1.5rem;
}

[data-testid="stSidebar"] hr {
    border-color: #3A5669;
    margin: 1.2rem 0;
}

.brand {
    color: #FFFFFF;
    font-size: 21px;
    font-weight: 750;
    letter-spacing: 1.5px;
    line-height: 1.4;
}

.brand-subtitle {
    color: #D8C39D;
    font-size: 10px;
    letter-spacing: 3px;
    margin-top: 6px;
}

.sidebar-label {
    color: #B9C9D3;
    font-size: 10px;
    letter-spacing: 1.8px;
    font-weight: 700;
    margin: 12px 0 8px;
}

/* Sidebar navigation */
[data-testid="stSidebar"] div[role="radiogroup"] {
    gap: 7px;
}

[data-testid="stSidebar"] div[role="radiogroup"] label {
    display: flex;
    align-items: center;
    background: rgba(255, 255, 255, 0.055);
    border: 1px solid rgba(219, 231, 237, 0.18);
    border-radius: 9px;
    padding: 11px 13px !important;
    margin: 0 !important;
    transition: all 0.2s ease;
}

/* Hide default radio circles */
[data-testid="stSidebar"] div[role="radiogroup"]
label > div:first-child {
    display: none !important;
}

[data-testid="stSidebar"] div[role="radiogroup"] label p {
    color: #E3EBF0 !important;
    font-size: 13px;
    font-weight: 500;
}

[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    background: #304F62 !important;
    border-color: #679B95 !important;
}

/* Selected navigation page */
[data-testid="stSidebar"] div[role="radiogroup"]
label:has(input:checked) {
    background: #397C78 !important;
    border: 1px solid #72A8A0 !important;
    box-shadow: inset 3px 0 0 #D8C39D;
}

[data-testid="stSidebar"] div[role="radiogroup"]
label:has(input:checked) p {
    color: #FFFFFF !important;
    font-weight: 700;
}

/* Main heading */
.eyebrow {
    color: var(--teal);
    font-size: 11px;
    font-weight: 750;
    letter-spacing: 2.2px;
    margin-bottom: 8px;
}

.hero {
    background: linear-gradient(
        115deg,
        #FFFFFF 0%,
        #F9FAF8 72%,
        #EAF2EF 100%
    );
    border: 1px solid var(--line);
    border-top: 4px solid var(--gold);
    border-radius: 15px;
    padding: 30px 32px;
    margin: 12px 0 26px;
    box-shadow: 0 8px 24px rgba(23, 47, 67, 0.045);
}

.hero h1 {
    color: var(--navy);
    font-size: clamp(27px, 3vw, 38px);
    line-height: 1.2;
    letter-spacing: -0.7px;
    margin: 0 0 10px;
}

.hero p {
    color: var(--muted);
    font-size: 15px;
    line-height: 1.75;
    margin: 0;
    max-width: 760px;
}

/* Section headings */
.section-heading {
    color: var(--navy);
    font-size: 21px;
    font-weight: 700;
    margin: 8px 0 6px;
}

.section-description {
    color: var(--muted);
    font-size: 13px;
    line-height: 1.7;
    margin-bottom: 18px;
}

/* Informational service cards */
.service-card {
    background: #FFFFFF;
    border: 1px solid var(--line);
    border-left: 3px solid var(--teal);
    border-radius: 12px;
    padding: 20px;
    min-height: 112px;
    margin-bottom: 14px;
    box-shadow: 0 4px 14px rgba(23, 47, 67, 0.035);
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.service-card:hover {
    border-color: #A9C7C1;
    border-left-color: var(--gold);
    box-shadow: 0 6px 18px rgba(23, 47, 67, 0.07);
}

.service-card-title {
    color: var(--navy);
    font-size: 15px;
    font-weight: 700;
    margin-bottom: 8px;
}

.service-card-description {
    color: var(--muted);
    font-size: 13px;
    line-height: 1.65;
}

/* General buttons */
div.stButton > button {
    width: 100%;
    min-height: 43px;
    background: #FFFFFF;
    color: var(--navy);
    border: 1px solid #D6E0DF;
    border-radius: 9px;
    font-weight: 600;
    transition: all 0.2s ease;
}

div.stButton > button:hover {
    background: var(--soft-teal);
    border-color: #78A8A1;
    color: var(--navy);
}

/* Highlighted chat input */
div[data-testid="stChatInput"] {
    background: #FFFFFF !important;
    border: 2px solid #397C78 !important;
    border-radius: 14px !important;
    box-shadow: 0 4px 16px rgba(23, 47, 67, 0.09);
    transition: all 0.2s ease;
}

div[data-testid="stChatInput"]:focus-within {
    background: #F4FAF8 !important;
    border: 2px solid #2D6865 !important;
    box-shadow: 0 0 0 4px rgba(57, 124, 120, 0.15);
}

div[data-testid="stChatInput"] textarea {
    color: #20364B !important;
    font-size: 15px !important;
}

div[data-testid="stChatInput"] textarea::placeholder {
    color: #71808C !important;
    opacity: 1;
}

/* Send button */
div[data-testid="stChatInput"] button {
    background: #397C78 !important;
    border-radius: 9px !important;
    color: #FFFFFF !important;
    border: none !important;
}

div[data-testid="stChatInput"] button:hover {
    background: #244F4C !important;
}

/* Chat messages */
div[data-testid="stChatMessage"] {
    background: #FFFFFF;
    border: 1px solid var(--line);
    border-radius: 12px;
    padding: 12px 14px;
    box-shadow: 0 3px 12px rgba(23, 47, 67, 0.025);
}

/* Footer */
.footer {
    border-top: 1px solid var(--line);
    padding-top: 15px;
    margin-top: 30px;
    color: var(--muted);
    font-size: 11px;
    text-align: center;
}

/* Responsive display */
@media (max-width: 700px) {
    .block-container {
        padding-top: 1.1rem;
    }

    .hero {
        padding: 22px 20px;
    }

    .hero h1 {
        font-size: 27px;
    }

    .service-card {
        padding: 15px;
    }
}
</style>
""", unsafe_allow_html=True)


# ======================== SESSION STATE ========================

if "agent" not in st.session_state:
    st.session_state.agent = TheGrandAzureMasterAgent()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = (
        "guest_" + datetime.now().strftime("%Y%m%d%H%M%S")
    )

if "pending_question" not in st.session_state:
    st.session_state.pending_question = None


def new_conversation():
    st.session_state.agent = TheGrandAzureMasterAgent()
    st.session_state.messages = []
    st.session_state.session_id = (
        "guest_" + datetime.now().strftime("%Y%m%d%H%M%S")
    )
    st.session_state.pending_question = None


# ======================== PAGE CONTENT ========================

services = {
    "Concierge Home": {
        "title": "Your stay, thoughtfully assisted",
        "description": (
            "Welcome to The Grand Azure Resort & Spa. Your personal "
            "concierge can help with hotel information, dining, local "
            "experiences, room service, and travel planning."
        ),
    },
    "Hotel Information": {
        "title": "Hotel Information",
        "description": (
            "Find information about hotel facilities, amenities, "
            "services, and policies."
        ),
    },
    "Dining": {
        "title": "Dining & Restaurants",
        "description": (
            "Explore dining options and request recommendations "
            "for your preferences."
        ),
    },
    "Local Experiences": {
        "title": "Local Experiences",
        "description": (
            "Discover attractions, activities, and places to visit "
            "during your stay."
        ),
    },
    "Room Service": {
        "title": "Room Service & Guest Requests",
        "description": (
            "Tell your concierge what you need during your stay."
        ),
    },
    "Travel Planning": {
        "title": "Travel & Itinerary Planning",
        "description": (
            "Get assistance planning sightseeing, local transport, "
            "and activities."
        ),
    },
}


# ======================== SIDEBAR NAVIGATION ========================

with st.sidebar:
    st.markdown(
        '<div class="brand">THE GRAND AZURE</div>'
        '<div class="brand-subtitle">RESORT & SPA</div>',
        unsafe_allow_html=True,
    )

    st.markdown("---")

    st.markdown(
        '<div class="sidebar-label">GUEST SERVICES</div>',
        unsafe_allow_html=True,
    )

    # Sidebar navigation is the only page navigation control.
    # No home-page buttons modify this widget's session state.
    section = st.radio(
        "Guest navigation",
        list(services.keys()),
        label_visibility="collapsed",
        key="guest_navigation",
    )

    st.markdown("---")

    if st.button("Start a new conversation", use_container_width=True):
        new_conversation()
        st.rerun()

    st.markdown("---")

    st.markdown(
        '<div class="sidebar-label">PERSONAL CONCIERGE</div>'
        '<div style="font-size:12px;line-height:1.8;color:#D0DCE3;">'
        'Personal assistance for a comfortable and memorable stay.'
        '</div>',
        unsafe_allow_html=True,
    )


# ======================== PAGE HEADER ========================

page = services[section]

st.markdown(
    '<div class="eyebrow">THE GRAND AZURE RESORT & SPA</div>'
    '<div class="hero">'
    f'<h1>{page["title"]}</h1>'
    f'<p>{page["description"]}</p>'
    '</div>',
    unsafe_allow_html=True,
)


# ======================== SERVICE SUGGESTIONS ========================

suggestions = {
    "Hotel Information": [
        "What facilities does the hotel offer?",
        "What are the check-in and check-out times?",
    ],
    "Dining": [
        "Tell me about the hotel's dining options.",
        "Can you recommend a restaurant?",
    ],
    "Local Experiences": [
        "What attractions are near the hotel?",
        "Recommend activities for my stay.",
    ],
    "Room Service": [
        "I need extra towels in my room.",
        "I would like to make a room service request.",
    ],
    "Travel Planning": [
        "Help me plan a local sightseeing itinerary.",
        "What transport options are available nearby?",
    ],
}


# ======================== HOME PAGE SERVICE CARDS ========================

if section == "Concierge Home" and not st.session_state.messages:

    st.markdown(
        '<div class="section-heading">Explore our services</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-description">'
        'Choose a service from the sidebar to view its page. '
        'You can also ask the concierge a question below.'
        '</div>',
        unsafe_allow_html=True,
    )

    home_cards = [
        (
            "Hotel Information",
            "Find details about facilities, amenities, and hotel policies.",
        ),
        (
            "Dining & Restaurants",
            "Explore dining options and get restaurant recommendations.",
        ),
        (
            "Local Experiences",
            "Discover attractions and activities around your destination.",
        ),
        (
            "Room Service",
            "Ask for in-room assistance and help with guest requests.",
        ),
        (
            "Travel Planning",
            "Plan sightseeing, transportation, and local itineraries.",
        ),
    ]

    # Cards are informational only. There are no Explore buttons.
    card_cols = st.columns(2)

    for i, (name, detail) in enumerate(home_cards):
        with card_cols[i % 2]:
            st.markdown(
                '<div class="service-card">'
                f'<div class="service-card-title">{name}</div>'
                f'<div class="service-card-description">{detail}</div>'
                '</div>',
                unsafe_allow_html=True,
            )


# ======================== PAGE-SPECIFIC QUICK QUESTIONS ========================

elif section != "Concierge Home":

    st.markdown(
        '<div class="section-heading">Popular questions</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-description">'
        'Select a question below or type your own message to the concierge.'
        '</div>',
        unsafe_allow_html=True,
    )

    question_cols = st.columns(len(suggestions[section]))

    for i, question in enumerate(suggestions[section]):
        if question_cols[i].button(
            question,
            key=f"question_{section}_{i}",
            use_container_width=True,
        ):
            st.session_state.pending_question = question
            st.rerun()


# ======================== CHAT HISTORY ========================

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# ======================== CHAT INPUT ========================

prompt = st.chat_input(
    "Write your message to the concierge..."
)

if st.session_state.pending_question:
    prompt = st.session_state.pending_question
    st.session_state.pending_question = None


# ======================== PROCESS GUEST MESSAGE ========================

if prompt:
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Your concierge is preparing a response..."):
            try:
                result = (
                    st.session_state.agent.process_guest_interaction(
                        query=prompt,
                        image_input=None,
                        room_number="302",
                        guest_name="Guest",
                        session_id=st.session_state.session_id,
                    )
                )

                answer = result.response_text
                st.markdown(answer)

            except Exception as exc:
                answer = (
                    "We could not process your request right now. "
                    "Please try again or contact hotel staff."
                )
                st.error(answer)

                # Technical details remain in the terminal for debugging.
                print(f"Concierge error: {exc}")

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
    })


# ======================== FOOTER ========================

st.markdown(
    '<div class="footer">'
    'THE GRAND AZURE RESORT & SPA'
    ' &nbsp; | &nbsp; GUEST CONCIERGE'
    '</div>',
    unsafe_allow_html=True,
)
