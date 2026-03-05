from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import auth, workspaces, documents, chat

app = FastAPI(title="AI Whiteboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://ai-whiteboard.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(workspaces.router, prefix="/api/workspaces", tags=["workspaces"])
app.include_router(documents.router, prefix="/api/workspaces", tags=["documents"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])

@app.get("/")
def read_root():
    return {"message": "Welcome to AI Whiteboard Backend"}
