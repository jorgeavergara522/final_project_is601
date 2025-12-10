from contextlib import asynccontextmanager
from datetime import datetime, timezone, timedelta
from uuid import UUID
from typing import List
import os

from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    status,
    Request,
)
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_active_user
from app.auth.jwt import create_token
from app.schemas.token import TokenType, TokenResponse
from app.models.calculation import Calculation
from app.models.user import User
from app.schemas.calculation import (
    CalculationBase,
    CalculationResponse,
    CalculationUpdate,
)
from app.schemas.user import UserCreate, UserResponse, UserLogin
from app.database import Base, get_db, engine


# --------------------------------------------------------------------------
# Lifespan: create tables at startup
# --------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Only reset DB when running actual E2E tests with a live server
    # Integration tests manage their own DB through fixtures
    if os.getenv("E2E_TESTS") and not os.getenv("PYTEST_CURRENT_TEST"):
        print("⚠️ E2E MODE - Resetting database")
        db_file = "./test.db"
        if os.path.exists(db_file):
            print("🧨 Removing stale test.db")
            os.remove(db_file)
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
    else:
        # Normal startup or pytest - just ensure tables exist
        Base.metadata.create_all(bind=engine)
    
    yield

# --------------------------------------------------------------------------
# Create FastAPI app with lifespan
# --------------------------------------------------------------------------
app = FastAPI(lifespan=lifespan)


# --------------------------------------------------------------------------
# Static files and templates
# --------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "..", "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "..", "templates")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


# --------------------------------------------------------------------------
# Web (HTML) routes
# --------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse, tags=["web"])
def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/login", response_class=HTMLResponse, tags=["web"])
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register", response_class=HTMLResponse, tags=["web"])
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/dashboard", response_class=HTMLResponse, tags=["web"])
def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/dashboard/view/{calc_id}", response_class=HTMLResponse, tags=["web"])
def view_calculation_page(request: Request, calc_id: str):
    return templates.TemplateResponse(
        "view_calculation.html", {"request": request, "calc_id": calc_id}
    )


@app.get("/dashboard/edit/{calc_id}", response_class=HTMLResponse, tags=["web"])
def edit_calculation_page(request: Request, calc_id: str):
    return templates.TemplateResponse(
        "edit_calculation.html", {"request": request, "calc_id": calc_id}
    )


# --------------------------------------------------------------------------
# Health endpoint
# --------------------------------------------------------------------------
@app.get("/health", tags=["health"])
def read_health():
    return {"status": "ok"}


# --------------------------------------------------------------------------
# Auth: registration
# --------------------------------------------------------------------------
@app.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["auth"])
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered"
        )
    
    # Register user
    user = User.register(db, user_data.dict())
    db.commit()
    db.refresh(user)
    
    return user


# --------------------------------------------------------------------------
# Auth: JSON login
# --------------------------------------------------------------------------
@app.post("/auth/login", response_model=TokenResponse, tags=["auth"])
def login_json(user_login: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate using username/password.
    Return TokenResponse exactly as tests expect.
    """
    user = User.authenticate(db, user_login.username, user_login.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create tokens
    access_token = create_token(
        user_id_or_data=str(user.id),
        token_type=TokenType.ACCESS,
        username=user.username,
    )

    refresh_token = create_token(
        user_id_or_data=str(user.id),
        token_type=TokenType.REFRESH,
        username=user.username,
    )

    # Tests expect a timezone-aware expires_at
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_at=expires_at,
        user_id=user.id,
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        is_active=user.is_active,
        is_verified=user.is_verified,
    )


# --------------------------------------------------------------------------
# Auth: form login (Swagger / OAuth2PasswordRequestForm)
# --------------------------------------------------------------------------
@app.post("/auth/token", tags=["auth"])
def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """OAuth2 compatible token login (for Swagger UI)."""
    user = User.authenticate(db, form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token = create_token(
        user_id_or_data=str(user.id),
        token_type=TokenType.ACCESS,
        username=user.username,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


# --------------------------------------------------------------------------
# Calculations API (BREAD)
# --------------------------------------------------------------------------
@app.post(
    "/calculations",
    response_model=CalculationResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["calculations"],
)
def create_calculation(
    calculation_data: CalculationBase,
    current_user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    try:
        new_calculation = Calculation.create(
            calculation_type=calculation_data.type,
            user_id=current_user.id,
            inputs=calculation_data.inputs,
        )
        new_calculation.result = new_calculation.get_result()

        db.add(new_calculation)
        db.commit()
        db.refresh(new_calculation)
        return new_calculation
    except ValueError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@app.get(
    "/calculations",
    response_model=List[CalculationResponse],
    tags=["calculations"],
)
def list_calculations(
    current_user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    calculations = (
        db.query(Calculation)
        .filter(Calculation.user_id == current_user.id)
        .all()
    )
    return calculations


@app.get(
    "/calculations/{calc_id}",
    response_model=CalculationResponse,
    tags=["calculations"],
)
def get_calculation(
    calc_id: str,
    current_user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    try:
        calc_uuid = UUID(calc_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid calculation id format.")

    calculation = (
        db.query(Calculation)
        .filter(
            Calculation.id == calc_uuid,
            Calculation.user_id == current_user.id,
        )
        .first()
    )
    if not calculation:
        raise HTTPException(status_code=404, detail="Calculation not found.")

    return calculation


@app.put(
    "/calculations/{calc_id}",
    response_model=CalculationResponse,
    tags=["calculations"],
)
def update_calculation(
    calc_id: str,
    calculation_update: CalculationUpdate,
    current_user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    try:
        calc_uuid = UUID(calc_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid calculation id format.")

    calculation = (
        db.query(Calculation)
        .filter(
            Calculation.id == calc_uuid,
            Calculation.user_id == current_user.id,
        )
        .first()
    )
    if not calculation:
        raise HTTPException(status_code=404, detail="Calculation not found.")

    if calculation_update.inputs is not None:
        calculation.inputs = calculation_update.inputs
        calculation.result = calculation.get_result()

    calculation.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(calculation)
    return calculation


@app.delete(
    "/calculations/{calc_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["calculations"],
)
def delete_calculation(
    calc_id: str,
    current_user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    try:
        calc_uuid = UUID(calc_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid calculation id format.")

    calculation = (
        db.query(Calculation)
        .filter(
            Calculation.id == calc_uuid,
            Calculation.user_id == current_user.id,
        )
        .first()
    )
    if not calculation:
        raise HTTPException(status_code=404, detail="Calculation not found.")

    db.delete(calculation)
    db.commit()
    return None


if __name__ == "__main__":
    import uvic