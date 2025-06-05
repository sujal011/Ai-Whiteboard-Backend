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
from fastapi.responses import JSONResponse
import re
import google.genai as genai
from google.genai import types
from diagram_examples import get_all_examples

# Print to verify application start
print("Application started")

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","https://ai-whiteboard.vercel.app"],  # Replace "*" with your frontend's origin, e.g., ["http://localhost:5173"]
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
    model_name="deepseek-r1-distill-llama-70b"
).with_structured_output(dict, method="json_mode")

# Initialize Gemini client
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API"))

# Define valid diagram types globally
VALID_DIAGRAM_TYPES = [
    'flowchart', 'sequenceDiagram', 'classDiagram',
    'stateDiagram', 'erDiagram', 'gantt', 'pie', 'journey',
    'mindmap', 'xychart-beta', 'gitGraph'
]

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

class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
    details: str | None = None

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            message="Internal server error",
            details=str(exc)
        ).model_dump()
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            message=exc.detail,
            details=str(exc)
        ).model_dump()
    )

@app.get("/")
def read_root():
    return {"message": "Welcome to AI Whiteboard Backend"}

def validate_mermaid_syntax(mermaid_code: str) -> bool:
    """Validate if the given string is valid Mermaid syntax."""
    # Basic Mermaid syntax validation
    if not mermaid_code:
        return False
        
    # Remove any leading/trailing whitespace and newlines
    code = mermaid_code.strip()   
            
    return True

@app.post("/generate-mermaid", response_model=DiagramResponse)
async def generate_mermaid(data: DiagramRequest):
    user_prompt = data.prompt
    
    example_data = get_all_examples()
    # Try Gemini first
    try:
        gemini_prompt = f"""You are an AI assistant that generates diagrams in Mermaid syntax.
        You can create various types of diagrams that are supported by Excalidraw:
        1. Flowcharts (graph/flowchart) - For process flows, decision trees, etc.
        2. Sequence Diagrams - For showing interactions between components
        3. Class Diagrams - For object-oriented design
        4. Entity Relationship (ER) Diagrams - For database design
        5. Gantt Charts - For project timelines and schedules
        6. Pie Charts - For showing proportions and percentages
        7. Mind Maps - For hierarchical information organization
        8. XY Data Charts - For plotting data points and trends
        9. Git Graphs - For visualizing git branches and commits
        10. State Diagrams - For showing state transitions
        11. Journey Diagrams - For user journeys and experiences

        Follow these rules:
        1. Use appropriate Mermaid syntax for the requested diagram type
        2. Start with the correct diagram type keyword (graph, flowchart, sequenceDiagram, classDiagram, erDiagram, gantt, pie, mindmap, xychart-beta, gitGraph, stateDiagram, journey)
        3. Use proper node definitions and connections
        4. Always respond in the following JSON format: {{"mermaid_syntax": "Mermaid code here"}}
        5. Do not include any additional explanations or outputs
        6. Ensure all nodes and connections are properly defined
        7. Use clear, readable syntax that is guaranteed to work
        8. For mindmaps, use proper hierarchical structure with parent-child relationships
        9. For charts (pie, xy), include proper data formatting
        10. For git graphs, use proper branch and commit syntax"""

        # Load all example formats into the system prompt
        if example_data:
            gemini_prompt += "\n\nHere are some example diagrams for reference:\n"
            for diagram_type, examples in example_data.items():
                gemini_prompt += f"\n{diagram_type} diagram example:\n"
                gemini_prompt += f"Prompt: {examples['prompt']}\n"
                gemini_prompt += f"Example:\n{examples['example']}\n"
                gemini_prompt += "Use these as references for syntax and structure, but create new diagrams based on the user's prompt.\n"

        # Configure generation settings for Gemini
        generate_content_config = types.GenerateContentConfig(
            response_mime_type="application/json"
        )
        # Generate content using Gemini with separate user prompt
        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                types.Content(
                    role="system",
                    parts=[types.Part.from_text(text=gemini_prompt)]
                ),
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=user_prompt)]
                )
            ],
            config=generate_content_config
        )
        
        # Parse the response
        mermaid_syntax = response.text
        if not mermaid_syntax:
            print("Empty response from Gemini, falling back to Groq")
            raise ValueError("Empty response from Gemini")
            
        # Validate the Mermaid syntax
        if not validate_mermaid_syntax(mermaid_syntax):
            print(f"Invalid Mermaid syntax from Gemini. Generated syntax:\n{mermaid_syntax}")
            raise ValueError("Invalid Mermaid syntax from Gemini")
            
        return DiagramResponse(mermaid_syntax=mermaid_syntax)
        
    except Exception as e:
        # Print the error from Gemini
        print(f"Gemini generation failed: {str(e)}")
        if "API_KEY_INVALID" in str(e) or "API key expired" in str(e):
            print("Gemini API key has expired")
            
        print(f"Gemini generation failed: {str(e)}, falling back to Groq")
        
        messages = [
            ("system", gemini_prompt),
            ("human", user_prompt)
        ]

        try:
            # Invoke the LLM chain with the user input
            response = llm.invoke(messages)
            
            # Extract Mermaid syntax from the response
            mermaid_syntax = response.get("mermaid_syntax")
            if not mermaid_syntax:
                print("Invalid response format from Groq")
                raise HTTPException(
                    status_code=400,
                    detail="Invalid response format from AI model"
                )
            
            # Replace escaped newlines with actual newlines
            mermaid_syntax = mermaid_syntax.replace('\\n', '\n')
                
            # Validate the Mermaid syntax
            if not validate_mermaid_syntax(mermaid_syntax):
                print(f"Invalid Mermaid syntax from Groq. Generated syntax:\n{mermaid_syntax}")
                raise HTTPException(
                    status_code=400,
                    detail="Groq: Generated Mermaid syntax is invalid. Please try again with a different prompt."
                )
        
        except Exception as e:
            print(f"Groq generation failed: {str(e)}")
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=500,
                detail=f"Error generating diagram: {str(e)}"
            )

        return DiagramResponse(mermaid_syntax=mermaid_syntax)


@app.post('/calculate')
async def run(data: ImageData):
    try:
        # Validate input
        if not data.image or not data.image.startswith('data:image/'):
            raise HTTPException(
                status_code=400,
                detail="Invalid image data format. Please provide a valid base64 encoded image."
            )
            
        # Process image
        try:
            image_data = base64.b64decode(data.image.split(",")[1])
            image_bytes = BytesIO(image_data)
            image = Image.open(image_bytes)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Error processing image: {str(e)}"
            )
            
        # Analyze image
        try:
            responses = analyze_image(image, dict_of_vars=data.dict_of_vars)
            if not responses:
                return {
                    "status": "success",
                    "message": "No mathematical expressions found in the image",
                    "data": []
                }
                
            return {
                "status": "success",
                "message": "Image processed successfully",
                "data": responses
            }
        except Exception as e:
            # Check if it's a Gemini API error
            if "503" in str(e) and "UNAVAILABLE" in str(e):
                raise HTTPException(
                    status_code=503,
                    detail="Gemini API is currently overloaded. Please try again later."
                )
            # For other errors from analyze_image
            raise HTTPException(
                status_code=500,
                detail=f"Error analyzing image: {str(e)}"
            )
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing calculation: {str(e)}"
        )

@app.post("/ask-ai")
async def generate_answer(data: QuestionData):
    try:
        question = data.question
        llm_chain = get_llm()

        # Invoke the LLM chain with the user input
        response = llm_chain.invoke({'question': question})
        result = response.get("result")
        if not result:
            raise HTTPException(
                status_code=400,
                detail="Invalid response format from AI model"
            )
    
        return {
            "status": "success",
            "message": "Answer generated successfully",
            "data": response
        }
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500,
            detail=f"Error generating answer: {str(e)}"
        )
