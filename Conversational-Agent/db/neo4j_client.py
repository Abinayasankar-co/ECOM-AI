from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
import logging

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

def get_driver():
    """Get Neo4j driver with error handling"""
    try:
        # Check if environment variables are set
        if not NEO4J_URI:
            raise ValueError("NEO4J_URI environment variable is not set. Please set it in your .env file or environment variables.")
        if not NEO4J_USER:
            raise ValueError("NEO4J_USER environment variable is not set. Please set it in your .env file or environment variables.")
        if not NEO4J_PASSWORD:
            raise ValueError("NEO4J_PASSWORD environment variable is not set. Please set it in your .env file or environment variables.")
        
        # Debug logging
        logger.info(f"Connecting to Neo4j with URI: {NEO4J_URI}")
        logger.info(f"Username: {NEO4J_USER}")
        
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        # Test the connection
        with driver.session() as session:
            session.run("RETURN 1")
        return driver
    except Exception as e:
        logger.error(f"Failed to connect to Neo4j: {e}")
        raise

def store_product(title, price, star_rating, store_name):
    """Store a product in Neo4j with error handling"""
    try:
        driver = get_driver()
        query = """
        MERGE (p:Product {title: $title})
        SET p.price = $price,
            p.star_rating = $star_rating,
            p.store = $store_name,
            p.created_at = datetime()
        """
        with driver.session() as session:
            session.run(query, title=title, price=price, star_rating=star_rating, store_name=store_name)
        logger.info(f"Successfully stored product: {title}")
    except Exception as e:
        logger.error(f"Failed to store product {title}: {e}")
        raise
    finally:
        if 'driver' in locals():
            driver.close()

def run_cypher_query(query):
    """Run a Cypher query with error handling"""
    try:
        driver = get_driver()
        with driver.session() as session:
            result = session.run(query)
            return [record.data() for record in result]
    except Exception as e:
        logger.error(f"Failed to run Cypher query: {e}")
        raise
    finally:
        if 'driver' in locals():
            driver.close()

def initialize_database():
    """Initialize the database with constraints and indexes"""
    try:
        driver = get_driver()
        with driver.session() as session:
            # Create constraints
            session.run("CREATE CONSTRAINT product_title IF NOT EXISTS FOR (p:Product) REQUIRE p.title IS UNIQUE")
            # Create indexes for better performance
            session.run("CREATE INDEX product_store IF NOT EXISTS FOR (p:Product) ON (p.store)")
            session.run("CREATE INDEX product_price IF NOT EXISTS FOR (p:Product) ON (p.price)")
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    finally:
        if 'driver' in locals():
            driver.close()
