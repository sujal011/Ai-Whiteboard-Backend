from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import UserCreate, UserResponse
from app.schemas.token import Token
from app.services import auth_service
from app.core.logging import setup_logger

logger = setup_logger(__name__)
router = APIRouter()

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    logger.info("Received request to /signup endpoint.")
    return auth_service.create_user(db=db, user_in=user_in)

@router.post("/login", response_model=Token)
def login_access_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
):
    logger.info("Received request to /login endpoint.")
    return auth_service.authenticate_user(db=db, email=form_data.username, password=form_data.password)
