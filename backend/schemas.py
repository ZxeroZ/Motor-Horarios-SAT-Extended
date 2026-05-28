from typing import Optional
from pydantic import BaseModel, Field


# --- Infraestructura ---
class ColegioUpdate(BaseModel):
    nombre_colegio: str = Field(..., min_length=1, max_length=200)


class SedesCreate(BaseModel):
    id_colegio: Optional[int] = None
    nombre_sede: str = Field(..., min_length=1, max_length=200)


class GradoCreate(BaseModel):
    numero: int = Field(..., ge=1, le=12)


class DiasCreate(BaseModel):
    nombre_dia: str = Field(..., min_length=1, max_length=20)
    orden: int = Field(..., ge=1)


class TurnoCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=50)


class BloqueCreate(BaseModel):
    id_turno: int
    numero_bloque: Optional[int] = Field(None, ge=1)
    hora_inicio: Optional[str] = None
    hora_final: Optional[str] = None


class GradoDiaConfigCreate(BaseModel):
    id_grado: int
    id_dia: int
    bloques_dia: int = Field(..., ge=1, le=24)


# --- Académico ---
class AreasCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    max_horas_dia: Optional[int] = Field(None, ge=1, le=24)


class CursosCreate(BaseModel):
    nombre_curso: str = Field(..., min_length=1, max_length=100)
    id_area: int


class ProfesoresCreate(BaseModel):
    nombre_profesor: str = Field(..., min_length=1, max_length=200)


class ProfesorCursoCreate(BaseModel):
    id_profesor: int
    id_curso: int


class SeccionCreate(BaseModel):
    id_sede: int
    id_grado: int
    nombre: Optional[str] = Field(None, max_length=50)


class PlanEstudioCreate(BaseModel):
    id_grado: int
    id_curso: int
    horas_semanales: int = Field(..., ge=1, le=40)


class SeccionTurnoCreate(BaseModel):
    id_seccion: int
    id_turno: int
    id_dia: int


class TutoriaCreate(BaseModel):
    id_seccion: int
    id_profesor: int


# --- Disponibilidad ---
class ProfesorDisponibilidadCreate(BaseModel):
    id_profesor: int
    id_dia: int
    id_turno: int
    id_sede: int
    nro_bloque: int = Field(..., ge=1)


class ProfesorPreferenciaCreate(BaseModel):
    id_profesor: int
    id_dia: int
    id_turno: int
    id_sede: int
    nro_bloque: int = Field(..., ge=1)


# --- Horario ---
class HorarioFinalCreate(BaseModel):
    id_seccion: int
    id_dia: int
    num_bloque: int = Field(..., ge=1)
    id_curso: int
    id_profesor: int
    id_turno: int


# --- Snapshot ---
class SnapshotUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=200)
    descripcion: Optional[str] = Field(None, max_length=500)
