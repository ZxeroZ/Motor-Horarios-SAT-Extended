import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine, select
from sqlmodel.pool import StaticPool

from backend.main import app
from backend.database import get_session
from backend.models import (
    Colegio, Sedes, Grado, Dias, Turno, Areas, Cursos,
    Profesores, Seccion, PlanEstudio, GradoDiaConfig
)


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session

    # Crear usuario admin para tests (el lifespan no corre en tests)
    from backend.models import Usuario
    admin = session.exec(select(Usuario).where(Usuario.email == "admin@colegio.com")).first()
    if not admin:
        session.add(Usuario(email="admin@colegio.com", nombre="Administrador"))
        session.commit()

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def seed_infra(session: Session):
    """Crea datos base de infraestructura para los tests."""
    colegio = Colegio(nombre_colegio="Colegio Test")
    session.add(colegio)
    session.commit()
    session.refresh(colegio)

    sede = Sedes(nombre_sede="Sede Principal", id_colegio=colegio.id_colegio)
    session.add(sede)

    turno = Turno(nombre="Mañana")
    session.add(turno)

    dia = Dias(nombre_dia="Lunes", orden=1)
    session.add(dia)

    grado = Grado(numero=1)
    session.add(grado)

    area = Areas(nombre="Matemáticas", max_horas_dia=4)
    session.add(area)

    curso = Cursos(nombre_curso="Álgebra", id_area=None)
    session.add(curso)

    profesor = Profesores(nombre_profesor="Juan Pérez")
    session.add(profesor)

    session.commit()
    session.refresh(sede)
    session.refresh(turno)
    session.refresh(dia)
    session.refresh(grado)
    session.refresh(area)
    session.refresh(curso)
    session.refresh(profesor)

    return {
        "colegio": colegio,
        "sede": sede,
        "turno": turno,
        "dia": dia,
        "grado": grado,
        "area": area,
        "curso": curso,
        "profesor": profesor,
    }
