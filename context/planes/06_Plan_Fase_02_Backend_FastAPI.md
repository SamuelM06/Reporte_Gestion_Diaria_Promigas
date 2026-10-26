# ⚙️ Plan Fase 02 — Backend (FastAPI)

**Proyecto:** Reporte de Gestión Diaria - Retención Promigas
**Stack:** Python 3.11+ · FastAPI · SQLAlchemy 2.x · psycopg2 · Pydantic v2 · Uvicorn
**Base de datos:** PostgreSQL 16.14 — esquema `gestion_diaria` (Fase 01)
**Última actualización:** 21 de octubre de 2026
**Estado:** ⏳ NO INICIADA — bloqueada por la puerta G4 de la Fase 01

> ⚠️ **Prerrequisito duro:** esta fase no inicia hasta que la Fase 01 (base de datos)
> esté cerrada con la puerta G4: modelo dimensional publicado + KPIs aprobados +
> `fact_gestion` cuadrando al 100% con el staging. Construir la API sobre datos no
> auditados solo propagaría cifras erróneas al frontend.

---

## 1. Objetivo

Exponer la base de datos (ya armada en la Fase 01) mediante una **API REST** que sirva
de única puerta de entrada para el frontend (React/Astro) y para los reportes, con:

- Autenticación y autorización por roles.
- Endpoints de consulta filtrada y paginada sobre `fact_gestion`, `fact_pqrs` y las
  dimensiones.
- Endpoints de KPIs (retención, abandono, motivos, operadores, calidad del dato).
- Endpoints de escritura para la **tipificación** y las **cancelaciones** que realizan
  los asesores desde el aplicativo (conectados al esquema para que los reportes se
  alimenten).
- Documentación OpenAPI automática y tests.

---

## 2. Stack y estructura propuesta

```
backend/
├── app/
│   ├── main.py                 # FastAPI app, CORS, middlewares, routers
│   ├── core/
│   │   ├── config.py           # Settings (pydantic-settings, .env)
│   │   ├── security.py         # JWT, hashing, roles
│   │   └── database.py         # Engine SQLAlchemy, session, sslmode=require
│   ├── api/
│   │   ├── deps.py             # Dependencias (get_db, get_current_user, roles)
│   │   └── v1/
│   │       ├── health.py
│   │       ├── auth.py
│   │       ├── gaseras.py
│   │       ├── cabinas.py
│   │       ├── resultados.py
│   │       ├── motivos.py
│   │       ├── operadores.py
│   │       ├── gestion.py      # fact_gestion (lectura + tipificación)
│   │       ├── pqrs.py
│   │       ├── abandono.py
│   │       ├── kpis.py
│   │       └── calidad.py      # cargas, rechazos, POR_REVISAR
│   ├── models/                 # SQLAlchemy ORM (mapeo a tablas del esquema)
│   ├── schemas/                # Pydantic (request/response)
│   ├── services/               # Lógica de negocio (KPIs, normalización, validación)
│   └── repositories/           # Acceso a datos (queries parametrizadas)
├── tests/
├── alembic/                    # (opcional) migraciones de esquema de app
├── requirements.txt
└── .env.example
```

---

## 3. Prerrequisitos

- Fase 01 cerrada (puerta G4): `fact_gestion`, `fact_pqrs`, dimensiones, vistas,
  KPIs aprobados.
- Decisión A-11 resuelta (define si los KPIs de productividad por asesor se exponen
  solo para GDO o se ocultan).
- Rol de BD con mínimo privilegio para la API (lectura sobre vistas/dimensiones y
  escritura solo sobre las tablas de tipificación/cancelaciones y bitácora).
- Variables de entorno seguras (S-01…S-17 del doc `06_Documentacion.md` §6).

---

## 4. Sub-fases y tareas

### 4.1 Sub-fase 2.1 — Fundación del backend (esfuerzo S)

- Crear el proyecto FastAPI con la estructura propuesta.
- Configurar `pydantic-settings` leyendo `.env` (sin valores reales en el repo).
- Conexión a PostgreSQL con `sslmode=require` (S-12), pool de conexiones, manejo de
  sesiones.
- CORS restringido al origen del frontend; headers de seguridad (S-08).
- Endpoint `/health` y `/version`.
- Logging sin PII (S-14); `Cache-Control: no-store` en endpoints con datos de gestión
  (S-07).
- Tests básicos (pytest) y CI (GitHub Actions).

### 4.2 Sub-fase 2.2 — Modelos y repositorios (esfuerzo M)

- Mapear con SQLAlchemy las tablas del esquema `gestion_diaria`: `fact_gestion`,
  `fact_pqrs`, `dim_gasera`, `dim_cabina`, `dim_resultado`, `dim_motivo`,
  `dim_operador`, `dim_producto`, `dim_aseguradora`, `dim_medio`, `dim_tipo_contacto`,
  `dim_carga`, `dim_origen`, `quarantine`, y la vista `v_gestion_diaria`.
- Repositorios con queries parametrizadas (sin interpolación de strings) y filtros
  por fecha, gasera, cabina, resultado, operador, motivo.
- Paginación (limit/offset) y ordenamiento.
- Proyección de columnas: **nunca devolver PII** (nombre, documento, teléfono,
  dirección, correo) en respuestas agregadas (S-15, B-23).

### 4.3 Sub-fase 2.3 — Autenticación y autorización (esfuerzo M)

- JWT con access token de TTL corto y refresh token rotativo (S-10).
- Roles: `admin`, `analista`, `asesor`, `solo_lectura`.
- Principio de mínimo privilegio por rol (S-11): un asesor solo ve/escribe lo suyo;
  un analista ve agregados; admin gestiona catálogos y cargas.
- Sin datos sensibles en URLs (S-09); sin PII en logs (S-14).

### 4.4 Sub-fase 2.4 — Endpoints de lectura (esfuerzo M)

| Endpoint | Fuente | Filtros |
| :--- | :--- | :--- |
| `GET /api/v1/gaseras` | `dim_gasera` | activo |
| `GET /api/v1/cabinas` | `dim_cabina` | — |
| `GET /api/v1/resultados` | `dim_resultado` | clasificación (APTA/NO_APTA/POR_REVISAR) |
| `GET /api/v1/motivos` | `dim_motivo` | familia |
| `GET /api/v1/operadores` | `dim_operador` | tipo (EMPRESA/PERSONA) |
| `GET /api/v1/gestion` | `v_gestion_diaria` / `fact_gestion` | fecha, gasera, cabina, resultado, operador, motivo, paginación |
| `GET /api/v1/pqrs` | `fact_pqrs` | fecha, gasera, estado |
| `GET /api/v1/abandono` | `fact_gestion` (subtipo ABANDONO) | fecha, gasera, cabina |
| `GET /api/v1/kpis/resumen` | `fact_gestion` | volumen, APTA/NO APTA, % retención |
| `GET /api/v1/kpis/retencion` | `fact_gestion` | Total Retenciones = `retenido` + `cancelado + venta`; % Retención |
| `GET /api/v1/kpis/abandono` | `fact_gestion` (ABANDONO) | tasa por hora/día (bloqueado por A-12 para GDO) |
| `GET /api/v1/kpis/motivos` | `fact_gestion` + `dim_motivo` | distribución de motivos |
| `GET /api/v1/kpis/operadores` | `fact_gestion` + `dim_operador` | volumen por empresa (A-11) |
| `GET /api/v1/calidad/cargas` | `dim_carga` | cargas, rechazos, estado |
| `GET /api/v1/calidad/pendientes` | `resultado_pendiente` | POR_REVISAR, ocurrencias |
| `GET /api/v1/calidad/cuadre` | `fact_gestion` vs staging | diferencias |

**Semántica a respetar (no negociable):**
- `APTA` ≠ "retención": Total Retenciones = `retenido` + `cancelado + venta` (2 de los 4
  APTA); `CANCELADO` (sin venta) no cuenta (H-22, D-01, D-02).
- `operador` es la empresa operadora, no el asesor (H-23, D-08). Productividad individual
  solo para GDO (A-11).
- `anio` es año de venta, no de gestión (H-07): nunca agregar por `anio`.

### 4.5 Sub-fase 2.5 — Endpoints de escritura (tipificación y cancelaciones) (esfuerzo M)

El frontend (Fase 03) permite que los **asesores tipifiquen en el sistema** y registren
**cancelaciones**. La API debe:

- `POST /api/v1/gestion` — registrar una gestión tipificada (gasera, cabina, contrato,
  fecha, resultado, motivo, operador, tipo de contacto, canal, producto, aseguradora).
  - Validar contra R-01…R-20 (dominio, rango, completitud).
  - Normalizar el resultado con el algoritmo del doc 09 (limpieza → variante → exacto →
    bloqueo de negaciones → fuzzy → POR_REVISAR) y guardar `resultado_original`,
    `resultado_normalizado`, `clasificacion`, `metodo_normalizacion`, `score_similitud`.
  - Insertar en `fact_gestion` con `origen = OCM` o `EXCEL` según el flujo; asignar
    `carga_id` (bitácora).
  - Si falla validación → `quarantine` (regla + valor + motivo), nunca descarte silencioso.
- `POST /api/v1/gestion/cancelacion` — registrar una cancelación realizada por un asesor
  (contrato, fecha, motivo, asesor, gasera), conectada a `fact_gestion` con el resultado
  `cancelado` (o `cancelado + venta` / `cancelado + reintegro` según el caso) para que
  alimente los reportes.
- `POST /api/v1/pqrs` — registrar PQRS (radicado, fechas ANS, estado).
- `PATCH /api/v1/pendientes/{id}/resolver` — resolver un `POR_REVISAR` (agrega la
  variante a `resultado_variante` con `validado` según el rol).
- Idempotencia por clave natural (`md5`) con marcado de duplicados (`es_duplicado`),
  nunca borrado silencioso (D-10, H-05).
- Auditoría de quién registró (usuario, timestamp) en `dim_carga`/bitácora.

### 4.6 Sub-fase 2.6 — KPIs y reportes (esfuerzo M)

- Implementar los KPIs definidos en `03_Definicion_de_KPIs.md` (7 KPIs comunes
  definidos y confirmados) como servicios reutilizables.
- Endpoints de exportación (CSV/Excel) con minimización de PII (S-15).
- Caché de solo lectura para agregados pesados (con invalidación por `carga_id`),
  nunca cachear datos sensibles (S-07).

### 4.7 Sub-fase 2.7 — Calidad, observabilidad y documentación (esfuerzo S)

- Endpoint de métricas de calidad (cargas, rechazos, `POR_REVISAR`, cobertura,
  duplicados).
- Health checks de BD y de la API.
- OpenAPI/Swagger documentado (FastAPI automático) con ejemplos.
- Tests de integración contra una BD de prueba (no contra producción).
- Documentación de despliegue y de variables de entorno (`.env.example`).

---

## 5. Seguridad (obligatoria — doc `06_Documentacion.md` §6)

| Regla | Aplicación en el backend |
| :--- | :--- |
| S-01 | `.env` en `.gitignore`; verificar antes de cada commit |
| S-07 | `Cache-Control: no-store, no-cache, must-revalidate` en endpoints con datos de gestión |
| S-08 | Headers: HSTS, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, CSP |
| S-09 | Sin PII ni credenciales en query params |
| S-10 | JWT de vida corta, refresh rotativo |
| S-11 | Mínimo privilegio por rol |
| S-12 | `sslmode=require` a PostgreSQL |
| S-14 | No loguear PII |
| S-15 | Minimización en reportes: solo lo necesario |
| S-17 | Procedimiento de derecho al olvido (Ley 1581) |

---

## 6. Entregables de esta fase

1. Proyecto FastAPI funcional con OpenAPI documentado.
2. Endpoints de lectura (gaseras, cabinas, resultados, motivos, operadores, gestión,
   PQRS, abandono, KPIs, calidad).
3. Endpoints de escritura para tipificación y cancelaciones conectados a `fact_gestion`.
4. Autenticación/autorización por roles.
5. Tests de integración y de seguridad.
6. Documentación de despliegue y variables de entorno.

---

## 7. Riesgos

- Construir la API antes de cerrar la Fase 01 → cifras no auditables.
- Exponer PII por descuido → violación de Ley 1581 (S-04, S-15).
- KPI de productividad por asesor prometido sin A-11 resuelto (R-11).
- Abandono de GDO no confiable contaminando nivel de servicio (R-12).

---

## 8. Referencias

- `context/planes/05_Plan_Fase_01_Base_Datos.md` — prerrequisito
- `context/Analisis/03_Modelo_Datos.md` — modelo y migraciones
- `context/Analisis/06_Documentacion.md` — seguridad §6
- `context/Analisis/010_Registro_Decisiones_Riesgos.md` — decisiones y riesgos
- `context/Analisis/03_Definicion_de_KPIs.md` — KPIs
- `context/Analisis/11_OCM_Configuracion_Llamadas.md` — matriz OCM
- `context/Analisis/12_Asesores_Gestion_Diaria.md` — asesores

> **Siguiente fase:** una vez cerrada esta fase, iniciar
> `07_Plan_Fase_03_Frontend_React_Astro.md`.