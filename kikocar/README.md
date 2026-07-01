# 🏗️ Kikocar Construcción — Sistema de Gestión de Flota

Sistema modular y desacoplado para la administración de órdenes de servicio, control de combustible, mantenimiento predictivo con IA y monitoreo de flota de grúas en tiempo real.

---

## 📦 Stack Tecnológico

| Capa | Tecnología | Propósito |
|------|-----------|-----------|
| **Backend** | [FastAPI](https://fastapi.tiangolo.com/) (Python 3.14) | API REST con tipado estático, inyección manual de dependencias |
| **Frontend** | [Streamlit](https://streamlit.io/) 1.41 | UI reactiva con sesión por roles y paneles en tiempo real |
| **Base de Datos** | [Supabase](https://supabase.com/) (PostgreSQL 15) | Base de datos relacional con API auto-generada, RLS, tiempo real |
| **ORM / Cliente DB** | [supabase-py](https://github.com/supabase/supabase-py) 2.6 | Cliente nativo para operaciones CRUD sobre Supabase |
| **Validación** | [Pydantic](https://docs.pydantic.dev/) 2.10 | Modelos de dominio con validación estricta y tipado |
| **ML / Reglas** | Árbol de Decisión propietario | Modelo multi-variable para diagnóstico predictivo |
| **Frontend Data** | [pandas](https://pandas.pydata.org/) 2.2, [requests](https://requests.readthedocs.io/) | Procesamiento de tablas y consumo de API |

---

## 🧠 Arquitectura Hexagonal (Ports & Adapters)

```
┌─────────────────────────────────────────────────────────┐
│                    ENTRADA (Drivers)                      │
│  ┌──────────────┐          ┌──────────────────────────┐ │
│  │  Streamlit    │          │       FastAPI            │ │
│  │  (UI Web)     │  HTTP    │  (REST API)              │ │
│  │  app.py       │ ──────►  │  main.py                 │ │
│  └──────────────┘          └────────────┬─────────────┘ │
└──────────────────────────────────────────────────────────┘
                                          │
┌─────────────────────────────────────────▼─────────────────┐
│              PUERTOS (Application/Ports)                    │
│  ┌────────────────────────────────────────────────────┐   │
│  │  repository_port.py  (Interfaces abstractas)        │   │
│  │  • MaquinaRepositoryPort   • OperadorRepositoryPort │   │
│  │  • OrdenRepositoryPort     • ReporteRepositoryPort  │   │
│  │  • MantenimientoRepositoryPort                      │   │
│  │  • DashboardAnalyticsPort                           │   │
│  └────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────┘
                                          │
┌─────────────────────────────────────────▼─────────────────┐
│              DOMINIO (Domain/Entities)                      │
│  ┌────────────────────────────────────────────────────┐   │
│  │  entities.py  (Pydantic puros, sin dependencias)    │   │
│  │  • Maquina  • Operador  • OrdenServicio             │   │
│  │  • ReporteDiario  • Mantenimiento                   │   │
│  └────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────┘
                                          │
┌─────────────────────────────────────────▼─────────────────┐
│           ADAPTADORES DE SALIDA (Driven)                    │
│  ┌──────────────────────┐  ┌──────────────────────────┐   │
│  │  supabase_repository │  │  predictive_adapter.py   │   │
│  │  • CRUD real contra  │  │  • Árbol de decisión     │   │
│  │    Supabase/Postgres │  │  • 6 variables:          │   │
│  │  • Mapeo fila→entidad│  │    - horas desde mant    │   │
│  └──────────────────────┘  │    - vida útil           │   │
│                             │    - consumo vs teórico  │   │
│                             │    - capacidad ton       │   │
│                             │    - alertas previas     │   │
│                             │    - tipo equipo/frente  │   │
│                             └──────────────────────────┘   │
└──────────────────────────────────────────────────────────┘
```

### Principios
- **Dominio puro**: Las entidades de negocio no dependen de frameworks, BD ni UI
- **Puertos abstractos**: Interfaces que definen contratos sin implementación
- **Adaptadores intercambiables**: Se puede cambiar Supabase por MySQL, MongoDB, etc. sin tocar una línea de dominio
- **Inyección manual de dependencias**: Sin frameworks pesados, todo explícito

---

## 🗂️ Estructura del Proyecto

```
kikocar/
├── supabase/
│   ├── schema.sql              # DDL completo + seed data
│   ├── schema_v2.sql            # Flota específica (5 grúas)
│   └── migracion_v4.sql         # Fallas reportadas + mantenimientos
│
├── src/
│   ├── domain/
│   │   └── entities.py          # Entidades Pydantic puras
│   │
│   ├── application/
│   │   └── ports/
│   │       └── repository_port.py  # Interfaces abstractas (ABC)
│   │
│   └── infrastructure/
│       └── adapters/
│           ├── predictive_adapter.py   # ML multi-variable
│           └── supabase_repository.py  # Implementación real Supabase
│
├── backend/
│   └── main.py                  # FastAPI — 12 endpoints REST
│
├── frontend/
│   └── app.py                   # Streamlit — 7 pestañas (Admin) + 2 (Operador)
│
├── .env.example                 # Template de variables de entorno
├── requirements.txt             # Dependencias Python
└── README.md
```

---

## 🚀 Instalación y Ejecución

### 1. Requisitos
- Python 3.12+
- Cuenta gratuita en [Supabase](https://supabase.com/)
- PowerShell (Windows) o bash (Linux/Mac)

### 2. Clonar e instalar dependencias

```bash
# Windows PowerShell
cd kikocar
& "$env:LOCALAPPDATA\Programs\Python\Python314\python.exe" -m pip install -r requirements.txt

# Linux/Mac
python3 -m pip install -r requirements.txt
```

### 3. Configurar Supabase

1. Crear proyecto en [supabase.com](https://supabase.com/)
2. Ir a **SQL Editor** → ejecutar en orden:
   - `supabase/schema_v2.sql` (esquema + datos iniciales)
   - `supabase/migracion_v4.sql` (fallas, mantenimientos)
3. Ir a **Project Settings → API** → copiar:
   - `Project URL` (ej: `https://xxxxx.supabase.co`)
   - `service_role` secret key

### 4. Variables de entorno

```bash
cp .env.example .env
```

Editar `.env`:

```env
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu_service_role_key
API_BASE_URL=http://127.0.0.1:8000
```

### 5. Iniciar servicios

**Terminal 1 — Backend:**
```bash
# Windows
cd kikocar
& "$env:LOCALAPPDATA\Programs\Python\Python314\python.exe" -m uvicorn backend.main:app --reload

# Linux/Mac
cd kikocar
uvicorn backend.main:app --reload
```

**Terminal 2 — Frontend:**
```bash
# Windows
cd kikocar
& "$env:LOCALAPPDATA\Programs\Python\Python314\python.exe" -m streamlit run frontend/app.py

# Linux/Mac
cd kikocar
streamlit run frontend/app.py
```

### 6. Abrir navegador

| Servicio | URL |
|----------|-----|
| Frontend | [http://localhost:8501](http://localhost:8501) |
| API Docs | [http://localhost:8000/docs](http://localhost:8000/docs) |

---

## 🧩 Endpoints de la API

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/api/v1/maquinaria` | Lista todas las grúas con horómetros y estado |
| `GET` | `/api/v1/maquinaria/{id}/diagnostico` | Diagnóstico ML de una máquina |
| `GET` | `/api/v1/operadores` | Lista de operadores disponibles |
| `POST` | `/api/v1/ordenes` | Crear orden de servicio |
| `GET` | `/api/v1/ordenes` | Órdenes activas con % avance |
| `GET` | `/api/v1/ordenes/operador/{id}` | Orden asignada a un operador |
| `POST` | `/api/v1/reportes` | Registrar parte diario (con validaciones) |
| `GET` | `/api/v1/reportes/ultimo/{orden_id}` | Último reporte (para precarga) |
| `GET` | `/api/v1/reportes/alertas` | Reportes con alerta de robo |
| `GET` | `/api/v1/reportes/atencion` | Reportes con fallas reportadas |
| `GET` | `/api/v1/reportes/predictivo` | Diagnósticos ML de todos los reportes |
| `POST` | `/api/v1/mantenimientos` | Registrar mantenimiento realizado |
| `GET` | `/api/v1/mantenimientos` | Historial de mantenimientos |
| `GET` | `/api/v1/dashboard/kpis` | KPIs (facturado, horas, flota) |

---

## 🧠 Modelo de Diagnóstico Predictivo (ML)

Árbol de decisión multi-variable que evalúa:

| Variable | Peso | Fuente |
|----------|------|--------|
| Horas desde último mantenimiento | 45% | `horometro_actual - ultimo_mant_horas` |
| Vida útil acumulada (fatiga) | 20% | `horometro_actual / 15000` |
| Relación consumo real vs teórico | 15% | `(gal_consumidos / horas) / consumo_teórico` |
| Capacidad de la grúa | 10% | `capacidad_ton / 500` |
| Historial de alertas de robo | 10% | `cantidad_alertas_previas * 0.15` |
| Tipo de equipo + frente | Factor | `oruga: 1.2, todoterreno: 1.1, móvil: 1.0` |

**Salidas:**
- `probabilidad_fallo` (0% – 99.99%)
- `dias_restantes_mant` (días hábiles hasta próximo mantenimiento)
- `criticidad`: 🔴 CRÍTICO (≥85%) | 🟡 MEDIO (≥60%) | 🟢 BAJO (<60%)
- `diagnostico`: Texto legible con recomendación

---

## 👥 Roles del Sistema

### ADMINISTRADOR (6 pestañas)

| Pestaña | Funcionalidad |
|---------|---------------|
| 📋 Registrar Orden | Crea orden + selecciona grúa/operador + ve diagnóstico ML |
| 📊 Dashboard y KPIs | Total facturado, horas, disponibilidad de flota |
| 📋 Órdenes Activas | Lista con % de avance por horas |
| ⛽ Control Combustible | Alertas de robo resaltadas en rojo |
| 🔧 Mantenimiento Predictivo | Semáforo de criticidad + registrar mantenimiento |
| 🛑 Alertas de Operador | Fallas reportadas por operadores en tiempo real |

### OPERADOR (2 pestañas)

| Pestaña | Funcionalidad |
|---------|---------------|
| 📄 Mi Orden Asignada | Datos de la orden activa |
| 📝 Rellenar Parte Diario | Horómetro final + combustible + reporte de fallas |

---

## ✅ Reglas de Negocio Implementadas

| Regla | Implementación |
|-------|---------------|
| **Robo de combustible** | `alerta = galones_consumidos > horas * consumo_teórico * 1.15` |
| **Horómetro continuo** | Cada parte usa el `horometro_fin` del anterior como `horometro_inicio` |
| **Fecha secuencial** | No se permiten partes con fecha anterior al último registrado |
| **Fallas → Alerta** | Si el operador reporta fallas, `requiere_atencion = True` y el admin lo ve |
| **Mantenimiento** | Al registrar mant, se actualiza `ultimo_mant_horas` y se guarda historial |
| **Progreso** | `% avance = horas_trabajadas / horas_estimadas * 100` |

---

## 📄 Licencia

Uso interno — Kikocar Construcción © 2026
