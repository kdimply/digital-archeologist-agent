import os
from agents.core import DigitalArcheologist

try:
    print("--- Initializing Agent ---")
    agent = DigitalArcheologist()
    print("--- Testing Context Retrieval ---")
    # This checks if the FAISS tool is broken
    from tools.faiss_tool import retrieve_context
    ctx = retrieve_context("test", k=1)
    print(f"Context found: {len(ctx)} snippets")
    
    print("--- System Healthy ---")
except Exception as e:
    print(f"!!! SYSTEM CRASHED: {e}")
