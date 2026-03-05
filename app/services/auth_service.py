from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import timedelta

from app.models.user import User
from app.schemas.user import UserCreate
from app.core import security
from app.core.config import settings
from app.core.logging import setup_logger

logger = setup_logger(__name__)

def create_user(db: Session, user_in: UserCreate) -> User:
    logger.info(f"Attempting to create user with email: {user_in.email}")
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        logger.warning(f"Registration failed: User with email {user_in.email} already exists.")
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    
    hashed_password = security.get_password_hash(user_in.password)
    db_user = User(email=user_in.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    logger.info(f"Successfully created user with id: {db_user.id}")
    return db_user

def authenticate_user(db: Session, email: str, password: str) -> dict:
    logger.info(f"Authenticating user with email: {email}")
    user = db.query(User).filter(User.email == email).first()
    if not user or not security.verify_password(password, user.hashed_password):
        logger.warning(f"Authentication failed for user: {email}")
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        user.id, expires_delta=access_token_expires
    )
    logger.info(f"Authentication successful for user id: {user.id}")
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }
