# app/routers/customer.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth_validation import require_user
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerOut
from app.services.customer_service import CustomerService

from fastapi import HTTPException

router = APIRouter(prefix='/customers', tags=['Customers'])


@router.post('/', response_model=CustomerOut)
async def create_customer(
    data: CustomerCreate,
    session: AsyncSession = Depends(get_db),
    user=Depends(require_user),
):
    response = await CustomerService.create(session, data, user)
    return response


@router.get('/', response_model=CustomerOut)
async def get_customer(
    email: str = Query(..., description='Customer email'),
    session: AsyncSession = Depends(get_db),
    user=Depends(require_user),
):
    response = await CustomerService.get_by_email(session, email, user)

    if response is None:
        raise HTTPException(status_code=404, detail='Customer not found')
    return response


@router.put('/', response_model=CustomerOut)
async def update_customer(
    data: CustomerUpdate,
    customer_id: str = Query(..., description='Customer id'),
    session: AsyncSession = Depends(get_db),
    user=Depends(require_user),
):
    response = await CustomerService.update(session, customer_id, data, user)
    return response


@router.delete('/')
async def delete_customer(
    customer_id: str = Query(..., description='Customer id'),
    session: AsyncSession = Depends(get_db),
    user=Depends(require_user),
):
    await CustomerService.soft_delete(session, customer_id, user)
    return {'detail': 'Customer deleted'}
