import streamlit as st

st.title("User Story Generator")

if "step" not in st.session_state:
    st.session_state.step = 0

if "answers" not in st.session_state:
    st.session_state.answers = {}

questions = [
    ("who", "Voor wie is dit bedoeld?"),
    ("what", "Wat moet de app doen?"),
    ("why", "Waarom is dit belangrijk?"),
    ("system", "In welk systeem gebeurt dit?"),
    ("trigger", "Wanneer moet dit gebeuren?")
]

if st.session_state.step < len(questions):
    key, question = questions[st.session_state.step]
    st.write(question)
    user_input = st.chat_input("Typ je antwoord")
    if user_input:
        st.session_state.answers[key] = user_input
        st.session_state.step += 1
        st.rerun()
else:
    st.success("Alle informatie is compleet")
    st.write("### User story")
    st.write(
        f"Als {st.session_state.answers['who']} "
        f"wil ik {st.session_state.answers['what']} "
        f"zodat {st.session_state.answers['why']}."
    )
    st.write("### Context")
    st.write(st.session_state.answers)