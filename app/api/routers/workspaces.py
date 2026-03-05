from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.models.workspace import Workspace
from app.schemas.workspace import WorkspaceCreate, WorkspaceUpdate, WorkspaceResponse
from app.api.deps import get_current_user

router = APIRouter()

@router.post("/", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
def create_workspace(
    *,
    db: Session = Depends(get_db),
    workspace_in: WorkspaceCreate,
    current_user: User = Depends(get_current_user)
):
    workspace = Workspace(
        name=workspace_in.name,
        user_id=current_user.id
    )
    db.add(workspace)
    db.commit()
    db.refresh(workspace)
    return workspace

@router.get("/", response_model=List[WorkspaceResponse])
def read_workspaces(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    workspaces = db.query(Workspace).filter(Workspace.user_id == current_user.id).offset(skip).limit(limit).all()
    return workspaces

@router.get("/{id}", response_model=WorkspaceResponse)
def read_workspace(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user: User = Depends(get_current_user)
):
    workspace = db.query(Workspace).filter(Workspace.id == id, Workspace.user_id == current_user.id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return workspace

@router.put("/{id}", response_model=WorkspaceResponse)
def update_workspace(
    *,
    db: Session = Depends(get_db),
    id: int,
    workspace_in: WorkspaceUpdate,
    current_user: User = Depends(get_current_user)
):
    workspace = db.query(Workspace).filter(Workspace.id == id, Workspace.user_id == current_user.id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    update_data = workspace_in.dict(exclude_unset=True)
    for field in update_data:
        setattr(workspace, field, update_data[field])
        
    db.add(workspace)
    db.commit()
    db.refresh(workspace)
    return workspace

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workspace(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user: User = Depends(get_current_user)
):
    workspace = db.query(Workspace).filter(Workspace.id == id, Workspace.user_id == current_user.id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    db.delete(workspace)
    db.commit()
    return None
