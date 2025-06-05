import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from fastapi.middleware.cors import CORSMiddleware
import base64
from io import BytesIO
from PIL import Image
from utils import analyze_image
from note_enhance import get_llm

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ai-whiteboard.vercel.app", "http://localhost:5173"],  # Explicitly allow frontend domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Retrieve Groq API key from environment variables
groq_api_key = os.getenv("GROQ_API")

# Initialize the LLM with ChatGroq
llm = ChatGroq(
    temperature=0.7,
    groq_api_key=groq_api_key,
    model_name="llama-3.3-70b-versatile"
).with_structured_output(dict, method="json_mode")

# # Define a prompt template to instruct the AI to respond with Mermaid syntax in JSON format
# prompt_template = PromptTemplate.from_template(
#     """
#     You are an AI assistant that generates diagrams in Mermaid syntax.
#     Always respond in the following JSON format:
#     {{"mermaid_syntax": "Mermaid code here"}}
    
#     Do not include any additional explanations or outputs.
    
#     user input: {input}
#     """
# )

# # Combine the prompt template and LLM chain
# llm_chain = prompt_template | llm

# Request and Response Models
class DiagramRequest(BaseModel):
    prompt: str
    
class QuestionData(BaseModel):
    question: str
    
    
class ImageData(BaseModel):
    image: str
    dict_of_vars: dict

class DiagramResponse(BaseModel):
    mermaid_syntax: str
    
class AnswerData(BaseModel):
    result: str

@app.get("/")
def read_root():
    return {"message": "Welcome to AI Whiteboard Backend"}

# Generate Mermaid Syntax Endpoint
@app.post("/generate-mermaid", response_model=DiagramResponse)
async def generate_mermaid(data: DiagramRequest):
    user_prompt = data.prompt
    messages=[("system","You are an AI assistant that generates diagrams in Mermaid syntax.\n Always respond in the following JSON format:\n {\"mermaid_syntax\": \"Mermaid code here\"}\n Do not include any additional explanations or outputs."),]

    messages.append(("human", user_prompt))

    try:
        # Invoke the LLM chain with the user input
        response = llm.invoke(messages)
        
        # Extract Mermaid syntax from the response
        mermaid_syntax = response.get("mermaid_syntax")
        if not mermaid_syntax:
            raise ValueError("Invalid Mermaid syntax received.")
    
    except Exception as e:
        # Handle errors and return a meaningful message
        raise HTTPException(status_code=500, detail=f"Error generating Mermaid syntax: {str(e)}")

    # Return the Mermaid syntax as a response
    return DiagramResponse(mermaid_syntax=mermaid_syntax)


@app.post('/calculate')
async def run(data: ImageData):
    try:
        # Validate input
        if not data.image or not data.image.startswith('data:image/'):
            raise HTTPException(status_code=400, detail="Invalid image data format")
            
        # Process image
        try:
            image_data = base64.b64decode(data.image.split(",")[1])
            image_bytes = BytesIO(image_data)
            image = Image.open(image_bytes)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error processing image: {str(e)}")
            
        # Analyze image
        responses = analyze_image(image, dict_of_vars=data.dict_of_vars)
        if not responses:
            return {"message": "No results found", "data": [], "status": "success"}
            
        # Process responses
        data = []
        for response in responses:
            data.append(response)
        print('response in route: ', response)
        return {"message": "Image processed", "data": data, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/ask-ai")
async def generate_answer(data: QuestionData):
    question = data.question
    llm_chain = get_llm()

    try:
        # Invoke the LLM chain with the user input
        response = llm_chain.invoke({'question': question})
        result = response.get("result")
        if not result:
            raise ValueError("Invalid llm syntax received.")
    
    except Exception as e:
        # Handle errors and return a meaningful message
        return HTTPException(status_code=500, detail=f"Error generating answer syntax: {str(e)}")

    # Return the Mermaid syntax as a response
    print(response)
    return response
