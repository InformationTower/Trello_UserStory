import streamlit as st
from openai import OpenAI

st.title("OpenAI key test")

if "openai_api_key" not in st.secrets:
    st.error("openai_api_key ontbreekt")
    st.stop()

client = OpenAI(api_key=st.secrets["openai_api_key"])

st.write("De knop staat hieronder.")

if st.button("Test OpenAI"):
    st.write("Knop geklikt")
    try:
        response = client.responses.create(
            model="gpt-4o-mini",
            input="Zeg alleen: ok"
        )
        st.success(response.output_text)
    except Exception as e:
        st.error(str(e))
