from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from backend.database import get_session
from backend.models import (
    Colegio, Sedes, Grado, Dias, Turno, Bloque, GradoDiaConfig
)
from backend.schemas import (
    ColegioUpdate, SedesCreate, GradoCreate, DiasCreate,
    TurnoCreate, BloqueCreate, GradoDiaConfigCreate
)

router = APIRouter(prefix="/api", tags=["Infraestructura"])


def _validate_fk(session: Session, model, id_value: int, label: str):
    if not session.get(model, id_value):
        raise HTTPException(status_code=400, detail=f"{label} {id_value} no existe")


# --- Colegio ---
@router.get("/colegio", response_model=List[Colegio])
def get_colegio(session: Session = Depends(get_session)):
    return session.exec(select(Colegio)).all()


@router.put("/colegio/{id}", response_model=Colegio)
def update_colegio(id: int, col: ColegioUpdate, session: Session = Depends(get_session)):
    db_c = session.get(Colegio, id)
    if not db_c:
        raise HTTPException(status_code=404, detail="Colegio no encontrado")
    db_c.nombre_colegio = col.nombre_colegio
    session.add(db_c)
    session.commit()
    session.refresh(db_c)
    return db_c


# --- Sedes ---
@router.get("/sedes", response_model=List[Sedes])
def get_sedes(session: Session = Depends(get_session)):
    return session.exec(select(Sedes)).all()


@router.post("/sedes", response_model=Sedes, status_code=201)
def create_sede(sede: SedesCreate, session: Session = Depends(get_session)):
    if sede.id_colegio:
        _validate_fk(session, Colegio, sede.id_colegio, "Colegio")
    db = Sedes(**sede.model_dump())
    session.add(db)
    session.commit()
    session.refresh(db)
    return db


# --- Grados ---
@router.get("/grados", response_model=List[Grado])
def get_grados(session: Session = Depends(get_session)):
    return session.exec(select(Grado)).all()


@router.post("/grados", response_model=Grado, status_code=201)
def create_grado(grado: GradoCreate, session: Session = Depends(get_session)):
    db = Grado(**grado.model_dump())
    session.add(db)
    session.commit()
    session.refresh(db)
    return db


# --- Días ---
@router.get("/dias", response_model=List[Dias])
def get_dias(session: Session = Depends(get_session)):
    return session.exec(select(Dias).order_by(Dias.orden)).all()


@router.post("/dias", response_model=Dias, status_code=201)
def create_dia(dia: DiasCreate, session: Session = Depends(get_session)):
    db = Dias(**dia.model_dump())
    session.add(db)
    session.commit()
    session.refresh(db)
    return db


# --- Turnos ---
@router.get("/turnos", response_model=List[Turno])
def get_turnos(session: Session = Depends(get_session)):
    return session.exec(select(Turno)).all()


@router.post("/turnos", response_model=Turno, status_code=201)
def create_turno(turno: TurnoCreate, session: Session = Depends(get_session)):
    db = Turno(**turno.model_dump())
    session.add(db)
    session.commit()
    session.refresh(db)
    return db


# --- Bloques ---
@router.get("/bloques", response_model=List[Bloque])
def get_bloques(session: Session = Depends(get_session)):
    return session.exec(select(Bloque)).all()


@router.post("/bloques", response_model=Bloque, status_code=201)
def create_bloque(bloque: BloqueCreate, session: Session = Depends(get_session)):
    _validate_fk(session, Turno, bloque.id_turno, "Turno")
    db = Bloque(**bloque.model_dump())
    session.add(db)
    session.commit()
    session.refresh(db)
    return db


# --- Grado-Día Config ---
@router.get("/grado-dia-config", response_model=List[GradoDiaConfig])
def get_grado_dia_config(session: Session = Depends(get_session)):
    return session.exec(select(GradoDiaConfig)).all()


@router.post("/grado-dia-config", response_model=GradoDiaConfig, status_code=201)
def create_grado_dia_config(config: GradoDiaConfigCreate, session: Session = Depends(get_session)):
    _validate_fk(session, Grado, config.id_grado, "Grado")
    _validate_fk(session, Dias, config.id_dia, "Dia")
    db = GradoDiaConfig(**config.model_dump())
    session.add(db)
    session.commit()
    session.refresh(db)
    return db


@router.delete("/grado-dia-config/{id_config}")
def delete_grado_dia_config(id_config: int, session: Session = Depends(get_session)):
    db = session.get(GradoDiaConfig, id_config)
    if not db:
        raise HTTPException(status_code=404, detail="Config no encontrada")
    session.delete(db)
    session.commit()
    return {"message": "Config borrada"}
