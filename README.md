<div align="center">
  <h1>Motor de Horarios Extended</h1>
  <p><em>Generador de horarios escolares con optimización matemática.</em></p>

  <p>
    <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
    <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI"/>
    <img src="https://img.shields.io/badge/OR_Tools-4285F4?style=for-the-badge&logo=google&logoColor=white" alt="Google OR-Tools"/>
    <img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" alt="React"/>
    <img src="https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite"/>
  </p>
  <p>
    <em>Fork extendido del <a href="https://github.com/Clatt4noia/timetable-engine">timetable-engine original por Clatt4noia</a></em>
  </p>
</div>

---

## De qué va esto

Básicamente es una herramienta para generar horarios de clases automáticamente. Le tirás los datos del colegio (profesores, cursos, secciones, disponibilidad) y el motor busca la mejor combinación posible usando programación de restricciones.

No es un CRUD más — la parte interesante es el solver que resuelve un problema NP-Hard con OR-Tools. El backend maneja la lógica de negocio y el frontend muestra todo bonito.

---

## Cómo está armado

### Backend (Python + FastAPI)

La API está organizada por dominios en routers separados:

```
backend/
├── main.py              → Configuración de la app, CORS, lifespan
├── database.py          → Conexión a SQLite
├── models.py            → 15+ tablas (SQLModel)
├── schemas.py           → Validación de inputs (Pydantic)
├── engine_connector.py  → Puente entre la BD y el motor matemático
├── exceptions.py        → Errores personalizados
├── config.py            → Variables de entorno
├── logging_config.py    → Logs configurados
└── routes/
    ├── auth.py          → Login
    ├── infra.py         → Sedes, Turnos, Bloques, Grados
    ├── academic.py      → Cursos, Profesores, Secciones, Planes
    ├── availability.py  → Disponibilidad y Preferencias docentes
    └── schedule.py      → Generación, historial, snapshots
```

**Lo que hace cada parte:**
- `engine_connector.py` es el más heavy — lee toda la BD, la transforma al formato que entiende el motor, y luego guarda el resultado
- `routes/schedule.py` maneja la generación con progreso en tiempo real (threading)
- `schemas.py` valida que no mandes basura al backend (campos vacíos, IDs que no existen, etc.)

### Motor matemático (el corazón)

```
engine/
├── loader.py       → Carga los datos del JSON
├── validators.py   → Validación antes de procesar
├── preprocessor.py → Convierte datos jerárquicos a estructuras matemáticas
├── model.py        → Construye el modelo CP-SAT con restricciones
├── solver.py       → Ejecuta OR-Tools (máx 60 segundos)
├── exporter.py     → Formatea la solución
└── metrics.py      → Calcula métricas post-ejecución
```

El solver busca maximizar un puntaje que suma: que se asignen todos los cursos (+10,000), que caigan en el horario preferido del profesor (+500), y que los bloques sean contiguos (+100).

### Frontend (React + Vite)

```
frontend/src/
├── App.jsx              → Componente principal (estado + lógica)
├── index.css            → Estilos con glassmorphism
└── components/
    ├── Toast.jsx        → Notificaciones emergentes
    ├── LoginForm.jsx    → Pantalla de login
    ├── Sidebar.jsx      → Navegación lateral
    ├── ScheduleGrid.jsx → La malla horaria como tal
    └── HistoryPanel.jsx → Histórico de horarios generados
```

**Features del frontend:**
- Tema claro con efecto glass (blur sobre gradiente)
- Material Icons en vez de emojis
- Paginación y búsqueda en todas las tablas de administración
- Toasts para feedback de acciones
- Confirmación antes de borrar
- Edición inline de registros
- Barra de progreso real cuando se genera el horario
- Historial de todos los horarios generados (cargar, renombrar, eliminar)

---

## Restricciones del motor

El solver respeta estas reglas:

**Restricciones duras (no se pueden romper):**
- Un profesor no puede estar en dos clases al mismo tiempo
- Un profesor solo se asigna si está disponible en ese día/horario/sede
- No se puede dictar en dos sedes en bloques consecutivos (tiempo de traslado)
- Límite de horas por área de conocimiento por día
- Si un curso se divide en partes, no caen el mismo día

**Restricciones blandas (el intenta pero no garantiza):**
- Ubicar las clases en el horario que el profesor prefiere

---

## Para levantarlo

```bash
# Clonar
git clone https://github.com/ZxeroZ/Motor-Horarios-SAT-Extended.git
cd Motor-Horarios-SAT-Extended

# Entorno virtual
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Dependencias
pip install -r requirements.txt

# Base de datos (esquema en blanco)
sqlite3 database.db < esquema_bd.sql

# Backend (puerto 8000)
uvicorn backend.main:app --reload

# Frontend (puerto 5173)
cd frontend
npm install
npm run dev
```

La base de datos viene vacía. Los datos se cargan desde el panel de administración en el frontend, o podés usar el seeder con un JSON de prueba.

**Variables de entorno (opcional):** Copiá `.env.example` a `.env` y configurá lo que necesites.

---

## Tests

```bash
python -m pytest tests/ -v
```

Hay 37 tests de integración que cubren los endpoints principales: CRUD de infraestructura, validación de inputs, duplicados, y el flujo de generación.

---

## Cosas que me gustaría mejorar a futuro

- [ ] Editor visual de horarios (arrastrar bloques)
- [ ] Validación en tiempo real al editar
- [ ] Exportar a PDF
- [ ] Soporte para múltiples colegios
- [ ] Dashboard con estadísticas de uso

---

<div align="center">
  <i>Armado con paciencia, café y algo de matemáticas</i>
</div>
