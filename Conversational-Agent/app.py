import streamlit as st
from utils.tts import speak
from ui.components import show_url_input, show_summary, play_audio
from utils.assistant_agent import RoyalEnfieldBikeAssistant

st.set_page_config(page_title="Neo4j Voice Assistant", layout="wide")
st.title("🔍 Neo4j Query Assistant with Voice")

information = RoyalEnfieldBikeAssistant()

if "query_history" not in st.session_state:
    st.session_state.query_history = []

user_input = st.text_input("Ask your question about the graph:")

if user_input:
   
    st.session_state.query_history.append((user_input, cypher))
    if results:
        spoken_text = f"{results}"
        speak(spoken_text)
        st.success("Result spoken aloud.")
    else:
        speak("No results found.")
        st.warning("No results found.")

with st.sidebar:
    st.header("🕘 Query History")
    if st.session_state.query_history:
        for i, (q, c) in enumerate(reversed(st.session_state.query_history), 1):
            st.markdown(f"**{i}.** {q}")
            st.code(c, language="cypher")
    else:
        st.write("No queries yet.")
