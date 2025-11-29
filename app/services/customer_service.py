from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from app.models.customer import Customer
from fastapi import HTTPException


class CustomerService:
    @staticmethod
    async def get_by_email(session, customer_email, current_user):

        if (
            current_user['email'] != customer_email
            and 'CUSTOMER' in current_user['roles']
        ):
            raise HTTPException(
                status_code=403,
                detail='Customer can only request their own registration',
            )

        stmt = select(Customer).where(
            Customer.email == customer_email, Customer.deleted_at.is_(None)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def create(session: AsyncSession, data, current_user):
        if (
            current_user['email'] == data.email
            and 'ADMIN' in current_user['roles']
        ):
            raise HTTPException(
                status_code=403,
                detail='Admin cannot create customer for themselves',
            )

        if (
            current_user['email'] != data.email
            and 'CUSTOMER' in current_user['roles']
        ):
            raise HTTPException(
                status_code=403, detail='Only the customer can register'
            )

        cust = Customer(**data.model_dump())
        session.add(cust)

        try:
            await session.commit()
        except Exception as e:
            await session.rollback()

            # Verifica se o erro é de duplicidade
            if 'uq_customer_active' in str(e):
                raise HTTPException(
                    status_code=409,
                    detail='Customer with this email already exists',
                )

            # Relevanta erros inesperados
            raise

        await session.refresh(cust)
        return cust

    @staticmethod
    async def update(session, customer_id: str, data, user):

        query = await session.execute(
            select(Customer).where(
                Customer.id == customer_id, Customer.deleted_at.is_(None)
            )
        )
        cust = query.scalar_one_or_none()

        if not cust:
            raise HTTPException(404, 'Customer not found')

        roles = user.get('roles', [])

        is_customer = 'CUSTOMER' in roles

        if 'CUSTOMER' in user['roles'] and cust.email != user['email']:
            raise HTTPException(
                403, 'Customers can only update their own data'
            )

        allowed_fields = ['name'] if is_customer else ['name', 'email']

        incoming_data = data.model_dump(exclude_unset=True)

        sanitized_data = {
            k: v for k, v in incoming_data.items() if k in allowed_fields
        }

        if not sanitized_data:
            raise HTTPException(400, 'No valid fields to update')

        for k, v in sanitized_data.items():
            setattr(cust, k, v)

        await session.commit()
        await session.refresh(cust)

        return cust

    @staticmethod
    async def soft_delete(session, customer_id, user):
        query = await session.execute(
            select(Customer).where(
                Customer.id == customer_id, Customer.deleted_at.is_(None)
            )
        )
        cust = query.scalar_one_or_none()

        if not cust:
            raise HTTPException(404, 'Customer not found')

        if 'CUSTOMER' in user['roles'] and cust.email != user['email']:
            raise HTTPException(
                403, 'Customers can only delete their own data'
            )

        cust.deleted_at = datetime.now(timezone.utc)
        await session.commit()
