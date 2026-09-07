from typing import Optional, List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.models import User, Bidder, Bid

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

def get_current_user(
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme)
) -> User:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token required. Please sign in.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    username: str = payload.get("sub")
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
        
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User account not found")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user account")
    
    # If bidder user without bidder_id, attempt auto-resolution
    if user.role == "BIDDER" and not user.bidder_id:
        linked_bidder = db.query(Bidder).filter(
            (Bidder.user_id == user.id) | (Bidder.email == user.email)
        ).first()
        if linked_bidder:
            user.bidder_id = linked_bidder.id
            if not linked_bidder.user_id:
                linked_bidder.user_id = user.id
            db.commit()

    return user

def get_current_user_optional(
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme)
) -> Optional[User]:
    if not token:
        return None
    try:
        payload = decode_access_token(token)
        if not payload:
            return None
        username: str = payload.get("sub")
        if not username:
            return None
        user = db.query(User).filter(User.username == username).first()
        if not user or not user.is_active:
            return None
        if user.role == "BIDDER" and not user.bidder_id:
            linked_bidder = db.query(Bidder).filter(
                (Bidder.user_id == user.id) | (Bidder.email == user.email)
            ).first()
            if linked_bidder:
                user.bidder_id = linked_bidder.id
                if not linked_bidder.user_id:
                    linked_bidder.user_id = user.id
                db.commit()
        return user
    except Exception:
        return None

def require_role(required_role: str):
    def role_dependency(current_user: User = Depends(get_current_user)) -> User:
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication token required. Please sign in."
            )
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied."
            )
        return current_user
    return role_dependency

def require_any_role(*allowed_roles: str):
    def role_dependency(current_user: User = Depends(get_current_user)) -> User:
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication token required. Please sign in."
            )
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied."
            )
        return current_user
    return role_dependency

def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied."
        )
    return current_user

def get_current_officer(
    current_user: User = Depends(get_current_user)
) -> User:
    if current_user.role not in ["PROCUREMENT_OFFICER", "ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied."
        )
    return current_user

def get_current_officer_only(
    current_user: User = Depends(get_current_user)
) -> User:
    if current_user.role != "PROCUREMENT_OFFICER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied."
        )
    return current_user

def get_current_bidder(
    current_user: User = Depends(get_current_user)
) -> User:
    if current_user.role != "BIDDER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied."
        )
    return current_user

def verify_bidder_ownership(bidder_id: str, current_user: User, db: Session) -> Bidder:
    """
    Object-level authorization check.
    Procurement Officers and Admins can access all bidders according to permissions.
    Bidders can ONLY access their own registered bidder record.
    """
    bidder = db.query(Bidder).filter(Bidder.id == bidder_id).first()
    if not bidder:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bidder not found")

    if current_user and current_user.role == "BIDDER":
        effective_id = current_user.effective_bidder_id
        if not effective_id or bidder.id != effective_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied."
            )
    return bidder

def verify_bid_ownership(bid_id: str, current_user: User, db: Session) -> Bid:
    """
    Object-level authorization check for formal bids.
    A BIDDER may access a bid ONLY if: bid.bidder_id == current_user.bidder_id.
    Otherwise strictly returns HTTP 403 Forbidden ("Access denied.").
    """
    bid = db.query(Bid).filter(Bid.id == bid_id).first()
    if not bid:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bid not found")

    if current_user and current_user.role == "BIDDER":
        if bid.bidder_id != current_user.bidder_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied."
            )
    return bid
