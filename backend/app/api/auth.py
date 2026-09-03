from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.models.models import User
from app.schemas.schemas import LoginRequest, Token, UserCreate, UserResponse
from app.api.deps import get_current_user
from app.audit.audit_service import AuditService

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter((User.email == user_in.email) | (User.username == user_in.username)).first()
    if existing:
        raise HTTPException(status_code=400, detail="User with this email or username already exists")
    
    user = User(
        name=user_in.name,
        email=user_in.email,
        username=user_in.username,
        password_hash=get_password_hash(user_in.password),
        role=user_in.role.upper(),
        department=user_in.department or "GeM Central Procurement Cell"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    AuditService.log_action(
        db=db,
        action="USER_REGISTERED",
        entity_type="USER",
        entity_id=user.id,
        user_id=user.id,
        user_name=user.name,
        new_state={"email": user.email, "role": user.role},
        reason=f"Registered new user {user.username} with role {user.role}"
    )

    return user

@router.post("/login", response_model=Token)
def login(login_req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(
        (User.username == login_req.username_or_email) | (User.email == login_req.username_or_email)
    ).first()
    
    if not user or not verify_password(login_req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username/email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user account")

    access_token = create_access_token(data={"sub": user.username, "role": user.role, "uid": user.id})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
