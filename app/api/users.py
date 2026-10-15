from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from app.models.schemas import UserResponse, UserCreate, UserUpdate
from app.core.security import require_role, get_password_hash
from app.db.session import get_db

router = APIRouter(prefix="/users", tags=["User & Role Management"])

@router.get("", response_model=dict)
def list_users(current_user: dict = Depends(require_role(["Administrator", "Auditor", "Reviewer"]))):
    """Lists all enterprise system users and their assigned RBAC roles."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, full_name, email, role, status FROM users ORDER BY id ASC")
        rows = cursor.fetchall()
        users = [
            UserResponse(
                user_id=r["user_id"],
                full_name=r["full_name"],
                email=r["email"],
                role=r["role"],
                status=r["status"]
            ).model_dump()
            for r in rows
        ]
        return {"users": users}

@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate, current_user: dict = Depends(require_role(["Administrator"]))):
    """Creates a new enterprise user with designated RBAC role."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ?", (user_data.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="User with this email already exists")
        
        cursor.execute("SELECT COUNT(*) as count FROM users")
        count = cursor.fetchone()["count"] + 1
        user_id = f"USR-{count:03d}"
        
        hashed_pwd = get_password_hash(user_data.password)
        cursor.execute(
            "INSERT INTO users (user_id, full_name, email, hashed_password, role, status) VALUES (?, ?, ?, ?, ?, 'Active')",
            (user_id, user_data.full_name, user_data.email, hashed_pwd, user_data.role)
        )
        
        return UserResponse(
            user_id=user_id,
            full_name=user_data.full_name,
            email=user_data.email,
            role=user_data.role,
            status="Active"
        )

@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: str, user_data: UserUpdate, current_user: dict = Depends(require_role(["Administrator"]))):
    """Updates an existing user's name, email, RBAC role, or active status."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail=f"User '{user_id}' not found")
        
        full_name = user_data.full_name if user_data.full_name is not None else row["full_name"]
        email = user_data.email if user_data.email is not None else row["email"]
        role = user_data.role if user_data.role is not None else row["role"]
        usr_status = user_data.status if user_data.status is not None else row["status"]
        
        cursor.execute(
            "UPDATE users SET full_name = ?, email = ?, role = ?, status = ? WHERE user_id = ?",
            (full_name, email, role, usr_status, user_id)
        )
        
        return UserResponse(
            user_id=user_id,
            full_name=full_name,
            email=email,
            role=role,
            status=usr_status
        )
