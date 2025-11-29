from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth_validation import require_role
from app.schemas.customer import (
    CustomerCreate,
    CustomerUpdate,
    CustomerOut,
    CustomerDelete,
)
from app.services.customer_service import CustomerService

from fastapi import HTTPException

router = APIRouter(prefix='/v1/customers', tags=['Customers'])


@router.post('/', response_model=CustomerOut)
async def create_customer(
    data: CustomerCreate,
    session: AsyncSession = Depends(get_db),
    user=Depends(require_role('CUSTOMER', 'ADMIN')),
):
    """Creates a new customer.

    Args:
        data: Customer information for creation.
        session: Database session.
        user: Authenticated user.

    Returns:
        Created customer data.
    """
    response = await CustomerService.create(session, data, user)
    return response


@router.get('/', response_model=CustomerOut)
async def get_customer(
    email: str = Query(..., description='Customer email'),
    session: AsyncSession = Depends(get_db),
    user=Depends(require_role('CUSTOMER', 'ADMIN')),
):
    """Retrieves a customer by email.

    Args:
        email: Customer email.
        session: Database session.
        user: Authenticated user.

    Returns:
        Customer data.

    Raises:
        HTTPException: If no customer is found.
    """
    response = await CustomerService.get_by_email(session, email, user)

    if response is None:
        raise HTTPException(status_code=404, detail='Customer not found')
    return response


@router.put('/', response_model=CustomerOut)
async def update_customer(
    data: CustomerUpdate,
    customer_id: str = Query(..., description='Customer Id'),
    session: AsyncSession = Depends(get_db),
    user=Depends(require_role('CUSTOMER', 'ADMIN')),
):
    """Updates an existing customer.

    Args:
        data: Fields to update.
        customer_id: ID of the target customer.
        session: Database session.
        user: Authenticated user.

    Returns:
        Updated customer data.
    """
    response = await CustomerService.update(session, customer_id, data, user)
    return response


@router.delete('/{customer_id}')
async def delete_customer(
    customer_id: str = Path(..., description='Customer Id'),
    session: AsyncSession = Depends(get_db),
    user=Depends(require_role('CUSTOMER', 'ADMIN')),
) -> CustomerDelete:
    """Soft deletes a customer.

    Args:
        customer_id: ID of the customer.
        session: Database session.
        user: Authenticated user.

    Returns:
        Deletion confirmation.
    """
    await CustomerService.soft_delete(session, customer_id, user)
    return CustomerDelete(detail='Customer deleted')
