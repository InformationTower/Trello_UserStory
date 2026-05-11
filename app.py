import requests
import streamlit as st
from openai import OpenAI
from pathlib import Path

st.set_page_config(page_title="User Story Generator", page_icon="📝", layout="wide")
st.title("User Story Generator")
st.write("Beantwoord de vragen stap voor stap. De AI gebruikt jouw instructions.md om betere vragen en output te maken.")

def read_instructions():
    path = Path("instructions.md")
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""

def build_question_from_instructions(instructions, answers):
    client = OpenAI(api_key=st.secrets["openai_api_key"])
    prompt = f"""
Je bent een product owner assistent.

Gebruik deze instructies:
{instructions}

Tot nu toe hebben we deze antwoorden:
- gebruiker: {answers.get("who", "")}
- functionaliteit: {answers.get("what", "")}
- doel: {answers.get("why", "")}
- systeem: {answers.get("system", "")}
- trigger: {answers.get("trigger", "")}

Geef alleen de beste volgende vraag terug.
Stel 1 concrete vraag tegelijk.
Als alles compleet is, zeg dan: COMPLEET
"""
    response = client.responses.create(
        model="gpt-4o-mini",
        input=prompt
    )
    return response.output_text.strip()

def generate_story_with_ai(answers, instructions):
    client = OpenAI(api_key=st.secrets["openai_api_key"])
    prompt = f"""
Je bent een ervaren product owner.

Gebruik deze instructies:
{instructions}

Schrijf in het Nederlands:
1. Een duidelijke user story.
2. Minimaal 5 acceptatiecriteria.
3. Maak de tekst concreet, kort en professioneel.

Context:
- Gebruiker: {answers.get("who", "")}
- Functionaliteit: {answers.get("what", "")}
- Doel: {answers.get("why", "")}
- Systeem: {answers.get("system", "")}
- Trigger: {answers.get("trigger", "")}

Gebruik dit format:

User story:
Als ... wil ik ... zodat ...

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

if "step" not in st.session_state:
    st.session_state.step = 0

if "answers" not in st.session_state:
    st.session_state.answers = {}

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hoi, ik help je een user story te maken."}
    ]

if "ai_story" not in st.session_state:
    st.session_state.ai_story = None

instructions = read_instructions()

questions = [
    ("who", "Voor wie is dit bedoeld?"),
    ("what", "Wat wil je laten bouwen of oplossen?"),
    ("why", "Waarom is dit belangrijk?"),
    ("system", "In welk systeem gebeurt dit?"),
    ("trigger", "Wanneer of waardoor wordt dit gestart?"),
]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if st.session_state.step < len(questions):
    key, fallback_question = questions[st.session_state.step]

    if instructions:
        next_question = build_question_from_instructions(instructions, st.session_state.answers)
        if not next_question or next_question.upper() == "COMPLEET":
            next_question = fallback_question
    else:
        next_question = fallback_question

    with st.chat_message("assistant"):
        st.markdown(next_question)

    user_input = st.chat_input("Typ je antwoord")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.answers[key] = user_input
        st.session_state.step += 1
        st.rerun()

else:
    if st.session_state.ai_story is None:
        st.session_state.ai_story = generate_story_with_ai(st.session_state.answers, instructions)

    st.success("Klaar! De AI heeft een verbeterde story gegenereerd.")
    st.markdown(st.session_state.ai_story)

    with st.expander("Toon ingevulde antwoorden"):
        st.json(st.session_state.answers)

    if st.button("Opnieuw beginnen"):
        st.session_state.step = 0
        st.session_state.answers = {}
        st.session_state.messages = [
            {"role": "assistant", "content": "Hoi, ik help je een user story te maken."}
        ]
        st.session_state.ai_story = None
        st.rerun()

    st.button("Push naar Trello", disabled=False)

def push_to_trello(title, desc=""):
    url = "https://api.trello.com/1/cards"
    params = {
        "key": st.secrets["trello_api_key"],
        "token": st.secrets["trello_token"],
        "idList": st.secrets["trello_list_id"],
        "name": title,
        "desc": desc,
    }
    r = requests.post(url, params=params)
    r.raise_for_status()
    return r.json()

