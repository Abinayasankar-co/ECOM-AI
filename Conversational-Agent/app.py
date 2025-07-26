import streamlit as st
from dotenv import load_dotenv
from utils.tts import synthesize_voice, play_audio, cleanup_audio_file
from db.neo4j_client import run_cypher_query, store_product, initialize_database
from llm.query import generate_cypher_query
from ui.components import render_chat_button, render_header, render_info_box, render_success_message, render_error_message, render_warning_message

from bs4 import BeautifulSoup
import requests
import time
import os
load_dotenv()

st.set_page_config(
    page_title="Neo4j AI Assistant", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database on startup
try:
    initialize_database()
except Exception as e:
    st.error(f"Database initialization failed: {e}")
    st.error("Please check your Neo4j connection settings. You need to set up the following environment variables:")
    st.code("""
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
    """)
    st.info("Create a .env file in your project root with these variables, or set them in your environment.")

# Render the beautiful header
render_header()

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Database status
    st.subheader("Database Status")
    try:
        # Test database connection
        test_result = run_cypher_query("RETURN 1 as status")
        st.success("✅ Neo4j Connected")
    except Exception as e:
        st.error("❌ Neo4j Connection Failed")
        st.info("Please check your Neo4j connection settings in .env file")
    
    # API Status
    st.subheader("API Status")
    openai_key = "your_openai_api_key"  # Replace with your actual key or fetch from env
    if openai_key:
        st.success("✅ OpenAI API Key Configured")
    else:
        st.warning("⚠️ OpenAI API Key Missing")
        api_key = st.text_input("Enter OpenAI API Key:", type="password")
        if api_key:
            st.session_state["OPENAI_API_KEY"] = api_key
            st.success("✅ API Key Saved")

# Main content
st.header("🛒 Scrape Products from E-Commerce Page")

render_info_box(
    "Enter a product listing URL from any e-commerce site to scrape and store product information in Neo4j.",
    "💡"
)

product_url = st.text_input("Enter Product Listing URL:", placeholder="https://example.com/products")

if st.button("🚀 Scrape Products", type="primary"):
    if not product_url:
        render_error_message("Please enter a valid URL")
    else:
        with st.spinner("🔍 Scraping product details..."):
            def scrape_products(url):
                try:
                    # Use requests instead of Playwright for better compatibility
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                    }
                    response = requests.get(url, headers=headers, timeout=30)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.content, "html.parser")
                    scraped = 0

                    # More generic selectors for different e-commerce sites
                    product_selectors = [
                        ".product-card", ".product-item", ".item", 
                        "[data-testid*='product']", ".product", ".card"
                    ]
                    
                    products_found = False
                    for selector in product_selectors:
                        products = soup.select(selector)
                        if products:
                            products_found = True
                            render_info_box(f"Found {len(products)} products using selector: {selector}", "🔍")
                            break
                    
                    if not products_found:
                        render_warning_message("No products found with common selectors. Please check the URL or provide a different one.")
                        return 0

                    # Create a progress bar
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    for i, product in enumerate(products[:10]):  # Limit to first 10 products
                        # Try multiple selectors for each field
                        title_selectors = [".product-title", ".title", "h3", "h2", "[data-testid*='title']"]
                        price_selectors = [".price", ".cost", ".amount", "[data-testid*='price']"]
                        rating_selectors = [".rating", ".stars", "[data-testid*='rating']"]
                        store_selectors = [".store-name", ".store", ".brand", "[data-testid*='store']"]
                        
                        title = None
                        price = None
                        rating = "N/A"
                        store = "Unknown"
                        
                        # Extract title
                        for selector in title_selectors:
                            title_el = product.select_one(selector)
                            if title_el:
                                title = title_el.get_text(strip=True)
                                break
                        
                        # Extract price
                        for selector in price_selectors:
                            price_el = product.select_one(selector)
                            if price_el:
                                price = price_el.get_text(strip=True)
                                break
                        
                        # Extract rating
                        for selector in rating_selectors:
                            rating_el = product.select_one(selector)
                            if rating_el:
                                rating = rating_el.get_text(strip=True)
                                break
                        
                        # Extract store
                        for selector in store_selectors:
                            store_el = product.select_one(selector)
                            if store_el:
                                store = store_el.get_text(strip=True)
                                break

                        if title and price:
                            try:
                                store_product(title, price, rating, store)
                                scraped += 1
                                status_text.text(f"✅ Stored: {title[:50]}...")
                            except Exception as e:
                                render_error_message(f"Failed to store product: {str(e)}")
                        
                        # Update progress
                        progress_bar.progress((i + 1) / min(len(products), 10))

                    return scraped
                    
                except requests.RequestException as e:
                    render_error_message(f"Failed to fetch URL: {str(e)}")
                    return 0
                except Exception as e:
                    render_error_message(f"Scraping error: {str(e)}")
                    return 0

            try:
                total = scrape_products(product_url)
                if total > 0:
                    message = f"Successfully scraped and stored {total} products!"
                    render_success_message(message)
                    
                    # Generate and play audio
                    audio_path = synthesize_voice(message)
                    if audio_path:
                        st.audio(audio_path)
                        play_audio(audio_path)
                        # Clean up the audio file
                        cleanup_audio_file(audio_path)
                else:
                    render_warning_message("No products were scraped. Please check the URL and try again.")
            except Exception as e:
                render_error_message(f"Error: {str(e)}")
                audio_path = synthesize_voice("An error occurred while scraping.")
                if audio_path:
                    st.audio(audio_path)
                    play_audio(audio_path)
                    cleanup_audio_file(audio_path)

# LLM Assistant Section
st.markdown("---")
st.header("💬 Ask About Products")

render_info_box(
    "Ask questions about the products in your database using natural language. The AI will generate Cypher queries to find the information you need.",
    "🤖"
)

# Voice greeting button
col1, col2 = st.columns([1, 4])
with col1:
    if st.button("🎤 Voice Greeting"):
        greeting = "Hi! How may I help you with product information?"
        audio_path = synthesize_voice(greeting)
        if audio_path:
            st.audio(audio_path)
            play_audio(audio_path)
            cleanup_audio_file(audio_path)

with col2:
    st.write("Click the button to hear a voice greeting")

# Chat interface
user_input = st.text_input("Type your question:", placeholder="e.g., Show me all products under $50")

if user_input:
    with st.spinner("🤔 Thinking..."):
        try:
            # Generate Cypher query
            cypher = generate_cypher_query(user_input)
            
            # Display the generated query
            with st.expander("🔍 Generated Cypher Query", expanded=False):
                st.code(cypher, language="cypher")
            
            # Execute the query
            results = run_cypher_query(cypher)
            
            # Display results
            st.subheader("📊 Results")
            if results:
                st.json(results)
                
                # Create a summary
                summary = f"Found {len(results)} results for your query."
                render_success_message(summary)
                
                # Generate and play audio
                audio_path = synthesize_voice(summary)
                if audio_path:
                    st.audio(audio_path)
                    play_audio(audio_path)
                    cleanup_audio_file(audio_path)
            else:
                render_warning_message("No results found for your query.")
                
        except Exception as e:
            render_error_message(f"LLM Query Failed: {e}")
            audio_path = synthesize_voice("Sorry, I couldn't understand that.")
            if audio_path:
                st.audio(audio_path)
                play_audio(audio_path)
                cleanup_audio_file(audio_path)

# Render the floating chat button
render_chat_button()
