import streamlit as st
from llm.query import generate_cypher_query
from utils.tts import speak
from neo4j import GraphDatabase

st.set_page_config(page_title="Neo4j Voice Assistant", layout="wide")
st.title("🔍 Neo4j Query Assistant with Voice")

if "query_history" not in st.session_state:
    st.session_state.query_history = []

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))

def run_query(cypher):
    with driver.session() as session:
        result = session.run(cypher)
        return [record.data() for record in result]

user_input = st.text_input("Ask your question about the graph:")

if user_input:
    cypher = generate_cypher_query(user_input)
    st.code(cypher, language="cypher")
    st.session_state.query_history.append((user_input, cypher))
    results = run_query(cypher)
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
