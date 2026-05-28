from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from backend.database import get_session
from backend.models import (
    ProfesorDisponibilidad, ProfesorPreferencia,
    Profesores, Dias, Turno, Sedes
)
from backend.schemas import ProfesorDisponibilidadCreate, ProfesorPreferenciaCreate

router = APIRouter(prefix="/api", tags=["Disponibilidad"])


def _validate_fk(session: Session, model, id_value: int, label: str):
    if not session.get(model, id_value):
        raise HTTPException(status_code=400, detail=f"{label} {id_value} no existe")


# --- Profesor-Disponibilidad ---
@router.get("/profesor-disponibilidad")
def get_profesor_disponibilidad(session: Session = Depends(get_session)):
    return session.exec(select(ProfesorDisponibilidad)).all()


@router.post("/profesor-disponibilidad", status_code=201)
def create_profesor_disponibilidad(pd: ProfesorDisponibilidadCreate, session: Session = Depends(get_session)):
    _validate_fk(session, Profesores, pd.id_profesor, "Profesor")
    _validate_fk(session, Dias, pd.id_dia, "Dia")
    _validate_fk(session, Turno, pd.id_turno, "Turno")
    _validate_fk(session, Sedes, pd.id_sede, "Sede")
    db = ProfesorDisponibilidad(**pd.model_dump())
    session.add(db)
    session.commit()
    session.refresh(db)
    return db


@router.delete("/profesor-disponibilidad/{id_disponibilidad}")
def delete_profesor_disponibilidad(id_disponibilidad: int, session: Session = Depends(get_session)):
    db = session.get(ProfesorDisponibilidad, id_disponibilidad)
    if not db:
        raise HTTPException(status_code=404, detail="Disponibilidad no encontrada")
    session.delete(db)
    session.commit()
    return {"message": "Disponibilidad borrada"}


# --- Profesor-Preferencia ---
@router.get("/profesor-preferencia")
def get_profesor_preferencia(session: Session = Depends(get_session)):
    return session.exec(select(ProfesorPreferencia)).all()


@router.post("/profesor-preferencia", status_code=201)
def create_profesor_preferencia(pp: ProfesorPreferenciaCreate, session: Session = Depends(get_session)):
    _validate_fk(session, Profesores, pp.id_profesor, "Profesor")
    _validate_fk(session, Dias, pp.id_dia, "Dia")
    _validate_fk(session, Turno, pp.id_turno, "Turno")
    _validate_fk(session, Sedes, pp.id_sede, "Sede")
    db = ProfesorPreferencia(**pp.model_dump())
    session.add(db)
    session.commit()
    session.refresh(db)
    return db


@router.delete("/profesor-preferencia/{id_preferencia}")
def delete_profesor_preferencia(id_preferencia: int, session: Session = Depends(get_session)):
    db = session.get(ProfesorPreferencia, id_preferencia)
    if not db:
        raise HTTPException(status_code=404, detail="Preferencia no encontrada")
    session.delete(db)
    session.commit()
    return {"message": "Preferencia borrada"}
