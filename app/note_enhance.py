import os
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
# Load environment variables
load_dotenv()

# Retrieve Groq API key from environment variables
groq_api_key = os.getenv("GROQ_API")

# Initialize the LLM with ChatGroq
llm = ChatGroq(
    temperature=0.7,
    groq_api_key=groq_api_key,
    model_name="llama-3.2-90b-text-preview"
).with_structured_output(dict, method="json_mode")

prompt_template = ChatPromptTemplate([
    ("system", """
     You are a helpful assistant that respond with the as short as answer to the question if the answer is within one-two words or numbers (if mathematical expresions or equations asked)
     Note : when asked to create/generate a checklist of topic use this syntax with markdown syntax : 
     - [ ] Unchecked item
     Note: when asked to write/generate code then write a enclosed your answer withing ``` & ```
     Remember to respond only in the json format : 
     {{
         result:"<You short answer inn the markdown format>"
     }}
     """),
    ("user", "{question}")
])

def get_llm():
    llm_chain = prompt_template | llm
    return llm_chain
