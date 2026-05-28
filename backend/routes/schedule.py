import json
import logging
from typing import List
from collections import defaultdict
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from backend.database import get_session, engine
from backend.models import (
    HorarioFinal, HorarioSnapshot, Dias, Turno, Seccion, Cursos, Profesores
)
from backend.schemas import SnapshotUpdate
from backend.engine_connector import generar_horario_engine, start_generation, get_progress
from backend.exceptions import AppError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Horario"])


# --- Horario Final ---
@router.get("/horario-final", response_model=List[HorarioFinal])
def get_horario_final(session: Session = Depends(get_session)):
    return session.exec(select(HorarioFinal)).all()


@router.post("/horario-final", response_model=HorarioFinal, status_code=201)
def create_horario_final(hf: HorarioFinal, session: Session = Depends(get_session)):
    session.add(hf)
    session.commit()
    session.refresh(hf)
    return hf


@router.delete("/horario-final/{id_horario_final}")
def delete_horario_final(id_horario_final: int, session: Session = Depends(get_session)):
    db = session.get(HorarioFinal, id_horario_final)
    if not db:
        raise HTTPException(status_code=404, detail="Horario no encontrado")
    session.delete(db)
    session.commit()
    return {"message": "Borrado"}


# --- Motor (legacy sync) ---
@router.post("/generar-horario")
def desencadenar_motor(session: Session = Depends(get_session)):
    try:
        resultado = generar_horario_engine(session)
        return resultado
    except AppError as e:
        return {"status": "error", "errores": e.errors}


# --- Motor con progreso ---
@router.post("/generar-horario/start")
def start_generar_horario():
    """Lanza la generación en background y devuelve task_id."""
    from backend.database import engine
    task_id = start_generation(engine)
    return {"task_id": task_id}


@router.get("/horario-progress/{task_id}")
def horario_progress(task_id: str):
    """Devuelve el progreso actual de la generación."""
    return get_progress(task_id)


@router.get("/cargar-horario")
def cargar_horario_guardado(session: Session = Depends(get_session)):
    """Lee horario_final de la BD y lo devuelve en formato del motor."""
    rows = session.exec(select(HorarioFinal)).all()
    if not rows:
        return {"status": "empty", "resultado": None}

    dias_db = {d.id_dia: d.nombre_dia for d in session.exec(select(Dias)).all()}
    turnos_db = {t.id_turno: t.nombre for t in session.exec(select(Turno)).all()}

    grupos = defaultdict(list)
    for r in rows:
        turno_nombre = turnos_db.get(r.id_turno, "Mañana")
        key = (r.id_seccion, r.id_curso, r.id_profesor, r.id_dia, turno_nombre)
        grupos[key].append(r.num_bloque)

    asignaciones = []
    for (sec, cur, prof, dia_id, turno), slots in grupos.items():
        slots.sort()
        asignaciones.append({
            "seccion_id": f"SEC_{sec}",
            "curso_id": f"CUR_{cur}",
            "profesor_id": f"PROF_{prof}",
            "dia": dias_db.get(dia_id, ""),
            "turno": turno,
            "slot_inicio": slots[0] - 1,
            "horas": len(slots)
        })

    return {
        "status": "success",
        "resultado": {
            "estado": "GUARDADO",
            "mensaje": "Horario cargado desde la base de datos.",
            "estadisticas": {"tiempo_segundos": 0, "ramas_exploradas": 0, "conflictos": 0},
            "asignaciones": asignaciones
        }
    }


# --- Snapshots (Historial) ---
@router.get("/horario-snapshots")
def get_snapshots(session: Session = Depends(get_session)):
    snapshots = session.exec(select(HorarioSnapshot).order_by(HorarioSnapshot.created_at.desc())).all()
    return [
        {
            "id_snapshot": s.id_snapshot,
            "nombre": s.nombre,
            "descripcion": s.descripcion,
            "asignaciones_count": s.asignaciones_count,
            "estado": s.estado,
            "tiempo_segundos": s.tiempo_segundos,
            "is_active": s.is_active,
            "created_at": s.created_at,
        }
        for s in snapshots
    ]


@router.get("/horario-snapshots/{id_snapshot}")
def get_snapshot(id_snapshot: int, session: Session = Depends(get_session)):
    snapshot = session.get(HorarioSnapshot, id_snapshot)
    if not snapshot:
        raise HTTPException(status_code=404, detail="Snapshot no encontrado")
    return {
        "id_snapshot": snapshot.id_snapshot,
        "nombre": snapshot.nombre,
        "descripcion": snapshot.descripcion,
        "json_data": json.loads(snapshot.json_data),
        "asignaciones_count": snapshot.asignaciones_count,
        "estado": snapshot.estado,
        "tiempo_segundos": snapshot.tiempo_segundos,
        "is_active": snapshot.is_active,
        "created_at": snapshot.created_at,
    }


@router.put("/horario-snapshots/{id_snapshot}")
def update_snapshot(id_snapshot: int, update: SnapshotUpdate, session: Session = Depends(get_session)):
    snapshot = session.get(HorarioSnapshot, id_snapshot)
    if not snapshot:
        raise HTTPException(status_code=404, detail="Snapshot no encontrado")
    if update.nombre is not None:
        snapshot.nombre = update.nombre
    if update.descripcion is not None:
        snapshot.descripcion = update.descripcion
    session.add(snapshot)
    session.commit()
    session.refresh(snapshot)
    return {"message": "Snapshot actualizado"}


@router.delete("/horario-snapshots/{id_snapshot}")
def delete_snapshot(id_snapshot: int, session: Session = Depends(get_session)):
    snapshot = session.get(HorarioSnapshot, id_snapshot)
    if not snapshot:
        raise HTTPException(status_code=404, detail="Snapshot no encontrado")
    session.delete(snapshot)
    session.commit()
    return {"message": "Snapshot eliminado"}


@router.post("/horario-snapshots/{id_snapshot}/load")
def load_snapshot(id_snapshot: int, session: Session = Depends(get_session)):
    """Carga un snapshot como horario activo (reescribe horario_final)."""
    snapshot = session.get(HorarioSnapshot, id_snapshot)
    if not snapshot:
        raise HTTPException(status_code=404, detail="Snapshot no encontrado")

    data = json.loads(snapshot.json_data)
    asignaciones = data.get("asignaciones", [])
    if not asignaciones:
        raise HTTPException(status_code=400, detail="El snapshot no tiene asignaciones")

    old = session.exec(select(HorarioFinal)).all()
    for o in old:
        session.delete(o)
    session.commit()

    all_snapshots = session.exec(select(HorarioSnapshot)).all()
    for s in all_snapshots:
        s.is_active = False
        session.add(s)

    snapshot.is_active = True
    session.add(snapshot)

    dias_db = {d.nombre_dia: d.id_dia for d in session.exec(select(Dias)).all()}
    turno_db = {t.nombre: t.id_turno for t in session.exec(select(Turno)).all()}

    for asig in asignaciones:
        sec_id = int(asig["seccion_id"].replace("SEC_", ""))
        if asig["curso_id"] == "TUT1":
            tut_curso = session.exec(select(Cursos).where(Cursos.nombre_curso.like("%Tutoría%"))).first()
            cur_id = tut_curso.id_curso if tut_curso else 18
        else:
            cur_id = int(asig["curso_id"].replace("CUR_", ""))
        prof_id = int(asig["profesor_id"].replace("PROF_", ""))
        id_dia = dias_db.get(asig["dia"])
        id_turno = turno_db.get(asig.get("turno", "Mañana"))
        slot_inicio = asig.get("slot_inicio", 0)
        horas = asig.get("horas", 1)

        for i in range(horas):
            session.add(HorarioFinal(
                id_seccion=sec_id,
                id_dia=id_dia,
                num_bloque=slot_inicio + i + 1,
                id_turno=id_turno,
                id_curso=cur_id,
                id_profesor=prof_id
            ))

    session.commit()
    return {"message": f"Snapshot '{snapshot.nombre}' cargado como horario activo"}
