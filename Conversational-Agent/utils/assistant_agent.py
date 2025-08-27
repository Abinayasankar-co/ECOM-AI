from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from tavily import TavilyClient
import redis
from document_store import DocumentStore

class RollsRoyceBikeAssistant:
    def __init__(self, llm_model: str, tavily_api_key: str, redis_url: str, redis_cache_host: str, redis_cache_port: int, redis_cache_db: int, vector_index: str):
        self.llm = ChatOpenAI(model_name=llm_model, temperature=0)
        self.tavily = TavilyClient(api_key=tavily_api_key)
        self.prompt = ChatPromptTemplate.from_template(
            "You are a polite Rolls Royce showroom assistant. Always greet the customer first. "
            "Step 1: Transform their query into a list of related sub-questions. "
            "Step 2: Retrieve relevant data from Tavily API and vector store. "
            "Step 3: Consolidate findings. Step 4: Provide a neat, structured, and polite answer."
        )
        self.memory = ConversationBufferMemory(memory_key="chat_history")
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt, memory=self.memory)
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

    def process_query(self, user_query: str) -> str:
        cached = self._check_cache(user_query)
        if cached:
            return cached
        struct = self.chain.run(user_query)
        tv = self.tavily.search(user_query)
        vs = self.doc_store.retrieve_similar(user_query, k=3)
        combined = (
            f"Query: {user_query}\nSub-questions: {struct}\nTavily: {tv}\n"
            f"VectorResults: {[d.page_content for d in vs]}"
        )
        final = self.chain.run(combined)
        self._update_cache(user_query, final)
        return final

if __name__ == "__main__":
    agent = RollsRoyceBikeAssistant(
        llm_model="gpt-4",
        tavily_api_key="TAVILY_API_KEY",
        redis_url="redis://localhost:6379",
        redis_cache_host="localhost",
        redis_cache_port=6379,
        redis_cache_db=0,
        vector_index="bike_index"
    )
    user_input = "Tell me about the latest Rolls Royce bike model available."
    print(agent.process_query(user_input))
