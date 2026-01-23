# llm.py

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
import streamlit as st

load_dotenv()

@st.cache_resource
def get_llm():
    """
    Cache the LLM so Streamlit does NOT recreate it
    on every rerun (major speed improvement)
    """
    return ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.2,
        api_key=os.getenv("GROQ_API_KEY")
    )
