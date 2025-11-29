from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from app.services.wishlist_service import WishlistService
from app.models import Customer


from fastapi import HTTPException


class FakeScalarResult:
    def __init__(self, values):
        self._values = values

    def all(self):
        return self._values


class FakeResult:
    def __init__(self, scalar_value=None, scalar_list=None):
        self.scalar_value = scalar_value
        self.scalar_list = scalar_list or []

    def scalar_one_or_none(self):
        return self.scalar_value

    def scalars(self):
        return FakeScalarResult(self.scalar_list)


@pytest.mark.asyncio
async def test_list_items_success():
    session = AsyncMock()

    session.execute.side_effect = [
        FakeResult(scalar_value=Customer(id=1, email="a@b.com", deleted_at=None)),
        FakeResult(scalar_list=[10, 20]),  
    ]

    # mock ProductService.get_product
    with patch("app.services.wishlist_service.ProductService.get_product") as gp:
        gp.side_effect = [
            ({"id": 10}, "api"),
            ({"id": 20}, "cache_short"),
        ]

        result = await WishlistService.list_items(
            session=session,
            customer_id=1,
            user={"roles": ["ADMIN"], "email": "admin@x.com"},
            limit=10,
            offset=0,
        )

    assert result["pagination"]["count"] == 2
    assert len(result["items"]) == 2
    assert result["source"]["from_api"] == [10]
    assert result["source"]["from_cache_short"] == [20]



@pytest.mark.asyncio
async def test_add_product_not_found():

    session = AsyncMock()

    session.execute.side_effect = [
        FakeResult(scalar_value=Customer(id=1, email="a@b.com", deleted_at=None)),
        FakeResult(scalar_list=[10, 20]),  
    ]

    # mock get_product -> retorna None
    with patch("app.services.wishlist_service.ProductService.get_product") as gp:
        gp.return_value = (None, "not_found")

        with pytest.raises(HTTPException) as e:
            await WishlistService.add_product(
                session=session,
                customer_id=1,
                product_id="999",
                user={"roles": ["ADMIN"], "email": "admin@x.com"},
            )

    assert e.value.status_code == 400
    assert "Product does not exist" in e.value.detail

import pytest
from unittest.mock import AsyncMock
from fastapi import HTTPException
from app.services.wishlist_service import WishlistService
from app.models import Customer


@pytest.mark.asyncio
async def test_soft_delete_product_not_found():
    session = AsyncMock()

    session.execute.side_effect = [
        FakeResult(scalar_value=Customer(id=1, email="a@b.com", deleted_at=None)),
        FakeResult(scalar_list=[10, 20]),  
    ]

    with pytest.raises(HTTPException) as e:
        await WishlistService.soft_delete(
            session=session,
            customer_id=1,
            product_id=55,
            user={"roles": ["ADMIN"], "email": "admin@x.com"},
        )

    assert e.value.status_code == 404
    assert "Product not found" in e.value.detail