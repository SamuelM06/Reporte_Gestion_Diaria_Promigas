# 📋 Plan 01: Estructura del Proyecto y Fases de Trabajo

**Proyecto:** Gestión Diaria Promigas
**Alcance:** esquema `gestion_diaria` de `DataCenter_Promigas` (PostgreSQL 16.14)
**Última actualización:** 19 de octubre de 2026

Este documento establece la hoja de ruta integral. Sigue una metodología orientada a
datos (*Data-First*), donde cada fase depende de la total compresión de la fase anterior.

> **Reformulación del 19-oct-2026.** La versión anterior describía un plan de
> construcción desde cero. La verificación contra la base de datos mostró que la capa
> de datos **ya está construida y cargada** (48.036 filas en 16 tablas), que la
> homologación **existe parcialmente** (catálogo de 40 variantes, 4 funciones de
> normalización) y que el déficit real es de **gobernanza del dato**: trazabilidad,
> catálogo completo, y la semántica de `APTA` comunicada con claridad.

---

## 1. Visión del Plan

| Antes (suposición) | Ahora (verificado el 19-oct-2026) |
| :--- | :--- |
| Hay que construir la base de datos central | **Ya existe**: `gestion_diaria`, 18 tablas, 48.036 filas de datos |
| Hay que crear el catálogo de homologación | **Existe parcial**: `clasificacion` (40 filas, **solo GasCaribe**) + 4 funciones |
| La base consolidada refleja las fuentes | **No cuadra**: 7 de 8 pares no reconcilian (S-08) |
| El abandono y PQRS están en el modelo | **No**: son 12.710 + 6.280 filas en 4+4 tablas, fuera del modelo de gestión |
| `operador` es el asesor | **No**: es la **empresa operadora**; el asesor individual solo existe en GDO (D-08) |
| El reporte medirá productividad por asesor | **Solo en GDO**. A-11 debe resolverse antes de prometerlo |

> **Tesis del plan:** el proyecto no tiene un problema de construcción de datos, tiene
> un problema de **gobernanza del dato**. Cada pieza existe, pero fue construida por
> alguien distinto, con reglas distintas, y hoy no se concilian entre sí.

---

## 2. Cronograma de Fases

### 🔷 Fase 0: Preparación y Gobernanza ✅ **COMPLETADA**
* [x] Repositorio Git vinculado con GitHub.
* [x] Estructura de carpetas analíticas (`context/Analisis`, `context/planes`, `database`).
* [x] Documentos iniciales de flujo y análisis de requerimientos.
* [x] Plantilla base de conexión a base de datos segura.
* [x] **Conexión real a `DataCenter_Promigas` validada** (PostgreSQL 16.14).
* [x] **Credenciales reales en `database/.env`** (ignorado por Git) + `.env.example` como plantilla limpia.
* [x] **Herramienta de inspección reutilizable**: `database/inspeccion_esquema.py`.

---

### 🔷 Fase 1: Inmersión y Auditoría de Datos en Origen ✅ **COMPLETADA (19-oct-2026)**
* **Objetivo:** Comprender al 100% cada archivo Excel, cada hoja, cada columna y el estado de la base de datos antes de proponer transformaciones.
* [x] Conexión a la BD y validación de conectividad.
* [x] Inventario de las 18 tablas, 5 vistas y 4 funciones del esquema `gestion_diaria`.
* [x] Perfilado de las 16 tablas de datos (48.036 filas): tipos, nulos, cardinalidad, dominios.
* [x] Dominio completo de las columnas de tipificación (resultado por gasera).
* [x] Verificación de las reglas de negocio originales con datos (Efigas `FECHA BASE`, GDO `informativo`, Surtigas fragmentado).
* [x] Diagnóstico de sangrado de columnas y su causa raíz (celdas con tabulador).
* [x] Verificación de codificación a nivel de bytes (UTF-8 correcto).
* [x] 36 hallazgos documentados con evidencia.
* **Entregables:** `01_Diccionario_de_Datos.md`, `02_Mapeo_Origen_Destino.md`, `03_Modelo_Datos.md`, `04_Hallazgos_y_Backlog.md`, `05_Calidad_de_Datos.md`.

---

### 🔷 Fase 2: Homologación y Reglas de Negocio Multigasera 🔄 **EN CURSO — BLOQUEADA**
* **Objetivo:** Resolver la dispersión de criterios entre las 5 gaseras.
* [x] **D-01 verificada**: los 4 resultados APTA ya existen en la base de datos.
* [x] **D-07 / A-09 resuelta**: la clasificación no varía por gasera.
* [ ] **A-11: ¿empresa o asesor?** Definir la granularidad del reporte (bloqueante para el KPI de productividad).
* [ ] **A-14: campos obligatorios por gasera** (negocio).
* [ ] P-04 · Catálogo maestro de 2 niveles (`dim_resultado` + `resultado_variante`).
* [ ] P-05 · Regla determinista de `clasificacion_norm`.
* [ ] P-06 · **Normalizar la `/` en `normalizar_texto`** (27 filas APTA de CEO hoy sin clasificar).
* [ ] P-07 · Guardia de conceptos ambiguos (`devolucion`, `reintegro`, `previa`).
* [ ] P-08 · Limpieza de artefactos de Excel (tabulador, saltos de línea, `_x000D_`).
* [ ] P-09 · Adoptar el catálogo de 52 motivos de GDO como maestro.
* [ ] P-11 · Extender `fn_parse_fecha` (4 formatos).
* [ ] **Cola de revisión: 43 variantes pendientes / 236 filas** (≈4-5 h de trabajo humano).
* [ ] P-33 · Extender a las 4 gaseras restantes el modelo de Surtigas (`validacion`, `tipo_contacto_homolog`).
* **Entregable:** `dim_resultado` + `dim_motivo` poblados, con 0 estados sin catalogar en las 5 gaseras.

---

### 🔷 Fase 3: Ingesta Automatizada, Homologada y Trazable ⏳ **NO INICIADA**
* **Objetivo:** Reemplazar la carga manual por snapshot con una ingesta reproducible, validada y con lineage.
* [x] Configuración segura de variables de entorno y validación de conectividad.
* [ ] P-10 · **Validación de dominio por columna** en la ingesta (detectar sangrado).
* [ ] P-12 · Bitácora de carga con `sha256` del archivo origen.
* [ ] P-13 · Tabla de cuarentena (nada se descarta en silencio).
* [ ] P-14 · Separar `anio_gestion` de `anio_venta`.
* [ ] P-15 · **Reingerir de forma reproducible y cuadrar con el consolidado al 100%** (S-08).
* [ ] Migraciones M0–M8 del doc 03, probadas **contra una copia** (S-05: no hay entorno de pruebas).
* **Entregable:** Pipeline de ingesta con bitácora, cuarentena, validaciones y cuadre de cifras al 100%.

---

### 🔷 Fase 4: Modelo Analítico y Métricas ⏳ **NO INICIADA**
* [ ] M2–M4: `dim_*` + `fact_gestion` + `fact_pqrs` (doc 03 §6).
* [ ] M5: extender `clasificacion` a las 5 gaseras.
* [ ] M6: carga inicial (29.046 atenciones + 12.710 abandono + PQRS).
* [ ] Definir la clave natural con `es_duplicado` (D-10, resuelve A-03).
* [ ] Definir los KPIs con el negocio (doc 06, **falta redactar**).
* [ ] Cuadre `fact_gestion` vs `gestion_diaria` = 0 diferencias.
* **Entregable:** Modelo dimensional publicado + KPIs aprobados.

---

### 🔷 Fase 5: Dashboard y Reportes ⏳ **NO INICIADA**
* [ ] M7: vistas de consumo (`v_gestion_diaria`).
* [ ] Dashboard por gasera, cabina, mes, resultado, motivo y operador.
* [ ] Panel de calidad del dato (cargas, rechazos, cobertura, `POR_REVISAR`).
* [ ] Panel de nivel de servicio y abandono (requiere A-12 para GDO).
* [ ] Exportación de reportes operativos.
* [ ] Plan de desconexión de Excel por gasera (doc 07, **falta redactar**).
* **Entregable:** Reportes validados por la jefatura.

---

## 3. Criterio de Control: "No avanzar sin entender la Data"

> **Regla de oro:** No se programará ninguna interfaz ni se cerrará ningún backend sin haber revisado exhaustivamente cada hoja de cálculo, cada tabla y cada caso atípico en la data.

**Estado:** ✅ **Cumplido.** 48.036 filas perfiladas, 36 hallazgos con SQL reproducible, 16 reglas de validación definidas.

### 3.1 Puertas de calidad por fase

| Puerta | Criterio de paso | Estado |
| ---: | :--- | :--- |
| G1 → Fase 2 | Data auditada y documentada | ✅ Superada (19-oct-2026) |
| G2 → Fase 3 | A-11 y A-14 resueltas; cola de 43 variantes cerrada | ❌ Pendiente |
| G3 → Fase 4 | Bitácora + cuarentena + validación de dominio activas; cuadre al 100% | ❌ Pendiente |
| G4 → Fase 5 | Modelo dimensional publicado + KPIs aprobados (doc 06) | ❌ Pendiente |
| G5 → Apagado de Excel | Cobertura OCM ≥ umbral acordado por gasera | ❌ Pendiente |

---

## 4. Documentos del proyecto

| # | Documento | Estado |
| ---: | :--- | :---: |
| 01 | `planes/01_Plan_Estructura.md` (este) | ✅ |
| 02 | `planes/02_Plan_Migracion_y_Estrategia_DB.md` | ✅ |
| 03 | `Analisis/01_Diccionario_de_Datos.md` | ✅ **Nuevo** |
| 04 | `Analisis/02_Mapeo_Origen_Destino.md` | ✅ **Nuevo** |
| 05 | `Analisis/03_Modelo_Datos.md` | ✅ **Nuevo** |
| 06 | `planes/03_Definicion_de_KPIs.md` | ⬜ **Falta redactar** |
| 07 | `planes/04_Transicion_a_OCM.md` | ⬜ **Falta redactar** |
| 08 | `planes/05_Plan_Fase_01_Base_Datos.md` | 🔴 **En curso** (DB primero) |
| 09 | `planes/06_Plan_Fase_02_Backend_FastAPI.md` | ⏳ No iniciada |
| 10 | `planes/07_Plan_Fase_03_Frontend_React_Astro.md` | ⏳ No iniciada |
| 11 | `planes/08_Plan_Fase_04_Integracion_Despliegue.md` | ⏳ No iniciada |
| 08 | `Analisis/010_Registro_Decisiones_Riesgos.md` | ✅ Actualizado |
| 09 | `Analisis/09_Normalizacion_y_Clasificacion.md` | ✅ Actualizado |
| 10 | `Analisis/04_Hallazgos_y_Backlog.md` | ✅ |
| 11 | `Analisis/05_Calidad_de_Datos.md` | ✅ |
| — | `Analisis/06_Documentacion.md` | ✅ Índice y contexto |
| — | `Analisis/08_Flujo_De_Datos.md` | ✅ |
| — | `Analisis/07_Estructura_de_datos.md` | ✅ |

---

## 5. Próximos 5 Días

| # | Tarea | Responsable | Entregable |
| ---: | :--- | :--- | :--- |
| 1 | **Resolver A-11** (¿empresa o asesor?) con la jefatura | Negocio | Definición de la granularidad del reporte |
| 2 | **Revisar la cola de 43 variantes** (≈4-5 h) y cargar el catálogo completo | Análisis + Negocio | `clasificacion` con 0 estados sin mapear en las 5 gaseras |
| 3 | **Corregir `normalizar_texto`** (normalizar `/`) y extender `fn_parse_fecha` | Análisis | P-06 y P-11 aplicados y verificados contra las 48.036 filas |
| 4 | **Pedir a cada gasera el layout real de cada pestaña de Excel** | Análisis | Mapa de columnas por archivo (resuelve S-03 y el bloque de 27% sin datos de Caribe) |
| 5 | **Pedir el hash y el nombre de los archivos** de las últimas cargas | Análisis | Permite reconstruir la trazabilidad (P-12) |

---

## 6. Riesgos del Proyecto

| # | Riesgo | Probabilidad | Impacto | Mitigación |
| ---: | :--- | :--- | :--- | :--- |
| R-1 | La semántica de `APTA` se interpreta como "retención" y se reporta inflado | Alta | Crítico | D-01/D-02 están aclaradas; la comunicación en el dashboard debe ser literal |
| R-2 | El consolidado y la fuente son dos verdades | Alta | Crítico | P-15: reingerir con lineage y cuadrar al 100% |
| R-3 | El KPI de productividad por asesor no es calculable en 4 de 5 gaseras | Alta | Alto | A-11 antes de comprometer el alcance |
| R-4 | Las gaseras no cambian sus procesos de registro | Alta | Alto | A-14: acuerdo de campos obligatorios |
| R-5 | El acceso a la escritura en la BD está bloqueado para el usuario de análisis | Media | Alto | Solicitar rol de escritura **solo sobre `gestion_diaria`**, o un pipeline con credenciales propias |
| R-6 | No hay entorno de pruebas (S-05) | Alta | Alto | Probar las migraciones contra una copia |
| R-7 | El corte a OCM del 1-nov llega sin casamiento de datos | Alta | Alto | Doc 07 (falta redactar) |
