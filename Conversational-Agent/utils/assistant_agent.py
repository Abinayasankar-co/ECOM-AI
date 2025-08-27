import os
import asyncio
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.chains.api.base import LLMChain
from langchain_core.runnables import (
    RunnableSequence,
)
from langchain_core.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferMemory
from tavily import TavilyClient
import redis
from document_store import DocumentStore

load_dotenv()

class RoyalEnfieldBikeAssistant:
    def __init__(self, llm_model: str, tavily_api_key: str, redis_url: str, redis_cache_host: str, redis_cache_port: int, redis_cache_db: int, vector_index: str):
        self.llm = ChatOpenAI(model_name=llm_model, temperature=0)
        self.tavily = TavilyClient(api_key=tavily_api_key)
        self.redis_cache = redis.StrictRedis(host=redis_cache_host, port=redis_cache_port, db=redis_cache_db)
        self.doc_store = DocumentStore(redis_url=redis_url, index_name=vector_index)

    def _check_cache(self, query: str) -> str:
        key = f"bike_cache:{query}"
        if self.redis_cache.exists(key):
            return self.redis_cache.get(key).decode("utf-8")
        return None

    def _update_cache(self, query: str, response: str):
        key = f"bike_cache:{query}"
        self.redis_cache.set(key, response, ex=3600)

    async def process_query(self, user_query: str) -> str:
        prompt = ChatPromptTemplate.from_template(
            "You are a polite showroom assistant. Always greet the customer first. "
            "Step 1: Transform their query into a list of related sub-questions. "
            "Step 2: Retrieve relevant data from Tavily API and vector store. "
            "Step 3: Consolidate findings. "
            "Step 4: Provide a neat, structured, and polite answer. "
            f"The Query from the user is : {user_query} "
            "NOTE: The written answers should be more human friendly and conversational like you're an assistant"
        )
        runner = RunnableSequence(prompt, self.llm)
        cached = self._check_cache(user_query)
        if cached:
            return cached
        struct = await runner.ainvoke(user_query + "\nStep 1: list sub-questions")
        tv = self.tavily.search(user_query)
        vs = self.doc_store.retrieve_similar(user_query, k=3)
        combined = (
            f"Query: {user_query}\nSub-questions: {struct}\n"
            f"Web searched Results from Tavily: {tv}\n"
            f"Stored Results from VectorDB: {[d.page_content for d in vs]}"
        )
        final = await runner.ainvoke(combined)
        self._update_cache(user_query, final)
        return final
    
if __name__ == "__main__":
    agent = RoyalEnfieldBikeAssistant(
        llm_model="gpt-4",
        tavily_api_key=os.environ["TAVILY_API_KEY"],
        redis_url="redis://localhost:6379",
        redis_cache_host="localhost",
        redis_cache_port=6379,
        redis_cache_db=0,
        vector_index="bike_index"
    )
    user_input = "Tell me about the latest Royal Enfield bike model available with larger spec and its features"
    print(asyncio.run(agent.process_query(user_input)))
