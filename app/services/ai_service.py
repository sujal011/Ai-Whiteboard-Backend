import os
import base64
from io import BytesIO
from PIL import Image
import json
import ast

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector


from app.core.config import settings
import google.genai as genai
from google.genai import types
from app.api.deps import get_db
from app.core.exceptions import AIAnalysisError

# LLM setup
groq_llm = ChatGroq(
    model_name="qwen/qwen3-32b",
    groq_api_key=settings.GROQ_API_KEY
)

gemini_llm = ChatGoogleGenerativeAI(
    model="gemini-flash-lite-latest",
)

gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY)

from app.rag.vectorstore import get_vectorstore

def generate_mermaid_syntax(prompt: str) -> str:
    gemini_prompt = """You are an AI assistant that generates diagrams in Mermaid syntax.
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
    4. Always respond in the following JSON format: {"mermaid_syntax": "Mermaid code here"}
    5. Do not include any additional explanations or outputs
    6. Ensure all nodes and connections are properly defined
    7. Use clear, readable syntax that is guaranteed to work
    8. For mindmaps, use proper hierarchical structure with parent-child relationships
    9. For charts (pie, xy), include proper data formatting
    10. For git graphs, use proper branch and commit syntax"""

    try:
        generate_content_config = types.GenerateContentConfig(response_mime_type="application/json")
        response = gemini_client.models.generate_content(
            model="gemini-flash-lite-latest",
            contents=[
                types.Content(role="system", parts=[types.Part.from_text(text=gemini_prompt)]),
                types.Content(role="user", parts=[types.Part.from_text(text=prompt)])
            ],
            config=generate_content_config
        )
        return json.loads(response.text)["mermaid_syntax"]
    except Exception as e:
        # Fallback to Groq
        chat_prompt = ChatPromptTemplate.from_messages([
            ("system", gemini_prompt.replace("{", "{{").replace("}", "}}")),
            ("human", "{prompt}")
        ])
        chain = chat_prompt | groq_llm.with_structured_output(dict, method="json_mode")
        res = chain.invoke({"prompt": prompt})
        return res.get("mermaid_syntax")

def answer_from_documents(question: str, workspace_id: int) -> str:
    # Use the vector store directly instead of deprecated chains
    docs = get_vectorstore().similarity_search(
        question, 
        k=4, 
        filter={"workspace_id": workspace_id}
    )
    
    context = "\n\n".join([doc.page_content for doc in docs])
    
    system_prompt = (
        "You are an assistant for question-answering tasks. "
        "Use the following pieces of retrieved context to answer the question. "
        "If you don't know the answer, say that you don't know. "
        "Use three sentences maximum and keep the answer concise."
        f"\n\nContext:\n{context}"
    )
    
    response = gemini_llm.invoke([
        ("system", system_prompt),
        ("human", question),
    ])
    
    return response.content

def analyze_excalidraw_image(image_base64: str, dict_of_vars: dict = None, prompt: str = None) -> list:
    img_data = base64.b64decode(image_base64.split(",")[1] if "," in image_base64 else image_base64)
    img_byte_arr = BytesIO(img_data).getvalue()
    
    dict_of_vars_str = json.dumps(dict_of_vars or {}, ensure_ascii=False)
    
    sys_prompt = prompt or (
        f"You have been given an image with some mathematical expressions, equations, or graphical problems, and you need to solve them. "
        f"Note: Use the PEMDAS rule for solving mathematical expressions."
        f"YOU CAN HAVE FIVE TYPES OF EQUATIONS/EXPRESSIONS IN THIS IMAGE, AND ONLY ONE CASE SHALL APPLY EVERY TIME: "
        f"1. Simple mathematical expressions like 2 + 2, 3 * 4, 5 / 6, 7 - 8, etc.: In this case, solve and return the answer in the format of a LIST OF ONE DICT [{{'expr': given expression, 'steps':step by step solution to the problem ,'result': calculated answer}}]. "
        f"2. Set of Equations like x^2 + 2x + 1 = 0, 3y + 4x = 0, 5x^2 + 6y + 7 = 12, etc.: In this case, solve for the given variable, and the format should be a COMMA SEPARATED LIST OF DICTS, with dict 1 as {{'expr': 'x', 'result': 2, 'assign': True}} and dict 2 as {{'expr': 'y', 'result': 5, 'assign': True}}. "
        f"3. Assigning values to variables like x = 4, y = 5, z = 6, etc.: In this case, assign values to variables and return another key in the dict called {{'assign': True}}, keeping the variable as 'expr' and the value as 'result' in the original dictionary. RETURN AS A LIST OF DICTS. "
        f"4. Analyzing Graphical Math problems, which are word problems represented in drawing form, such as cars colliding, trigonometric problems, problems on the Pythagorean theorem, adding runs from a cricket wagon wheel, etc. You need to return the answer in the format of a LIST OF ONE DICT [{{'expr': given expression, 'steps': step by step solution to the problem(do not use latex syntax at all just use the normal text code instead) ,'result': calculated answer}}]. "
        f"5. Detecting Abstract Concepts that a drawing might show, such as love, hate, jealousy, patriotism, etc. USE THE SAME FORMAT AS OTHERS TO RETURN THE ANSWER, where 'expr' will be the explanation of the drawing, and 'result' will be the abstract concept. "
        f"Here is a dictionary of user-assigned variables. If the given expression has any of these variables, use its actual value from this dictionary accordingly: {dict_of_vars_str}. "
        f"DO NOT USE BACKTICKS OR MARKDOWN FORMATTING. "
        f"PROPERLY QUOTE THE KEYS AND VALUES IN THE DICTIONARY FOR EASIER PARSING WITH Python's ast.literal_eval."
    )

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_bytes(mime_type="image/png", data=img_byte_arr),
                types.Part.from_text(text=sys_prompt)
            ]
        )
    ]

    try:
        generate_content_config = types.GenerateContentConfig(response_mime_type="application/json")
        response = gemini_client.models.generate_content(
            model="gemini-flash-lite-latest",
            contents=contents,
            config=generate_content_config
        )
        answers = ast.literal_eval(response.text)
        
        for answer in answers:
            if 'assign' in answer:
                answer['assign'] = True
            else:
                answer['assign'] = False
                
        return answers
    except Exception as e:
        print(f"Error parsing Gemini response: {e}")
        raise AIAnalysisError(detail=f"Error parsing Gemini response: {str(e)}")
