from pydantic import BaseModel, EmailStr, ConfigDict, constr
from datetime import datetime
from typing import Optional, List
from .models import UserRole, TaskStatus, TaskPriority

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str

# class UserCreate(UserBase):
#     password: str
#     role: Optional[UserRole] = UserRole.user


class UserCreate(BaseModel):
    email: EmailStr
    password: constr(min_length=8)

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class UserInDB(UserBase):
    id: int
    role: UserRole
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class User(UserInDB):
    pass

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[str] = None

# Task Schemas
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.medium
    due_date: Optional[datetime] = None

class TaskCreate(TaskBase):
    assigned_to: Optional[int] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assigned_to: Optional[int] = None
    due_date: Optional[datetime] = None
    class Config:
        from_attributes = True

class TaskInDB(TaskBase):
    id: int
    status: TaskStatus
    created_by: int
    assigned_to: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class Task(TaskInDB):
    creator: Optional[User] = None
    assignee: Optional[User] = None

# Response Schemas
class TaskListResponse(BaseModel):
    tasks: List[Task]
    total: int
    page: int
    size: int