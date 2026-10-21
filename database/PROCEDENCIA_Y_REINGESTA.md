# 🧾 Procedencia de los Datos y Plan de Persistencia

**Proyecto:** Reporte de Gestión Diaria - Retención Promigas
**Instancia:** `DataCenter_Promigas` (PostgreSQL 16.14) · Esquema de trabajo: `gestion_diaria`
**Última verificación en BD:** 21 de octubre de 2026
**Estado:** 📌 **Modo documentación. NO se trunca nada todavía.**

> 🔴 **Decisión vigente (D-11, 21-oct-2026):** hasta que se defina el **día de cierre de
> Excel**, los registros de gestión diaria de **2026 de las 5 gaseras** deben quedar
> **registrados en la base de datos**. El snapshot manual actual se va a reemplazar, pero
> **la estrategia exacta sigue abierta (A-16):**
> * **Opción A** — `TRUNCATE` de las 16 tablas + recarga completa de 2026.
> * **Opción B** — esquema paralelo (`gestion_diaria_2026`) + consolidación posterior.
> * **Opción C** — carga incremental sobre el staging actual, sin borrar nada.
>
> 🔴 **D-12 (21-oct-2026):** los registros de **OCM también deben persistirse** en la base
> de datos, no solo estar disponibles en la réplica de lectura. Cuando las gaseras
> empiecen a registrar en OCM, esos registros deben quedar en el modelo **con su origen**,
> para que la transición **no pierda el histórico ni duplique** lo ya registrado en Excel.
> (Llave de casamiento: **A-17**.)

---

## 1. Respuesta corta: ¿de dónde salen los datos?

| Capa de la BD | Origen físico | ¿Automático? | Evidencia |
| :--- | :--- | :--- | :--- |
| `gestion_diaria` (16 tablas de datos, 48.036 filas) | **Libros Excel de SharePoint** (13 libros, 5 gaseras) | ❌ **Manual, por snapshot** | `fecha_carga` con un único valor por tabla (15-sep y 01-oct-2026) |
| `gestion_diaria.clasificacion` (40 filas) | Catálogo interno, **no viene de Excel** | ❌ Manual | Solo cubre GasCaribe |
| `reportes.reporte_promi` (29.222 filas) | Consolidado del mismo universo Excel | ❌ Externo al repo | Reconstruido hoy 21-oct 15:57 en un único batch de 6 s |
| `ocm_retencion` (`log_calls` 339.499) | **Plataforma OCM** (contact center) | ✅ **Automático, ~2 min** | `sync_log`: 53.735 sincronizaciones desde 14-ago-2026 |

> ⚠️ **No hay ningún Excel local versionado.** El `.gitignore` excluye `*.xlsx`, `*.xls`,
> `*.csv` y `data/raw/`. Los archivos viven **en SharePoint** y se descargan a
> `data/raw/` (ignorado por Git) en el momento de la carga.
>
> ⚠️ **No existe ingesta automática.** En la BD solo hay 4 funciones de normalización
> (`normalizar_texto`, `fn_parse_fecha`, `normalizar_aseguradora`, `normalizar_producto`),
> la extensión `dblink`, **cero triggers, cero procedimientos y cero jobs**. En el repo
> solo hay 2 scripts, ambos de **solo lectura**
> (`conexion_template.py`, `inspeccion_esquema.py`). No hay ETL.

---

## 2. Evidencia del snapshot manual (verificado en BD, 21-oct-2026)

> 📁 **Ruta física verificada** (OneDrive del equipo, sincronizada con SharePoint):
> ```text
> <OneDrive>\
>   Team Experiencia al Cliente - Promigas\Retención\Promigas\
>     Gestión diaria Promigas Inb -Outbound\      ← 📂 RUTA MADRE (5 gaseras)
> ```
> Inventario completo (9 libros, 41 hojas de datos, volumetría 2026):
> **`context/Analisis/14_Estructura_Origen_Excel.md`**
> Vista operativa: **`database/FICHA_ORIGEN_POR_GASERA.md`**

### 2.1 `fecha_carga`: solo 6 de 16 tablas la tienen, y con un único valor

| Tabla | Filas | `fecha_carga` (min → max) | Valores distintos |
| :--- | ---: | :--- | ---: |
| `ceo_inbound` | 2.749 | 2026-09-15 17:22:38 | 1 |
| `ceo_abandono` | 4.020 | 2026-09-15 17:22:39 | 1 |
| `efigas_outbound` | 999 | 2026-09-15 17:22:40 | 1 |
| `caribe_inbound` | 6.797 | 2026-10-01 17:19:22 | 1 |
| `caribe_outbound` | 1.305 | 2026-10-01 17:19:22 | 1 |
| `caribe_abandono` | 5.064 | 2026-09-15 17:22:37 → 2026-10-01 17:24:56 | 2 |
| `surti_*` (4 tablas) | 13.773 | **sin columna** | — |
| `gdo_*` (6 tablas) | 13.329 | **sin columna** | — |

**Lectura:** la BD contiene **dos fotos de la misma realidad separadas 16 días**. El
archivo de GDO se actualiza **en vivo** en SharePoint, pero su copia en la BD es de
septiembre: **la BD ya está desactualizada respecto de SharePoint.**

### 2.2 Inventario completo de lo que hay hoy (a truncar)

| # | Tabla | Filas | Libro Excel de origen | Hoja / pestaña |
| ---: | :--- | ---: | :--- | :--- |
| 1 | `ceo_inbound` | 2.749 | `CEO / Gestion diaria CEO.xlsx` | `Gestion Diaria Inbound Ceo` |
| 2 | `ceo_abandono` | 4.020 | `CEO / Gestion diaria CEO.xlsx` | `Abandono` |
| 3 | `efigas_outbound` | 999 | `Efigas / Gestion Diaria Outbound - Efigas.xlsx` | `base efigas` |
| 4 | `caribe_inbound` | 6.797 | `Gestion diaria Inbound -gases del caribe.xlsx` | `Enero 2026`…`Septiembre 2026` |
| 5 | `caribe_abandono` | 5.064 | `Gestion diaria Inbound -gases del caribe.xlsx` | `abandono` |
| 6 | `caribe_outbound` | 1.305 | `gestión diaria outbound-gases del caribe.xlsx` | `outbound` |
| 7 | `gdo_inbound` | 4.190 | `VALIDACION INFORMACION GDO- 24 de Junio 2026.xlsx` | `gestión inbound` |
| 8 | `gdo_outbound` | 3.284 | mismo archivo | `out` |
| 9 | `gdo_pqrs` | 747 | mismo archivo | `prqs escritas` |
| 10 | `gdo_pqrs_escritas` | 86 | mismo archivo | `prqs escritas` (reestructurada a mano) |
| 11 | `gdo_informativo` | 4.191 | mismo archivo | `informativo` |
| 12 | `gdo_abandono` | 831 | mismo archivo | `abandono` |
| 13 | `surti_inbound` | 9.423 | `SURTIGAS ARCHIVO RECUPERADO - Copia.xlsx` + `Gestión diaria Inbound Surtigas.xlsx` | `Enero a Marzo`, `abrl`, `mayo`, `junio` |
| 14 | `surti_abandono` | 2.795 | `Gestión diaria Inbound Surtigas.xlsx` | `ABANDONO` |
| 15 | `surti_outbound` | 299 | `gestión diaria outbound surtugas.xlsx` | `outbound` |
| 16 | `surti_qr` | 1.256 | `Gestión diaria Inbound Surtigas.xlsx` | hoja de QR |
| — | `clasificacion` | 40 | *(catálogo interno)* | — |
| — | `gdo_gestion_diaria` | 0 | *(artefacto, vacía)* | — |

**Total datos: 48.036 filas.**

### 2.3 Rutas de SharePoint (origen físico)

* **Ruta madre** (CEO, Efigas, Gas Caribe, Surtigas):
  `https://chariotandcastle.sharepoint.com/:f:/s/teamexperienciaalcliente/IgCMliHwe9GjTZbIUZDTZdpoAY0MFBoTaxKnLBbmFNDX7Gg?e=yCdsBa`
* **Ruta archivo en vivo** (GDO):
  `https://chariotandcastle.sharepoint.com/:x:/r/sites/teamexperienciaalcliente/_layouts/15/doc2.aspx?sourcedoc=%7B89E8CBEE-0646-4F78-B9C8-4B2B8B0A86D6%7D&file=VALIDACION%20INFORMACION%20GDO-%2024%20de%20Junio%202026.xlsx`

> 📌 La definición exacta de rutas, libros, hojas y columnas **de cada gasera** está
> pendiente de documentar por negocio. Plantilla lista en
> **`FICHA_ORIGEN_POR_GASERA.md`** — es el insumo bloqueante de la reingesta.

---

## 3. La otra capa: `reportes.reporte_promi`

| Aspecto | Verificado |
| :--- | :--- |
| Filas | 29.222 (auditoría del 19-oct: 31.122 → **la tabla cambió**) |
| `created_at` | Todas las filas entre **21-oct-2026 15:57:38 y 15:57:44** → reconstrucción total en un batch de 6 s |
| Distribución | CEO 3.271 · EFIGAS 1.146 · CARIBE 6.360 · GDO 7.261 · SURTIGAS 11.184 |
| Solape con staging | CEO: 2.560 de 3.271 filas coinciden en `(contrato, fecha_ejecucion)` con `ceo_inbound` → **mismo universo, consolidación distinta** |
| Índices | `idx_reporte_promi_fecha`, `_mes`, `_estado`, `_dist`, `_cabina`, `_clas` |
| Trigger / vista | No es vista: es tabla física, sin trigger, sin función que la mantenga |

> 🔴 **Doble fuente de verdad.** `gestion_diaria` (staging crudo) y
> `reportes.reporte_promi` (core consolidado) cuentan cosas distintas y no
> reconcilian. Mientras la reingesta no se defina, **hay que decidir cuál gobierna**.
> Recomendación: `reportes` se reconstruye **desde** `gestion_diaria` una vez exista
> el modelo dimensional (`fact_gestion`), no en paralelo.

---

## 4. OCM: la única fuente viva y automática

| Aspecto | Verificado |
| :--- | :--- |
| Tablas | 10 (`log_calls`, `log_agentstatus`, `log_agentstatus_detail`, `agent`, `agent_historial`, `campaign`, `groups`, `skill_loads`, `sync_config`, `sync_log`) |
| `log_calls` | 339.499 llamadas, de **2023-06-05** a **2026-10-21 15:49** |
| `sync_log` | 53.735 sincronizaciones desde **2026-08-14 17:58**; última 2026-10-21 20:56, cadencia **~2 min**, `status = success` |
| `sync_config` | 0 filas (no hay configuración de sync persistida en la BD) |

> OCM es el **destino de la transición**, no la fuente actual. El número que falta y
> que define el proyecto sigue siendo el **casamiento**: qué % de las gestiones de
> Excel tienen su llamada en OCM. Ese número no existe todavía.

---

## 5. Plan de reingesta (truncar → cargar lo real)

> 🔴 **Este plan es destructivo. No ejecutar hasta completar los prerrequisitos.**
> `TRUNCATE` no tiene rollback. El paso 0 (respaldo) no es opcional.

### 5.1 Prerrequisitos bloqueantes

| # | Prerrequisito | Responsable | Estado |
| ---: | :--- | :--- | :--- |
| 1 | Ficha de origen por gasera completa (ruta, libro, hoja, columnas, columna fecha maestra) | Negocio | 🟡 **En curso** — plantilla lista, en espera del detalle por gasera |
| 2 | Confirmar qué del snapshot actual se conserva (histórico 2025–2026 que no está en SharePoint) | Negocio | ⬜ |
| 3 | Decidir la estrategia de persistencia: **A** (truncado + recarga) / **B** (esquema paralelo) / **C** (incremental) | Equipo de datos + DBA | ⬜ **A-16** |
| 4 | Definir la llave de casamiento Excel ↔ OCM y dónde se persisten los registros de OCM | Equipo de datos + OCM | ⬜ **A-17** |
| 5 | Definir el día de cierre de Excel | Negocio | ⬜ **A-18** |
| 6 | Respaldo verificado del esquema `gestion_diaria` + `reportes` | Análisis | ⬜ (solo si se elige A o B) |
| 7 | `sha256` de cada archivo descargado | Análisis | ⬜ Automatizable |
| 8 | Extender `clasificacion` a las 5 gaseras (hoy: 40 filas, solo GasCaribe) | Análisis | ⬜ 43 variantes pendientes |
| 9 | Corregir `normalizar_texto` (la `/`) y extender `fn_parse_fecha` (3 formatos) | Análisis | ⬜ |

### 5.2 Las tres estrategias de persistencia (decisión abierta, A-16)

> 📊 **Con el origen verificado (21-oct-2026), 2026 son ≈ 42.070 filas**
> (33.501 atención/outbound + 3.383 abandono + 5.186 PQRS). La base actual tiene
> 48.036 filas de un snapshot parcial → cargar 2026 real la deja en ~42.000 filas.

| | **Opción A — Truncado + recarga** | **Opción B — Esquema paralelo** | **Opción C — Carga incremental** |
| :--- | :--- | :--- | :--- |
| Qué se hace | `TRUNCATE` de las 16 tablas y recarga completa de 2026 desde SharePoint | Se crea `gestion_diaria_2026` y se carga 2026 ahí; el staging actual queda congelado como histórico | Se carga día a día sobre el staging actual, **sin borrar**; el snapshot viejo se marca como `carga_id` antiguo |
| Ventaja | Resultado limpio: una sola verdad, sin duplicados ni datos de 2025 | Cero riesgo sobre lo actual; se valida en paralelo antes de Consolidar | Es la opción más natural para el flujo diario una vez automatizado |
| Costo | Irreversible; exige respaldo previo y doble verificación | Dos fuentes vivas hasta consolidar; hay que definir la consolidación | El staging mezcla snapshot antiguo y cargas reales: hay que diferenciar por `carga_id` |
| Riesgo principal | 🔴 Pérdida del histórico 2025 que no está en SharePoint | 🟠 Divergencia de cifras si se reporta sobre los dos esquemas | 🟠 Necesita `dim_carga` para distinguir el snapshot manual de las cargas reales |
| Requiere | Respaldo + checklist + `BEGIN/COMMIT` | Definir el proceso de consolidación | **`dim_carga` + `dim_origen` (sha256)** |
| Recomendación | ⚠️ Solo si el histórico 2025 ya no se necesita | ✅ **Preferible si 2025 tiene valor** | ✅ **Preferible para el día a día**, combinada con B |

> 💡 **Las tres convergen en lo importante:** los registros de 2026 quedan en la base con
> su `origen` y su `carga_id`, y **nada se descarta en silencio** (cuarentena + bitácora).
> Lo que cambia es si el snapshot manual sobrevive o no.

### 5.3 Respaldo (obligatorio si se elige A o B)

```sql
-- Un solo comando de respaldo para el staging actual.
-- Crear un esquema nuevo, nunca reemplazar el vivo.
CREATE SCHEMA IF NOT EXISTS gestion_diaria_bak_20261021;

-- Backup real (ejecutar ANTES de cualquier truncate o carga masiva)
CREATE TABLE gestion_diaria_bak_20261021.ceo_inbound AS SELECT * FROM gestion_diaria.ceo_inbound;
-- … repetido por cada tabla (17) …
```

> ℹ️ En esta máquina **no hay cliente `pg_dump` instalado** (`psql`/`pg_dump` no están
> en el PATH). El respaldo vía SQL (`CREATE TABLE … AS SELECT`) funciona con el driver
> Python ya presente. Alternativa: instalar PostgreSQL Client Tools.

### 5.4 Opción A — Truncado del staging (SQL de referencia, **NO ejecutar**)

```sql
-- 16 tablas de datos (contenido estático y desactualizado)
TRUNCATE TABLE
    gestion_diaria.ceo_inbound, gestion_diaria.ceo_abandono,
    gestion_diaria.efigas_outbound,
    gestion_diaria.caribe_inbound, gestion_diaria.caribe_abandono,
    gestion_diaria.caribe_outbound,
    gestion_diaria.gdo_inbound, gestion_diaria.gdo_outbound,
    gestion_diaria.gdo_pqrs, gestion_diaria.gdo_pqrs_escritas,
    gestion_diaria.gdo_informativo, gestion_diaria.gdo_abandono,
    gestion_diaria.surti_inbound, gestion_diaria.surti_abandono,
    gestion_diaria.surti_outbound, gestion_diaria.surti_qr
RESTART IDENTITY;

-- clasificacion: NO truncar hasta extenderla a las 5 gaseras (la usan 5 vistas y el JOIN
-- de resultado_normalizado/clasificacion). Si se trunca, esas vistas devuelven vacío.
-- TRUNCATE TABLE gestion_diaria.clasificacion RESTART IDENTITY;

-- gdo_gestion_diaria: 0 filas, es un artefacto -> DROP definitivo
DROP TABLE IF EXISTS gestion_diaria.gdo_gestion_diaria;
```

**Verificación post-truncado:**

```sql
SELECT table_name, (xpath('/row/c/text()', query_to_xml(
    format('SELECT count(*) AS c FROM gestion_diaria.%I', table_name),
    false, true, '')))[1]::text::bigint AS filas
FROM information_schema.tables
WHERE table_schema = 'gestion_diaria' AND table_type = 'BASE TABLE'
ORDER BY 1;
-- Esperado: 0 en las 16 de datos, 40 en clasificacion
```

> 💡 **Trampa de seguridad verificada (21-oct-2026):** en PostgreSQL `TRUNCATE` **es
> transaccional**. Se puede envolver en una transacción y deshacer con `ROLLBACK` si
> algo no cuadra. Probado en esta instancia: los 16 `TRUNCATE ... RESTART IDENTITY`
> se ejecutaron dentro de un `BEGIN` y el `ROLLBACK` devolvió los conteos intactos
> (2.749 / 9.423 / … verificados). Aun así, **esto no sustituye el respaldo**: un
> rollback deshace la sesión actual, no un `COMMIT` ya ejecutado.
>
> Secuencia segura recomendada:
> ```sql
> BEGIN;
> TRUNCATE TABLE ... RESTART IDENTITY;
> -- verificar conteos = 0
> -- si todo cuadra:
> COMMIT;
> -- si algo no cuadra:
> ROLLBACK;
> ```

### 5.5 Carga de la gestión diaria real (común a las 3 opciones)

```
OneDrive / SharePoint (ruta madre "Gestión diaria Promigas Inb -Outbound")
   ↓  descarga a data/raw/<gasera>/<archivo>_<sha8>.xlsx
   ↓  manifest: sha256 + ruta + fecha descarga + filas por hoja
Landing (misma estructura que el Excel — D-13: mismas columnas, mismos nombres)
   ↓  L-01..L-07 limpieza → tipado → normalización → homologación
   ↓  R-01..R-20 validación
   ↓  válidos → carga   |   inválidos → quarantine (regla + valor + motivo)
fact_gestion / fact_pqrs (modelo dimensional, doc 03)
```

**Reglas de carga verificadas contra los archivos (21-oct-2026):**

| Regla | Detalle |
| :--- | :--- |
| **D-13** | La tabla conserva la **misma estructura del Excel**: mismas columnas, mismos nombres, mismo orden. |
| **D-14** | El filtro de 2026 es por **columna de fecha de la fila**, **nunca** por nombre de hoja (la hoja `ENERO A MARZO` de Surtigas trae datos de dic-2025). |
| **D-15** | En las hojas de **abandono** la fecha real está en la **primera columna** (`FECHA`/`fecha`), no en `Fecha de llamada` (vacía en el 98–100% de las filas). |
| Columna fecha por gasera | CEO `FECHA INGRESO LLAMADA` · Efigas `FECHA DE EJECUCION` · Caribe `FECHA DE ATENCION`/`fecha de atencion` · GDO `FECHA DE LLAMADA`/`FECHA EJECUCION` · Surtigas `FECHA DE LLAMADA` |
| Columna resultado por gasera | CEO `Resultado de retencion` · Efigas `ESTADO` · Caribe `RESULTADO DE RETENCION` · GDO `RESULTADO FINAL`/`Resultado de retencion` · Surtigas `RESULTADO FINAL` |
| `FECHA DE BASE` / `BASE` | **Nunca** como fecha de gestión (Efigas: fecha de carga del lote) |
| GDO `ESTADO` | Ignorar: es la marca manual "NO APTO" (H-29) |

Convenciones de respaldo:

| Elemento | Regla |
| :--- | :--- |
| Ruta de descarga | `data/raw/<gasera>/<nombre_archivo>_<sha8>.xlsx` |
| Registro de trazabilidad | `dim_carga` (lote) + `dim_origen` (sha256, ruta SharePoint) |
| Manifest local | `data/raw/manifest.csv` (ignorado por Git: contiene rutas y PII) |
| Idempotencia | Clave natural `md5(gasera|cabina|contrato|fecha|resultado_norm|tipo_contacto|operador|fecha_carga)` |
| Duplicados | **Nunca se borran**: se marcan `es_duplicado = true` y se auditan |

### 5.6 Reconstrucción de `reportes`

Después de la carga real, `reportes.reporte_promi` se reconstruye **desde** el staging
nuevo (o se depreca el esquema `reportes` a favor de `fact_gestion`). Decisión
pendiente de negocio: ¿`reportes` sigue siendo la capa de consumo del dashboard, o
lo reemplaza el modelo dimensional?

### 5.7 Persistencia de los registros de OCM (D-12, A-17)

> 🔴 **Requisito:** cuando las gaseras empiecen a registrar en OCM, **esos registros
> también quedan en la base de datos**. Hoy `ocm_retencion` es una **réplica de
> lectura**: sirve para consultar, pero el modelo de reportes no los usa.

Diseño propuesto (a confirmar en A-17):

| Elemento | Propuesta |
| :--- | :--- |
| Dónde | `fact_gestion` con un discriminante **`origen` ∈ {EXCEL, OCM}** (o tablas separadas si A-17 lo decide así) |
| Granularidad | 1 llamada = 1 registro, con su `carga_id` y su `dim_origen` (agente, campaña, skill) |
| Llave de casamiento | Clave de evento (contrato + fecha/hora + tipo de llamada + id de OCM) para **enlazar** el registro de Excel con el de OCM sin duplicar |
| Durante la transición | Ambos conjuntos coexisten y se marcan; la regla de exclusión se define por **gasera** según el día de cierre (A-18) |
| Histórico | El histórico en Excel **no se borra** al cerrar: queda en la base con `origen = EXCEL` |
| Forbidden | No usar la réplica `ocm_retencion` como fuente del reporte sin persistir: `sync_log` y `log_calls` son de lectura y no tienen trazabilidad de carga al modelo |

Campos disponibles hoy en `ocm_retencion.log_calls` (verificado) para construir el
registro persistido: `fecha`, `extension`, `agent`, `idcampaign`, `typecall`,
`typeskill`, `skill`, `numbercall`, `resultcall`, `resultcalldesc`, `timering`,
`timequeue`, `timecall`, `timeacw`, `timeivr`, `timedialplan`, `timetotal`,
`result`, `resultdesc`, `resultgroup`, `callscheduled_at`.

> ⚠️ **Pendiente de negocio:** qué campos de OCM equivalen a los del modelo
> (`estado`, `motivo`, `operador`, `tipo_contacto`, `fecha_gestion`) y cuál es el
> identificador único de llamada por gasera. Requiere la matriz de configuración de
> llamadas (`context/Analisis/011_OCM_Configuracion_Llamadas.md`) y la validación de
> A-17.

---

## 6. Riesgos de la operación

| # | Riesgo | Mitigación |
| ---: | :--- | :--- |
| 1 | 🔴 `TRUNCATE` es irreversible | **D-11: no truncar todavía.** Si se elige la opción A: respaldo previo + `BEGIN`/`COMMIT` con verificación de conteos en medio |
| 2 | 🔴 Pérdida del histórico 2025–2026 que no está en SharePoint | Confirmar con negocio (prereq. 2). Si tiene valor → opción B (esquema paralelo) |
| 3 | 🟠 `clasificacion` truncada → 5 vistas vacías y JOIN de clasificación roto | No truncar hasta extenderla a 5 gaseras |
| 4 | 🟠 Las 5 vistas sobreviven al truncate pero quedan vacías | `v_caribe_inbound_clasificado`, `v_caribe_outbound_clasificado`, `v_caribe_abandono_franja`, `v_valores_sin_mapear`, `vw_gestion_diaria` |
| 5 | 🟠 `id serial` no reiniciado → huecos en las PK | `RESTART IDENTITY` en el truncate (17 secuencias) |
| 6 | 🟠 Ingesta automatizada con otra cuenta sin permisos | Hoy el owner es `<usuario_conexion>`; delegar `GRANT USAGE, SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA gestion_diaria TO <rol>` |
| 7 | 🟡 Cero bitácora → no se sabe qué versión del Excel está cargada | `dim_carga` + `dim_origen` (sha256) desde la primera carga |
| 8 | 🟡 Doble fuente de verdad (`gestion_diaria` vs `reportes`) | Decidir capa que gobierna (§5.6) |
| 9 | 🔴 Pérdida de registros en la transición Excel → OCM | D-12: persistir **ambos** conjuntos con su `origen`; llave de casamiento (A-17) |
| 10 | 🔴 Doble conteo del mismo evento durante la transición | Regla de exclusión por gasera y fecha de cierre (A-18, R-01, R-19) |
| 11 | 🟠 Truncado accidental (el usuario es owner y tiene `TRUNCATE`) | R-17: siempre dentro de `BEGIN`, verificación en medio y doble confirmación humana |

---

## 7. Permisos reales (verificado 21-oct-2026)

| Objeto | `SELECT` | `INSERT` | `UPDATE` | `DELETE` | `TRUNCATE` | Owner |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| 18 tablas de `gestion_diaria` | ✅ | ✅ | ✅ | ✅ | ✅ | `<usuario_conexion>` |
| 2 tablas de `reportes` | ✅ | ✅ | — | — | ✅ | `<usuario_conexion>` |

> ⚠️ **Corrección a la documentación previa.** `database/README.md` y el `README.md`
> raíz afirmarían que *"el usuario de conexión no es superusuario y no tiene permiso de
> escritura sobre los esquemas de producción verificados"*. **Eso ya no es cierto**:
> `<usuario_conexion>` es el **owner** de las tablas de `gestion_diaria` y `reportes` y tiene
> permisos completos de escritura. Esto **baja el riesgo operativo del truncado**
> (se puede respaldar y revertir desde la propia BD), pero **sube el riesgo de
> error**: nada impide truncar por accidente. Por eso la Fase 0 es obligatoria.

---

## 8. Documentos relacionados

| Documento | Contenido |
| :--- | :--- |
| `database/README.md` | Configuración y uso del módulo de conexión |
| `database/FICHA_ORIGEN_POR_GASERA.md` | **Plantilla** para documentar rutas, libros, hojas y columnas por gasera |
| `context/Analisis/01_Diccionario_de_Datos.md` | Inventario columna por columna de las 17 tablas |
| `context/Analisis/02_Mapeo_Origen_Destino.md` | Especificación de la ingesta campo por campo |
| `context/Analisis/08_Flujo_De_Datos.md` | Arquitectura de flujo de datos (actual vs objetivo) |
| `context/Analisis/03_Modelo_Datos.md` | Modelo en estrella y migraciones M0–M8 |
| `context/planes/02_Plan_Migracion_y_Estrategia_DB.md` | Estrategia de migración y estado de los 3 pilares |
