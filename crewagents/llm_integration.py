

from crewai import LLM
import os
old_llm = LLM(
    #model="azure/gpt4-TURBO",
    #api_key=os.getenv("OPENAI_API_KEY"),
    #base_url=os.getenv("API_BASE")
    model="gemini/gemini-1.5-flash",
    api_key=os.getenv("GOOGLE_API_KEY")
)

llm = LLM(
    model="openrouter/deepseek/deepseek-chat-v3.1:free",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)


    

