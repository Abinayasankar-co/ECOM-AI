import os
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, CSVLoader
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters.character import RecursiveCharacterTextSplitter
from langchain_redis import RedisVectorStore
from langchain_openai import OpenAIEmbeddings
import streamlit as st

load_dotenv()

class DocumentStore:
    def __init__(self, redis_url: str, index_name: str, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.redis_url = redis_url
        self.index_name = index_name
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.embeddings = OpenAIEmbeddings(
            api_key=st.secrets["openai"]["api_key"]
        )

    def ingest_directory(self, directory_path: str, glob_pattern: str = "*.*"):
        loader = DirectoryLoader(directory_path, glob=glob_pattern)
        docs = loader.load()
        return self._chunk_and_store(docs)

    def ingest_csv(self, csv_path: str):
        loader = CSVLoader(csv_path)
        docs = loader.load()
        return self._chunk_and_store(docs)

    def ingest_text(self, text_path: str):
        loader = TextLoader(text_path, encoding="utf-8")
        docs = loader.load()
        return self._chunk_and_store(docs)

    def _chunk_and_store(self, documents):
        splitter = RecursiveCharacterTextSplitter(chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)
        chunks = splitter.split_documents(documents)
        vector_store = RedisVectorStore.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            index_name=self.index_name,
            redis_url=self.redis_url
        )
        return vector_store

    def load_existing_store(self):
        try:
            return RedisVectorStore(
                embeddings=self.embeddings,
                redis_url=self.redis_url,
                index_name=self.index_name,
            )
        except Exception as e:
            print(f"The Error While Loading the Store:{e}")

    def retrieve_similar(self, query: str, k: int = 3):
        store = self.load_existing_store()
        return store.similarity_search(query, k=k)
