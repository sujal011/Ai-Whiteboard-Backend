from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.workspace import WorkspaceCreate, WorkspaceUpdate, WorkspaceResponse
from app.api.deps import get_current_user
from app.services import workspace_service
from app.core.logging import setup_logger

logger = setup_logger(__name__)
router = APIRouter()

@router.post("/", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
def create_workspace(
    *,
    db: Session = Depends(get_db),
    workspace_in: WorkspaceCreate,
    current_user: User = Depends(get_current_user)
):
    logger.info("Received request to create a workspace.")
    return workspace_service.create_workspace(db=db, workspace_in=workspace_in, user_id=current_user.id)

@router.get("/", response_model=List[WorkspaceResponse])
def read_workspaces(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    logger.info("Received request to retrieve all workspaces.")
    return workspace_service.get_workspaces(db=db, user_id=current_user.id, skip=skip, limit=limit)

@router.get("/{id}", response_model=WorkspaceResponse)
def read_workspace(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user: User = Depends(get_current_user)
):
    logger.info(f"Received request to retrieve workspace id: {id}.")
    return workspace_service.get_workspace(db=db, workspace_id=id, user_id=current_user.id)

@router.put("/{id}", response_model=WorkspaceResponse)
def update_workspace(
    *,
    db: Session = Depends(get_db),
    id: int,
    workspace_in: WorkspaceUpdate,
    current_user: User = Depends(get_current_user)
):
    logger.info(f"Received request to update workspace id: {id}.")
    return workspace_service.update_workspace(db=db, workspace_id=id, workspace_in=workspace_in, user_id=current_user.id)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workspace(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user: User = Depends(get_current_user)
):
    logger.info(f"Received request to delete workspace id: {id}.")
    workspace_service.delete_workspace(db=db, workspace_id=id, user_id=current_user.id)
    return None
