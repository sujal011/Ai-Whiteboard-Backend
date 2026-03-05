
import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.getcwd())

load_dotenv()

from app.services.ai_service import gemini_llm
from langchain_core.messages import SystemMessage, HumanMessage

def test_ask_prompt(question, context):
    system_prompt = (
        "You are a helpful assistant that responds with the shortest possible answer to the question if the answer is within one-two words or numbers (if mathematical expressions or equations are asked). "
        "Use the following pieces of retrieved context to answer the question. "
        "If you don't know the answer, say that you don't know. "
        "Note: when asked to create/generate a checklist of topics, use this markdown syntax:\n"
        "- [ ] Unchecked item\n"
        "Note: when asked to write/generate code, enclose your answer within ``` and ```. "
        "Always respond in proper markdown format."
        f"\n\nContext:\n{context}"
    )
    
    response = gemini_llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=question),
    ])
    
    print(f"--- Question: {question} ---")
    print(f"Response: {response.content}\n")

if __name__ == "__main__":
    context = "The capital of France is Paris. The CEO of Tesla is Elon Musk. FastAPI is a modern web framework for building APIs with Python."
    
    # Test short answer
    test_ask_prompt("What is the capital of France?", context)
    
    # Test checklist
    test_ask_prompt("Create a checklist of the facts mentioned in the context.", context)
    
    # Test code block (using general knowledge as context doesn't have code, but LLM should still follow instruction)
    test_ask_prompt("Write a simple hello world in Python.", context)
    
    # Test markdown formatting
    test_ask_prompt("Summarize the context in bold.", context)
