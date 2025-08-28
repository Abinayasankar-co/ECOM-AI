import os
import json
import redis
import asyncio
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from tavily import TavilyClient
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
    
    #Algorithm for Determining the User Query Regaridng the Request
    async def processed_query(self, user_query : str) -> str:
        try:
            prompt1 = ChatPromptTemplate.from_messages(
                [
                    ("system", "The task for you is to write an elaborative and more informative question from the user's normal question. The answer must be strictly in JSON format with key 'questions' and value as a list."),
                    ("user", f"The Query to be given is: {user_query}")
                ]
            )

            llm = self.llm 
            runner1 = prompt1 | llm 
            ai_message = await runner1.ainvoke({"user_query": user_query})
            subqs_content = ai_message.content if hasattr(ai_message, "content") else str(ai_message)
            
            # Debug: print the raw response
            #print("Raw LLM response:", subqs_content)
            try:
                queries = json.loads(subqs_content)
            except Exception as json_err:
                print(f"JSON parsing error: {json_err}")
                return None

            if not queries or "questions" not in queries or not isinstance(queries["questions"], list):
                print("Invalid JSON structure or missing 'questions' key.")
                return None

            cached = [self._check_cache(query) for query in queries["questions"]]
            if all(cached):
                return cached
            tavily_results = [self.tavily.search(query) for query in queries["questions"]]
            docs = [self.doc_store.retrieve_similar(query, k=3) for query in queries["questions"]]
            docs_content = ["\n".join([d.page_content for d in doc]) for doc in docs]

            prompt2 = ChatPromptTemplate.from_messages(
                [
                    ("system", "Use the sub-questions, Tavily results, and document content to craft a conversational response."),
                    ("user","Sub-questions: {subqs}\nTavily: {tavily}\nDocuments: {docs}")
                ],
            )
            runner2 = prompt2 | llm 
            final_result = await runner2.ainvoke({
                "subqs": queries['questions'],
                "tavily": tavily_results,
                "docs": docs_content
            })
            self._update_cache(user_query, final_result.content if hasattr(final_result, "content") else str(final_result))
            return final_result.content if hasattr(final_result, "questions") else str(final_result)
        
        except Exception as e:
            print(f"The Exception : {e}")
            return None
    
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
    result = asyncio.run(agent.processed_query(user_input))
    if isinstance(result, dict) and "content" in result and "metadata" in result:
        content, metadata = result["content"] , result["metadata"]
        print(f"The Content : {content} , Metadata : {metadata}")
