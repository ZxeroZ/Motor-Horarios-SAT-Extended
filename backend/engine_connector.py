import json
import logging
import uuid
import threading
from datetime import datetime
from collections import defaultdict
from sqlmodel import Session, select
from backend.models import (
    Sedes, Dias, Areas, Cursos, Grado, Seccion, PlanEstudio,
    Profesores, ProfesorCurso, GradoDiaConfig, SeccionTurno, Turno, Tutoria,
    ProfesorDisponibilidad, ProfesorPreferencia, Bloque, HorarioSnapshot
)
from backend.exceptions import ValidationError, EngineError, DatabaseError
from engine.preprocessor import preprocesar
from engine.model import construir_modelo
from engine.solver import resolver_modelo
from utils.validators import validar_todo

logger = logging.getLogger(__name__)

# --- Progress Store ---
progress_store = {}


def get_progress(task_id: str) -> dict:
    return progress_store.get(task_id, {"status": "not_found"})


def _update_progress(task_id: str, step: str, percent: int, message: str):
    if task_id:
        progress_store[task_id] = {
            "status": "running",
            "step": step,
            "percent": percent,
            "message": message,
        }


def _batch_load(session: Session):
    """Carga todas las tablas relacionadas en queries mínimas y retorna dicts agrupados."""
    sedes = session.exec(select(Sedes)).all()
    turnos_db = session.exec(select(Turno)).all()
    dias_db = session.exec(select(Dias).order_by(Dias.orden)).all()
    areas = session.exec(select(Areas)).all()
    cursos = session.exec(select(Cursos)).all()
    grados = session.exec(select(Grado)).all()
    secciones = session.exec(select(Seccion)).all()
    profesores = session.exec(select(Profesores)).all()
    tutorias_db = session.exec(select(Tutoria)).all()

    all_planes = session.exec(select(PlanEstudio)).all()
    all_configs = session.exec(select(GradoDiaConfig)).all()
    all_sec_turnos = session.exec(select(SeccionTurno)).all()
    all_pcs = session.exec(select(ProfesorCurso)).all()
    all_disp = session.exec(select(ProfesorDisponibilidad)).all()
    all_pref = session.exec(select(ProfesorPreferencia)).all()

    sede_map = {s.id_sede: s.nombre_sede for s in sedes}
    dia_map = {d.id_dia: d.nombre_dia for d in dias_db}
    turno_map = {t.id_turno: t.nombre for t in turnos_db}

    planes_por_grado = defaultdict(list)
    for p in all_planes:
        planes_por_grado[p.id_grado].append(p)

    configs_por_grado = defaultdict(list)
    for c in all_configs:
        configs_por_grado[c.id_grado].append(c)

    sec_turnos_por_seccion = defaultdict(list)
    for st in all_sec_turnos:
        sec_turnos_por_seccion[st.id_seccion].append(st)

    pcs_por_profesor = defaultdict(list)
    for pc in all_pcs:
        pcs_por_profesor[pc.id_profesor].append(pc)

    disp_por_profesor = defaultdict(list)
    for d in all_disp:
        disp_por_profesor[d.id_profesor].append(d)

    pref_por_profesor = defaultdict(list)
    for p in all_pref:
        pref_por_profesor[p.id_profesor].append(p)

    return {
        "sedes": sedes,
        "turnos_db": turnos_db,
        "dias_db": dias_db,
        "areas": areas,
        "cursos": cursos,
        "grados": grados,
        "secciones": secciones,
        "profesores": profesores,
        "tutorias_db": tutorias_db,
        "sede_map": sede_map,
        "dia_map": dia_map,
        "turno_map": turno_map,
        "nombres_dias": [d.nombre_dia for d in dias_db],
        "nombres_turnos": [t.nombre for t in turnos_db] if turnos_db else ["Mañana", "Tarde"],
        "planes_por_grado": planes_por_grado,
        "configs_por_grado": configs_por_grado,
        "sec_turnos_por_seccion": sec_turnos_por_seccion,
        "pcs_por_profesor": pcs_por_profesor,
        "disp_por_profesor": disp_por_profesor,
        "pref_por_profesor": pref_por_profesor,
    }


def build_json_from_db(session: Session) -> dict:
    """Extrae datos de SQLite y construye el formato EXACTO que el motor CP-SAT espera."""
    b = _batch_load(session)

    datos = {
        "configuracion": {},
        "categorias": [],
        "cursos": [],
        "grados": [],
        "secciones": [],
        "profesores": [],
        "tutorias": {}
    }

    datos["configuracion"] = {
        "sedes": [s.nombre_sede for s in b["sedes"]],
        "turnos": b["nombres_turnos"],
        "dia_id_to_nombre": b["dia_map"],
        "turno_id_to_nombre": b["turno_map"]
    }

    for a in b["areas"]:
        datos["categorias"].append({
            "id": f"CAT_{a.id_area}",
            "nombre": a.nombre,
            "max_horas_dia": a.max_horas_dia
        })

    tutoria_id_bd = None
    for c in b["cursos"]:
        cid = "TUT1" if "Tutoría" in c.nombre_curso else f"CUR_{c.id_curso}"
        if cid == "TUT1":
            tutoria_id_bd = c.id_curso
        datos["cursos"].append({
            "id": cid,
            "nombre": c.nombre_curso,
            "categoria_id": f"CAT_{c.id_area}"
        })

    for g in b["grados"]:
        planes = b["planes_por_grado"].get(g.id_grado, [])
        configs = b["configs_por_grado"].get(g.id_grado, [])

        if configs:
            horario_plantilla = {}
            for cfg in configs:
                dia_nombre = b["dia_map"].get(cfg.id_dia)
                if dia_nombre:
                    horario_plantilla[dia_nombre] = cfg.bloques_dia
        else:
            horario_plantilla = {d: 6 for d in b["nombres_dias"]}

        datos["grados"].append({
            "id": f"GRA_{g.id_grado}",
            "nombre": f"{g.numero}°",
            "cursos_requeridos": [
                {
                    "curso_id": "TUT1" if p.id_curso == tutoria_id_bd else f"CUR_{p.id_curso}",
                    "horas_semanales": p.horas_semanales
                } for p in planes
            ],
            "horario_plantilla": horario_plantilla
        })

    for s in b["secciones"]:
        sec_turnos = b["sec_turnos_por_seccion"].get(s.id_seccion, [])
        if sec_turnos:
            disponibilidad = {}
            for st in sec_turnos:
                dia_nombre = b["dia_map"].get(st.id_dia)
                turno_nombre = b["turno_map"].get(st.id_turno)
                if dia_nombre and turno_nombre:
                    if dia_nombre not in disponibilidad:
                        disponibilidad[dia_nombre] = []
                    if turno_nombre not in disponibilidad[dia_nombre]:
                        disponibilidad[dia_nombre].append(turno_nombre)
        else:
            disponibilidad = {d: list(b["nombres_turnos"]) for d in b["nombres_dias"]}

        sede_nombre = b["sede_map"].get(s.id_sede, "Sede A")
        datos["secciones"].append({
            "id": f"SEC_{s.id_seccion}",
            "nombre": f"{s.nombre}",
            "grado": f"GRA_{s.id_grado}",
            "sede": sede_nombre,
            "disponibilidad": disponibilidad
        })

    todos_los_dias = b["dias_db"]
    turnos_db = b["turnos_db"]
    nombres_turnos = b["nombres_turnos"]

    max_bloques_por_dia = {}
    for cfg in b["configs_por_grado"].values():
        for c in cfg:
            dia_nombre = b["dia_map"].get(c.id_dia)
            if dia_nombre and c.bloques_dia:
                if c.bloques_dia > max_bloques_por_dia.get(dia_nombre, 0):
                    max_bloques_por_dia[dia_nombre] = c.bloques_dia

    for p in b["profesores"]:
        pcs = b["pcs_por_profesor"].get(p.id_profesor, [])
        disp_records = b["disp_por_profesor"].get(p.id_profesor, [])
        pref_records = b["pref_por_profesor"].get(p.id_profesor, [])

        sedes_del_prof = set()
        for dr in disp_records:
            sede_nombre = b["sede_map"].get(dr.id_sede)
            if sede_nombre:
                sedes_del_prof.add(sede_nombre)
        sedes_del_prof = list(sedes_del_prof)
        if not sedes_del_prof:
            sedes_del_prof = [s.nombre_sede for s in b["sedes"]]

        disponibilidad = {}
        if disp_records:
            grouped = defaultdict(set)
            for dr in disp_records:
                dia_n = b["dia_map"].get(dr.id_dia)
                turno_n = b["turno_map"].get(dr.id_turno)
                sede_n = b["sede_map"].get(dr.id_sede, "Sede A")
                if dia_n and turno_n:
                    grouped[(dia_n, turno_n, sede_n)].add(dr.nro_bloque)
            for (dia_n, turno_n, sede_n), bloques in grouped.items():
                if dia_n not in disponibilidad:
                    disponibilidad[dia_n] = {}
                if turno_n not in disponibilidad[dia_n]:
                    disponibilidad[dia_n][turno_n] = {}
                disponibilidad[dia_n][turno_n][sede_n] = sorted(bloques)
        else:
            for dia in todos_los_dias:
                dia_nombre = dia.nombre_dia
                max_b = max_bloques_por_dia.get(dia_nombre)
                if max_b is None:
                    continue
                slots = list(range(1, max_b + 1))
                disponibilidad[dia_nombre] = {}
                for t in turnos_db:
                    disponibilidad[dia_nombre][t.nombre] = {
                        sede: list(slots) for sede in sedes_del_prof
                    }

        prof_data = {
            "id": f"PROF_{p.id_profesor}",
            "nombre": p.nombre_profesor,
            "cursos_habilitados": ["TUT1" if pc.id_curso == tutoria_id_bd else f"CUR_{pc.id_curso}" for pc in pcs],
            "disponibilidad": disponibilidad
        }

        if pref_records:
            grouped_pref = defaultdict(set)
            for pr in pref_records:
                dia_n = b["dia_map"].get(pr.id_dia)
                turno_n = b["turno_map"].get(pr.id_turno)
                if dia_n and turno_n:
                    grouped_pref[(dia_n, turno_n)].add(pr.nro_bloque)
            disponibilidad_preferente = {}
            for (dia_n, turno_n), bloques in grouped_pref.items():
                if dia_n not in disponibilidad_preferente:
                    disponibilidad_preferente[dia_n] = {}
                disponibilidad_preferente[dia_n][turno_n] = {
                    sede: sorted(bloques) for sede in sedes_del_prof
                }
            prof_data["disponibilidad_preferente"] = disponibilidad_preferente

        datos["profesores"].append(prof_data)

    for t in b["tutorias_db"]:
        datos["tutorias"][f"SEC_{t.id_seccion}"] = f"PROF_{t.id_profesor}"

    return datos


def generar_horario_engine(session: Session, task_id: str = None) -> dict:
    """Proceso completo con reporte de progreso."""
    logger.info("Iniciando generación de horario...")

    _update_progress(task_id, "extracting", 10, "Leyendo base de datos...")
    datos = build_json_from_db(session)

    _update_progress(task_id, "validating", 20, "Validando integridad...")
    errores = validar_todo(datos)
    if errores:
        if task_id:
            progress_store[task_id] = {"status": "error", "message": "Error de validación", "errors": errores}
        raise ValidationError(errors=errores)

    try:
        _update_progress(task_id, "preprocessing", 35, "Construyendo estructuras...")
        datos_procesados = preprocesar(datos)

        _update_progress(task_id, "modeling", 50, "Generando restricciones CP-SAT...")
        modelo, variables_x = construir_modelo(datos_procesados)

        _update_progress(task_id, "solving", 65, "Buscando solución óptima...")
        dict_resultado = resolver_modelo(modelo, variables_x)

        if dict_resultado.get("estado") in ("OPTIMAL", "FEASIBLE") and dict_resultado.get("asignaciones"):
            _update_progress(task_id, "saving", 90, "Persistiendo horario...")
            _guardar_horario(session, dict_resultado["asignaciones"])
            _guardar_snapshot(session, dict_resultado)
        else:
            logger.warning("Solver no encontró solución: %s", dict_resultado.get("estado"))

        # Escritura atómica: status + resultado juntos
        if task_id:
            progress_store[task_id] = {
                "status": "done",
                "step": "done",
                "percent": 100,
                "message": "¡Horario generado!",
                "resultado": dict_resultado
            }

        return {
            "status": "success",
            "resultado": dict_resultado
        }
    except ValidationError:
        raise
    except Exception as e:
        logger.exception("Error inesperado durante la generación")
        if task_id:
            progress_store[task_id] = {"status": "error", "message": str(e)}
        raise EngineError(message=f"Error durante la ejecución del motor: {str(e)}")


def start_generation(db_engine) -> str:
    """Lanza la generación en un thread aparte y devuelve task_id."""
    task_id = str(uuid.uuid4())[:8]
    progress_store[task_id] = {"status": "starting", "step": "init", "percent": 0, "message": "Iniciando..."}

    def _run():
        from sqlmodel import Session
        with Session(db_engine) as session:
            try:
                generar_horario_engine(session, task_id)
            except Exception as e:
                progress_store[task_id] = {"status": "error", "message": str(e)}

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
    return task_id


def _guardar_horario(session: Session, asignaciones: list):
    """Persiste las asignaciones del motor en la tabla horario_final."""
    from backend.models import HorarioFinal

    old = session.exec(select(HorarioFinal)).all()
    for o in old:
        session.delete(o)
    session.commit()

    dias_db = session.exec(select(Dias)).all()
    dia_map = {d.nombre_dia: d.id_dia for d in dias_db}

    turnos_db = session.exec(select(Turno)).all()
    turno_map = {t.nombre: t.id_turno for t in turnos_db}

    for asig in asignaciones:
        sec_id = int(asig["seccion_id"].replace("SEC_", ""))

        if asig["curso_id"] == "TUT1":
            from backend.models import Cursos
            tut_curso = session.exec(select(Cursos).where(Cursos.nombre_curso.like("%Tutoría%"))).first()
            cur_id = tut_curso.id_curso if tut_curso else 18
        else:
            cur_id = int(asig["curso_id"].replace("CUR_", ""))

        prof_id = int(asig["profesor_id"].replace("PROF_", ""))
        id_dia = dia_map.get(asig["dia"])
        id_turno = turno_map.get(asig.get("turno", "Mañana"))

        slot_inicio = asig.get("slot_inicio", 0)
        horas = asig.get("horas", 1)

        for i in range(horas):
            num_bloque = slot_inicio + i + 1
            session.add(HorarioFinal(
                id_seccion=sec_id,
                id_dia=id_dia,
                num_bloque=num_bloque,
                id_turno=id_turno,
                id_curso=cur_id,
                id_profesor=prof_id
            ))

    session.commit()


def _guardar_snapshot(session: Session, dict_resultado: dict):
    """Guarda un snapshot del horario generado."""
    old_active = session.exec(select(HorarioSnapshot).where(HorarioSnapshot.is_active == True)).all()
    for o in old_active:
        o.is_active = False
        session.add(o)

    now = datetime.now()
    nombre = f"Horario {now.strftime('%d/%m %H:%M')}"

    snapshot = HorarioSnapshot(
        nombre=nombre,
        json_data=json.dumps(dict_resultado, ensure_ascii=False),
        asignaciones_count=len(dict_resultado.get("asignaciones", [])),
        estado=dict_resultado.get("estado"),
        tiempo_segundos=dict_resultado.get("estadisticas", {}).get("tiempo_segundos"),
        is_active=True,
        created_at=now.isoformat()
    )
    session.add(snapshot)
    session.commit()
    logger.info("Snapshot guardado: %s", nombre)
