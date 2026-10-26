# 🗄️ Plan Fase 01 — Base de Datos (Data-First)

**Proyecto:** Reporte de Gestión Diaria - Retención Promigas
**Esquema:** `gestion_diaria` de `DataCenter_Promigas` (PostgreSQL 16.14)
**Stack de datos:** PostgreSQL 16.14 · SQLAlchemy/pandas · Python 3.11+
**Última actualización:** 21 de octubre de 2026
**Estado:** 🔄 EN CURSO (Fase 1 de auditoría completada; homologación bloqueada)

> 🔴 **Regla de oro del proyecto (plan 01 §3):** no se programa ninguna interfaz ni se
> cierra ningún backend sin haber revisado exhaustivamente la data. **La base de datos
> es el primer entregable.** Sin una DB armada, trazable y cuadrada al 100%, ni el
> backend (FastAPI) ni el frontend (React/Astro) tienen sobre qué construirse.

---

## 1. Por qué la base de datos va primero

Análisis de la documentación existente (`context/Analisis/*` y `database/*`) — conclusión:

1. **El sistema no tiene un problema de construcción de datos, tiene un problema de
   gobierno del dato** (README §⚠️, `04_Hallazgos` §1). La capa está construida y cargada
   (48.036 filas en 16 tablas), pero cada pieza fue hecha por alguien distinto y **no se
   concilian entre sí** (7 de 8 pares fuente→consolidado no cuadran, S-08).
2. **No existe modelo de hechos consolidado** (H-02): 8 tablas de atención, 4 de abandono y
   4 de PQRS, sin un destino común. Ningún reporte transversal es posible sin `UNION ALL`
   de esquemas distintos.
3. **El abandono y los PQRS no son analizables por fecha** (H-09, H-10): 63–100% de las
   fechas no parseables en 4 tablas.
4. **El catálogo solo cubre GasCaribe** (H-04): 43 variantes sin catalogar (236 filas) en
   las otras 4 gaseras.
5. **Cero FKs y cero índices de negocio** (H-17); **1.589 filas con sangrado de columnas**
   (H-24, H-25); **sin bitácora ni cuarentena** (H-13, H-14).
6. **La semántica de `APTA` no es "retención"** (H-22): 3 de los 4 resultados APTA implican
   cancelación. Reportar sobre eso sin homologar **invierte el indicador**.
7. **El contenido actual es un snapshot manual** (D-11): hay que reemplazarlo por los
   ≈42.070 registros reales de 2026 de las 5 gaseras, y persistir también los de OCM
   (D-12) para no perder nada en la transición.

**Consecuencia:** construir FastAPI o React sobre este estado produciría una API y un
dashboard que reportan cifras no auditables. Por eso **la Fase 01 es exclusivamente de
base de datos**; el backend (Fase 02) y el frontend (Fase 03) dependen de ella.

---

## 2. Alcance de esta fase

- **Esquema:** `gestion_diaria` (y, cuando se decida, el modelo dimensional sobre el mismo
  esquema o uno paralelo — A-16).
- **Objetos a crear/modificar:** las migraciones **M0–M8** del doc `03_Modelo_Datos.md` §6,
  más las extensiones de `clasificacion`, `normalizar_texto`, `fn_parse_fecha` y el ciclo
  de aprendizaje de variantes (doc 09).
- **Datos:** reingesta reproducible de los ≈42.070 registros de 2026 (33.501 atención/outbound
  + 3.383 abandono + 5.186 PQRS) y persistencia de los registros de OCM (D-12).
- **Fuera de alcance de esta fase:** endpoints HTTP, UI, despliegue (Fases 02–04).

---

## 3. Prerrequisitos bloqueantes (decisiones de negocio)

Antes de escribir DDL definitivo deben resolverse (doc `010` §1.3):

| ID | Decisión | Bloquea |
| :--- | :--- | :--- |
| **A-11** | ¿El reporte mide productividad por **empresa** o por **asesor**? (solo GDO tiene asesor persona) | KPI de productividad, `dim_operador` |
| **A-12** | ¿El abandono de GDO se incluye, se reprocesa o se declara no confiable? | Cobertura de abandono, panel de nivel de servicio |
| **A-13** | ¿`gdo_informativo` se carga como bitácora o se descarta? | Carga de PQRS (`fact_pqrs`) |
| **A-14** | ¿Qué campos son obligatorios por gasera? | Completitud, reglas R-12 |
| **A-16** | Estrategia de persistencia: A (truncado+recarga) / B (esquema paralelo) / C (incremental) | Toda la reingesta |
| **A-17** | Dónde y cómo se persisten los registros de OCM; llave de casamiento | `fact_gestion.origen`, transición |
| **A-18** | Día de cierre de Excel por gasera | Regla de exclusión, R-01 |

Además: entorno de pruebas (S-05, R-14) — hoy **no existe**; las migraciones se probarían
sobre 48.036 filas reales. Mitigación: probar contra una copia (`gestion_diaria_bak_<fecha>`).

---

## 4. Sub-fases y tareas

### 4.1 Sub-fase 1.1 — Gobernanza y desbloqueo (esfuerzo S–M)

- Resolver A-11, A-12, A-13, A-14 con la jefatura (actas).
- Resolver A-16, A-17, A-18 con equipo de datos + DBA + OCM.
- Cerrar la **cola de 43 variantes** (B-03) y extender `clasificacion` a las 5 gaseras
  (≈4–5 h de revisión humana). Instalar el **ciclo de aprendizaje continuo** (B-03b):
  fuzzy contra conceptos + cola permanente + aprendizaje de variantes.
- Pedir a cada gasera el layout real de cada pestaña (B-25) y confirmar sept/oct de
  Surtigas Inbound (B-26).
- Solicitar permiso de escritura acotado sobre `gestion_diaria` (B-27) — hoy el usuario es
  owner (R-14, R-17).

**Puerta de salida (G2):** A-11 y A-14 resueltas; cola de 43 variantes cerrada; 0 estados
sin catalogar en las 5 gaseras.

### 4.2 Sub-fase 1.2 — Homologación y normalización (esfuerzo M)

- **P-06** — corregir `normalizar_texto` para normalizar la `/` (27 filas APTA de CEO).
- **P-07** — guardia de conceptos ambiguos (`devolucion`, `reintegro`, `previa`).
- **P-08** — limpieza de artefactos de Excel (tabulador, `\n`, `\r`, `_x000D_`).
- **P-11** — extender `fn_parse_fecha` (4 formatos: `DD/MM/YYYY`, `DD/MM/YYYY HH:MM:SS AM/PM`,
  `MMM-YY`, seriales Excel) → `YYYY-MM-DD HH:MM:SS`.
- **B-10** — verificar `cancelado/reintegro` clasifica como APTA.
- **B-11** — consolidar los 23 NO APTA literales en el catálogo maestro (≤15 valores
  distintos en `resultado_normalizado`).
- **B-13** — validar `fn_parse_fecha` contra las 48.036 filas (≥99% parseable).
- **B-20** — mapear el resultado de GDO desde `resultado_final` / `resultado_de_retencion`
  (no desde `estado`).
- **B-21** — guardia de conceptos ambiguos en el algoritmo.
- **B-28** — adoptar el catálogo de 52 motivos de GDO como `dim_motivo`.
- **B-29** — extender a las 4 gaseras restantes el modelo de Surtigas
  (`validacion`, `tipo_contacto_homolog`).
- **B-30** — consolidar los 3 catálogos de motivo en texto libre.
- **M5** — extender `clasificacion` a las 5 gaseras (0 estados sin catalogar).

**Puerta de salida:** `dim_resultado` + `dim_motivo` poblados, con 0 estados sin catalogar
en las 5 gaseras; `fn_parse_fecha` ≥99% parseable.

### 4.3 Sub-fase 1.3 — Modelo dimensional (esfuerzo L)

Aplicar las migraciones **M0–M8** del doc `03_Modelo_Datos.md` §6, en este orden:

| Migración | Qué hace | Criterio de aceptación |
| :--- | :--- | :--- |
| **M0** | Vista de saneamiento de nombres (`v_gdo_pqrs`) | Vista expone solo columnas con nombre válido |
| **M1** | `dim_origen`, `dim_carga`, `quarantine` | Existen y aceptan una carga de prueba |
| **M2** | 11 catálogos (`dim_gasera`, `dim_cabina`, `dim_tipo_gestion`, `dim_resultado`, `dim_motivo`, `dim_operador`, `dim_producto`, `dim_aseguradora`, `dim_medio`, `dim_tipo_contacto`) | Poblados desde `clasificacion` y `normalizar_*` |
| **M3** | `fact_gestion` | Carga las 29.046 filas de atención sin perder ninguna |
| **M4** | `fact_pqrs` | Carga las PQRS deduplicadas |
| **M5** | Extender `clasificacion` a las 5 gaseras | 0 estados sin catalogar en las 5 (ya en 4.2) |
| **M6** | Carga inicial | `COUNT(fact_gestion)` = 29.046 + 12.710 (abandono) |
| **M7** | Vistas de consumo (`v_gestion_diaria`) | Responde y cuadra con el staging |
| **M8** | Limpieza: `DROP TABLE gdo_gestion_diaria` | Artefacto eliminado |

Reglas del modelo (doc 03 §5) a respetar: M-01…M-10 (clave natural generated, índice único
parcial, dimensiones no se borran, temporales `date`/`timestamptz`, `anio_gestion`/`mes_gestion`
generated, `resultado_original` inmutable, referencia a `dim_carga`, sin PII en dimensiones,
catálogos como `varchar` + FK).

**Decisión A-04:** una sola `fact_gestion` con `subtipo_gestion` ∈ {ATENCION, ABANDONO, PQRS}
discriminado; PQRS aparte en `fact_pqrs` (D-09). **A-03:** `id_gestion` + `clave_natural`
(md5) con `es_duplicado`.

**Puerta de salida (G3):** bitácora + cuarentena + validación de dominio activas; cuadre al
100%.

### 4.4 Sub-fase 1.4 — Ingesta reproducible y trazabilidad (esfuerzo L)

- **P-10 + P-13** — validación de dominio por columna + cuarentena (0 filas con sangrado
  en la siguiente carga).
- **P-12 + P-15** — bitácora con `sha256` (`dim_carga` + `dim_origen`) y reingesta
  reproducible con cuadre al 100% (S-08).
- Reingerir de forma reproducible los ≈42.070 registros de 2026 (B-15), respetando D-13
  (misma estructura que el Excel), D-14 (filtro por columna de fecha, no por nombre de
  hoja) y D-15 (abandono: fecha en la primera columna).
- Persistir los registros de OCM (D-12, A-17): `fact_gestion` con `origen` ∈ {EXCEL, OCM},
  llave de casamiento para no duplicar; regla de exclusión por gasera y fecha de cierre
  (A-18, R-01, R-19).
- **B-12** — regla de rango de fechas `[2025-01-01, hoy+1]` + cuarentena (4 fechas
  imposibles).
- **B-16** — negociar campos obligatorios por gasera y cuantificar nulos (A-14).
- **B-17** — índices de negocio del modelo nuevo (sin seq scan en la consulta mensual).
- **B-18** — limpieza de artefactos de Excel en la ingesta (L-01…L-07).
- **B-19** — marcar `base`/`FECHA DE BASE` como "no usar para análisis".
- **B-22** — entorno de pruebas (o copia para migraciones).
- **B-23** — minimización de PII: vistas de consumo sin datos personales.
- **B-24** — eliminar `gdo_gestion_diaria` (M8).
- **B-25 / B-26** — layout real por pestaña; confirmar sept/oct de Surtigas.
- **B-35** — separar `anio_gestion` de `anio_venta` (P-14).

**Puerta de salida (G3):** bitácora + cuarentena + validación de dominio activas; cuadre
`fact_gestion` vs `gestion_diaria` = 0 diferencias; 100% de cargas con bitácora.

### 4.5 Sub-fase 1.5 — Calidad y validación (esfuerzo S–M)

- Implementar las 20 reglas de validación (R-01…R-20) en `05_Calidad_de_Datos.md` §8.
- Panel de calidad del dato (B-34): cargas, rechazos, `POR_REVISAR`, cobertura.
- Métricas de aceptación (`05_Calidad` §9): cuadre al 100%, 0 estados sin catalogar,
  `<0.5%` en `POR_REVISAR` y visibles, 0 filas con sangrado, 0 fechas fuera de rango,
  100% cargas con bitácora, duplicados `<2%`.
- Redactar el doc 06 (Definición de KPIs) con el negocio (B-31) — 7 KPIs comunes
  definidos y confirmados (ya en `03_Definicion_de_KPIs.md`).

**Puerta de salida (G4):** modelo dimensional publicado + KPIs aprobados.

---

## 5. Entregables de esta fase

1. `dim_*` + `fact_gestion` + `fact_pqrs` publicados en `gestion_diaria`.
2. `dim_carga` + `dim_origen` + `quarantine` operativos.
3. `clasificacion` extendida a las 5 gaseras (0 estados sin catalogar).
4. `normalizar_texto` y `fn_parse_fecha` corregidas y verificadas.
5. Ingesta reproducible de los ≈42.070 registros de 2026 con cuadre al 100%.
6. Persistencia de OCM con `origen` y llave de casamiento.
7. Vistas de consumo (`v_gestion_diaria`) respondiendo y cuadrando.
8. Documentación actualizada: diccionario, mapeo, modelo, KPIs.

---

## 6. Riesgos y mitigaciones (doc `010` §4)

| Riesgo | Mitigación |
| :--- | :--- |
| R-10 (semántica de APTA) | D-01/D-02 aclaradas; comunicación literal en el dashboard |
| R-13 (consolidado vs fuente) | P-12 + P-15: reingerir con lineage y cuadrar al 100% |
| R-14 (migraciones sobre producción) | Probar contra una copia; migraciones aditivas |
| R-17 (truncado accidental) | D-11: no truncar todavía; `BEGIN/COMMIT`; respaldo previo |
| R-18 (pérdida del histórico 2026) | D-11/D-12: persistir Excel y OCM con `origen` y `carga_id` |
| R-19 (doble conteo en transición) | Llave de casamiento + regla de exclusión por gasera y fecha de cierre |

---

## 7. Secuencia y dependencias

```
Sub-fase 1.1 (decisiones) ──► 1.2 (homologación) ──► 1.3 (modelo) ──► 1.4 (ingesta) ──► 1.5 (calidad)
        │                            │                      │                  │
        └── G2 ──────────────────────┘                      │                  │
                                   G3 ──────────────────────┘                  │
                                                              G4 ─────────────┘
```

**Regla de no retorno:** mientras `fact_gestion` no cuadre al 100% con `gestion_diaria`
(29.046 + 12.710 filas, más PQRS), **no se publica ningún reporte ni se inicia la
Fase 02 (backend).**

---

## 8. Referencias

- `context/Analisis/03_Modelo_Datos.md` — modelo en estrella y migraciones M0–M8
- `context/Analisis/04_Hallazgos_y_Backlog.md` — 36 hallazgos + backlog B-01…B-35
- `context/Analisis/05_Calidad_de_Datos.md` — perfil de calidad + 20 reglas R-01…R-20
- `context/Analisis/09_Normalizacion_y_Clasificacion.md` — algoritmo de normalización
- `context/Analisis/010_Registro_Decisiones_Riesgos.md` — decisiones D, propuestas P, abiertas A
- `context/Analisis/13_ERD_Estado_Actual.md` — ERD estado actual
- `context/Analisis/14_Estructura_Origen_Excel.md` — inventario verificado del origen
- `database/PROCEDENCIA_Y_REINGESTA.md` — procedencia y plan de persistencia
- `database/FICHA_ORIGEN_POR_GASERA.md` — rutas/libros/hojas/columnas por gasera
- `context/planes/01_Plan_Estructura.md` — hoja de ruta por fases y puertas de calidad
- `context/planes/02_Plan_Migracion_y_Estrategia_DB.md` — estrategia y cuestionario respondido
- `context/planes/03_Definicion_de_KPIs.md` — KPIs definidos

> **Siguiente fase:** una vez cerrada la puerta G4, iniciar
> `06_Plan_Fase_02_Backend_FastAPI.md`.