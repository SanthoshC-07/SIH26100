from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_password_hash
from app.models.models import User
from app.schemas.schemas import UserCreate, UserResponse, UserUpdate
from app.api.deps import require_role, get_current_user
from app.audit.audit_service import AuditService

router = APIRouter(prefix="/users", tags=["User Administration (Admin Only)"])

VALID_ROLES = {"ADMIN", "PROCUREMENT_OFFICER", "BIDDER"}

@router.get("", response_model=List[UserResponse])
def list_users(
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_role("ADMIN"))
):
    """
    Returns registered system users. Administrator access required.
    """
    query = db.query(User)
    if role:
        query = query.filter(User.role == role.upper())
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    if search:
        s_pat = f"%{search}%"
        query = query.filter(
            (User.name.ilike(s_pat)) |
            (User.username.ilike(s_pat)) |
            (User.email.ilike(s_pat))
        )
    return query.order_by(User.created_at.desc()).offset(offset).limit(limit).all()

@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_role("ADMIN"))
):
    """
    Creates a new user with designated role (ADMIN, PROCUREMENT_OFFICER, BIDDER).
    Administrator access required.
    """
    assigned_role = user_in.role.upper() if user_in.role else "PROCUREMENT_OFFICER"
    if assigned_role not in VALID_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role '{assigned_role}'. Role must be one of: {', '.join(sorted(VALID_ROLES))}."
        )

    existing = db.query(User).filter(
        (User.email == user_in.email) | (User.username == user_in.username)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="User with this email or username already exists")

    new_user = User(
        name=user_in.name,
        email=user_in.email,
        username=user_in.username,
        password_hash=get_password_hash(user_in.password),
        role=assigned_role,
        department=user_in.department or "Ministry of Petroleum & Natural Gas",
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    AuditService.log_event(
        db=db,
        action="USER_REGISTERED",
        entity_type="USER",
        entity_id=new_user.id,
        user_id=current_admin.id,
        user_name=current_admin.name,
        role=current_admin.role,
        description=f"Admin {current_admin.username} created user {new_user.username} with role {new_user.role}"
    )

    return new_user

@router.get("/{id}", response_model=UserResponse)
def get_user(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Inspects user record. Accessible by Administrator or self.
    """
    if current_user.role != "ADMIN" and current_user.id != id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.patch("/{id}", response_model=UserResponse)
def update_user(
    id: str,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_role("ADMIN"))
):
    """
    Updates user account: assigns roles, activates/deactivates, updates department.
    Administrator access required.
    """
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user_update.role is not None:
        new_role = user_update.role.upper()
        if new_role not in VALID_ROLES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role '{new_role}'. Role must be one of: {', '.join(sorted(VALID_ROLES))}."
            )
        user.role = new_role

    if user_update.name is not None:
        user.name = user_update.name
    if user_update.department is not None:
        user.department = user_update.department
    if user_update.is_active is not None:
        user.is_active = user_update.is_active
    if user_update.bidder_id is not None:
        user.bidder_id = user_update.bidder_id

    db.commit()
    db.refresh(user)

    AuditService.log_event(
        db=db,
        action="USER_UPDATED",
        entity_type="USER",
        entity_id=user.id,
        user_id=current_admin.id,
        user_name=current_admin.name,
        role=current_admin.role,
        description=f"Admin {current_admin.username} updated user {user.username} (role={user.role}, active={user.is_active})"
    )

    return user

@router.delete("/{id}")
def deactivate_user(
    id: str,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_role("ADMIN"))
):
    """
    Deactivates user account. Administrator access required.
    """
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.id == current_admin.id:
        raise HTTPException(status_code=400, detail="Cannot deactivate own administrator account.")

    user.is_active = False
    db.commit()

    AuditService.log_event(
        db=db,
        action="USER_DEACTIVATED",
        entity_type="USER",
        entity_id=user.id,
        user_id=current_admin.id,
        user_name=current_admin.name,
        role=current_admin.role,
        description=f"Admin {current_admin.username} deactivated user {user.username}"
    )

    return {"status": "ok", "message": f"User {user.username} successfully deactivated."}
