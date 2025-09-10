

from crewai import LLM
import os
llm = LLM(
    #model="azure/gpt4-TURBO",
    #api_key=os.getenv("OPENAI_API_KEY"),
    #base_url=os.getenv("API_BASE")
    model="gemini/gemini-1.5-flash",
    api_key=os.getenv("GOOGLE_API_KEY")
)


llm = LLM(
    model="gemini/gemini-1.5-flash",
    api_key=os.getenv("GOOGLE_API_KEY")
)