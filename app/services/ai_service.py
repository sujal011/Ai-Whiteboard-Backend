import os
import base64
import logging
from io import BytesIO
from PIL import Image
import json
import ast

logger = logging.getLogger(__name__)

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector


from app.core.config import settings
from app.api.deps import get_db
from app.core.exceptions import AIAnalysisError

# Ensure GOOGLE_API_KEY is set for langchain-google-genai
if not os.environ.get("GOOGLE_API_KEY") and settings.GEMINI_API_KEY:
    os.environ["GOOGLE_API_KEY"] = settings.GEMINI_API_KEY

# LLM setup
groq_llm = ChatGroq(
    model_name="qwen/qwen3-32b",
    groq_api_key=settings.GROQ_API_KEY
)

gemini_llm = ChatGoogleGenerativeAI(
    model="gemini-flash-lite-latest",
)

from app.rag.vectorstore import get_vectorstore

def generate_mermaid_syntax(prompt: str) -> str:
    # ── Primary: deepagents-powered mermaid agent ──
    try:
        from app.services.mermaid_agent_service import generate_mermaid_with_agent
        return generate_mermaid_with_agent(prompt)
    except Exception as e:
        logger.warning("DeepAgent mermaid generation failed, falling back to direct LLM: %s", e)

    # ── Fallback: direct Gemini/Groq call ──
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
        chain = gemini_llm.with_structured_output(dict, method="json_mode")
        response = chain.invoke([
            SystemMessage(content=gemini_prompt),
            HumanMessage(content=prompt),
        ])
        return response.get("mermaid_syntax")
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

    # Encode image as base64 data URL for langchain multimodal
    img_b64 = base64.b64encode(img_byte_arr).decode("utf-8")
    image_url = f"data:image/png;base64,{img_b64}"

    message = HumanMessage(
        content=[
            {"type": "image_url", "image_url": {"url": image_url}},
            {"type": "text", "text": sys_prompt},
        ]
    )

    try:
        response = gemini_llm.invoke([message])
        answers = ast.literal_eval(response.content)
        
        for answer in answers:
            if 'assign' in answer:
                answer['assign'] = True
            else:
                answer['assign'] = False
                
        return answers
    except Exception as e:
        print(f"Error parsing Gemini response: {e}")
        raise AIAnalysisError(detail=f"Error parsing Gemini response: {str(e)}")
