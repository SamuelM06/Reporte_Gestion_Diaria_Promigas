# 🏛️ Estructura de Datos Técnica y Operativa - Promigas

> **Fuente Oficial:** Documento de Especificación Técnica & Operativa - *Estructura de Datos y Flujo de Gestión Diaria Promigas*.  
> **Objetivo:** Definir la matriz de fuentes, tipología de cabinas, libros, hojas y campos clave para la unificación y posterior migración a Base de Datos.
>
> **Actualización 2026-10-19:** Cada sección se enriqueció con la **estructura real
> verificada en la base de datos** `DataCenter_Promigas` (esquema `gestion_diaria`).
> Ver la columna «Estructura en BD» y los bloques de verificación al final de cada gasera.

---

## 1. Matriz General de Cabinas y Reglas Operativas

| Concepto Operativo | Definición Técnica | Aplica a | Regla de Negocio / Calidad | Verificación en BD |
| :--- | :--- | :--- | :--- | :--- |
| **Cabina / Cabinas** | Término que engloba conjuntamente las operaciones de **INBOUND** (entrantes) y **OUTBOUND** (salientes). | Operación General Promigas | Diferenciar siempre el tipo de tráfico telefónico. | ✅ `cabina` ∈ {INBOUND, OUTBOUND}; 14 filas sin valor en el consolidado |
| **Inbound** | Recepción de llamadas entrantes por parte del equipo de asesores de retención. | CEO, Gas Caribe, GDO, Surtigas | Requiere auditar tiempos de atención y tasa de abandono. *(Efigas NO tiene Inbound)*. | ✅ Confirmado: 4 tablas `_inbound` + 4 tablas `_abandono` |
| **Outbound** | Gestión de llamadas salientes realizadas por el asesor hacia el usuario. | Efigas, Gas Caribe, GDO, Surtigas | La fecha válida es la de ejecución del contacto. *(CEO NO tiene Outbound)*. | ✅ Confirmado: `efigas_outbound`, `caribe_outbound`, `gdo_outbound`, `surti_outbound` |
| **Abandono** | Llamadas entrantes que se cortan antes de ser atendidas por un asesor. | Exclusivo de Cabina Inbound | No tiene asesor asignado; se usa para métricas de nivel de servicio. | 🔴 **12,710 filas de abandono NO están en el consolidado** (H-02) |
| **PQRS / Informativo** | Peticiones, Quejas, Reclamos y Solicitudes radicadas por escrito. | GDO | La pestaña `informativo` es conceptualmente PQRS y debe homologarse. | ⚠️ `gdo_informativo` (4,191) es **bitácora de seguimiento**, no maestro (H-11) |

---

## 2. Inventario Detallado de Fuentes por Gasera

### 🏢 1. CEO (Compañía Energética del Cauca)
* **Cabina:** Exclusivamente **Inbound** (no maneja Outbound).
* **Ruta / Carpeta:** Carpeta `CEO` (SharePoint).
* **Archivo Principal:** `Gestion diaria CEO.xlsx`
* **Estructura de Hojas:**
  1. `Gestion Diaria Inbound Ceo`: Registros de atención de llamadas entrantes.
  2. `Abandono`: Registros de llamadas no contestadas / cortadas.
* **Campo Clave Temporal:** `FECHA INGRESO LLAMADA` (columna obligatoria para consolidar totales mensuales).
* **Estructura en BD:** `ceo_inbound` (2,749 filas, 21 col.) + `ceo_abandono` (4,020 filas, 11 col.).

**🔍 Verificado (2026-10-19)**
* `subtipificacion` está **100% vacía** → CEO no registra motivo de gestión.
* `localidad` 97.3% nula · `operador` 38.4% nulo · `anio` 61.6% nulo.
* `fecha_de_ejecucion` con **1 registro en 3748-11-16** (año imposible) y 153 nulos (5.6%).
* `ceo_abandono`: `hora` 99.2% nula, `contrato` 70.2% nulo, `fecha_llamada` 62.4% nula
  → **2,508 abandonos sin fecha**.
* **35 estados distintos**, de los cuales **22 no están en el catálogo** `clasificacion`.
* `fecha_carga` = `2026-09-15 17:22:38` (carga snapshot única).

---

### 🏢 2. Efigas
* **Cabina:** Exclusivamente **Outbound** (no maneja Inbound ni abandono).
* **Ruta / Carpeta:** Carpeta `Efigas` (SharePoint).
* **Archivo Principal:** `Gestion Diaria Outbound - Efigas.xlsx`
* **Estructura de Hojas:**
  1. `base efigas`: Hoja única de gestión saliente.
* **Reglas Críticas de Fechas:**
  * ✅ **Usar:** `FECHA DE EJECUCION` (indica el momento real en que se efectuó la llamada saliente).
  * ⚠️ **IGNORAR:** `FECHA BASE` (únicamente refleja la fecha en que se cargó el listado al sistema, no la gestión).
* **Estructura en BD:** `efigas_outbound` (999 filas, 21 col.).

**🔍 Verificado (2026-10-19) — REGLA CONFIRMADA CON DATOS**
* El lote `base = 2026-03-02` (64 filas) contiene ejecuciones reales del **2026-09-03 al
  2026-11-02**: el 100% de sus ejecuciones son de meses posteriores al lote.
  El lote `base = 26/01/2026` (48 filas, en texto) contiene ejecuciones del 2026-03-02 al
  2026-05-02: también el 100% fuera del mes del lote.
  El lote `base = 2026-06-09` (99 filas) contiene ejecuciones del 2026-03-01 al 2026-07-03.
  **`base` es la fecha de carga del lote, no la de la gestión.** ✅
* `base` es `varchar` con **formatos mezclados**: `2026-11-02 00:00:00` (timestamp) y
  `26/01/2026` / `17/02/2026` (texto).
* `fecha_de_ejecucion` nula en **172 de 999 filas (17.2%)** → 172 registros no ubicables.
* `localidad` 98.8% nula · `anio` 64.2% nulo · `subtipificacion` 51.5% nula.
* `contrato`, `canal`, `aseguradora`, `base`, `mes` al **100%** → identificadores sólidos.
* 1 estado sin catalogar: `retnida` (5 filas) — typo de `retenida`.

---

### 🏢 3. Gas Caribe (Gases del Caribe)
* **Cabina:** **Ambas Cabinas** (Inbound y Outbound).
* **Ruta / Carpeta:** Carpeta `Gas Caribe` (SharePoint). Se debe enfocar **únicamente en los 2 libros principales**:
* **Libros de Trabajo:**
  1. **Cabina Inbound:** `Gestion diaria Inbound -gases del caribe.xlsx`
     * *Estructura de Hojas:* Organizado en pestañas por mes (ej. `Enero 2026`) + hoja `abandono`.
     * *Columna de Agrupación:* `FECHA DE ATENCION` o sufijo de año en el nombre de la pestaña (`2026`).
  2. **Cabina Outbound:** `gestión diaria outbound-gases del caribe.xlsx`
     * *Estructura de Hojas:* Hoja `outbound`.
     * *Columna de Agrupación:* Columna directa `MES` para agrupación rápida.
* **Estructura en BD:** `caribe_inbound` (6,797, 35 col.) + `caribe_outbound` (1,305, 34 col.) + `caribe_abandono` (5,064, 12 col.).

**🔍 Verificado (2026-10-19)**
* `mes` viene con **el año embebido**: `"ABRIL 2026"`, `"MARZO 2026"`. Rompe el join con
  `mes_norm` de las demás gaseras (H-08).
* `caribe_inbound` tiene un **bloque de ~27% de filas sin datos** (1,774 sin fecha **y**
  1,828 sin contrato **y** 1,825 sin teléfono **y** 1,953 sin canal). Patrón de filas
  estructuralmente distintas — requiere investigación del layout del Excel.
* `caribe_outbound.localidad` está **100% vacía**.
* `caribe_outbound` tiene **2 filas con fecha `1970-01-01`**.
* `caribe_inbound.estado`: 0 nulos, 15/15 estados catalogados ✅ — **la gasera mejor
  catalogada**.
* `caribe_outbound.estado`: 26/26 estados catalogados ✅.
* `caribe_abandono` es la **tabla de abandono mejor estructurada**: `fecha_llamada` y
  `hora` al 100%, `telefono` al 99.1%. Tiene además `gestionado_inbound` (flag) que no
  existe en las otras gaseras.
* 509 grupos duplicados por `(contrato, fecha, estado)` → 2,821 filas (**41.5%**).
* `v_valores_sin_mapear` devuelve **0 filas** → Caribe está 100% homologado ✅.
* `fecha_carga` = `2026-10-01 17:19:22` (carga snapshot única).

---

### 🏢 4. GDO (Gases de Occidente) - Registro En Vivo
* **Cabina:** **Ambas Cabinas + PQRS Escritas**.
* **Condición Especial:** Archivo independiente conectado directamente con los asesores (operación en vivo).
* **Archivo:** `VALIDACION INFORMACION GDO- 24 de Junio 2026.xlsx` (en SharePoint).
* **Estructura de Hojas:**
  1. `gestión inbound`
  2. `out`
  3. `prqs escritas`
  4. `informativo`
  5. `abandono`
* **Regla de Limpieza y Homologación:**
  * La hoja `informativo` corresponde técnicamente a **PQRS** y debe renombrarse/unificarse bajo la tipología de PQRS durante la ingesta a la base de datos.
* **Estructura en BD:** 6 tablas — `gdo_inbound` (4,190, 39 col.), `gdo_outbound` (3,284, 68 col.),
  `gdo_pqrs` (747, 63 col.), `gdo_pqrs_escritas` (86, 20 col.), `gdo_informativo` (4,191, 29 col.),
  `gdo_abandono` (831, 18 col.) + `gdo_gestion_diaria` (0 filas, artefacto).

**🔍 Verificado (2026-10-19)**
* **GDO es la gasera mejor estructurada**: `gdo_inbound` tiene `resultado_final`,
  `fecha_de_llamada`, `mes`, `contrato` y `subtipificacion` prácticamente al 100%
  (2.7% nulos). **Es el estándar de calidad del proyecto.**
* `gdo_inbound.estado` está **100% vacía** → la columna válida es `resultado_final`.
  Un dashboard que use `estado` para GDO no retorna nada.
* `gdo_inbound.categoria`: `Peticion` (2,699) + `Petición` (1,470) — **cuatro** variantes
  de casing/tilde para el mismo valor.
* `gdo_inbound.tipo_contacto`: `TIULAR/ASEGURADO` (typo, 1,912) convive con
  `TITULAR/ASEGURADO` (1,585) y `TIULAR /ASEGURADO` (53).
* **`gdo_inbound.subtipificacion` (52 valores) es el mejor catálogo de motivos del
  proyecto** — jerárquico y numerado (`1.1`…`13.1`). Adopción propuesta como vocabulario
  maestro (D-02).
* `gdo_informativo` **no es un maestro**: es una bitácora de seguimiento con
  `estado_inf` = `PRIMER REGISTRO` / `2 REGISTRO - N DÍAS` y `tipo_registro` =
  `REGISTRO ÚNICO` (2,392) / `REGISTRO DUPLICADO` (619). 1,180 filas (29%) con todas las
  columnas nulas. `fecha_regi` con **3 formatos** y 99.7% no parseable (H-21).
* `gdo_pqrs` tiene la columna **`♣`** (símbolo U+2663, pos. 15 — decorativo en el Excel
  de origen) y artefactos `columna1`, `columna2`, `column62` (H-12).
  `fecha_atencion` 98.8% no parseable.
* `gdo_pqrs_escritas` es el **único modelo de PQRS con trazabilidad de ANS completa**
  (notificación GDO→Xuma, radicación Xuma→Aseguradora, respuesta de la aseguradora).
  Modelo de referencia.
* `gdo_abandono` es **prácticamente inutilizable**: `contrato` 92.1% nulo,
  `resultado_final` 88.1% nulo, `gestor` 82.3% nulo, `fecha_llamada` 79.9% nulo, y
  la columna fecha contiene **nombres de personas** (`"CARLOS DIAZ"`) (H-10).
* `gdo_outbound.resultado_de_retencion` 8.5% nulo; `gdo_outbound.estado` 7.8% nulo.
* Sin columnas `fecha_carga` → **no hay trazabilidad de ingesta** en GDO.

---

### 🏢 5. Surtigas
* **Cabina:** **Ambas Cabinas** (Inbound y Outbound).
* **Ruta / Carpeta:** Carpeta `SURTIGAS` (SharePoint).
* **Particularidad de Inbound (Fragmentación Histórica vs Continuidad):**
  1. **Inbound Histórico (Enero - Junio):**
     * Archivo: `SURTIGAS ARCHIVO RECUPERADO - Copia.xlsx` *(Sustituye archivo que sufrió daño)*.
     * Hojas: `Enero a Marzo`, `abrl` [sic], `mayo`, `junio`.
  2. **Inbound Continuidad (Julio - Octubre y subsiguientes):**
     * Ubicación: Subcarpeta `JULIO - AGOSTO 2026`.
     * Archivo: `Gestión diaria Inbound Surtigas.xlsx` (incluye hoja `ABANDONO`).
  3. **Cabina Outbound:**
     * Ubicación: Carpeta `SURTIGAS`.
     * Archivo: `gestión diaria outbound surtugas.xlsx`.
* **Columna Clave Temporal:** `FECHA DE LLAMADA` (aplica uniformemente a ambas cabinas).
* **Estructura en BD:** `surti_inbound` (9,423, 24 col.) + `surti_outbound` (299, 24 col.) + `surti_abandono` (2,795, 5 col.) + `surti_qr` (1,256, 54 col.).

**🔍 Verificado (2026-10-19)**
* **Surtigas tiene el mayor volumen (9,423 + 1,256 filas) y el peor contexto**:
  `operador` **87.6% nulo**, `subtipificacion` **70.7% nulo**, `localidad` **57.4% nulo**.
  → **No se puede medir productividad por asesor en la principal gasera por volumen.**
* **Es la única gasera con columnas de homologación ya enactadas** (precedente clave, H-20):
  * `validacion` ∈ {`VÁLIDO` (8,160), `REVISAR` (1,263)} — **control de calidad**, 100% poblado.
    ⚠️ `REVISAR` marca 4,246 filas (**31.6%**) pendientes de validación humana.
  * `tipo_contacto_homolog` ∈ {`TITULAR/ASEGURADO` (7,286), `TITULAR` (856), `ASEGURADO` (821), `CONTACTO A TERCERO` (260), `REVISAR` (163), `NO APLICA` (36), `LINK MARKETING` (1)} — **taxonomía de contacto** ya unificada, 100% poblado.
  * `maduracion_desde_la_venta_queja` — cohorte de maduración (13 valores), 100% poblado.
  * `asesor_venta_val` — asesor validado (303 nulos).
* `surti_abandono` tiene **0 nulos** pero: **no tiene columna `contrato`** y su
  `fecha_llamada` (formato `10/06/2026 10:05:04 a. m.`) es **100% no parseable** por
  `fn_parse_fecha`.
* `surti_qr.fecha_registro_solicitud` es **100% parseable** ✅ (a diferencia de GDO).
* 18 estados distintos, **11 sin catalogar** (incluye typos: `llaamda colgada`).
* 1,472 grupos duplicados (2,984 filas) — el mayor volumen absoluto de duplicados.
* `surti_outbound` arranca en **2023-08-13** (fuera de la ventana 2026 del resto).

---

### 🏢 6. Modelo de hechos (propuesto — aún no existe)

* **Estructura en BD:** el esquema `gestion_diaria` **no tiene todavía una tabla de
  hechos consolidada**. La capa actual son 16 tablas independientes: 8 de
  atención/outbound, 4 de abandono y 4 de PQRS.
* **Propuesta (doc 03):** `fact_gestion` con `subtipo_gestion` ∈ {ATENCION, ABANDONO},
  `fact_pqrs`, y 12 dimensiones (`dim_resultado`, `dim_motivo`, `dim_operador`,
  `dim_gasera`, `dim_cabina`, `dim_producto`, `dim_aseguradora`, `dim_medio`,
  `dim_tipo_contacto`, `dim_tipo_gestion`, `dim_carga`, `dim_origen`).

**🔍 Verificado (2026-10-19)**
* El abandono (12.710 filas) y los PQRS (6.280 filas) **no tienen hoy un destino común**
  con la atención (H-02).
* La clave de negocio natural **no está definida**: 3.114 grupos duplicados (20.2%) (H-05).
* `anio` es el año de **venta** en el 100% de las filas (H-07) y `mes` tiene 5 formatos
  distintos según gasera (H-08).
* El catálogo `clasificacion` solo cubre GasCaribe: 43 variantes sin catalogar (H-31).

---

## 3. Matriz Comparativa de Homologación de Fuentes

| Gasera | Cabina Inbound | Cabina Outbound | PQRS / Otros | Abandono | Columna Fecha Maestra | Ubicación / Archivo(s) | Tabla(s) en BD |
| :--- | :---: | :---: | :---: | :---: | :--- | :--- | :--- |
| **CEO** | Sí | No | No | Sí | `FECHA INGRESO LLAMADA` | `CEO / Gestion diaria CEO.xlsx` | `ceo_inbound`, `ceo_abandono` |
| **Efigas** | No | Sí | No | No | `FECHA DE EJECUCION` *(ignorar FECHA BASE)* | `Efigas / Gestion Diaria Outbound - Efigas.xlsx` | `efigas_outbound` |
| **Gas Caribe** | Sí | Sí | No | Sí | `FECHA DE ATENCION` (Inb) / `MES` (Out) | 2 libros: `Gestion diaria Inbound...` y `gestión diaria outbound...` | `caribe_inbound`, `caribe_outbound`, `caribe_abandono` |
| **GDO** | Sí | Sí | Sí (`prqs escritas` + `informativo`) | Sí | Fecha de registro en vivo | 1 libro en vivo: `VALIDACION INFORMACION GDO...` | `gdo_inbound`, `gdo_outbound`, `gdo_pqrs`, `gdo_pqrs_escritas`, `gdo_informativo`, `gdo_abandono` |
| **Surtigas** | Sí | Sí | No | Sí | `FECHA DE LLAMADA` | 3 libros: Histórico Ene-Jun, Continuidad Jul-Oct, Outbound | `surti_inbound`, `surti_outbound`, `surti_abandono`, `surti_qr` |

### 3.1 Volumetría por gasera en el esquema `gestion_diaria`

| Gasera | Atención | Abandono | PQRS | Total |
| :--- | ---: | ---: | ---: | ---: |
| CEO | 2,749 | 4,020 | 0 | 6,769 |
| Efigas | 999 | 0 | 0 | 999 |
| Gas Caribe | 8,102 | 5,064 | 0 | 13,166 |
| GDO | 7,474 | 831 | 5,024 | 13,329 |
| Surtigas | 9,722 | 2,795 | 1,256 | 13,773 |
| **Total** | **29,046** | **12,710** | **6,280** | **48,036** |

> Las 3 familias de gestión (atención, abandono, PQRS) viven hoy en **tablas
> independientes con esquemas de columnas distintos**, y no tienen un destino común
> (H-02). El modelo de hechos del doc 03 las unifica.

---

## 4. Rutas Oficiales en SharePoint

* **Ruta Madre (CEO, Efigas, Gas Caribe, Surtigas):**  
  `https://chariotandcastle.sharepoint.com/:f:/s/teamexperienciaalcliente/IgCMliHwe9GjTZbIUZDTZdpoAY0MFBoTaxKnLBbmFNDX7Gg?e=yCdsBa`
* **Ruta Archivo en Vivo (GDO):**  
  `https://chariotandcastle.sharepoint.com/:x:/r/sites/teamexperienciaalcliente/_layouts/15/doc2.aspx?sourcedoc=%7B89E8CBEE-0646-4F78-B9C8-4B2B8B0A86D6%7D&file=VALIDACION%20INFORMACION%20GDO-%2024%20de%20Junio%202026.xlsx`

---

## 5. Puntos Críticos y Cuestionamientos — **RESPUESTOS con Evidencia**

> Las 4 preguntas originales de la "Reunión del Lunes" fueron respondidas técnicamente.
> Las que requieren criterio de negocio siguen abiertas y están en
> `04_Hallazgos_y_Backlog.md` (D-P1…D-P5).

### 5.1 Homogeneidad de Columnas por Hoja

**Respuesta:** *No, con evidencia cuantificada.*

| Dimensión | Variantes observadas |
| :--- | :--- |
| `estado` | 4–5 grafías por concepto. `CANCELADA +VENTA` / `CANCELADO+VENTA` / `CANCELADO + VENTA` / `CANCELADA + VENTA` |
| `mes` | 5 formatos: `"ABRIL 2026"` (Caribe), `"Abril"` (GDO In), `"AGOSTO"` (GDO Out), `"ABRIL"` (resto) |
| `tipo_contacto` | 11+ variantes de "titular/asegurado" entre las 3 gaseras que lo registran |
| `base` | `2026-11-02 00:00:00` (timestamp) y `26/01/2026` (texto) en la misma columna `varchar` |
| `fecha` (texto) | 4 formatos distintos: `YYYY-MM-DD`, `DD/MM/YYYY`, `MMM-YY`, `DD/MM/YYYY HH:MM:SS a. m.` |
| Nombres de columna | `♣` (símbolo), `ORDEN LOCALIDAD`, `resposable_del_pago_...`, `fehca_de_cancelacion`, `amplicacion_term` |

### 5.2 Definición de Clave Primaria (PK)

**Respuesta:** *No existe PK de negocio. Debe construirse.*

* Candidato recomendado: `(gasera, cabina, contrato, fecha_gestion, estado_norm, tipo_contacto_norm)`.
* Tasa de colisión con ese candidato: **20.2%** del consolidado (3,114 grupos).
* Por gasera: `surti_inbound` 1,472 grupos · `caribe_inbound` 509 · `ceo_inbound` 475 ·
  `gdo_inbound` 328 · `efigas_outbound` 135.
* **Alternativa preferible**: `id_gestion` sintética + **clave natural en columna
  generated** (`md5(concat_ws('|', gasera, cabina, contrato, fecha, estado, tipo_contacto))`),
  con índice único parcial sobre las filas no duplicadas, de modo que los duplicados
  **quedan visibles y auditables** en lugar de eliminados silenciosamente.

### 5.3 Estrategia con la Base Local Desactualizada

**Respuesta:** *Resuelta por la evidencia — la base local NO existe como tabla.*

* **La base local ya ES el esquema `gestion_diaria`**: no hay otra tabla de histórico
  acumulado que decidir.
* Cubre enero 2025 – diciembre 2026 según `fecha_de_ejecucion` (con 4 fechas imposibles).
* La decisión de truncar/sanear/reemplazar fue tomada de facto: **se conservó y se
  amplió**, pero **sin dimensionar** (`dim_gasera`, `dim_cabina`, `dim_operador`,
  `dim_motivo` no existen) y **sin bitácora de carga** (H-13, H-14).
* Detalle en `02_Plan_Migracion_y_Estrategia_DB.md` §3.

### 5.4 Ventana de Transición a OCM

**Respuesta:** *OCM ya es el presente; falta el casamiento.*

* La réplica está sincronizando cada ~2 min con 0 errores.
* Las gaseras **siguen usando Excel en paralelo** → hoy se reportan dos fuentes de verdad.
* Falta medir el **casamiento**: qué % de las gestiones de Excel tienen su llamada en OCM
  (y al revés). Ese número decide si Excel se apaga por gasera o se conserva (D-P5).

---

## 6. Inventario de Objetos del Esquema `gestion_diaria`

| Tipo | Cantidad | Detalle |
| :--- | ---: | :--- |
| Tablas base | 18 | 17 con contenido + `gdo_gestion_diaria` (vacía) |
| Vistas | 5 | `v_caribe_inbound_clasificado`, `v_caribe_outbound_clasificado`, `v_caribe_abandono_franja`, `v_valores_sin_mapear`, `vw_gestion_diaria` (sin acceso) |
| Funciones | 4 | `normalizar_texto`, `fn_parse_fecha`, `normalizar_aseguradora`, `normalizar_producto` |
| Secuencias | 17 | Una por tabla con `id` serial |
| Índices de negocio | **0** | Solo las PK |
| Claves foráneas | **0** | Sin integridad referencial declarada |

> Detalle campo a campo en `01_Diccionario_de_Datos.md`; calidad en `05_Calidad_de_Datos.md`.
