import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlmodel import Session, select

from backend.config import settings
from backend.database import create_db_and_tables, engine
from backend.models import Usuario
from backend.exceptions import AppError
from backend.logging_config import setup_logging

from backend.routes.auth import router as auth_router
from backend.routes.infra import router as infra_router
from backend.routes.academic import router as academic_router
from backend.routes.availability import router as availability_router
from backend.routes.schedule import router as schedule_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("Iniciando %s v%s [%s]", settings.APP_NAME, settings.APP_VERSION, settings.ENVIRONMENT)
    create_db_and_tables()
    with Session(engine) as session:
        admin = session.exec(select(Usuario).where(Usuario.email == "admin@colegio.com")).first()
        if not admin:
            session.add(Usuario(email="admin@colegio.com", nombre="Administrador"))
            session.commit()
            logger.info("Usuario admin creado")
    yield
    logger.info("Aplicación finalizada")


app = FastAPI(
    title=settings.APP_NAME,
    description="Backend refactorizado para el nuevo esquema de BD",
    version=settings.APP_VERSION,
    lifespan=lifespan
)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    logger.warning("Error controlado [%s]: %s", exc.status_code, exc.message)
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "error", "detail": exc.message, "errors": exc.errors}
    )


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception):
    logger.exception("Error no controlado en %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"status": "error", "detail": "Error interno del servidor"}
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(infra_router)
app.include_router(academic_router)
app.include_router(availability_router)
app.include_router(schedule_router)


@app.get("/")
def read_root():
    return {"message": "Bienvenido al Sistema Integral de Horarios V2"}
