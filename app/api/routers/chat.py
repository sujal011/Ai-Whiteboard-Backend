from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.api.deps import get_current_user
from app.schemas.chat import GenerateRequest, AskRequest, GeneralRequest, ChatResponse
from app.services.ai_service import generate_mermaid_syntax, answer_from_documents, analyze_excalidraw_image

router = APIRouter()

@router.post("/generate", response_model=ChatResponse)
def api_generate_diagram(
    request: GenerateRequest,
    current_user: User = Depends(get_current_user)
):
    try:
        mermaid_syntax = generate_mermaid_syntax(request.prompt)
        return {"result": mermaid_syntax}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ask", response_model=ChatResponse)
def api_ask_documents(
    request: AskRequest,
    current_user: User = Depends(get_current_user)
):
    try:
        answer = answer_from_documents(request.question, request.workspace_id)
        return {"result": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/general", response_model=ChatResponse)
def api_general_chat(
    request: GeneralRequest,
    current_user: User = Depends(get_current_user)
):
    try:
        if request.image_base64:
            result = analyze_excalidraw_image(request.image_base64, request.dict_of_vars, request.prompt)
            return {"result": result}
        else:
            # Simple text completion
            from app.services.ai_service import gemini_llm
            response = gemini_llm.invoke(request.prompt)
            return {"result": response.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
