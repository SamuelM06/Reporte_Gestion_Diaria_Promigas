# 03. Modelo de Datos (ERD)

**Proyecto:** Gestión Diaria Promigas
**Esquema de base de datos:** `gestion_diaria`
**Motor:** PostgreSQL 16.14
**Fecha:** 19 de octubre de 2026
**Estado:** Borrador para revisión y aprobación **antes de escribir el DDL definitivo**

---

## 1. Propósito

Este documento define el modelo de datos en **dos vistas**:

1. **Cómo está hoy** (§3) — verificado con el DDL real el 2026-10-19.
2. **Cómo debe quedar** (§4) — propuesta a aprobar.

Incluye las **migraciones SQL concretas** (§6) para pasar de una a otra.

**Decisiones que este documento pide aprobar:**

| # | Decisión | Opciones | Recomendación |
| ---: | :--- | :--- | :--- |
| A-04 | ¿Abandono, atención y PQRS en una tabla o en varias? | (a) Una tabla de hechos con nulos; (b) Una tabla de hechos con `subtipo_gestion`; (c) Tres tablas de hechos | **(b)** — una tabla con `subtipo_gestion` discriminado. Ver §4.2 |
| A-03 | ¿Llave primaria de las llamadas? | (a) Combinación de campos; (b) Hash de contenido; (c) ID generado + hash | **(c)** — `id_gestion` + `clave_natural` (md5). Ver §4.1 |
| — | ¿Qué dimensiones se necesitan? | — | `dim_gasera`, `dim_cabina`, `dim_resultado`, `dim_motivo`, `dim_operador`, `dim_producto`, `dim_aseguradora`, `dim_medio`. Ver §4.3 |
| — | ¿Tabla separada para abandono? | — | **No**: mismo modelo, `subtipo_gestion='ABANDONO'`. Ver §4.2 |
| A-09 | ¿La clasificación varía por gasera? | — | **Resuelto: no.** La tabla `clasificacion` es por gasera, pero los 4 resultados APTA son los mismos en las 5. Ver §4.3 |

---

## 2. Convenciones

| Notación | Significado |
| :--- | :--- |
| **PK** | Llave primaria |
| **FK** | Llave foránea |
| 🔴 | Deuda técnica a corregir |
| 🟠 | Deuda técnica a documentar |
| ✅ | Cumple el estándar objetivo |

**Estándar de nombres:** `snake_case`, sin tildes, sin espacios, sin typos, sin prefijos
de tabla redundantes. Los nombres actuales que lo incumplen están en §6.1.

---

## 3. Vista actual — cómo está la base de datos hoy

### 3.1 Diagrama

```mermaid
erDiagram
    ceo_inbound      { int id PK | varchar estado | date fecha_de_ejecucion | ... }
    ceo_abandono     { int id PK | date fecha_llamada | varchar hora | bigint telefono }
    efigas_outbound  { int id PK | varchar estado | date fecha_de_ejecucion | varchar base }
    caribe_inbound   { int id PK | varchar estado | date fecha_de_ejecucion | ... }
    caribe_outbound  { int id PK | varchar estado | date fecha_de_ejecucion | ... }
    caribe_abandono  { int id PK | date fecha_llamada | boolean gestionado_inbound }
    gdo_inbound      { int id PK | text resultado_final | text fecha_de_llamada | ... }
    gdo_outbound     { int id PK | text resultado_de_retencion | text fecha_ejecucion }
    gdo_abandono     { int id PK | text fecha_llamada | text numbercall }
    gdo_pqrs         { int id PK | varchar contrato | varchar fecha_registro_solicitud }
    gdo_pqrs_escritas{ int id PK | integer contrato | date radicado_usu_gdo }
    gdo_informativo  { int id PK | bigint solicitud | text fecha_regi }
    surti_inbound    { bigint id PK | text estado | text fecha_de_ejecucion }
    surti_outbound   { bigint id PK | text estado | text fecha_de_ejecucion }
    surti_abandono   { bigint id PK | text fecha_llamada | text telefono }
    surti_qr         { bigint id PK | text fecha_registro_solicitud }
    clasificacion    { text gasera PK | text variante PK | text resultado_normalizado | text clasificacion }

    ceo_inbound }o..o| clasificacion : "por estado (LEFT JOIN manual)"
    efigas_outbound }o..o| clasificacion : ""
    caribe_inbound }o..o| clasificacion : ""
    gdo_inbound }o..o| clasificacion : ""
    surti_inbound }o..o| clasificacion : ""
```

### 3.2 Inventario

| Tabla | Filas | PK | FK | Índices de negocio | Notas |
| :--- | ---: | :--- | :---: | :---: | :--- |
| `ceo_inbound` | 2.749 | `id` | 0 | 0 | `subtipificacion` 100% nula |
| `ceo_abandono` | 4.020 | `id` | 0 | 0 | `hora` 99.2% nula, `fecha_llamada` 62.4% nula |
| `efigas_outbound` | 999 | `id` | 0 | 0 | `base` con 2 formatos |
| `caribe_inbound` | 6.797 | `id` | 0 | 0 | Bloque de ~27% sin datos |
| `caribe_outbound` | 1.305 | `id` | 0 | 0 | `localidad` 100% nula |
| `caribe_abandono` | 5.064 | `id` | 0 | 0 | Mejor calidad de la capa |
| `gdo_inbound` | 4.190 | `id` | 0 | 0 | `estado` 100% nula |
| `gdo_outbound` | 3.284 | `id` | 0 | 0 | 68 columnas de `text` |
| `gdo_abandono` | 831 | `id` | 0 | 0 | 92% nula en lo importante |
| `gdo_pqrs` | 747 | `id` | 0 | 0 | Columna `♣`, `columna1/2/62` |
| `gdo_pqrs_escritas` | 86 | `id` | 0 | 0 | Único modelo de ANS completo |
| `gdo_informativo` | 4.191 | `id` | 0 | 0 | Bitácora, no maestro |
| `surti_inbound` | 9.423 | `id` | 0 | 0 | `operador` 87.6% nula y sangrada |
| `surti_outbound` | 299 | `id` | 0 | 0 | |
| `surti_abandono` | 2.795 | `id` | 0 | 0 | Sin columna `contrato`; fecha no parseable |
| `surti_qr` | 1.256 | `id` | 0 | 0 | 520 celdas con salto de línea |
| `clasificacion` | 40 | `(gasera, variante)` | 0 | 0 | Solo `GasCaribe` |
| `gdo_gestion_diaria` | **0** | `id` | 0 | 0 | 🔴 Artefacto vacío (H-18) — eliminar |

**Total: 48.036 filas de datos en 16 tablas, 0 FKs, 0 índices de negocio.**

### 3.3 Problemas estructurales del modelo actual

| # | Problema | Consecuencia |
| ---: | :--- | :--- |
| 1 | **No existe tabla de hechos consolidada** | Cada reporte tiene que hacer `UNION ALL` de 8 tablas con columnas distintas |
| 2 | **Cero claves foráneas** | Nada garantiza que un `contrato` exista, ni que un resultado esté clasificado |
| 3 | **Cero índices de negocio** | No hay forma de filtrar por fecha o contrato sin seq scan |
| 4 | **Una tabla por (gasera × cabina)** | 16 tablas con 3 plantillas de columnas diferentes; cada consulta es un `UNION ALL` frágil |
| 5 | **El resultado no está separado del detalle** | `estado` convive con `subtipificacion`, `motivo` y `cod_estado` sin jerarquía definida |
| 6 | **El estado y su clasificación no están en la tabla** | La clasificación requiere un JOIN externo que hoy solo existe para Caribe |
| 7 | **No hay bitácora de carga** | No se sabe de qué archivo salió cada fila |
| 8 | **No hay cuarentena** | Los registros inválidos o desaparecen o contaminan el dato |
| 9 | **`anio` es año de venta** | Mezcla dos ejes temporales en toda agregación |
| 10 | **Abandono y PQRS fuera del modelo de gestión** | No se puede hacer un único reporte de "llamadas del día" |

---

## 4. Vista objetivo — cómo debe quedar

### 4.1 Modelo en estrella

```mermaid
erDiagram
    dim_gasera      { smallint gasera_id PK | text codigo UK | text nombre | text nombre_normalizado }
    dim_cabina      { smallint cabina_id PK | text codigo UK | text nombre | text descripcion }
    dim_resultado   { smallint resultado_id PK | text codigo UK | text nombre | text clasificacion | boolean es_apto }
    dim_motivo      { smallint motivo_id PK | text codigo UK | text nombre | text familia | smallint orden }
    dim_operador    { smallint operador_id PK | text codigo UK | text nombre | text tipo | text normalizado }
    dim_producto    { smallint producto_id PK | text codigo UK | text nombre | text normalizado }
    dim_aseguradora { smallint aseguradora_id PK | text codigo UK | text nombre | text normalizado }
    dim_medio       { smallint medio_id PK | text codigo UK | text nombre | smallint medio_padre_id FK }
    dim_tipo_contacto { smallint tipo_contacto_id PK | text codigo UK | text nombre }
    dim_origen      { int origen_id PK | text archivo | text hoja | text sha256 | timestamp fecha_carga }
    dim_carga       { int carga_id PK | int origen_id FK | timestamp fecha_carga | int filas_leidas | int filas_cargadas | int filas_rechazadas | text estado }

    fact_gestion    { bigint id_gestion PK | text clave_natural | smallint gasera_id FK | smallint cabina_id FK | text subtipo_gestion | smallint resultado_id FK | smallint motivo_id FK | smallint operador_id FK | smallint producto_id FK | smallint aseguradora_id FK | smallint medio_id FK | smallint tipo_contacto_id FK | text contrato | text resultado_original | date fecha_gestion | timestamptz fecha_gestion_ts | date fecha_venta | smallint anio_gestion | text mes_gestion | int carga_id FK | boolean es_duplicado }
    fact_pqrs       { bigint id_pqrs PK | text clave_natural | smallint gasera_id FK | smallint resultado_id FK | smallint motivo_id FK | smallint tipo_gestion_id FK | text contrato | text numero_radicado | date fecha_radicado | date fecha_respuesta | int ans_notificacion | int ans_respuesta | text estado | int carga_id FK }
    dim_tipo_gestion { smallint tipo_gestion_id PK | text codigo UK | text nombre }

    fact_gestion }o--|| dim_gasera
    fact_gestion }o--|| dim_cabina
    fact_gestion }o--o| dim_resultado
    fact_gestion }o--o| dim_motivo
    fact_gestion }o--o| dim_operador
    fact_gestion }o--o| dim_producto
    fact_gestion }o--o| dim_aseguradora
    fact_gestion }o--o| dim_medio
    fact_gestion }o--o| dim_tipo_contacto
    fact_gestion }o--|| dim_carga
    fact_gestion }o--|| dim_origen
    fact_pqrs }o--|| dim_gasera
    fact_pqrs }o--o| dim_resultado
    fact_pqrs }o--o| dim_motivo
    fact_pqrs }o--|| dim_carga
```

### 4.2 A-04: ¿Una tabla de hechos o varias?

**Recomendación: UNA tabla de hechos de gestión (`fact_gestion`) con `subtipo_gestion`
discriminado**, más una tabla separada para PQRS.

| Opción | A favor | En contra | Veredicto |
| :--- | :--- | :--- | :--- |
| (a) Una tabla con nulos por tipo | Simplista | Mezcla 3 granularidades; muchas columnas nulas siempre | ❌ |
| (b) Una tabla con `subtipo_gestion` | Un solo lugar para "llamadas del día"; los KPIs se cruzan sin `UNION`; filtros por tipo | Renglón de abandono no tiene asesor → esas columnas quedan nulas solo para un subtipo | ✅ **Recomendada** |
| (c) Tres tablas de hechos | Cada una con su forma | 3 `UNION ALL` para cualquier reporte transversal; el cruce OCM×gestión se duplica | ❌ |

**Por qué (b) y no (c):** el abandonment y la atención comparten `gasera`, `cabina`,
`contrato`, `fecha` y `resultado`. El reporte central de retención necesita ambos. Con
(b) un solo `WHERE subtipo_gestion IN ('ATENCION','ABANDONO')` los cubre; con (c) hay
que unir dos tablas en cada consulta.

**Por qué PQRS sí va aparte:** un PQRS no es una llamada. No tiene `fecha_gestion` de
llamada, ni `cabina`, ni asesor de retención. Su granularidad es el radicado, no la
gestión. Meterlo en `fact_gestion` obligaría a 3 columnas siempre nulas y a confundir
dos conceptos distintos.

**Restricción CHECK que materializa la decisión:**

```sql
CHECK (
  (subtipo_gestion = 'ATENCION' AND resultado_id IS NOT NULL AND fecha_gestion IS NOT NULL)
  OR (subtipo_gestion = 'ABANDONO' AND fecha_gestion IS NOT NULL)
  OR (subtipo_gestion = 'PQRS'      AND fecha_gestion IS NOT NULL)
)
```

### 4.3 Dimensiones

| Dimensión | Filas estimadas | Origen | Nota |
| :--- | ---: | :--- | :--- |
| `dim_gasera` | 5 | Constante | CEO, EFIGAS, CARIBE, GDO, SURTIGAS |
| `dim_cabina` | 3 | Constante | INBOUND, OUTBOUND, ABANDONO |
| `dim_resultado` | **4 APTA + catálogo NO APTA** | `clasificacion` | **A-09 resuelto**: los 4 APTA son iguales en las 5 gaseras |
| `dim_motivo` | 52 | `gdo_inbound.subtipificacion` | Único catálogo jerárquico. **Pendiente de limpiar duplicados** |
| `dim_operador` | ~35 | `operador` | **Es la empresa operadora, no una persona** (H-23). Solo GDO aporta el asesor individual |
| `dim_producto` | 16 | `normalizar_producto` | Ya existe la función |
| `dim_aseguradora` | 6 | `normalizar_aseguradora` | Ya existe la función |
| `dim_medio` | ~10 | `canal` + `medio_de_recepcion` | Jerarquía: medio → canal |
| `dim_tipo_contacto` | 6 | Homologación | TITULAR, ASEGURADO, TITULAR_ASEGURADO, TERCERO, NO_APLICA, REVISAR |
| `dim_tipo_gestion` | 3 | Constante | ATENCION, ABANDONO, PQRS |
| `dim_origen` | 1 por archivo | Bitácora | Ruta, hoja, sha256 |
| `dim_carga` | 1 por ingesta | Bitácora | filas_leidas / cargadas / rechazadas / estado |

> **`dim_operador` y la granularidad del asesor (H-23).** La dimensión tiene dos niveles:
> `tipo` = `EMPRESA` | `PERSONA`. Las 4 gaseras con BPO solo llegan a `EMPRESA`; GDO
> llega a `PERSONA`. El KPI de productividad individual **solo es calculable para GDO**,
> y eso debe quedar explícito en el modelo y en el dashboard, no ser un bug silencioso.

### 4.4 Tablas de soporte

| Tabla | Propósito |
| :--- | :--- |
| `dim_carga` | Bitácora de ingesta. Patrón copiado de `siniestros.cargas` (misma instancia, ya probado). |
| `dim_origen` | Línea al archivo Excel: ruta, hoja, `sha256`, fecha de lectura. Da trazabilidad a nivel de registro. |
| `quarantine` | Registros rechazados con la regla que los rechaza, el valor original (jsonb) y el motivo. |

### 4.5 Lo que NO cambia

| Elemento | Decisión |
| :--- | :--- |
| Las 16 tablas de `gestion_diaria` | **Se conservan como staging.** No se modifican ni se borran. Son el origen crudo auditable. |
| `gestion_diaria.clasificacion` | **Se conserva** y se extiende a las 5 gaseras. Pasa a ser el respaldo del `dim_resultado`. |
| Las 4 funciones de normalización | **Se conservan y se extienden** (P-11b). |
| La clave sintética `id` de las tablas staging | **Se conserva.** |

---

## 5. Reglas del modelo

| # | Regla | Motivo |
| ---: | :--- | :--- |
| M-01 | Toda tabla de hechos tiene `id` sintética + `clave_natural` | Trazabilidad y deduplicación sin perder multigestiones |
| M-02 | `clave_natural` es una columna `GENERATED ALWAYS AS ... STORED` | No se puede desincronizar del dato |
| M-03 | Índice **único parcial** sobre `clave_natural` `WHERE NOT es_duplicado` | Los duplicados quedan **visibles**, no se borran |
| M-04 | Ninguna dimensión se borra: se marca `activo = false` | Historia |
| M-05 | Toda columna temporal es `date` o `timestamptz`; el texto original va en `*_raw` | Trazabilidad |
| M-06 | `anio_gestion` y `mes_gestion` son columnas generadas desde `fecha_gestion` | Nunca más se confunde venta con gestión (H-07) |
| M-07 | `resultado_original` nunca se modifica | D-03 |
| M-08 | Toda tabla de hechos referencia `dim_carga` | Lineage a nivel de registro |
| M-09 | Ninguna columna de PII entra en las dimensiones | Minimización (Ley 1581) |
| M-10 | Los campos que hoy son `text` y representan un catálogo pasan a `varchar` + FK | Integridad |

---

## 6. Migraciones SQL

> Todas las migraciones son **aditivas**: no destruyen nada de `gestion_diaria`.
> La vista actual permanece como respaldo auditable mientras el modelo nuevo se llena.

### 6.1 M0 — Saneamiento de nombres (vista de consumo, no toca el origen)

```sql
-- Renombra las columnas con problemas SOLO en una vista de consumo.
-- El origen (gestion_diaria) queda intacto como respaldo.
CREATE OR REPLACE VIEW gestion_diaria.v_gdo_pqrs AS
SELECT
    id,
    contrato::text                                   AS contrato,
    producto::text                                  AS producto,
    tipo_producto,
    interaccion::text                               AS interaccion,
    numero_solicitud::text                          AS numero_solicitud,
    nombre_solicitud,
    causal_registro_solicitud,
    area_causante_solicitud,
    area_duena_solicitud,
    area_real_causante,
    pto_atencion_reg_solicitud,
    clasificacion_solicitud,
    estado_solicitud,
    medio_recepcion,
    semana_registro,
    funcionario_registra,
    observacion_solicitud,
    fecha_registro_solicitud,
    gestion_diaria.fn_parse_fecha(fecha_registro_solicitud) AS fecha_registro,
    gestion_diaria.fn_parse_fecha(fecha_atencion)          AS fecha_atencion,
    tipo_respuesta,
    respuesta,
    amplicacion_term            AS ampliacion_term,
    ans,
    dias_registro_solicitud,
    cumplimiento_ans,
    nombre_solicitante,
    identificacion_solicitante::text AS identificacion_solicitante,
    direccion,
    barrio_solicitud,
    departamento_solicitud,
    localidad_solicitud,
    ciclo_solicitud,
    numero_orden_trabajo,
    tipo_trabajo_orden_trabajo,
    unidad_trabajo_orden,
    area_causante_en_el_registro,
    tipo_unidad_de_trabajo,
    clasificacion_orden_trabajo,
    estado_orden_trabajo,
    direccion_orden_trabajo,
    barrio_orden_trabajo,
    agendamiento_visita,
    agendamiento_vta_cruzada,
    estado_vta,
    dias_agendamiento,
    "ORDEN LOCALIDAD"          AS orden_localidad,
    estado,
    "tipo poliza"               AS tipo_poliza,
    fecha_creacion_orden_trabajo,
    fecha_asignacion_orden_trab,
    fecha_finali_ejec_ord_trab,
    fecha_lega_orden_trabajo,
    dias_ejecucion_ordenes,
    comentario_orden_trabajo,
    causal_legal_ord_trab,
    func_legaliza_orden_trabajo
    -- Las columnas `♣`, `columna1`, `columna2`, `column62` se omiten a propósito.
FROM gestion_diaria.gdo_pqrs;
```

### 6.2 M1 — Tablas de soporte (bitácora, origen, cuarentena)

```sql
CREATE TABLE gestion_diaria.dim_origen (
    origen_id      serial PRIMARY KEY,
    gasera         text NOT NULL,
    ruta           text,
    nombre_archivo text NOT NULL,
    hoja           text,
    sha256         text,
    fecha_lectura  timestamptz NOT NULL DEFAULT now(),
    UNIQUE (gasera, nombre_archivo, hoja, sha256)
);

CREATE TABLE gestion_diaria.dim_carga (
    carga_id         serial PRIMARY KEY,
    origen_id        integer NOT NULL REFERENCES gestion_diaria.dim_origen(origen_id),
    fecha_carga      timestamptz NOT NULL DEFAULT now(),
    filas_leidas     integer,
    filas_cargadas   integer,
    filas_rechazadas integer,
    estado           text NOT NULL CHECK (estado IN ('OK','PARCIAL','ERROR')),
    notas            text,
    CONSTRAINT chk_carga_filas CHECK (
        filas_leidas IS NULL OR (filas_cargadas + filas_rechazadas) <= filas_leidas)
);

CREATE TABLE gestion_diaria.quarantine (
    id_quarantine  bigserial PRIMARY KEY,
    carga_id       integer REFERENCES gestion_diaria.dim_carga(carga_id),
    gasera         text,
    tabla_destino  text,
    regla          text NOT NULL,
    valor_original jsonb,
    motivo         text NOT NULL,
    detectado_en   timestamptz NOT NULL DEFAULT now(),
    resuelto       boolean NOT NULL DEFAULT false
);
```

### 6.3 M2 — Catálogos (dimensiones)

```sql
CREATE TABLE gestion_diaria.dim_gasera (
    gasera_id           smallserial PRIMARY KEY,
    codigo              text NOT NULL UNIQUE,
    nombre              text NOT NULL,
    nombre_normalizado  text NOT NULL,
    activo              boolean NOT NULL DEFAULT true
);

CREATE TABLE gestion_diaria.dim_cabina (
    cabina_id  smallserial PRIMARY KEY,
    codigo     text NOT NULL UNIQUE,
    nombre     text NOT NULL,
    descripcion text
);

CREATE TABLE gestion_diaria.dim_tipo_gestion (
    tipo_gestion_id smallserial PRIMARY KEY,
    codigo          text NOT NULL UNIQUE,   -- ATENCION | ABANDONO | PQRS
    nombre          text NOT NULL
);

-- A-09: la clasificación es la misma en las 5 gaseras (verificado).
-- Se modela por gasera igual, para no bloquear si en el futuro difiere.
CREATE TABLE gestion_diaria.dim_resultado (
    resultado_id   smallserial PRIMARY KEY,
    codigo         text NOT NULL UNIQUE,       -- cancelado | cancelado + venta | ...
    nombre         text NOT NULL,
    clasificacion  text NOT NULL CHECK (clasificacion IN ('APTA','NO_APTA','POR_REVISAR')),
    es_apto        boolean GENERATED ALWAYS AS (clasificacion = 'APTA') STORED,
    activo         boolean NOT NULL DEFAULT true
);

CREATE TABLE gestion_diaria.dim_motivo (
    motivo_id  smallserial PRIMARY KEY,
    codigo     text NOT NULL UNIQUE,           -- '1.11', '2.1', ...
    nombre     text NOT NULL,
    familia    text,                           -- '1', '2', '3', '4', '13'
    orden      smallint,
    activo     boolean NOT NULL DEFAULT true
);

CREATE TABLE gestion_diaria.dim_operador (
    operador_id smallserial PRIMARY KEY,
    codigo      text NOT NULL UNIQUE,
    nombre      text NOT NULL,
    tipo        text NOT NULL CHECK (tipo IN ('EMPRESA','PERSONA')),  -- H-23
    normalizado text,
    activo      boolean NOT NULL DEFAULT true
);

CREATE TABLE gestion_diaria.dim_producto (
    producto_id smallserial PRIMARY KEY,
    codigo      text NOT NULL UNIQUE,
    nombre      text NOT NULL,
    normalizado text,
    activo      boolean NOT NULL DEFAULT true
);

CREATE TABLE gestion_diaria.dim_aseguradora (
    aseguradora_id smallserial PRIMARY KEY,
    codigo         text NOT NULL UNIQUE,
    nombre         text NOT NULL,
    normalizado    text,
    activo         boolean NOT NULL DEFAULT true
);

CREATE TABLE gestion_diaria.dim_medio (
    medio_id       smallserial PRIMARY KEY,
    codigo         text NOT NULL UNIQUE,
    nombre         text NOT NULL,
    medio_padre_id smallint REFERENCES gestion_diaria.dim_medio(medio_id),
    activo         boolean NOT NULL DEFAULT true
);

CREATE TABLE gestion_diaria.dim_tipo_contacto (
    tipo_contacto_id smallserial PRIMARY KEY,
    codigo           text NOT NULL UNIQUE,
    nombre           text NOT NULL,
    activo           boolean NOT NULL DEFAULT true
);
```

### 6.4 M3 — Tabla de hechos de gestión

```sql
CREATE TABLE gestion_diaria.fact_gestion (
    id_gestion       bigserial PRIMARY KEY,
    clave_natural    text GENERATED ALWAYS AS (
                         md5(concat_ws('|',
                             coalesce(gasera_id::text,''),
                             coalesce(cabina_id::text,''),
                             coalesce(contrato,''),
                             coalesce(fecha_gestion::text,''),
                             coalesce(resultado_id::text,''),
                             coalesce(tipo_contacto_id::text,''),
                             coalesce(operador_id::text,''),
                             coalesce(carga_id::text,'')
                         ))
                     ) STORED,

    gasera_id        smallint NOT NULL REFERENCES gestion_diaria.dim_gasera(gasera_id),
    cabina_id        smallint NOT NULL REFERENCES gestion_diaria.dim_cabina(cabina_id),
    tipo_gestion_id  smallint NOT NULL REFERENCES gestion_diaria.dim_tipo_gestion(tipo_gestion_id),
    resultado_id     smallint REFERENCES gestion_diaria.dim_resultado(resultado_id),
    motivo_id        smallint REFERENCES gestion_diaria.dim_motivo(motivo_id),
    operador_id      smallint REFERENCES gestion_diaria.dim_operador(operador_id),
    producto_id      smallint REFERENCES gestion_diaria.dim_producto(producto_id),
    aseguradora_id   smallint REFERENCES gestion_diaria.dim_aseguradora(aseguradora_id),
    medio_id         smallint REFERENCES gestion_diaria.dim_medio(medio_id),
    tipo_contacto_id smallint REFERENCES gestion_diaria.dim_tipo_contacto(tipo_contacto_id),
    carga_id         integer NOT NULL REFERENCES gestion_diaria.dim_carga(carga_id),

    contrato            text,
    resultado_original  text,        -- nunca se modifica (D-03)
    metodo_normalizacion text CHECK (metodo_normalizacion IN
                            ('exacto','variante','fuzzy','manual','sin_match')),
    score_similitud     numeric(5,2),

    fecha_gestion    date NOT NULL,
    fecha_gestion_ts timestamptz,
    fecha_venta      date,
    anio_gestion     smallint GENERATED ALWAYS AS (EXTRACT(YEAR FROM fecha_gestion)::smallint) STORED,
    mes_gestion      text    GENERATED ALWAYS AS (upper(to_char(fecha_gestion,'TMMonth'))) STORED,

    es_duplicado     boolean NOT NULL DEFAULT false,
    creado_en        timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT chk_fact_gestion_sin_tipo CHECK (
        (tipo_gestion_id IN (SELECT tipo_gestion_id FROM gestion_diaria.dim_tipo_gestion WHERE codigo='ATENCION')
         AND resultado_id IS NOT NULL)
        OR tipo_gestion_id <> (SELECT tipo_gestion_id FROM gestion_diaria.dim_tipo_gestion WHERE codigo='ATENCION')
    )
);

CREATE UNIQUE INDEX uq_fact_gestion_clave
    ON gestion_diaria.fact_gestion (clave_natural) WHERE NOT es_duplicado;
CREATE INDEX ix_fact_gestion_fecha     ON gestion_diaria.fact_gestion (fecha_gestion);
CREATE INDEX ix_fact_gestion_gasera    ON gestion_diaria.fact_gestion (gasera_id, fecha_gestion);
CREATE INDEX ix_fact_gestion_cabina    ON gestion_diaria.fact_gestion (cabina_id, fecha_gestion);
CREATE INDEX ix_fact_gestion_resultado ON gestion_diaria.fact_gestion (resultado_id, fecha_gestion);
CREATE INDEX ix_fact_gestion_operador  ON gestion_diaria.fact_gestion (operador_id, fecha_gestion);
CREATE INDEX ix_fact_gestion_carga     ON gestion_diaria.fact_gestion (carga_id);
```

### 6.5 M4 — Tabla de hechos de PQRS

```sql
CREATE TABLE gestion_diaria.fact_pqrs (
    id_pqrs         bigserial PRIMARY KEY,
    clave_natural   text GENERATED ALWAYS AS (
                        md5(concat_ws('|', coalesce(gasera_id::text,''),
                                       coalesce(numero_radicado,''),
                                       coalesce(fecha_radicado::text,''),
                                       coalesce(carga_id::text,'')))
                    ) STORED,
    gasera_id       smallint NOT NULL REFERENCES gestion_diaria.dim_gasera(gasera_id),
    tipo_gestion_id smallint NOT NULL REFERENCES gestion_diaria.dim_tipo_gestion(tipo_gestion_id),
    resultado_id    smallint REFERENCES gestion_diaria.dim_resultado(resultado_id),
    motivo_id       smallint REFERENCES gestion_diaria.dim_motivo(motivo_id),
    carga_id        integer NOT NULL REFERENCES gestion_diaria.dim_carga(carga_id),

    contrato               text,
    numero_radicado        text,
    fecha_radicado         date,        -- radicado_usu_gdo
    fecha_notificacion_xuma date,       -- fecha_gdo_xuma
    fecha_xuma_aseguradora  date,       -- fecha_xuma_aseg
    fecha_respuesta        date,        -- fecha_respuesta_aseguradora
    ans_notificacion       integer,
    ans_respuesta          integer,
    estado                 text,
    respuesta              text,
    es_duplicado           boolean NOT NULL DEFAULT false,
    creado_en              timestamptz NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX uq_fact_pqrs_clave
    ON gestion_diaria.fact_pqrs (clave_natural) WHERE NOT es_duplicado;
CREATE INDEX ix_fact_pqrs_fecha  ON gestion_diaria.fact_pqrs (fecha_radicado);
CREATE INDEX ix_fact_pqrs_gasera ON gestion_diaria.fact_pqrs (gasera_id, fecha_radicado);
```

### 6.6 M5 — Extensión del catálogo `clasificacion` a las 5 gaseras

```sql
-- 1. Las variantes que hoy solo existen para GasCaribe se registran para las demás
--    gaseras: la clasificación del resultado canónico es la misma (A-09 resuelto).
INSERT INTO gestion_diaria.clasificacion (gasera, variante, resultado_normalizado, clasificacion)
SELECT g.codigo, c.variante, c.resultado_normalizado, c.clasificacion
FROM gestion_diaria.clasificacion c
CROSS JOIN (VALUES ('CEO'),('EFIGAS'),('SURTIGAS'),('GDO')) AS g(codigo)
WHERE c.gasera = 'GasCaribe'
ON CONFLICT (gasera, variante) DO NOTHING;

-- 2. Se corrige `normalizar_texto` para que también normalice la barra.
--    (P-11 / H-32: `cancelado/reintegro` debe coincidir con `cancelado /reintegro`)
CREATE OR REPLACE FUNCTION gestion_diaria.normalizar_texto(p text)
RETURNS text LANGUAGE plpgsql IMMUTABLE AS $$
DECLARE v TEXT;
BEGIN
  IF p IS NULL THEN RETURN NULL; END IF;
  v := lower(p);
  v := translate(v, 'áéíóúñü', 'aeiouunu');
  v := regexp_replace(v, '\s*/\s*', ' / ', 'g');   -- <-- nuevo
  v := regexp_replace(v, '\s*\+\s*', ' + ', 'g');
  v := regexp_replace(v, '\s+', ' ', 'g');
  RETURN btrim(v);
END $$;

-- 3. Se cargan las 43 variantes que hoy no resuelven, con su clasificación revisada.
INSERT INTO gestion_diaria.clasificacion (gasera, variante, resultado_normalizado, clasificacion)
VALUES
  ('CEO','cancelado/reintegro','cancelado + reintegro','APTA'),
  ('CEO','cancelada + reintegro','cancelado + reintegro','APTA'),
  ('CEO','cancelada previa','cancelado previa','NO APTA'),
  ('EFIGAS','retnida','retenido','APTA'),
  ('CARIBE','no es proteceso de retencion','no es proceso de retencion','NO APTA')
ON CONFLICT (gasera, variante) DO NOTHING;
-- Las restantes 38 variantes se cargan con `POR_REVISAR` tras la cola de revisión
-- (documento 09, §8).
```

### 6.7 M6 — Carga inicial desde el staging

```sql
-- Un solo INSERT para las 8 tablas de atención/outbound: la lógica de mapeo vive
-- en el script de ingesta, no en SQL. Este es el patrón de referencia.
INSERT INTO gestion_diaria.fact_gestion (
    gasera_id, cabina_id, tipo_gestion_id, resultado_id, motivo_id,
    operador_id, producto_id, aseguradora_id, medio_id, tipo_contacto_id,
    carga_id, contrato, resultado_original, metodo_normalizacion,
    fecha_gestion, fecha_venta, es_duplicado)
SELECT
    g.gasera_id,
    c.cabina_id,
    tg.tipo_gestion_id,
    r.resultado_id,
    NULL,
    o.operador_id,
    p.producto_id,
    a.aseguradora_id,
    m.medio_id,
    tc.tipo_contacto_id,
    :carga_id,
    x.contrato,
    x.estado,
    'exacto',
    x.fecha_de_ejecucion,
    x.fecha_de_venta,
    FALSE
FROM gestion_diaria.ceo_inbound x
JOIN gestion_diaria.dim_gasera g       ON g.codigo = x.distribuidora
JOIN gestion_diaria.dim_cabina c       ON c.codigo = x.cabina
JOIN gestion_diaria.dim_tipo_gestion tg ON tg.codigo = 'ATENCION'
LEFT JOIN gestion_diaria.dim_resultado r
       ON r.codigo = (SELECT resultado_normalizado FROM gestion_diaria.clasificacion
                      WHERE gasera = g.codigo
                        AND variante = gestion_diaria.normalizar_texto(x.estado))
LEFT JOIN gestion_diaria.dim_operador o
       ON o.normalizado = gestion_diaria.normalizar_texto(x.operador)
LEFT JOIN gestion_diaria.dim_producto p
       ON p.normalizado = gestion_diaria.normalizar_producto(x.producto)
LEFT JOIN gestion_diaria.dim_aseguradora a
       ON a.normalizado = gestion_diaria.normalizar_aseguradora(x.aseguradora)
LEFT JOIN gestion_diaria.dim_medio m
       ON m.codigo = upper(btrim(x.canal))
LEFT JOIN gestion_diaria.dim_tipo_contacto tc
       ON tc.codigo = upper(regexp_replace(btrim(x.tipo_de_contacto), '[^A-Za-z]', '', 'g'))
WHERE x.fecha_de_ejecucion BETWEEN '2025-01-01' AND CURRENT_DATE + 1
ON CONFLICT DO NOTHING;
```

### 6.8 M7 — Vistas de consumo

```sql
-- Vista de reporte diario: une atención y abandono en una sola vista.
CREATE OR REPLACE VIEW gestion_diaria.v_gestion_diaria AS
SELECT
    f.id_gestion,
    g.codigo                AS gasera,
    c.codigo                AS cabina,
    tg.codigo               AS subtipo_gestion,
    f.fecha_gestion,
    f.anio_gestion,
    f.mes_gestion,
    f.contrato,
    f.resultado_original,
    r.codigo                AS resultado,
    r.clasificacion,
    o.nombre                AS operador,
    o.tipo                  AS tipo_operador,
    p.nombre                AS producto,
    a.nombre                AS aseguradora,
    m.nombre                AS canal,
    tc.nombre               AS tipo_contacto,
    f.metodo_normalizacion,
    f.es_duplicado,
    f.carga_id
FROM gestion_diaria.fact_gestion f
JOIN gestion_diaria.dim_gasera g       ON g.gasera_id = f.gasera_id
JOIN gestion_diaria.dim_cabina c       ON c.cabina_id = f.cabina_id
JOIN gestion_diaria.dim_tipo_gestion tg ON tg.tipo_gestion_id = f.tipo_gestion_id
LEFT JOIN gestion_diaria.dim_resultado r   ON r.resultado_id = f.resultado_id
LEFT JOIN gestion_diaria.dim_operador o    ON o.operador_id = f.operador_id
LEFT JOIN gestion_diaria.dim_producto p    ON p.producto_id = f.producto_id
LEFT JOIN gestion_diaria.dim_aseguradora a ON a.aseguradora_id = f.aseguradora_id
LEFT JOIN gestion_diaria.dim_medio m       ON m.medio_id = f.medio_id
LEFT JOIN gestion_diaria.dim_tipo_contacto tc ON tc.tipo_contacto_id = f.tipo_contacto_id;
```

### 6.9 M8 — Limpieza

```sql
-- Eliminar el artefacto vacío (H-18). Es la única operación destructiva y
-- no afecta ningún dato: la tabla tiene 0 filas.
DROP TABLE IF EXISTS gestion_diaria.gdo_gestion_diaria;
```

---

## 7. Orden de ejecución y criterios de aceptación

| Migración | Qué hace | Criterio de aceptación | Bloquea |
| ---: | :--- | :--- | :--- |
| **M0** | Vista de saneamiento de nombres | La vista expone solo columnas con nombre válido | — |
| **M1** | `dim_origen`, `dim_carga`, `quarantine` | Existen y aceptan una carga de prueba | M3, M4 |
| **M2** | 11 catálogos | Poblados desde `clasificacion` y `normalizar_*` | M3, M4 |
| **M3** | `fact_gestion` | Carga las 29.046 filas de atención sin perder ninguna | Dashboard |
| **M4** | `fact_pqrs` | Carga las PQRS deduplicadas | Dashboard |
| **M5** | Extender `clasificacion` a 5 gaseras | 0 estados sin catalogar en las 5 | M6 |
| **M6** | Carga inicial | `COUNT(fact_gestion)` = 29.046 + 12.710 (abandono) | — |
| **M7** | Vistas de consumo | `v_gestion_diaria` responde y cuadra con el staging | Reportes |
| **M8** | Limpieza | `gdo_gestion_diaria` no existe | — |

**Regla de no retorno:** mientras `fact_gestion` no cuadre al 100% con
`gestion_diaria` (29.046 + 12.710 filas, más las de PQRS), **no se publica ningún
reporte**. El cuadre se verifica con:

```sql
-- Debe devolver 0 filas
SELECT 'ceo_inbound' AS origen, count(*) FROM gestion_diaria.ceo_inbound
EXCEPT
SELECT 'ceo_inbound', count(*) FROM gestion_diaria.fact_gestion f
JOIN gestion_diaria.dim_gasera g ON g.gasera_id = f.gasera_id
WHERE g.codigo = 'CEO' AND f.subtipo_gestion = 'ATENCION';
```

---

## 8. Lo que este documento pide aprobar

| # | Punto | Para quién | Fecha límite sugerida |
| ---: | :--- | :--- | :--- |
| 1 | **A-04**: una tabla de hechos con `subtipo_gestion` (no tres) | Equipo de datos + negocio | Antes de M3 |
| 2 | **A-03**: `id_gestion` + `clave_natural` md5, con `es_duplicado` | Equipo de datos | Antes de M3 |
| 3 | **A-09**: la clasificación NO varía por gasera | Equipo de datos | Antes de M5 |
| 4 | **`dim_operador.tipo`**: distinguir EMPRESA de PERSONA, y aceptar que la productividad individual solo aplica a GDO | Negocio | Antes de M2 |
| 5 | **`dim_motivo`**: adoptar el catálogo de 52 de GDO como maestro | Negocio | Antes de M2 |
| 6 | **Abandono de GDO**: declarar la fuente no confiable y no cargarla | Negocio + GDO | Antes de M6 |
| 7 | **`gdo_informativo`**: cargar como bitácora (no como PQRS) | Equipo de datos | Antes de M4 |
| 8 | **Entorno de pruebas** (A-01 del registro de riesgos): un esquema aparte para probar M0–M8 sin riesgo | DBA | Antes de M0 |
