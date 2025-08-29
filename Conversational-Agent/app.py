import os
import io
import base64
import asyncio
import re
import streamlit as st
from utils.tts import speak_stream, speaker_stream
from utils.assistant_agent import RoyalEnfieldBikeAssistant
from dotenv import load_dotenv
from utils.utilsreq import clean_text

load_dotenv()

st.set_page_config(page_title="Voice Assistant", layout="wide")
st.title("Query the Data Conversational Bot")

if "query_history" not in st.session_state:
    st.session_state.query_history = []

if "messages" not in st.session_state:
    st.session_state["messages"] = []

st.markdown("""
    <style>
    .chat-container {
        display: flex;
        flex-direction: column;
        width: 100%;
    }
    .user-bubble {
        background-color: #DCF8C6;
        color: black;
        padding: 12px 16px;
        border-radius: 18px;
        margin: 6px 0;
        max-width: 70%;
        align-self: flex-end;
        font-size: 1rem;
        font-family: 'Segoe UI', Arial, sans-serif;
        box-shadow: 0 1px 2px rgba(0,0,0,0.15);
    }
    .assistant-bubble {
        background-color: #E4E6EB;
        color: black;
        padding: 12px 16px;
        border-radius: 18px;
        margin: 6px 0;
        max-width: 70%;
        align-self: flex-start;
        font-size: 1rem;
        font-family: 'Segoe UI', Arial, sans-serif;
        box-shadow: 0 1px 2px rgba(0,0,0,0.15);
    }
    .query-card {
        background: #2c2f38;
        color: #f1f1f1;
        padding: 10px 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        font-size: 0.9rem;
        line-height: 1.4;
        font-family: 'Segoe UI', Arial, sans-serif;
    }
    .query-card strong {
        color: #4CAF50;
    }
    .query-card em {
        color: #9E9E9E;
        font-size: 0.85rem;
    }
    .stTextInput textarea {
        font-size: 1rem !important;
    }
    </style>
""", unsafe_allow_html=True)

chat_placeholder = st.container()

with chat_placeholder:
    for msg in st.session_state["messages"]:
        role_class = "user-bubble" if msg["role"] == "user" else "assistant-bubble"
        st.markdown(
            f"<div class='chat-container'><div class='{role_class}'>{msg['content']}</div></div>",
            unsafe_allow_html=True
        )
        if msg.get("audio"):
            st.audio(msg["audio"], format="audio/mp3")

user_input = st.text_input("Ask your question about the graph:", value="", key="user_input")

if user_input and (not st.session_state.messages or st.session_state.messages[-1]["content"] != clean_text(user_input)):
    st.session_state.messages.append({
        "role": "user",
        "content": clean_text(user_input),
        "audio": None
    })
    with st.spinner("Assistant is typing..."):
        try:
            agent = RoyalEnfieldBikeAssistant(
                llm_model="gpt-4",
                tavily_api_key=os.environ["TAVILY_API_KEY"],
                redis_url=os.environ["REDIS_URL"],
                redis_cache_host="localhost",
                redis_cache_port=6379,
                redis_cache_db=0,
                vector_index="bike_index"
            )
            results = asyncio.run(agent.processed_query(user_query=user_input))

            content, metadata = None, None
            if isinstance(results, dict) and "content" in results and "metadata" in results:
                content, metadata = results["content"], results["metadata"]
            else:
                if isinstance(results, str):
                    content = re.split(r"additional_kwargs", results, 1)[0]
                    content = clean_text(content)
                else:
                    content = clean_text(str(results))

            if content.lower().startswith("content"):
                content = content[7:].strip()

            st.session_state.query_history.append((user_input, content))

            if content and str(content).strip():
                audio_buf = speaker_stream(content)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": content,
                    "audio": audio_buf
                })
            else:
                audio_buf = speak_stream("No results found.")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "No results found.",
                    "audio": audio_buf
                })
        except Exception as e:
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"Error: {str(e)}",
                "audio": None
            })
            st.error(f"Some Unexpected Value Error Arised : {e}")

    st.rerun()

with st.sidebar:
    st.header("🕘 Query History")
    if st.session_state.query_history:
        for i, (q, c) in enumerate(reversed(st.session_state.query_history), 1):
            st.markdown(
                f"<div class='query-card'><strong>Q{i}:</strong> {q}<br><em>A:</em> {c}</div>",
                unsafe_allow_html=True
            )
    else:
        st.write("No queries yet.")
