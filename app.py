import streamlit as st
import requests

st.set_page_config(page_title="User Story Generator", page_icon="📝", layout="wide")

st.title("User Story Generator")
st.write("Beantwoord de vragen stap voor stap. Daarna maken we een user story.")

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
        {"role": "assistant", "content": "Hoi, ik help je om een user story te maken."}
    ]

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
    who = st.session_state.answers.get("who", "")
    what = st.session_state.answers.get("what", "")
    why = st.session_state.answers.get("why", "")
    system = st.session_state.answers.get("system", "")
    trigger = st.session_state.answers.get("trigger", "")

    story = f"Als {who} wil ik {what}, zodat {why}."
    criteria = [
        f"De functionaliteit is beschikbaar in {system}.",
        f"De oplossing ondersteunt het gewenste doel: {why}.",
        f"De gebruiker kan de functionaliteit gebruiken voor: {what}.",
        f"De actie wordt gestart wanneer: {trigger}.",
        "De output kan later worden doorgezet naar Trello.",
    ]

    st.success("Klaar! Hier is je story.")
    st.subheader("User story")
    st.write(story)

    st.subheader("Acceptatiecriteria")
    for c in criteria:
        st.write(f"- {c}")

    st.subheader("Antwoorden")
    st.json(st.session_state.answers)

    st.button("Push naar Trello", disabled=True)
