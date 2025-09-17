

from crewai import LLM
import os
llm = LLM(
    model="openai/gpt-4",
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("API_BASE")
    #model="gemini/gemini-1.5-flash",
    #api_key=os.getenv("GOOGLE_API_KEY"),
)

oldllm = LLM(
    model="openrouter/deepseek/deepseek-chat-v3.1:free",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)


    
    
llllllm = LLM(
        model="ollama/llama3", 
    base_url="http://localhost:11434"  # Ollama's API endpoint
)



