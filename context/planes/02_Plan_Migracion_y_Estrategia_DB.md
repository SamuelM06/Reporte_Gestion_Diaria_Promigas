# 📋 Plan 02: Estrategia de Migración a Base de Datos y Transición a OCM

**Proyecto:** Gestión Diaria Promigas
**Esquema:** `gestion_diaria` de `DataCenter_Promigas` (PostgreSQL 16.14)
**Última actualización:** 19 de octubre de 2026

> **Alcance acotado:** este plan cubre **exclusivamente el esquema `gestion_diaria`**.
> La instancia `DataCenter_Promigas` contiene otros esquemas (`ocm_retencion`,
> `reportes`, `siniestros`, `auditoria`) que **no pertenecen a este proyecto** y quedan
> fuera de alcance. OCM se trata aquí solo como **destino de la transición**, no como
> fuente de datos.

---

## 1. Estado Real: Los Tres Pilares

```text
[Pilar 1: Base de Datos]     ──▶ [Pilar 2: Ingesta SharePoint] ──▶ [Pilar 3: OCM]
   ✅ HECHO (100%)                   ⚠️ MANUAL (30%)                    ❌ SIN EMPEZAR
  18 tablas, 48.036 filas        sin bitácora ni lineage            falta el casamiento
  4 funciones de normalización   sin validación de dominio          falta apagar Excel
  1 catálogo (solo GasCaribe)    sin incrementalidad
```

### 🔹 Pilar 1: Base de Datos Central — ✅ **HECHO**

| Objeto | Estado | Detalle |
| :--- | :--- | :---: |
| 18 tablas | ✅ | 16 de datos (48.036 filas) + `clasificacion` (40) + `gdo_gestion_diaria` (vacía) |
| 5 vistas | ✅ | 2 clasificadas de Caribe, 1 de franja horaria, 1 de auditoría de mapeo, 1 de GDO (sin acceso) |
| 4 funciones de normalización | ✅ | `normalizar_texto`, `fn_parse_fecha`, `normalizar_aseguradora`, `normalizar_producto` |
| `gestion_diaria.clasificacion` | ⚠️ | 40 filas, **solo GasCaribe**, 17 APTA / 23 NO APTA |
| Claves foráneas | ❌ | 0 |
| Índices de negocio | ❌ | 0 (solo las PK) |
| Bitácora de ingesta | ❌ | No existe |
| Cuarentena | ❌ | No existe |
| Modelo dimensional (`dim_*` / `fact_*`) | ❌ | No existe (propuesta en doc 03) |

**Decisión sobre la base local desactualizada — RESUELTA POR EVIDENCIA:**

| Opción planteada | Veredicto |
| :--- | :--- |
| A. Truncar / Descartar | ❌ No aplica: la base local **ya es** `gestion_diaria` |
| B. Modificar / Sanear | ✅ **Es lo que ocurrió**: se conservó y se amplió, pero **sin reconciliar** y **sin dimensionar** |
| C. Reemplazar con histórico homologado | ❌ No aplica: el histórico ya está cargado |

> **Veredicto:** la decisión ya fue tomada de facto (opción B). El trabajo pendiente es
> **completar la homologación** y **restaurar la trazabilidad**.

---

### 🔹 Pilar 2: Automatización de la Ingesta — ⚠️ **LO MÁS DÉBIL**

**Estado verificado de las cargas:**

| Tabla | `fecha_carga` | Días distintos | Modo |
| :--- | :--- | ---: | :--- |
| `ceo_inbound` | 2026-09-15 17:22:38 | 1 | Snapshot |
| `ceo_abandono` | 2026-09-15 17:22:39 | 1 | Snapshot |
| `efigas_outbound` | 2026-09-15 17:22:40 | 1 | Snapshot |
| `caribe_inbound` | 2026-10-01 17:19:22 | 1 | Snapshot |
| `caribe_outbound` | 2026-10-01 17:19:22 | 1 | Snapshot |
| `caribe_abandono` | 2026-09-15 → 2026-10-01 | 2 | Snapshot |
| `surti_*`, `gdo_*` | *(sin columna)* | — | **Sin trazabilidad** |

> **No existe una sola función, job o procedimiento de ingesta en la base de datos.**
> No hay bitácora, ni verificación de filas leídas vs. cargadas, ni hash del archivo
> origen. Cada recarga es una operación manual que reescribe el staging.

**Lectores por gasera — especificación de su estado:**

| Lector | Reglas documentadas | Estado verificado |
| :--- | :--- | :--- |
| CEO | `FECHA INGRESO LLAMADA`; 2 hojas | ⚠️ `subtipificacion` 100% vacía; 22 estados sin catalogar; 1 fecha imposible (año 3748) |
| Efigas | Descartar `FECHA BASE`; 1 hoja | ✅ **Regla confirmada con datos** (lote `2026-03-02` → ejecuciones de sept-nov). 172 filas (17.2%) sin fecha de ejecución |
| Gas Caribe | Iterador de pestañas mensuales; 2 libros | 🔴 Bloque de ~27% sin datos; `MES` trae el año; 2 fechas epoch; `localidad` 100% vacía en Outbound |
| GDO | 5 hojas; `informativo` → PQRS | 🔴 `estado` 100% vacía (el resultado está en `resultado_final`); `gdo_abandono` inutilizable; `gdo_informativo` 99.7% no parseable |
| Surtigas | Conciliador de 3 libros | 🔴 `operador` no existe (11.7% sangrado); `surti_abandono` sin contrato y con fecha 100% no parseable; sin septiembre ni octubre |
| **Upsert / Deduplicación** | — | ❌ **No diseñado.** 3.114 grupos duplicados (20.2%). Propuesta en doc 03 §4.1 |

---

### 🔹 Pilar 3: Transición a OCM — ❌ **SIN EMPEZAR (y sin casamiento de datos)**

| Hito | Estado |
| ---: | :--- |
| 1. Habilitar API / Data Export de OCM | ⬜ Sin verificar |
| 2. Sustituir los conectores Excel por flujo directo | ⬜ Sin empezar |
| 3. Casar OCM con las planillas | ⬜ Sin empezar — **define el alcance de todo el Pilar 3** |
| 4. Cargar abandono y PQRS en el modelo de gestión | 🔴 En curso (M3–M6 del doc 03) |
| 5. Archivar y congelar las planillas de SharePoint | ⬜ Sin empezar |
| 6. Reducir errores de tipeo a 0 | ⬜ Sin empezar |

> **Corrección de rumbo respecto a la versión anterior:** este pilar estaba descrito
> como "habilitar la API". El trabajo real no es técnico sino de **datos y proceso**:
> medir qué % de las gestiones de Excel tiene su llamada registrada en OCM, y decidir
> gasera por gasera si Excel se apaga. Ese número **no existe todavía** y es el
> entregable central del doc 07 (pendiente de redactar).

---

## 2. Diseño del Esquema Target

Está desarrollado en detalle en **`03_Modelo_Datos.md`**:
modelo en estrella con `fact_gestion` + `fact_pqrs` + 12 dimensiones, y las
migraciones SQL M0–M8 con sus criterios de aceptación.

Resumen de las decisiones que ese documento pide aprobar:

| # | Decisión | Recomendación |
| ---: | :--- | :--- |
| A-04 | ¿Una tabla de hechos o varias? | **Una** `fact_gestion` con `subtipo_gestion`; PQRS aparte |
| A-03 | ¿Llave primaria? | `id_gestion` + `clave_natural` (md5), con `es_duplicado` |
| A-09 | ¿La clasificación varía por gasera? | **No** (D-07, verificado) |
| — | ¿Qué dimensiones? | `dim_gasera`, `dim_cabina`, `dim_resultado`, `dim_motivo`, `dim_operador`, `dim_producto`, `dim_aseguradora`, `dim_medio`, `dim_tipo_contacto`, `dim_tipo_gestion`, `dim_origen`, `dim_carga` |
| — | ¿Abandono en la misma tabla? | **Sí**, discriminado por `subtipo_gestion` |

---

## 3. Cuestionario Analítico del Lunes — **RESPONDIDO CON EVIDENCIA**

### ❓ Bloque 1: Calidad y Continuidad de la Data Histórica

**1. ¿Qué rango de fechas exacto cubre la base? ¿Tiene datos anteriores al 1 de enero de 2026?**

> **Respuesta:** `gestion_diaria` cubre, según `fecha_de_ejecucion`, de **2025-01-03**
> (Caribe) a **2026-12-06** (Surtigas Outbound). Por mes de gestión va de **enero a
> septiembre 2026** en las 5 gaseras.
>
> ⚠️ **Advertencia crítica:** el campo `anio` de las fuentes vale 2026 en el 100% de las
> filas porque es el **año de venta**, no el de gestión. `ceo_inbound.anio` reparte
> 1900→110, 2022→22 … 2026→233, NULL→1.694. **Nunca usar `anio` para medir cobertura
> temporal.** (P-14)

**2. ¿Existen solapamientos entre la base acumulada y los archivos de SharePoint?**

> **Respuesta:** la base **es** la carga de SharePoint (snapshot del 15-sep y 1-oct), así
> que no hay dos repositorios: hay **dos fotos de la misma realidad con 16 días de
> diferencia**. Lo que sí es un problema es que **no hay forma de saber cuál refleja la
> realidad actual**: no hay `sha256` ni bitácora por lote.
>
> Y al revés: `surti_inbound` no tiene septiembre ni octubre, aunque su archivo de
> continuidad se llama `JULIO - AGOSTO 2026` (I-08) — **o no llegaron, o no se cargaron**.

**3. Caso especial Surtigas — ¿las hojas `Enero a Marzo`, `abrl`, `mayo`, `junio` tienen las mismas columnas?**

> **Respuesta:** el resultado cargado es **homogéneo** (una sola estructura de 24
> columnas para las 9.423 filas), pero **no se puede verificar por hoja** porque no se
> conserva la hoja de origen. Tres indicadores apuntan a que **NO son idénticas**:
> * `surti_inbound.operador` está poblado en solo 1.165 de 9.423 filas (12.4%), y en
>   1.099 de esas contiene un **tipo de contacto** → la columna no existe en el origen.
> * `surti_inbound.mes` va de ENERO a AGOSTO sin septiembre ni octubre.
> * `surti_abandono` no tiene columna `contrato` (a diferencia de las otras 3 gaseras).
>
> **Pendiente:** pedir el layout real de cada pestaña.

**4. ¿Las hojas de `Abandono` tienen la misma granularidad que las llamadas atendidas?**

> **Respuesta: no, y varían mucho por gasera.**

| Gasera | Granularidad | Fecha | Hora | Contrato | Teléfono | ¿Utilizable? |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Caribe** | Atendidas | ✅ 100% | ✅ 100% | 33.8% | 99.1% | ✅ **La mejor** |
| **CEO** | Atendidas | ❌ 37.6% | ❌ 0.8% | 29.8% | 99.5% | 🟠 Parcial |
| **GDO** | Indefinida | ❌ 20.1% | 79.5% | 7.9% | 100% | 🔴 **No** (A-12) |
| **Surtigas** | Mínima (5 col.) | ⚠️ 100% no parseable | — | ❌ sin columna | 100% | 🔴 **No** |

> **2.508 abandonos de CEO y 2.131 de GDO no tienen fecha utilizable** (21.2% del
> abandono total). `caribe_abandono` además trae `gestionado_inbound` (flag) que las
> demás no tienen: es la única señal de que el abandono terminó en una gestión posterior.

### ❓ Bloque 2: Reglas de Homologación Multigasera

**5. ¿Cuáles son los valores permitidos para catalogar el resultado de la gestión?**

> **Respuesta (inventario, no decisión):** 4 resultados APTA canónicos
> (`cancelado`, `cancelado + venta`, `cancelado + reintegro`, `retenido`) y 23
> variantes NO APTA. 20–40 valores crudos por gasera, con 4–6 grafías por concepto.
> El catálogo actual tiene 40 filas, **solo para GasCaribe**.
>
> **43 variantes y 236 filas quedan sin clasificar** (CEO 22/65, Surtigas 11/100,
> GDO 9/66, Efigas 1/5).
>
> ⚠️ **La decisión sigue abierta (D-01 la aclara, pero no la cierra):** `APTA` significa
> *"a la llamada se le puede hacer una gestión al usuario"*, **no** *"el cliente se
> quedó"*. 3 de los 4 resultados APTA implican cancelación. Esta distinción debe
> comunicarse literalmente en el dashboard (R-10).

**6. GDO — ¿Qué columnas tiene `informativo` frente a `prqs escritas`?**

> **Respuesta:** son **modelos distintos**, y hay **3 fuentes PQRS** en GDO:

| | `gdo_informativo` | `gdo_pqrs_escritas` | `gdo_pqrs` |
| :--- | :--- | :--- | :--- |
| Filas | 4.191 | 86 | 747 |
| Columnas | 29 | 20 | 63 |
| Granularidad | **Bitácora de seguimiento** | Maestro de PQRS con ANS | Maestro de solicitud |
| Marca temporal | `fecha_regi` (3 formatos, 0.3% parseable) | `radicado_usu_gdo` (88% parseable) | `fecha_registro_solicitud` (100% parseable) |
| Trazabilidad ANS | ❌ | ✅ **completa** (GDO→Xuma→Aseguradora→Respuesta) | ❌ |
| Marcadores propios | `tipo_registro` (ÚNICO/DUPLICADO), `estado_inf` (PRIMER/2º REGISTRO) | `queja_escrita`, `numero_radicado` | `estado_solicitud`, `ciclo_solicitud` |
| Contratos coincidentes | — | 61 con `gdo_pqrs` | 142 con `gdo_informativo` |

> **Regla de fusión propuesta:** `gdo_pqrs_escritas` es el **maestro** (tiene ANS).
> `gdo_pqrs` es el **detalle de solicitud**. `gdo_informativo` es una **bitácora**:
> debe ir a una tabla aparte o descartarse. **Nunca los tres como "PQRS" a la vez.**
> Decisión abierta: A-13.

**7. Gas Caribe — ¿En qué columna está `FECHA DE ATENCION` y la pestaña sigue `Mes Año`?**

> **Respuesta:** la columna canónica es `fecha_de_ejecucion` (`date`, 73.9% poblada).
> El `mes` viene con **el año embebido**: `"ABRIL 2026"`, `"MARZO 2026"`. El `anio` es
> 2026 en el 100% de las filas.
>
> **Consecuencia verificada:** el join directo `mes` ↔ `mes_norm` con las demás gaseras
> **no funciona** (H-08).
>
> **Hallazgo adicional:** Caribe Inbound tiene un **bloque de ~27% de filas sin datos**
> (sin fecha **y** sin contrato **y** sin teléfono **y** sin canal). Requiere el layout
> real de cada pestaña.

### ❓ Bloque 3: Infraestructura y Acceso a Base de Datos

**8. ¿Qué motor de base de datos se seleccionó?**

> **Respuesta: PostgreSQL 16.14** en `DataCenter_Promigas` (host y puerto en `database/.env`), esquema
> `gestion_diaria`. **No hay decisión pendiente.**

**9. ¿Disponemos de un esquema/ambiente de pruebas (Dev/Staging)?**

> **Respuesta: no.** Solo existe `DataCenter_Promigas` con un esquema de trabajo y
> 48.036 filas reales. El usuario de conexión tiene **permiso de lectura** pero no de
> escritura, y no tiene acceso a otros esquemas.
>
> **Riesgo:** las migraciones del doc 03 se ejecutarían sobre producción.
> **Mitigación:** todas las migraciones M0–M8 son **aditivas** (no destruyen
> `gestion_diaria`), y `gdo_gestion_diaria` es la única operación destructiva (0 filas).
> Aun así, **deben probarse contra una copia** antes de aplicarse (S-05, R-14).

---

## 4. Plan de Acción

| # | Acción | Esfuerzo | Impacto | Responsable | Bloquea |
| ---: | :--- | :---: | :---: | :--- | :--- |
| 1 | Resolver **A-11** (empresa o asesor) con la jefatura | S | 🔴 | Negocio | Alcance del reporte |
| 2 | Cerrar la **cola de 43 variantes** y extender `clasificacion` a las 5 gaseras | M | 🔴 | Análisis + Negocio | Todo KPI de clasificación |
| 3 | **P-06** + **P-11**: corregir `normalizar_texto` y extender `fn_parse_fecha` | S | 🟠 | Análisis | Clasificación y temporalidad |
| 4 | **P-10 + P-13**: validación de dominio por columna + cuarentena | M | 🔴 | Análisis | Ingesta confiable |
| 5 | **P-12 + P-15**: bitácora con `sha256` y reingesta reproducible con cuadre al 100% | L | 🔴 | Análisis | Auditoría de cifras |
| 6 | Migraciones **M0–M6** del doc 03, probadas contra una copia | L | 🔴 | Análisis + DBA | Modelo analítico |
| 7 | Pedir el **layout real de cada pestaña** a las 5 gaseras | M | 🟠 | Análisis | Resuelve S-03 y el bloque de Caribe |
| 8 | **Doc 07**: plan de casamiento OCM × planilla y de apagado de Excel | M | 🟠 | Análisis + Negocio | Pilar 3 |
| 9 | **Doc 06**: definición de KPIs con el negocio | M | 🟠 | Negocio | Dashboard |
| 10 | Solicitar **permiso de escritura** sobre `gestion_diaria` (rol acotado) | S | 🟠 | DBA | Ingesta automatizada |

**Esfuerzo estimado total: ~9-11 semanas-persona.**

---

## 5. Métricas de control

| KPI | Meta | Medición |
| :--- | :--- | :--- |
| Cuadre staging → `fact_gestion` | 100% | `EXCEPT` en ambas direcciones (doc 03 §7) |
| Estados sin catalogar | 0 en las 5 gaseras | `v_valores_sin_mapear` extendido |
| Registros en `POR_REVISAR` | < 0.5% y visibles | `resultado_pendiente` |
| Filas con sangrado de columna | 0 | Validación de dominio en la ingesta |
| Fechas fuera de rango | 0 | R-01 |
| Cargas con bitácora completa | 100% | `dim_carga` |
| Líneas de código duplicado | < 2% | `uq_fact_gestion_clave` |
