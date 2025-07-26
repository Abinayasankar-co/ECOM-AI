import streamlit as st

def render_chat_button():
    """Render a floating chat button with improved styling"""
    custom_css = """
    <style>
    .ask-button {
        position: fixed;
        bottom: 40px;
        right: 40px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 50%;
        width: 70px;
        height: 70px;
        font-size: 30px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        cursor: pointer;
        z-index: 9999;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .ask-button:hover {
        transform: scale(1.1);
        box-shadow: 0 12px 35px rgba(0,0,0,0.4);
    }
    
    .ask-button:active {
        transform: scale(0.95);
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
    }
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        margin-bottom: 30px;
    }
    
    .info-box {
        background: #f8f9fa;
        border-left: 4px solid #667eea;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
    
    # Add JavaScript for button functionality
    js_code = """
    <script>
    function handleChatClick() {
        // Scroll to the chat input
        const chatInput = document.querySelector('input[placeholder*="question"]');
        if (chatInput) {
            chatInput.scrollIntoView({ behavior: 'smooth' });
            chatInput.focus();
        }
    }
    </script>
    """
    st.markdown(js_code, unsafe_allow_html=True)
    
    # Render the floating button
    st.markdown(
        '<button class="ask-button" onclick="handleChatClick()" title="Ask a question">🎤</button>', 
        unsafe_allow_html=True
    )

def render_header():
    """Render a beautiful header for the application"""
    st.markdown("""
    <div class="main-header">
        <h1 style="margin: 0; text-align: center;">🤖 Neo4j AI Assistant</h1>
        <p style="margin: 10px 0 0 0; text-align: center; opacity: 0.9;">
            Your intelligent product analysis and query assistant
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_info_box(message, icon="ℹ️"):
    """Render an information box with custom styling"""
    st.markdown(f"""
    <div class="info-box">
        <strong>{icon} {message}</strong>
    </div>
    """, unsafe_allow_html=True)

def render_success_message(message):
    """Render a success message with custom styling"""
    st.success(f"✅ {message}")

def render_error_message(message):
    """Render an error message with custom styling"""
    st.error(f"❌ {message}")

def render_warning_message(message):
    """Render a warning message with custom styling"""
    st.warning(f"⚠️ {message}")
