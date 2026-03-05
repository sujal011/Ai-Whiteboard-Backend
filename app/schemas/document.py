from pydantic import BaseModel

class DocumentBase(BaseModel):
    filename: str
    file_type: str

class DocumentCreate(DocumentBase):
    pass

class DocumentResponse(DocumentBase):
    id: int
    workspace_id: int

    class Config:
        from_attributes = True
