from fastapi import Depends, HTTPException, Request


def require_user(request: Request):
    """Returns the authenticated user.

    Args:
        request (Request): HTTP request.

    Returns:
        dict: The authenticated user.

    Raises:
        HTTPException: If no user is authenticated (401).
    """
    if not request.state.current_user:
        raise HTTPException(status_code=401, detail='Authentication required')
    return request.state.current_user


def require_role(*roles):
    """Creates a dependency that checks user roles.

    Args:
        *roles (str): Allowed roles.

    Returns:
        callable: Dependency function that returns the authenticated user.

    Raises:
        HTTPException: If the user does not have required roles (403).
    """
    def wrapper(user=Depends(require_user)):
        user_roles = user.get('roles', [])
        if not any(r in user_roles for r in roles):
            raise HTTPException(403, "Forbidden")
        return user
    return wrapper
