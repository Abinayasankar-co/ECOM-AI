import os
import re
import asyncio
import streamlit as st
from dotenv import load_dotenv
from utils.tts import speaker_stream
from utils.assistant_agent import RoyalEnfieldBikeAssistant
from utils.utilsreq import clean_text

# Load environment variables
load_dotenv()

# Set Streamlit page configuration
st.set_page_config(
    page_title="Voice Assistant",
    layout="wide",
    initial_sidebar_state="collapsed"  
)

# Initialize session state variables
if "query_history" not in st.session_state:
    st.session_state.query_history = []
if "messages" not in st.session_state:
    st.session_state.messages = []

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Poppins', sans-serif;
    }
    
    .st-emotion-cache-1g6x8q4 {
        padding-top: 1rem;
    }
    
    .st-emotion-cache-16txtv8 {
        padding: 1rem 1rem 8rem;
    }

    .sidebar-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #e0e0e0;
        margin-bottom: 20px;
        border-bottom: 2px solid #3e50b5;
        padding-bottom: 10px;
    }
    
    .query-card {
        background: #333;
        color: #ddd;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        font-size: 0.9rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }
    
    .query-card strong {
        color: #88aaff;
    }
    
    .query-card em {
        color: #ccc;
        font-size: 0.8rem;
    }
    
    .st-emotion-cache-1c7v0l1.e1f1d6gn2 {
        background-color: #262730;
    }
    </style>
""", unsafe_allow_html=True)

# Main Title
st.title("🚲 Conversational Assistant")

# Display chat messages from history on app rerun
for message in st.session_state.messages: 
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("audio"):
            st.audio(message["audio"], format="audio/mp3", autoplay=True)

# User input and chatbot logic
if prompt := st.chat_input("Ask your question:"):
    
    # Append user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get assistant response
    with st.spinner("Assistant is thinking..."):
        try:
            agent = RoyalEnfieldBikeAssistant(
                llm_model="gpt-4",
                openai_api_key=st.secrets["openai"]["OPENAI_API_KEY"],
                tavily_api_key=st.secrets["tavily"]["TAVILY_API_KEY"],
                redis_url=st.secrets["redis"]["REDIS_URL"],
                redis_cache_host=st.secrets["redis"]["REDIS_HOST"],
                redis_port=17094,
                redis_cache_password=st.secrets["redis"]["REDIS_PASSWORD"],
                redis_cache_db=0,
                vector_index="bike_index"
            )
            
            results = asyncio.run(agent.processed_query(user_query=prompt))
            
            content = None
            if isinstance(results, dict) and "content" in results:
                content = results["content"]
            else:
                if isinstance(results, str):
                    content = re.split(r"additional_kwargs", results, 1)[0]
                    content = clean_text(content)
                else:
                    content = clean_text(str(results))
            
            if content and content.lower().startswith("content"):
                content = content[7:].strip()
            
            st.session_state.query_history.append((prompt, content))
            
            # Display assistant message
            with st.chat_message("assistant"):
                if content and str(content).strip():
                    st.markdown(content)
                    audio_buf = speaker_stream(content)
                    st.audio(audio_buf, format="audio/mp3", autoplay=True)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": content,
                        "audio": audio_buf
                    })
                else:
                    no_results_text = "No results found."
                    st.markdown(no_results_text)
                    audio_buf = speak_stream(no_results_text)
                    st.audio(audio_buf, format="audio/mp3", autoplay=True)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": no_results_text,
                        "audio": audio_buf
                    })
        except Exception as e:
            with st.chat_message("assistant"):
                error_message = f"Error: {str(e)}"
                st.markdown(error_message)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_message,
                    "audio": None
                })
            st.error(f"Unexpected error: {e}")

# Sidebar for Query History
with st.sidebar:
    st.markdown("<h3 class='sidebar-header'>🕘 Query History</h3>", unsafe_allow_html=True)
    if st.session_state.query_history:
        for i, (q, c) in enumerate(reversed(st.session_state.query_history), 1):
            st.markdown(
                f"<div class='query-card'><strong>Q{i}:</strong> {q}<br><em>A:</em> {c}</div>",
                unsafe_allow_html=True
            )
    else:
        st.write("No queries yet.")