import streamlit as st
import asyncio
import os
from utils.tts import speak
from ui.components import show_url_input, show_summary, play_audio
from utils.assistant_agent import RoyalEnfieldBikeAssistant
from dotenv import load_dotenv

load_dotenv()


st.set_page_config(page_title="Neo4j Voice Assistant", layout="wide")
st.title("🔍 Neo4j Query Assistant with Voice")

information = RoyalEnfieldBikeAssistant()

if "query_history" not in st.session_state:
    st.session_state.query_history = []

user_input = st.text_input("Ask your question about the graph:")

if user_input:
    agent = RoyalEnfieldBikeAssistant(
        llm_model="gpt-4",
        tavily_api_key=os.environ["TAVILY_API_KEY"],
        redis_url="redis://localhost:6379",
        redis_cache_host="localhost",
        redis_cache_port=6379,
        redis_cache_db=0,
        vector_index="bike_index"
    )
    if isinstance(user_input , str):
      results , metadata = asyncio.run(agent.processed_query(user_query=user_input))
      
    st.session_state.query_history.append((user_input, results))
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
