import os
from dotenv import load_dotenv
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_redis import RedisVectorStore
from langchain_openai import OpenAIEmbeddings

load_dotenv()

embeddings = OpenAIEmbeddings(api_key=os.environ["OPENAI_API_KEY"])

def ingest_csv(
        csv_path: str, 
        redis_url: str, 
        index_name: str, 
        chunk_size: int = 1000, 
        chunk_overlap: int = 200
    ):
    loader = CSVLoader(file_path=csv_path)
    documents = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = splitter.split_documents(documents)
    vector_store = RedisVectorStore.from_documents(
        documents=chunks,
        embedding=embeddings,
        index_name=index_name,
        redis_url=redis_url
    )
    return vector_store

def retrieve_from_redis(
        query: str, 
        redis_url: str, 
        index_name: str, 
        k: int = 3
    ):
    store = RedisVectorStore(
        index_name=index_name,
        embedding=embeddings,
        redis_url=redis_url
    )
    results = store.similarity_search(query=query, k=k)
    return results


if __name__ == "__main__":
    try:
        csv_path = "../dataset/Inventory.csv"
        redis_url="redis://localhost:6379"
        index_name = "bike_index"
        vector_store = ingest_csv(
            csv_path=csv_path,
            redis_url=redis_url,
            index_name=index_name
        )
        print(vector_store)
        
    except Exception as e:
        print(f"The Retrival Error : {e}")