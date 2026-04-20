import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="User Story Generator", page_icon="📝", layout="wide")
st.title("User Story Generator")

questions = [
    ("who", "Voor wie is dit bedoeld?"),
    ("what", "Wat wil je laten bouwen of oplossen?"),
    ("why", "Waarom is dit belangrijk?"),
    ("system", "In welk systeem gebeurt dit?"),
    ("trigger", "Wanneer of waardoor wordt dit gestart?"),
]

if "step" not in st.session_state:
    st.session_state.step = 0

if "answers" not in st.session_state:
    st.session_state.answers = {}

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hoi, ik help je een user story te maken."}
    ]

def generate_story_with_ai(answers):
    client = OpenAI(api_key=st.secrets["openai_api_key"])
    prompt = f"""
Schrijf een duidelijke user story in het Nederlands en geef minimaal 5 acceptatiecriteria.

Context:
- Gebruiker: {answers.get("who", "")}
- Functionaliteit: {answers.get("what", "")}
- Doel: {answers.get("why", "")}
- Systeem: {answers.get("system", "")}
- Trigger: {answers.get("trigger", "")}

Geef als output:
1. User story
2. Acceptatiecriteria als bullets
3. Eventueel korte verbeterde formulering
"""
    response = client.responses.create(
        model="gpt-4o-mini",
        input=prompt
    )
    return response.output_text

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if st.session_state.step < len(questions):
    key, question = questions[st.session_state.step]
    with st.chat_message("assistant"):
        st.markdown(question)

    user_input = st.chat_input("Typ je antwoord")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.answers[key] = user_input
        st.session_state.step += 1
        st.rerun()
else:
    if "ai_story" not in st.session_state:
        st.session_state.ai_story = generate_story_with_ai(st.session_state.answers)

    st.success("Klaar! De AI heeft een verbeterde story gegenereerd.")
    st.markdown(st.session_state.ai_story)
    st.button("Push naar Trello", disabled=True)
