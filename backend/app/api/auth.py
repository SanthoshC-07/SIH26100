from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token, decode_access_token
from app.models.models import User
from app.schemas.schemas import LoginRequest, Token, UserCreate, UserResponse
from app.api.deps import get_current_user, oauth2_scheme
from app.audit.audit_service import AuditService

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse)
def register_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme)
):
    existing = db.query(User).filter((User.email == user_in.email) | (User.username == user_in.username)).first()
    if existing:
        raise HTTPException(status_code=400, detail="User with this email or username already exists")

    # Determine assigned role: only an authenticated Admin can assign ADMIN or PROCUREMENT_OFFICER
    assigned_role = "BIDDER"
    if token:
        try:
            payload = decode_access_token(token)
            if payload and payload.get("role") == "ADMIN":
                requested_role = (user_in.role or "BIDDER").upper()
                if requested_role in {"ADMIN", "PROCUREMENT_OFFICER", "BIDDER"}:
                    assigned_role = requested_role
        except Exception:
            pass
    
    user = User(
        name=user_in.name,
        email=user_in.email,
        username=user_in.username,
        password_hash=get_password_hash(user_in.password),
        role=assigned_role,
        department=user_in.department or ("GeM Bidder Portal" if assigned_role == "BIDDER" else "GeM Central Procurement Cell")
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
    ident = login_req.identifier
    user = db.query(User).filter(
        (User.username == ident) | (User.email == ident)
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

    # Log LOGIN audit event
    AuditService.log_event(
        db=db,
        action="LOGIN",
        entity_type="USER",
        entity_id=user.id,
        user_id=user.id,
        user_name=user.name or user.username,
        role=user.role,
        description=f"User {user.username} successfully signed in with role {user.role}",
        metadata={"email": user.email, "role": user.role}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.post("/logout")
def logout(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    AuditService.log_event(
        db=db,
        action="LOGOUT",
        entity_type="USER",
        entity_id=current_user.id,
        user_id=current_user.id,
        user_name=current_user.name or current_user.username,
        role=current_user.role,
        description=f"User {current_user.username} signed out",
        metadata={"email": current_user.email}
    )
    return {"status": "ok", "message": "Successfully logged out"}

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
