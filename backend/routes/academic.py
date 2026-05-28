from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from backend.database import get_session
from backend.models import (
    Areas, Cursos, Profesores, ProfesorCurso, Seccion,
    PlanEstudio, SeccionTurno, Tutoria, Sedes, Grado
)
from backend.schemas import (
    AreasCreate, CursosCreate, ProfesoresCreate, ProfesorCursoCreate,
    SeccionCreate, PlanEstudioCreate, SeccionTurnoCreate, TutoriaCreate
)

router = APIRouter(prefix="/api", tags=["Académico"])


def _validate_fk(session: Session, model, id_value: int, label: str):
    if not session.get(model, id_value):
        raise HTTPException(status_code=400, detail=f"{label} {id_value} no existe")


# --- Áreas ---
@router.get("/areas", response_model=List[Areas])
def get_areas(session: Session = Depends(get_session)):
    return session.exec(select(Areas)).all()


@router.post("/areas", response_model=Areas, status_code=201)
def create_area(area: AreasCreate, session: Session = Depends(get_session)):
    db = Areas(**area.model_dump())
    session.add(db)
    session.commit()
    session.refresh(db)
    return db


@router.put("/areas/{id_area}", response_model=Areas)
def update_area(id_area: int, area_update: AreasCreate, session: Session = Depends(get_session)):
    db_area = session.get(Areas, id_area)
    if not db_area:
        raise HTTPException(status_code=404, detail="Area no encontrada")
    db_area.nombre = area_update.nombre
    db_area.max_horas_dia = area_update.max_horas_dia
    session.add(db_area)
    session.commit()
    session.refresh(db_area)
    return db_area


@router.delete("/areas/{id_area}")
def delete_area(id_area: int, session: Session = Depends(get_session)):
    db_area = session.get(Areas, id_area)
    if not db_area:
        raise HTTPException(status_code=404, detail="Area no encontrada")
    session.delete(db_area)
    session.commit()
    return {"message": "Area borrada"}


# --- Cursos ---
@router.get("/cursos", response_model=List[Cursos])
def get_cursos(session: Session = Depends(get_session)):
    return session.exec(select(Cursos)).all()


@router.post("/cursos", response_model=Cursos, status_code=201)
def create_curso(curso: CursosCreate, session: Session = Depends(get_session)):
    _validate_fk(session, Areas, curso.id_area, "Area")
    db = Cursos(**curso.model_dump())
    session.add(db)
    session.commit()
    session.refresh(db)
    return db


@router.put("/cursos/{id_curso}", response_model=Cursos)
def update_curso(id_curso: int, curso_update: CursosCreate, session: Session = Depends(get_session)):
    db_curso = session.get(Cursos, id_curso)
    if not db_curso:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    _validate_fk(session, Areas, curso_update.id_area, "Area")
    db_curso.nombre_curso = curso_update.nombre_curso
    db_curso.id_area = curso_update.id_area
    session.add(db_curso)
    session.commit()
    session.refresh(db_curso)
    return db_curso


@router.delete("/cursos/{id_curso}")
def delete_curso(id_curso: int, session: Session = Depends(get_session)):
    db_curso = session.get(Cursos, id_curso)
    if not db_curso:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    session.delete(db_curso)
    session.commit()
    return {"message": "Curso borrado"}


# --- Profesores ---
@router.get("/profesores", response_model=List[Profesores])
def get_profesores(session: Session = Depends(get_session)):
    return session.exec(select(Profesores)).all()


@router.post("/profesores", response_model=Profesores, status_code=201)
def create_profesor(profesor: ProfesoresCreate, session: Session = Depends(get_session)):
    db = Profesores(**profesor.model_dump())
    session.add(db)
    session.commit()
    session.refresh(db)
    return db


@router.put("/profesores/{id_profesor}", response_model=Profesores)
def update_profesor(id_profesor: int, profesor_update: ProfesoresCreate, session: Session = Depends(get_session)):
    db_profesor = session.get(Profesores, id_profesor)
    if not db_profesor:
        raise HTTPException(status_code=404, detail="Profesor no encontrado")
    db_profesor.nombre_profesor = profesor_update.nombre_profesor
    session.add(db_profesor)
    session.commit()
    session.refresh(db_profesor)
    return db_profesor


@router.delete("/profesores/{id_profesor}")
def delete_profesor(id_profesor: int, session: Session = Depends(get_session)):
    db_profesor = session.get(Profesores, id_profesor)
    if not db_profesor:
        raise HTTPException(status_code=404, detail="Profesor no encontrado")
    session.delete(db_profesor)
    session.commit()
    return {"message": "Profesor borrado"}


# --- Profesor-Curso ---
@router.get("/profesor-curso", response_model=List[ProfesorCurso])
def get_profesor_curso(session: Session = Depends(get_session)):
    return session.exec(select(ProfesorCurso)).all()


@router.post("/profesor-curso", response_model=ProfesorCurso, status_code=201)
def create_profesor_curso(pc: ProfesorCursoCreate, session: Session = Depends(get_session)):
    _validate_fk(session, Profesores, pc.id_profesor, "Profesor")
    _validate_fk(session, Cursos, pc.id_curso, "Curso")
    existing = session.exec(
        select(ProfesorCurso).where(
            ProfesorCurso.id_profesor == pc.id_profesor,
            ProfesorCurso.id_curso == pc.id_curso
        )
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Este profesor ya tiene asignado este curso")
    db = ProfesorCurso(**pc.model_dump())
    session.add(db)
    session.commit()
    session.refresh(db)
    return db


# --- Secciones ---
@router.get("/secciones", response_model=List[Seccion])
def get_secciones(session: Session = Depends(get_session)):
    return session.exec(select(Seccion)).all()


@router.post("/secciones", response_model=Seccion, status_code=201)
def create_seccion(seccion: SeccionCreate, session: Session = Depends(get_session)):
    _validate_fk(session, Sedes, seccion.id_sede, "Sede")
    _validate_fk(session, Grado, seccion.id_grado, "Grado")
    db = Seccion(**seccion.model_dump())
    session.add(db)
    session.commit()
    session.refresh(db)
    return db


@router.put("/secciones/{id_seccion}", response_model=Seccion)
def update_seccion(id_seccion: int, seccion_update: SeccionCreate, session: Session = Depends(get_session)):
    db_seccion = session.get(Seccion, id_seccion)
    if not db_seccion:
        raise HTTPException(status_code=404, detail="Seccion no encontrada")
    _validate_fk(session, Sedes, seccion_update.id_sede, "Sede")
    _validate_fk(session, Grado, seccion_update.id_grado, "Grado")
    db_seccion.nombre = seccion_update.nombre
    db_seccion.id_grado = seccion_update.id_grado
    db_seccion.id_sede = seccion_update.id_sede
    session.add(db_seccion)
    session.commit()
    session.refresh(db_seccion)
    return db_seccion


@router.delete("/secciones/{id_seccion}")
def delete_seccion(id_seccion: int, session: Session = Depends(get_session)):
    db_seccion = session.get(Seccion, id_seccion)
    if not db_seccion:
        raise HTTPException(status_code=404, detail="Seccion no encontrada")
    session.delete(db_seccion)
    session.commit()
    return {"message": "Seccion borrada"}


# --- Plan de Estudio ---
@router.get("/planes", response_model=List[PlanEstudio])
def get_planes(session: Session = Depends(get_session)):
    return session.exec(select(PlanEstudio)).all()


@router.post("/planes", response_model=PlanEstudio, status_code=201)
def create_plan(plan: PlanEstudioCreate, session: Session = Depends(get_session)):
    _validate_fk(session, Grado, plan.id_grado, "Grado")
    _validate_fk(session, Cursos, plan.id_curso, "Curso")
    db = PlanEstudio(**plan.model_dump())
    session.add(db)
    session.commit()
    session.refresh(db)
    return db


@router.put("/planes/{id_plan}", response_model=PlanEstudio)
def update_plan(id_plan: int, plan_update: PlanEstudioCreate, session: Session = Depends(get_session)):
    db_plan = session.get(PlanEstudio, id_plan)
    if not db_plan:
        raise HTTPException(status_code=404, detail="Plan de Estudio no encontrado")
    _validate_fk(session, Grado, plan_update.id_grado, "Grado")
    _validate_fk(session, Cursos, plan_update.id_curso, "Curso")
    db_plan.id_grado = plan_update.id_grado
    db_plan.id_curso = plan_update.id_curso
    db_plan.horas_semanales = plan_update.horas_semanales
    session.add(db_plan)
    session.commit()
    session.refresh(db_plan)
    return db_plan


@router.delete("/planes/{id_plan}")
def delete_plan(id_plan: int, session: Session = Depends(get_session)):
    db_plan = session.get(PlanEstudio, id_plan)
    if not db_plan:
        raise HTTPException(status_code=404, detail="Plan de Estudio no encontrado")
    session.delete(db_plan)
    session.commit()
    return {"message": "Plan de Estudio borrado"}


# --- Sección-Turno ---
@router.get("/seccion-turno", response_model=List[SeccionTurno])
def get_seccion_turno(session: Session = Depends(get_session)):
    return session.exec(select(SeccionTurno)).all()


@router.post("/seccion-turno", response_model=SeccionTurno, status_code=201)
def create_seccion_turno(st: SeccionTurnoCreate, session: Session = Depends(get_session)):
    from backend.models import Sedes, Turno, Dias
    _validate_fk(session, Seccion, st.id_seccion, "Seccion")
    _validate_fk(session, Turno, st.id_turno, "Turno")
    _validate_fk(session, Dias, st.id_dia, "Dia")
    db = SeccionTurno(**st.model_dump())
    session.add(db)
    session.commit()
    session.refresh(db)
    return db


@router.delete("/seccion-turno/{id_seccion_turno}")
def delete_seccion_turno(id_seccion_turno: int, session: Session = Depends(get_session)):
    db = session.get(SeccionTurno, id_seccion_turno)
    if not db:
        raise HTTPException(status_code=404)
    session.delete(db)
    session.commit()
    return {"message": "Borrado"}


# --- Tutorías ---
@router.get("/tutorias")
def get_tutorias(session: Session = Depends(get_session)):
    return session.exec(select(Tutoria)).all()


@router.post("/tutorias", status_code=201)
def create_tutoria(tutoria: TutoriaCreate, session: Session = Depends(get_session)):
    _validate_fk(session, Seccion, tutoria.id_seccion, "Seccion")
    _validate_fk(session, Profesores, tutoria.id_profesor, "Profesor")
    existing = session.exec(
        select(Tutoria).where(
            Tutoria.id_seccion == tutoria.id_seccion
        )
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Esta seccion ya tiene un tutor asignado")
    db = Tutoria(**tutoria.model_dump())
    session.add(db)
    session.commit()
    session.refresh(db)
    return db


@router.delete("/tutorias/{id_tutoria}")
def delete_tutoria(id_tutoria: int, session: Session = Depends(get_session)):
    db_tutoria = session.get(Tutoria, id_tutoria)
    if not db_tutoria:
        raise HTTPException(status_code=404, detail="Tutoria no encontrada")
    session.delete(db_tutoria)
    session.commit()
    return {"message": "Tutoria borrada"}
