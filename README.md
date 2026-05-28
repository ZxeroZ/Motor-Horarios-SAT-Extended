<div align="center">

  <h1>🕐 Motor de Horarios Extended</h1>
  <p><strong>Generador de horarios escolares con optimización matemática.</strong></p>

  <p>
    <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
    <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI"/>
    <img src="https://img.shields.io/badge/OR_Tools-4285F4?style=for-the-badge&logo=google&logoColor=white" alt="Google OR-Tools"/>
    <img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" alt="React"/>
    <img src="https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite"/>
    <img src="https://img.shields.io/badge/Vite-B73BFE?style=for-the-badge&logo=vite&logoColor=white" alt="Vite"/>
  </p>

  <p>
    <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="License"/>
    <img src="https://img.shields.io/badge/Tests-37%20passed-brightgreen?style=flat-square" alt="Tests"/>
    <img src="https://img.shields.io/badge/Python-3.10+-blue?style=flat-square" alt="Python"/>
  </p>

  <br/>

  <p><em>Fork extendido del <a href="https://github.com/Clatt4noia/timetable-engine">timetable-engine original por Clatt4noia</a></em></p>

  <img src="https://raw.githubusercontent.com/Platane/snk/output/github-contribution-grid-snake-dark.svg" alt="snake animation" width="100%"/>

</div>

---

## 🏗 Cómo está armado

### Backend (Python + FastAPI)

<div align="center">

| Capa | Tecnología |
|:----:|:----------:|
| 🐍 Lenguaje | Python 3.10+ |
| ⚡ API | FastAPI |
| 🗄️ BD | SQLite + SQLModel |
| 🧠 Motor | Google OR-Tools CP-SAT |
| ✅ Validación | Pydantic |
| 🧪 Tests | Pytest |

</div>

La API está organizada por dominios en routers separados:

```
backend/
├── main.py              ⚙️  Configuración de la app, CORS, lifespan
├── database.py          🗄️  Conexión a SQLite
├── models.py            📊 15+ tablas (SQLModel)
├── schemas.py           ✅  Validación de inputs (Pydantic)
├── engine_connector.py  🔌 Puente entre la BD y el motor matemático
├── exceptions.py        🚨 Errores personalizados
├── config.py            🔑 Variables de entorno
├── logging_config.py    📝 Logs configurados
└── routes/
    ├── auth.py          🔐 Login
    ├── infra.py         🏫 Sedes, Turnos, Bloques, Grados
    ├── academic.py      📚 Cursos, Profesores, Secciones, Planes
    ├── availability.py  📅 Disponibilidad y Preferencias docentes
    └── schedule.py      🕐 Generación, historial, snapshots
```

### Motor matemático (el corazón)

<div align="center">

```
📥 Loader → ✅ Validators → ⚙️ Preprocessor → 🧠 Model → 🚀 Solver → 📤 Exporter → 📊 Metrics
```

</div>

| Módulo | Qué hace |
|:------:|:---------|
| 📥 `loader.py` | Carga los datos del JSON |
| ✅ `validators.py` | Validación antes de procesar |
| ⚙️ `preprocessor.py` | Convierte datos jerárquicos a estructuras matemáticas |
| 🧠 `model.py` | Construye el modelo CP-SAT con restricciones |
| 🚀 `solver.py` | Ejecuta OR-Tools (máx 60 segundos) |
| 📤 `exporter.py` | Formatea la solución |
| 📊 `metrics.py` | Calcula métricas post-ejecución |

El solver busca maximizar un puntaje que suma: que se asignen todos los cursos (+10,000), que caigan en el horario preferido del profesor (+500), y que los bloques sean contiguos (+100).

### Frontend (React + Vite)

<div align="center">

![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![Vite](https://img.shields.io/badge/Vite-B73BFE?style=for-the-badge&logo=vite&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)

</div>

```
frontend/src/
├── App.jsx              🎯 Componente principal (estado + lógica)
├── index.css            🎨 Estilos con glassmorphism
└── components/
    ├── Toast.jsx        🔔 Notificaciones emergentes
    ├── LoginForm.jsx    🔑 Pantalla de login
    ├── Sidebar.jsx      📱 Navegación lateral
    ├── ScheduleGrid.jsx 📅 La malla horaria como tal
    └── HistoryPanel.jsx 🕰️ Histórico de horarios generados
```

---

## ✨ Features

### Backend (by zero)

El backend no es solo un CRUD básico — tiene varias capas de lógica que lo hacen bastante completo para lo que necesitamos:

**📊 Gestión de datos:**
- CRUD completo para todas las entidades del dominio: Sedes, Turnos, Bloques, Grados, Secciones, Áreas, Cursos, Profesores, Planes de Estudio, Disponibilidad y Preferencias
- Cada endpoint tiene validación de inputs con Pydantic — no podés mandar campos vacíos, IDs que no existen, ni valores fuera de rango
- Las foreign keys se validan antes de hacer el INSERT/UPDATE, así que no vas a tener errores de integridad referencial a mitad de la carga

**🔐 Seguridad y configuración:**
- CORS configurable por ambiente (desarrollo vs producción) — ya no está hardcodeado como `*`
- Variables de entorno para todo: URL de la BD,logging, orígenes permitidos
- Logging configurado por nivel — los queries de SQL se silencian en producción

**🧠 Generación de horarios:**
- El endpoint de generación corre en un **thread separado** para no bloquear la API
- Barra de progreso real — el frontend puede consultar en qué paso va el motor (extrayendo datos, validando, preprocesando, modelando, resolviendo, guardando)
- Cada paso reporta progreso con porcentaje y mensaje descriptivo
- Timeout de seguridad de 120 segundos en el frontend

**🕰️ Sistema de historial (versionado):**
- Cuando generás un horario, se guarda automáticamente un **snapshot** con el JSON completo del resultado
- Cada snapshot tiene: nombre, fecha, estado (OPTIMAL/FEASIBLE/INFEASIBLE), tiempo de resolución, cantidad de asignaciones
- Puedes cargar cualquier snapshot anterior como horario activo — se reescribe la tabla `horario_final` con esos datos
- Puedes renombrar los snapshots para identificarlos mejor
- Puedes eliminar los que ya no necesitás
- El sistema trackea cuál snapshot está activo (el que se muestra en la malla)

**⚠️ Manejo de errores:**
- Excepciones personalizadas por tipo: ValidationError (422), EngineError (400), NotFoundError (404), ConflictError (409)
- Handler global de excepciones en FastAPI — cualquier error no controlado devuelve un 500 con mensaje genérico (no exponemos stack traces al frontend)
- Los errores del motor se distinguen de los errores de validación y de los errores de BD

**🧪 Tests:**
- 37 tests de integración con pytest
- Cada test usa una BD SQLite en memoria (no toca la BD real)
- Cubren: CRUD de infraestructura, validación de inputs, detección de duplicados, FK validation, login, y el flujo de generación

### Frontend

- <img src="https://img.shields.io/badge/-Glassmorphism-blueviolet" alt="Glass"/> Tema claro con efecto glass (blur + gradiente)
- <img src="https://img.shields.io/badge/-Material_Icons-grey" alt="Icons"/> Material Icons en vez de emojis
- <img src="https://img.shields.io/badge/-Paginación-green" alt="Paginación"/> Paginación en todas las tablas admin
- <img src="https://img.shields.io/badge/-Búsqueda-blue" alt="Búsqueda"/> Búsqueda en tiempo real
- <img src="https://img.shields.io/badge/-Toasts-orange" alt="Toasts"/> Notificaciones emergentes
- <img src="https://img.shields.io/badge/-Edición-purple" alt="Edición"/> Edición inline de registros
- <img src="https://img.shields.io/badge/-Progreso-red" alt="Progreso"/> Barra de progreso real al generar
- <img src="https://img.shields.io/badge/-Historial-cyan" alt="Historial"/> Cargar/renombrar/eliminar horarios previos

---

## ⚖️ Restricciones del motor

### 🔴 Restricciones duras (no se pueden romper)

| Restricción | Descripción |
|:-----------:|:------------|
| 🚫 **Profesor duplicado** | Un profesor no puede estar en dos clases al mismo tiempo |
| ✅ **Disponibilidad** | Un profesor solo se asigna si está disponible en ese día/horario/sede |
| 🚌 **Tiempo de traslado** | No se puede dictar en dos sedes en bloques consecutivos |
| 📊 **Límite de horas** | Límite de horas por área de conocimiento por día |
| 📅 **Repelencia de días** | Si un curso se divide en partes, no caen el mismo día |

### 🟢 Restricciones blandas (el intenta pero no garantiza)

| Restricción | Descripción |
|:-----------:|:------------|
| ⭐ **Preferencia docente** | Ubicar las clases en el horario que el profesor prefiere |

---

## 🚀 Para levantarlo

```bash
# 1. Clonar
git clone https://github.com/ZxeroZ/Motor-Horarios-SAT-Extended.git
cd Motor-Horarios-SAT-Extended

# 2. Entorno virtual
python -m venv venv
.\venv\Scripts\activate    # Windows
source venv/bin/activate   # Linux/Mac

# 3. Dependencias
pip install -r requirements.txt

# 4. Base de datos (esquema en blanco)
sqlite3 database.db < esquema_bd.sql

# 5. Backend (puerto 8000)
uvicorn backend.main:app --reload

# 6. Frontend (puerto 5173)
cd frontend
npm install
npm run dev
```

> **Nota:** La base de datos viene vacía. Los datos se cargan desde el panel de administración en el frontend.

---

## 🧪 Tests

```bash
python -m pytest tests/ -v
```

<div align="center">

![Tests](https://img.shields.io/badge/Pytest-37%20tests%20passed-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)

</div>

Hay 37 tests de integración que cubren los endpoints principales: CRUD de infraestructura, validación de inputs, duplicados, y el flujo de generación.

---

## 📁 Estructura del proyecto

```
Motor-Horarios-SAT-Extended/
├── 📄 main.py                 ← Entry point del motor standalone
├── 📄 requirements.txt        ← Dependencias Python
├── 📄 database.db             ← Base de datos SQLite
├── 📄 .env.example            ← Template de variables de entorno
├── 📂 backend/                ← API y lógica de negocio
├── 📂 engine/                 ← Motor matemático (OR-Tools)
├── 📂 frontend/               ← Interfaz web (React)
├── 📂 tests/                  ← Tests de integración
├── 📂 data/                   ← Datos de entrada y salida
└── 📂 utils/                  ← Utilidades compartidas
```

---

<div align="center">

![Backend by zero](https://img.shields.io/badge/Backend_by-Zero-purple?style=for-the-badge&logo=github&logoColor=white)

</div>
