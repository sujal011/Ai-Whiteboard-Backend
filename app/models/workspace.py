from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Workspace(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    
    excalidraw_data = Column(JSON, nullable=True)
    editorjs_data = Column(JSON, nullable=True)

    owner = relationship("User", backref="workspaces")
