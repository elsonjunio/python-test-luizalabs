from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from app.middleware.current_user_middleware import CurrentUserMiddleware
from fastapi import APIRouter, Depends, Security
from app.core.config import settings
from app.core.auth_validation import require_user, require_role

from app.routers.customer_router import router as customer_router
from app.routers.wishlist_router import router as wishlist_router
from app.core.seeder import create_products_cache
from contextlib import asynccontextmanager
from app.core.logging_config import setup_logger
import logging

setup_logger("DEBUG")

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_products_cache()
    yield
    logging.info("shutdown")


app = FastAPI(lifespan=lifespan)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title='Wishlist API',
        version='1.0.0',
        routes=app.routes,
    )

    if 'components' not in openapi_schema:
        openapi_schema['components'] = {}

    if 'securitySchemes' not in openapi_schema['components']:
        openapi_schema['components']['securitySchemes'] = {}

    openapi_schema['components']['securitySchemes']['oauth2'] = {
        'type': 'oauth2',
        'flows': {
            'authorizationCode': {
                'authorizationUrl': settings.AUTHORIZATION_URL,
                'tokenUrl': settings.TOKEN_URL,
                'scopes': {},
            }
        },
    }

    openapi_schema['security'] = [{'oauth2': []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


app.add_middleware(CurrentUserMiddleware)
app.include_router(customer_router)
app.include_router(wishlist_router)

