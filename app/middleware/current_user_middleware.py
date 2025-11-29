from fastapi import Request, HTTPException
import jwt
from jwt.algorithms import RSAAlgorithm
import requests
from app.core.config import settings
import time


class CurrentUserMiddleware:
    """Middleware for extracting and validating the authenticated user."""
    def __init__(self, app):
        self.app = app

        for _ in range(30):
            try:
                self.jwks = requests.get(settings.JWKS_URI).json()
                print("Keycloak started!")
                break
            except Exception:
                pass
            
            print("Waiting for Keycloak...")
            time.sleep(2)        

    @staticmethod
    def get_key(token, jwks):
        """Retrieves the RSA public key for the provided JWT.

        Args:
            token: The raw JWT string.
            jwks: The JWKS document containing public keys.

        Returns:
            RSA public key object.

        Raises:
            HTTPException: If no matching key ID is found.
        """
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header['kid']

        key = None

        for k in jwks['keys']:
            if k['kid'] == kid:
                key = k
                break

        if key is None:
            raise HTTPException(status_code=401, detail='Invalid token')

        return RSAAlgorithm.from_jwk(key)

    async def __call__(self, scope, receive, send):
        """Processes incoming requests and resolves the authenticated user."""

        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        request = Request(scope)
        auth = request.headers.get('Authorization')

        request.state.current_user = None

        if auth and auth.startswith('Bearer '):
            token = auth.split(' ')[1]

            try:
                public_key = self.get_key(token, self.jwks)
                payload = jwt.decode(
                    token,
                    public_key,
                    algorithms=['RS256'],
                    options={'verify_aud': False},
                )

                request.state.current_user = {
                    'id': payload.get('sub'),
                    'email': payload.get('email'),
                    'name': payload.get('name'),
                    'roles': payload.get('realm_access', {}).get('roles', []),
                }

            except Exception:
                raise HTTPException(status_code=401, detail='Invalid token')

        return await self.app(scope, receive, send)
