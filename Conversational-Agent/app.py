import streamlit as st
from llm.query import generate_cypher_query
from db.neo4j_client import save_product_to_neo4j, run_query
from utils.tts import synthesize_voice, play_audio, cleanup_audio_file  # updated import

st.set_page_config(page_title="Neo4j Voice Assistant", layout="wide")
st.title("🔍 Neo4j Query Assistant with Voice")

# Initialize history in session state
if "query_history" not in st.session_state:
    st.session_state.query_history = []

# Example product dictionary for testing
product = {
    "Product Name": "Example Product",
    "Brand": "BrandX",
    "Price": "100",
    "Discount": "10%",
    "Availability": "In Stock",
    "Rating": "4.5",
    "Review Count": "100",
    "Product URL": "http://example.com",
    "Category": "CategoryX"
}
# Save product to Neo4j
save_product_to_neo4j(product)

# Sidebar: Query History
with st.sidebar:
    st.header("🕘 Query History")
    if st.session_state.query_history:
        for i, (q, c) in enumerate(reversed(st.session_state.query_history), 1):
            st.markdown(f"**{i}.** {q}")
            st.code(c, language="cypher")
    else:
        st.write("No queries yet.")

# Main: User Input
user_input = st.text_input("Ask your question about the graph:")

if user_input:
    st.info("Generating Cypher query...")
    cypher = generate_cypher_query(user_input)
    st.code(cypher, language='cypher')

    # Store history
    st.session_state.query_history.append((user_input, cypher))

    st.info("Querying Neo4j...")
    results = run_query(cypher)
    st.json(results)

    # Prepare speech text
    if results:
        spoken_text = f"The result is {results}"
    else:
        spoken_text = "No results found."

    # Generate & play audio in browser
    file_path = synthesize_voice(spoken_text)
    play_audio(file_path)
    cleanup_audio_file(file_path)
