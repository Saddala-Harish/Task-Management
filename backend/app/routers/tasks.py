from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..schemas import Task, TaskCreate, TaskUpdate, TaskListResponse
from ..models import User, TaskStatus, UserRole
from .. import crud, auth

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("", response_model=Task)
async def create_task(
    task_in: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.check_manager_user)
):
    # Verify assigned user exists if provided
    if task_in.assigned_to:
        assigned_user = crud.get_user(db, id=task_in.assigned_to)
        if not assigned_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assigned user not found"
            )
    
    return crud.create_task(db=db, task=task_in, creator_id=current_user.id)

@router.get("", response_model=TaskListResponse)
async def read_tasks(
    status: Optional[TaskStatus] = None,
    assigned_to: Optional[int] = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_active_user)
):
    # Filter tasks based on user role
    if current_user.role == UserRole.admin:
        tasks = crud.get_tasks(
            db,
            status=status,
            assigned_to=assigned_to,
            skip=skip,
            limit=limit
        )
        total = crud.get_tasks_count(db, status=status, assigned_to=assigned_to)
    elif current_user.role == UserRole.manager:
        tasks = crud.get_tasks(
            db,
            creator_id=current_user.id,
            status=status,
            assigned_to=assigned_to,
            skip=skip,
            limit=limit
        )
        total = crud.get_tasks_count(
            db,
            creator_id=current_user.id,
            status=status,
            assigned_to=assigned_to
        )
    else:
        tasks = crud.get_tasks(
            db,
            assigned_to=current_user.id,
            status=status,
            skip=skip,
            limit=limit
        )
        total = crud.get_tasks_count(
            db,
            assigned_to=current_user.id,
            status=status
        )
    
    return TaskListResponse(
        tasks=tasks,
        total=total,
        page=skip // limit + 1,
        size=limit
    )

@router.get("/{task_id}", response_model=Task)
async def read_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_active_user)
):
    task = crud.get_task(db, id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check permissions
    if current_user.role == UserRole.user and \
       task.assigned_to != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    if current_user.role == UserRole.manager and \
       task.created_by != current_user.id and \
       task.assigned_to != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return task

@router.put("/{task_id}", response_model=Task)
async def update_task(
    task_id: int,
    task_in: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_active_user)
):
    task = crud.get_task(db, id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check permissions
    if current_user.role == UserRole.user:
        if task.assigned_to != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        # Users can only update status
        if task_in.title or task_in.description or \
           task_in.priority or task_in.assigned_to or \
           task_in.due_date:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Users can only update task status"
            )
    
    if current_user.role == UserRole.manager and \
       task.created_by != current_user.id and \
       task.assigned_to != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return crud.update_task(db=db, db_obj=task, obj_in=task_in)

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.check_manager_user)
):
    task = crud.get_task(db, id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    if current_user.role == UserRole.manager and \
       task.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    crud.delete_task(db=db, id=task_id)