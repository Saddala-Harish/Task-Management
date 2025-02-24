from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, List, Union, Dict, Any
from . import models, schemas, auth

# User CRUD operations
def get_user(db: Session, id: int) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == id).first()

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        password_hash=hashed_password,
        full_name=user.full_name,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(
    db: Session,
    db_obj: models.User,
    obj_in: Union[schemas.UserUpdate, Dict[str, Any]]
) -> models.User:
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.dict(exclude_unset=True)
    
    if "password" in update_data:
        hashed_password = auth.get_password_hash(update_data["password"])
        del update_data["password"]
        update_data["password_hash"] = hashed_password
    
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def authenticate_user(db: Session, email: str, password: str) -> Optional[models.User]:
    user = get_user_by_email(db, email=email)
    if not user:
        return None
    if not auth.verify_password(password, user.password_hash):
        return None
    return user

# Task CRUD operations
def get_task(db: Session, id: int) -> Optional[models.Task]:
    return db.query(models.Task).filter(models.Task.id == id).first()

def get_tasks(
    db: Session,
    creator_id: Optional[int] = None,
    assigned_to: Optional[int] = None,
    status: Optional[models.TaskStatus] = None,
    skip: int = 0,
    limit: int = 100
) -> List[models.Task]:
    query = db.query(models.Task)
    
    filters = []
    if creator_id is not None:
        filters.append(models.Task.created_by == creator_id)
    if assigned_to is not None:
        filters.append(models.Task.assigned_to == assigned_to)
    if status is not None:
        filters.append(models.Task.status == status)
    
    if filters:
        query = query.filter(and_(*filters))
    
    return query.offset(skip).limit(limit).all()

def get_tasks_count(
    db: Session,
    creator_id: Optional[int] = None,
    assigned_to: Optional[int] = None,
    status: Optional[models.TaskStatus] = None
) -> int:
    query = db.query(models.Task)
    
    filters = []
    if creator_id is not None:
        filters.append(models.Task.created_by == creator_id)
    if assigned_to is not None:
        filters.append(models.Task.assigned_to == assigned_to)
    if status is not None:
        filters.append(models.Task.status == status)
    
    if filters:
        query = query.filter(and_(*filters))
    
    return query.count()

def create_task(
    db: Session,
    task: schemas.TaskCreate,
    creator_id: int
) -> models.Task:
    db_task = models.Task(
        **task.dict(),
        created_by=creator_id
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

# backend/app/crud.py
def update_task(
    db: Session,
    *,
    db_obj: models.Task,
    obj_in: Union[schemas.TaskUpdate, Dict[str, Any]]
) -> models.Task:
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.dict(exclude_unset=True)
    
    for field in update_data:
        setattr(db_obj, field, update_data[field])
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete_task(db: Session, id: int) -> None:
    db_task = get_task(db, id=id)
    if db_task:
        db.delete(db_task)
        db.commit()