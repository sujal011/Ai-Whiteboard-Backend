import os
import shutil
from typing import List
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.models.document import Document
from app.services.workspace_service import get_workspace
from app.rag.vectorstore import get_vectorstore
from app.core.logging import setup_logger
from app.core.exceptions import UnsupportedFileTypeError

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = setup_logger(__name__)

def process_and_save_document(db: Session, workspace_id: int, user_id: int, file: UploadFile) -> Document:
    logger.info(f"Processing document upload '{file.filename}' for workspace_id: {workspace_id}")
    
    # Verify workspace ownership first
    get_workspace(db, workspace_id, user_id)
    
    temp_dir = f"temp_docs_{workspace_id}"
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, file.filename)
    
    try:
        # Save temp file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        logger.info(f"Saved temp file to {file_path}")
        
        # Load and parse document
        if file.filename.endswith(".pdf"):
            loader = PyPDFLoader(file_path)
            logger.info("Using PyPDFLoader")
        elif file.filename.endswith(".txt") or file.filename.endswith(".md"):
            loader = TextLoader(file_path)
            logger.info("Using TextLoader")
        else:
            logger.error(f"Unsupported file type: {file.filename}")
            raise UnsupportedFileTypeError(detail=f"Unsupported file type: {file.filename}")
            
        docs = loader.load()
        logger.info(f"Loaded {len(docs)} pages/sections from document.")
        
        # Split document
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(docs)
        logger.info(f"Split document into {len(splits)} chunks.")
        
        # Add metadata for filtering
        for split in splits:
            split.metadata["workspace_id"] = workspace_id
            split.metadata["filename"] = file.filename
            
        # Add to vectorstore
        logger.info("Generating embeddings and adding to PGVector...")
        get_vectorstore().add_documents(splits)
        
        # Save document record to relational DB
        db_doc = Document(
            workspace_id=workspace_id,
            filename=file.filename,
            file_type=file.filename.split(".")[-1]
        )
        db.add(db_doc)
        db.commit()
        db.refresh(db_doc)
        
        logger.info(f"Successfully processed document id: {db_doc.id}")
        return db_doc
        
    finally:
        # Cleanup temp file
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Cleaned up temp file: {file_path}")

def get_documents_by_workspace(db: Session, workspace_id: int, user_id: int) -> List[Document]:
    logger.info(f"Fetching documents for workspace_id: {workspace_id}")
    # Verify workspace ownership
    get_workspace(db, workspace_id, user_id)
    return db.query(Document).filter(Document.workspace_id == workspace_id).all()
