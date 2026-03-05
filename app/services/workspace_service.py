from typing import List
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.workspace import Workspace
from app.schemas.workspace import WorkspaceCreate, WorkspaceUpdate
from app.core.logging import setup_logger

logger = setup_logger(__name__)

def create_workspace(db: Session, workspace_in: WorkspaceCreate, user_id: int) -> Workspace:
    logger.info(f"Creating new workspace '{workspace_in.name}' for user_id: {user_id}")
    workspace = Workspace(
        name=workspace_in.name,
        user_id=user_id
    )
    db.add(workspace)
    db.commit()
    db.refresh(workspace)
    logger.info(f"Successfully created workspace id: {workspace.id}")
    return workspace

def get_workspaces(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Workspace]:
    logger.info(f"Fetching workspaces for user_id: {user_id} (skip={skip}, limit={limit})")
    return db.query(Workspace).filter(Workspace.user_id == user_id).offset(skip).limit(limit).all()

def get_workspace(db: Session, workspace_id: int, user_id: int) -> Workspace:
    logger.info(f"Fetching workspace id: {workspace_id} for user_id: {user_id}")
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id, Workspace.user_id == user_id).first()
    if not workspace:
        logger.warning(f"Workspace id: {workspace_id} not found or unauthorized for user_id: {user_id}")
        raise HTTPException(status_code=404, detail="Workspace not found")
    return workspace

def update_workspace(db: Session, workspace_id: int, workspace_in: WorkspaceUpdate, user_id: int) -> Workspace:
    logger.info(f"Updating workspace id: {workspace_id} for user_id: {user_id}")
    workspace = get_workspace(db, workspace_id, user_id)
    
    update_data = workspace_in.dict(exclude_unset=True)
    for field in update_data:
        setattr(workspace, field, update_data[field])
        
    db.add(workspace)
    db.commit()
    db.refresh(workspace)
    logger.info(f"Successfully updated workspace id: {workspace.id}")
    return workspace

def delete_workspace(db: Session, workspace_id: int, user_id: int) -> None:
    logger.info(f"Deleting workspace id: {workspace_id} for user_id: {user_id}")
    workspace = get_workspace(db, workspace_id, user_id)
    db.delete(workspace)
    db.commit()
    logger.info(f"Successfully deleted workspace id: {workspace_id}")
