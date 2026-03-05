from typing import Optional, Dict, Any
from pydantic import BaseModel

class WorkspaceBase(BaseModel):
    name: str
    excalidraw_data: Optional[Dict[str, Any]] = None
    editorjs_data: Optional[Dict[str, Any]] = None

class WorkspaceCreate(BaseModel):
    name: str

class WorkspaceUpdate(BaseModel):
    name: Optional[str] = None
    excalidraw_data: Optional[Dict[str, Any]] = None
    editorjs_data: Optional[Dict[str, Any]] = None

class WorkspaceResponse(WorkspaceBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
