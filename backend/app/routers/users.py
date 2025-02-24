from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..schemas import User, UserUpdate
from ..models import User as UserModel
from .. import crud, auth

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=User)
async def read_user_me(
    current_user: UserModel = Depends(auth.get_current_active_user)
):
    return current_user

@router.put("/me", response_model=User)
async def update_user_me(
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(auth.get_current_active_user)
):
    return crud.update_user(db, db_obj=current_user, obj_in=user_in)

@router.get("", response_model=List[User])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(auth.check_admin_user)
):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@router.get("/{user_id}", response_model=User)
async def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(auth.check_admin_user)
):
    user = crud.get_user(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user