import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Replace "*" with your frontend's origin, e.g., ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Retrieve Groq API key from environment variables
groq_api_key = os.getenv("groq_api")

# Initialize the LLM with ChatGroq
llm = ChatGroq(
    temperature=0.7,
    groq_api_key=groq_api_key,
    model_name="llama-3.2-90b-text-preview"
).with_structured_output(dict, method="json_mode")

# Define a prompt template to instruct the AI to respond with Mermaid syntax in JSON format
prompt_template = PromptTemplate.from_template(
    """
    You are an AI assistant that generates diagrams in Mermaid syntax.
    Always respond in the following JSON format:
    {{"mermaid_syntax": "Mermaid code here"}}
    
    For example, if asked to draw a flowchart, your response might be:
    {{"mermaid_syntax": "graph TD\\nA[Start] --> B[Login]\\nB -->|Success| C[Dashboard]\\nB -->|Fail| D[Error]"}}
    
    Do not include any additional explanations or outputs.
    
    user input: {input}
    """
)

# Combine the prompt template and LLM chain
llm_chain = prompt_template | llm

# Request and Response Models
class DiagramRequest(BaseModel):
    prompt: str

class DiagramResponse(BaseModel):
    mermaid_syntax: str

# Generate Mermaid Syntax Endpoint
@app.post("/generate-mermaid", response_model=DiagramResponse)
async def generate_mermaid(data: DiagramRequest):
    user_prompt = data.prompt

    try:
        # Invoke the LLM chain with the user input
        response = llm_chain.invoke({'input': user_prompt})
        
        # Extract Mermaid syntax from the response
        mermaid_syntax = response.get("mermaid_syntax")
        if not mermaid_syntax:
            raise ValueError("Invalid Mermaid syntax received.")
    
    except Exception as e:
        # Handle errors and return a meaningful message
        raise HTTPException(status_code=500, detail=f"Error generating Mermaid syntax: {str(e)}")

    # Return the Mermaid syntax as a response
    return DiagramResponse(mermaid_syntax=mermaid_syntax)
