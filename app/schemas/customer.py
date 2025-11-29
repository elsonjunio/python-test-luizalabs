from pydantic import BaseModel, EmailStr
from uuid import UUID


class CustomerCreate(BaseModel):
    name: str
    email: EmailStr


class CustomerUpdate(BaseModel):
    name: str | None = None
    email: EmailStr


class CustomerOut(BaseModel):
    id: UUID
    name: str
    email: EmailStr

    class Config:
        from_attributes = True


class CustomerDelete(BaseModel):
    detail: str
