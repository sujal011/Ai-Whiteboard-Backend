from typing import List
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.document import DocumentResponse
from app.api.deps import get_current_user
from app.services import document_service
from app.core.logging import setup_logger

logger = setup_logger(__name__)
router = APIRouter()

@router.post("/{workspace_id}/documents", response_model=DocumentResponse)
async def upload_document(
    workspace_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    logger.info(f"Received request to upload document to workspace id: {workspace_id}.")
    return document_service.process_and_save_document(db=db, workspace_id=workspace_id, user_id=current_user.id, file=file)

@router.get("/{workspace_id}/documents", response_model=List[DocumentResponse])
def get_documents(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    logger.info(f"Received request to retrieve documents for workspace id: {workspace_id}.")
    return document_service.get_documents_by_workspace(db=db, workspace_id=workspace_id, user_id=current_user.id)
