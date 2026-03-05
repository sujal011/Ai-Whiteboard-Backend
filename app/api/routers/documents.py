import os
import shutil
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from app.db.session import get_db, engine
from app.models.user import User
from app.models.workspace import Workspace
from app.models.document import Document
from app.schemas.document import DocumentResponse
from app.api.deps import get_current_user
from app.core.config import settings

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector
from langchain_postgres.vectorstores import PGVector

router = APIRouter()

# Setup Vector Store
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=settings.GEMINI_API_KEY)
vectorstore = PGVector(
    embeddings=embeddings,
    collection_name="workspace_documents",
    connection=settings.DATABASE_URL,
    use_jsonb=True,
)

@router.post("/{workspace_id}/documents", response_model=DocumentResponse)
async def upload_document(
    workspace_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify workspace belongs to user
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id, Workspace.user_id == current_user.id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
        
    # Save file temporarily
    temp_dir = f"temp_docs_{workspace_id}"
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        # Load and parse document
        if file.filename.endswith(".pdf"):
            loader = PyPDFLoader(file_path)
        elif file.filename.endswith(".txt"):
            loader = TextLoader(file_path)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")
            
        docs = loader.load()
        
        # Split document
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(docs)
        
        # Add metadata for filtering
        for split in splits:
            split.metadata["workspace_id"] = workspace_id
            split.metadata["filename"] = file.filename
            
        # Add to vectorstore
        vectorstore.add_documents(splits)
        
        # Save document record to relational DB
        db_doc = Document(
            workspace_id=workspace_id,
            filename=file.filename,
            file_type=file.filename.split(".")[-1]
        )
        db.add(db_doc)
        db.commit()
        db.refresh(db_doc)
        
        return db_doc
        
    finally:
        # Cleanup temp file
        if os.path.exists(file_path):
            os.remove(file_path)

@router.get("/{workspace_id}/documents", response_model=List[DocumentResponse])
def get_documents(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id, Workspace.user_id == current_user.id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
        
    documents = db.query(Document).filter(Document.workspace_id == workspace_id).all()
    return documents
