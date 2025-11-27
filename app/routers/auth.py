from fastapi import APIRouter, Depends, Security
from sqlalchemy.ext.asyncio import AsyncSession

#from core.database import get_db
#from app.core.auth_validation import require_user
from schemas.auth import UserCreate, UserLogin, Token, UserOut
from services.AuthService import AuthService
from fastapi.security import HTTPBearer

router = APIRouter()
bearer_scheme = HTTPBearer()

router = APIRouter(prefix='/auth', tags=['Auth'])


#@router.post('/signup', response_model=UserOut)
#async def signup(payload: UserCreate, db: AsyncSession = Depends(get_db)):
#    return await AuthService.register(db, payload)
#
#
#@router.post('/login', response_model=Token)
#async def login(payload: UserLogin, db: AsyncSession = Depends(get_db)):
#    token = await AuthService.login(db, payload)
#    return Token(access_token=token)
#
#
@router.get('/me')
def me( credentials=Security(bearer_scheme)):
    return "current_user"
