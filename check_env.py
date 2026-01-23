from dotenv import load_dotenv
import os

load_dotenv()

print("GROQ_API_KEY Loaded:", bool(os.getenv("GROQ_API_KEY")))
print("TAVILY_API_KEY Loaded:", bool(os.getenv("TAVILY_API_KEY")))
print("LANGCHAIN_API_KEY Loaded:", bool(os.getenv("LANGCHAIN_API_KEY")))
