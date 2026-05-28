from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from pydantic import BaseModel

from backend.database import get_session
from backend.models import Usuario

router = APIRouter(prefix="/api", tags=["Auth"])


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/login")
def login(req: LoginRequest, session: Session = Depends(get_session)):
    user = session.exec(select(Usuario).where(Usuario.email == req.email)).first()
    if not user:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    return {"status": "success", "user": {"nombre": user.nombre, "email": user.email}}
