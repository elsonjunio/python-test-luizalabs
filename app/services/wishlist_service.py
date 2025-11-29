from sqlalchemy import select
from app.models import WishlistItem, Customer
from app.services.product_service import ProductService
from fastapi import HTTPException
from datetime import datetime, timezone


class WishlistService:
    @staticmethod
    async def list_items(session, customer_id, user, limit, offset):
        """Returns the customer's wishlist.

        Args:
            customer_id: ID of the customer.
            limit: Maximum number of items to return.
            offset: Pagination offset.
            session: Database session.
            user: Authenticated user.

        Returns:
            Paginated list of wishlist items.
        """
        customer_query = select(Customer).where(
            Customer.id == customer_id, Customer.deleted_at.is_(None)
        )
        query_result = await session.execute(customer_query)
        customer = query_result.scalar_one_or_none()

        if not customer:
            raise HTTPException(400, 'Customer does not exist')

        # ACL
        if 'CUSTOMER' in user['roles'] and user['email'] != customer.email:
            raise HTTPException(
                403, 'Customers can only access their own list'
            )

        wishlist_item_query = (
            select(WishlistItem.product_id)
            .where(
                WishlistItem.customer_id == customer_id,
                WishlistItem.deleted_at.is_(None),
            )
            .offset(offset)
            .limit(limit)
        )
        rows = (await session.execute(wishlist_item_query)).scalars().all()

        items = []
        sources = {
            'from_cache_short': [],
            'from_cache_long': [],
            'from_api': [],
            'not_found': [],
        }

        for pid in rows:
            pdata, src = await ProductService.get_product(str(pid))

            if pdata:
                items.append(pdata)

            sources_map = {
                'cache_short': 'from_cache_short',
                'cache_long': 'from_cache_long',
                'api': 'from_api',
                'not_found': 'not_found',
            }
            sources[sources_map[src]].append(pid)

        return {
            'items': items,
            'source': sources,
            'pagination': {
                'limit': limit,
                'offset': offset,
                'count': len(items),
            },
        }

    @staticmethod
    async def add_product(session, customer_id, product_id, user):
        """Adds a product to the wishlist.

        Args:
            product_id: Product identifier.
            customer_id: ID of the customer.
            session: Database session.
            user: Authenticated user.

        Returns:
            Created wishlist item.
        """
        customer_query = select(Customer).where(
            Customer.id == customer_id, Customer.deleted_at.is_(None)
        )
        query_result = await session.execute(customer_query)
        customer = query_result.scalar_one_or_none()

        if not customer:
            raise HTTPException(400, 'Customer does not exist')

        if 'CUSTOMER' in user['roles'] and user['email'] != customer.email:
            raise HTTPException(
                403, 'Customers can only modify their own list'
            )

        data, src = await ProductService.get_product(product_id)
        if data is None:
            raise HTTPException(400, 'Product does not exist')

        item = WishlistItem(customer_id=customer_id, product_id=product_id)
        session.add(item)

        from sqlalchemy.exc import IntegrityError

        try:
            await session.commit()
        except IntegrityError as e:
            await session.rollback()
            if 'UniqueViolationError' in str(
                e
            ):   # if isinstance(e.orig, asyncpg.exceptions.UniqueViolationError):
                raise HTTPException(409, 'Product already in wishlist')
            raise

        await session.refresh(item)
        return {'product_id': product_id, 'added': True}

    @staticmethod
    async def soft_delete(session, customer_id, product_id, user):
        """Removes a product from the wishlist.

        Args:
            customer_id: ID of the customer.
            product_id: ID of the product.
            session: Database session.
            user: Authenticated user.

        Returns: None
        """
        customer_query = select(Customer).where(
            Customer.id == customer_id, Customer.deleted_at.is_(None)
        )
        query_result = await session.execute(customer_query)
        customer = query_result.scalar_one_or_none()

        if not customer:
            raise HTTPException(400, 'Customer does not exist')

        if 'CUSTOMER' in user['roles'] and user['email'] != customer.email:
            raise HTTPException(
                403, 'Customers can only modify their own list'
            )

        query = await session.execute(
            select(WishlistItem).where(
                WishlistItem.customer_id == customer_id,
                WishlistItem.product_id == product_id,
                WishlistItem.deleted_at.is_(None),
            )
        )
        cust = query.scalar_one_or_none()

        if not cust:
            raise HTTPException(404, 'Product not found')

        cust.deleted_at = datetime.now(timezone.utc)
        await session.commit()
