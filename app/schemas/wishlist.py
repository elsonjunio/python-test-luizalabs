from typing import Dict, List
from pydantic import BaseModel
from typing import TypedDict


class Product(TypedDict):
    price: float
    image: str
    brand: str
    id: int
    title: str
    reviewScore: float


class SourceList(TypedDict):
    from_cache_short: List[str]
    from_cache_long: List[str]
    from_api: List[str]
    not_found: List[str]


class Pagination(TypedDict):
    limit: int
    offset: int
    count: int


class WishItemList(BaseModel):
    items: List[Product]
    source: SourceList
    pagination: Pagination


class WishItemCreate(BaseModel):
    product_id: str


class WishItemCreateOut(BaseModel):
    product_id: str
    added: bool


class WishItemDelete(BaseModel):
    detail: str
