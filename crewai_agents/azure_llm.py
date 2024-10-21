

from crewai import LLM
import os
llm = LLM(
    model="azure/gpt4-TURBO",
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("API_BASE")
)
