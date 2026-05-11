import requests
import streamlit as st
from openai import OpenAI
from pathlib import Path

# =========================================================
# CONFIG
# =========================================================

st.set_page_config(
    page_title="User Story Generator",
    page_icon="📝",
    layout="wide"
)

st.title("📝 User Story Generator")
st.write(
    "Beantwoord stap voor stap de vragen. "
    "De AI gebruikt jouw instructions.md voor betere vragen en output."
)

# =========================================================
# OPENAI CLIENT
# =========================================================

client = OpenAI(api_key=st.secrets["openai_api_key"])

# =========================================================
# FUNCTIONS
# =========================================================

def read_instructions():
    path = Path("instructions.md")

    if path.exists():
        return path.read_text(encoding="utf-8")

    return ""


def build_next_question(instructions, answers):
    prompt = f"""
Je bent een ervaren product owner assistent.

Gebruik deze instructies:
{instructions}

Dit weten we al:

- gebruiker: {answers.get("who", "")}
- functionaliteit: {answers.get("what", "")}
- doel: {answers.get("why", "")}
- systeem: {answers.get("system", "")}
- trigger: {answers.get("trigger", "")}

Stel exact 1 slimme vervolgvraag.

Regels:
- Kort
- Concreet
- Geen uitleg
- Geen opsommingen
- Alleen de vraag teruggeven

Als alles compleet is:
antwoord exact met: COMPLEET
"""

    response = client.responses.create(
        model="gpt-4o-mini",
        input=prompt
    )

    return response.output_text.strip()


def generate_user_story(answers, instructions):
    prompt = f"""
Je bent een ervaren product owner.

Gebruik deze instructies:
{instructions}

Schrijf in het Nederlands:

1. Een professionele user story
2. Minimaal 5 acceptatiecriteria
3. Kort en concreet
4. Geen overbodige uitleg

Context:
- Gebruiker: {answers.get("who", "")}
- Functionaliteit: {answers.get("what", "")}
- Doel: {answers.get("why", "")}
- Systeem: {answers.get("system", "")}
- Trigger: {answers.get("trigger", "")}

Gebruik exact dit format:

User story:
Als ...
wil ik ...
zodat ...

Acceptatiecriteria:
- ...
- ...
- ...
- ...
- ...
"""

    response = client.responses.create(
        model="gpt-4o-mini",
        input=prompt
    )

    return response.output_text.strip()


def push_to_trello(title, desc=""):
    url = "https://api.trello.com/1/cards"

    params = {
        "key": st.secrets["trello_api_key"],
        "token": st.secrets["trello_token"],
        "idList": st.secrets["trello_list_id"],
        "name": title,
        "desc": desc,
    }

    response = requests.post(url, params=params)
    response.raise_for_status()

    return response.json()


# =========================================================
# SESSION STATE
# =========================================================

if "step" not in st.session_state:
    st.session_state.step = 0

if "answers" not in st.session_state:
    st.session_state.answers = {}

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hoi 👋 Ik help je een goede user story maken."
        }
    ]

if "current_question" not in st.session_state:
    st.session_state.current_question = None

if "ai_story" not in st.session_state:
    st.session_state.ai_story = None

# =========================================================
# DATA
# =========================================================

instructions = read_instructions()

questions = [
    ("who", "Voor wie is deze functionaliteit bedoeld?"),
    ("what", "Wat wil je laten bouwen of verbeteren?"),
    ("why", "Waarom is dit belangrijk?"),
    ("system", "In welk systeem gebeurt dit?"),
    ("trigger", "Wanneer wordt dit gestart?")
]

# =========================================================
# CHAT HISTORY
# =========================================================

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# =========================================================
# QUESTION FLOW
# =========================================================

if st.session_state.step < len(questions):

    key, fallback_question = questions[st.session_state.step]

    # Alleen nieuwe vraag genereren indien nodig
    if st.session_state.current_question is None:

        if instructions:

            with st.spinner("AI denkt na over de beste vraag..."):

                next_question = build_next_question(
                    instructions,
                    st.session_state.answers
                )

            if (
                not next_question
                or next_question.upper() == "COMPLEET"
            ):
                next_question = fallback_question

        else:
            next_question = fallback_question

        st.session_state.current_question = next_question

        st.session_state.messages.append({
            "role": "assistant",
            "content": next_question
        })

        st.rerun()

    # Toon huidige vraag
    with st.chat_message("assistant"):
        st.markdown(st.session_state.current_question)

    # Input
    user_input = st.chat_input("Typ je antwoord")

    if user_input:

        # User message opslaan
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })

        # Antwoord opslaan
        st.session_state.answers[key] = user_input

        # Volgende stap
        st.session_state.step += 1

        # Nieuwe vraag resetten
        st.session_state.current_question = None

        st.rerun()

# =========================================================
# GENERATE STORY
# =========================================================

else:

    if st.session_state.ai_story is None:

        with st.spinner("AI genereert de user story..."):

            st.session_state.ai_story = generate_user_story(
                st.session_state.answers,
                instructions
            )

    st.success("✅ User story succesvol gegenereerd")

    st.markdown(st.session_state.ai_story)

    # =====================================================
    # DEBUG / INPUTS
    # =====================================================

    with st.expander("📋 Toon ingevulde antwoorden"):
        st.json(st.session_state.answers)

    # =====================================================
    # TRELLO
    # =====================================================

    title = st.session_state.answers.get(
        "what",
        "Nieuwe user story"
    )

    if st.button("🚀 Push naar Trello"):

        try:
            card = push_to_trello(
                title=title,
                desc=st.session_state.ai_story
            )

            st.success("Trello kaart succesvol aangemaakt")

            st.markdown(
                f"[Open Trello kaart]({card.get('url', '')})"
            )

        except Exception as e:
            st.error(f"Fout bij Trello push: {e}")

    # =====================================================
    # RESET
    # =====================================================

    if st.button("🔄 Opnieuw beginnen"):

        st.session_state.step = 0
        st.session_state.answers = {}
        st.session_state.current_question = None
        st.session_state.ai_story = None

        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Hoi 👋 Ik help je een goede user story maken."
            }
        ]

        st.rerun()
