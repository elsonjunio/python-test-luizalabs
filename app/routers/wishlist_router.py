from fastapi import APIRouter, Depends, Query, Path
from app.core.database import get_db
from app.services.wishlist_service import WishlistService
from app.core.auth_validation import require_role
from app.schemas.wishlist import WishItemList, WishItemCreate, WishItemDelete

router = APIRouter(
    prefix='/v1/customers/{customer_id}/wishlist', tags=['Wishlist']
)


@router.get('/')
async def get_wishlist(
    customer_id: str,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session=Depends(get_db),
    user=Depends(require_role('CUSTOMER', 'ADMIN')),
) -> WishItemList:
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
    return await WishlistService.list_items(
        session, customer_id, user, limit, offset
    )


@router.post('/')
async def add_product(
    data: WishItemCreate,
    customer_id: str,
    session=Depends(get_db),
    user=Depends(require_role('CUSTOMER', 'ADMIN')),
) -> WishItemCreate:
    """Adds a product to the wishlist.

    Args:
        data: Product identifier payload.
        customer_id: ID of the customer.
        session: Database session.
        user: Authenticated user.

    Returns:
        Created wishlist item.
    """
    return await WishlistService.add_product(
        session, customer_id, data.product_id, user
    )


@router.delete('/{product_id}')
async def delete_customer(
    customer_id: str,
    product_id: str = Path(..., description='Product Id'),
    session=Depends(get_db),
    user=Depends(require_role('CUSTOMER', 'ADMIN')),
) -> WishItemDelete:
    """Removes a product from the wishlist.

    Args:
        customer_id: ID of the customer.
        product_id: ID of the product.
        session: Database session.
        user: Authenticated user.

    Returns:
        Deletion confirmation.
    """
    await WishlistService.soft_delete(session, customer_id, product_id, user)
    return WishItemDelete(detail='Product deleted')
