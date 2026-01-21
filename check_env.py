from dotenv import load_dotenv
import os

load_dotenv()

#print("OpenAI Loaded:", bool(os.getenv("OPENAI_API_KEY")))
#print("Tavily Loaded:", bool(os.getenv("TAVILY_API_KEY")))
print("GOOGLE_API_KEY Loaded:", bool(os.getenv("GOOGLE_API_KEY")))
print("TAVILY_API_KEY Loaded:", bool(os.getenv("TAVILY_API_KEY")))
print("LANGCHAIN_API_KEY Loaded:", bool(os.getenv("LANGCHAIN_API_KEY")))