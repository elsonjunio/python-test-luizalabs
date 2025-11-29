from fastapi import Depends, HTTPException, Request


def require_user(request: Request):
    if not request.state.current_user:
        raise HTTPException(status_code=401, detail='Authentication required')
    return request.state.current_user


def require_role(*roles):
    def wrapper(user=Depends(require_user)):
        user_roles = user.get('roles', [])
        if not any(r in user_roles for r in roles):
            raise HTTPException(403, "Forbidden")
        return user
    return wrapper
