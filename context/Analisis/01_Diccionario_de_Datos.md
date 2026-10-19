# 01. Diccionario de Datos

**Proyecto:** Gestión Diaria Promigas
**Esquema de base de datos:** `gestion_diaria`
**Alcance:** las 17 tablas del esquema `gestion_diaria` (16 con datos + 1 de catálogo)
**Fecha:** 19 de octubre de 2026
**Estado:** Borrador para revisión del equipo

---

## 1. Propósito

Este documento es la **fuente de verdad sobre qué contiene realmente cada archivo**. No
describe lo que *debería* contener el Excel, ni lo que dice la especificación oficial:
describe lo que hay en la base de datos después de la carga, columna por columna, con
nulos, valores de ejemplo y valores distintos.

Sirve para tres cosas concretas:

1. **Cuestionar el modelo con evidencia.** Cuando alguien diga "el estado es
   `RETENIDO`", aquí está el conteo real de cada grafía y en qué gasera aparece.
2. **Detectar diferencias entre gaseras.** El mismo concepto escrito de 5 formas
   distintas, con la volumetría de cada una.
3. **Detectar lo que falta.** Columnas al 100% nulas, columnas que no contienen lo que
   su nombre dice, y columnas que en realidad contienen el valor de otra.

### 1.1 Cómo se produjo

Todo lo que sigue se obtuvo por consulta directa a `DataCenter_Promigas`, no de la
documentación previa:

```sql
-- Nulos y cardinalidad por columna
SELECT count("columna"), count(DISTINCT "columna") FROM gestion_diaria."tabla";

-- Dominio de valores de una columna de tipificación
SELECT "columna", count(*) FROM gestion_diaria."tabla" GROUP BY 1 ORDER BY 2 DESC;
```

Las cifras son reproducibles con `python database/inspeccion_esquema.py --todo`.

### 1.2 Convenciones de lectura

| Convención | Significado |
| :--- | :--- |
| **Nulos** | Porcentaje de filas con `NULL` en esa columna |
| **Distintos** | Número de valores no nulos diferentes (`count(DISTINCT)`) |
| **Nombre original Excel** | Encabezado tal como venía en el Excel. En **negrita** cuando no se pudo confirmar y se infiere del patrón `snake_case` → `MAYÚSCULAS` |
| 🔴 | Problema crítico detectado en esa columna |
| 🟠 | Problema relevante |
| ⚠️ | Dato sensible (PII) — ver §4 |
| 📅 | Marca temporal |

---

## 2. Inventario de Orígenes (Excel → Base de datos)

| Gasera | Archivo en SharePoint | Hoja / pestaña | Tabla en BD | Filas |
| :--- | :--- | :--- | :--- | ---: |
| **CEO** | `CEO / Gestion diaria CEO.xlsx` | `Gestion Diaria Inbound Ceo` | `ceo_inbound` | 2,749 |
| **CEO** | `CEO / Gestion diaria CEO.xlsx` | `Abandono` | `ceo_abandono` | 4,020 |
| **Efigas** | `Efigas / Gestion Diaria Outbound - Efigas.xlsx` | `base efigas` | `efigas_outbound` | 999 |
| **Caribe** | `Gestion diaria Inbound -gases del caribe.xlsx` | `Enero 2026` … `Septiembre 2026` | `caribe_inbound` | 6,797 |
| **Caribe** | `Gestion diaria Inbound -gases del caribe.xlsx` | `abandono` | `caribe_abandono` | 5,064 |
| **Caribe** | `gestión diaria outbound-gases del caribe.xlsx` | `outbound` | `caribe_outbound` | 1,305 |
| **GDO** | `VALIDACION INFORMACION GDO- 24 de Junio 2026.xlsx` | `gestión inbound` | `gdo_inbound` | 4,190 |
| **GDO** | mismo archivo | `out` | `gdo_outbound` | 3,284 |
| **GDO** | mismo archivo | `prqs escritas` | `gdo_pqrs` | 747 |
| **GDO** | mismo archivo | `prqs escritas` (reestructurada) | `gdo_pqrs_escritas` | 86 |
| **GDO** | mismo archivo | `informativo` | `gdo_informativo` | 4,191 |
| **GDO** | mismo archivo | `abandono` | `gdo_abandono` | 831 |
| **Surtigas** | `SURTIGAS ARCHIVO RECUPERADO - Copia.xlsx` | `Enero a Marzo`, `abrl`, `mayo`, `junio` | `surti_inbound` | 9,423 |
| **Surtigas** | `Gestión diaria Inbound Surtigas.xlsx` | `ABANDONO` | `surti_abandono` | 2,795 |
| **Surtigas** | `gestión diaria outbound surtugas.xlsx` | `outbound` | `surti_outbound` | 299 |
| **Surtigas** | `Gestión diaria Inbound Surtigas.xlsx` | hoja de QR | `surti_qr` | 1,256 |
| — | *(catálogo interno, no viene de un Excel)* | — | `clasificacion` | 40 |

**Total: 48,036 filas de datos.**

### 2.1 Volumetría por familia

| Familia | Tablas | Filas |
| :--- | :---: | ---: |
| **Atención** (inbound + outbound) | 8 | 29,046 |
| **Abandono** | 4 | 12,710 |
| **PQRS** | 4 | 6,280 |
| **Catálogo de clasificación** | 1 | 40 |

---

## 3. Hallazgos transversales (afectan a varias tablas)

Estos 5 hallazgos se aplican a más de una tabla y no se repiten en cada inventario.

### 🔴 H-23 — `operador` NO es una persona: es la empresa operadora

**Evidencia** — el dominio completo de `operador`:

| Gasera | Valores más frecuentes |
| :--- | :--- |
| CEO | `SERVIPROTECCION BPO` (818), `SERVIPROTECCION` (514), `PUNTOS DE VENTAS SAC` (123), `GNP` (109), `PROEXEQUIAL` (43), `CREAMOS MARKETING` (13) |
| Caribe | `SERVIPROTECCION BPO` (2,176), `SERVIPROTECCION` (1,159), `MIGRACION` (289), `GNP` (194), `ACCION PLUS` (163), `CYS SERVICIOS INTEGRALES` (132) |
| Efigas | `SERVIPROTECCION BPO` (436), `ASESOR GENERAL MIGRACION` (58), `MIGRACION` (34), `ACCION PLUS` (33), `GNP` (19) |
| Surtigas Outbound | `SERVIPROTECCION BPO` (98), `LINK MARKETING` (63), `ACCION PLUS` (4) |

Son **empresas de tercerización de contact center**, no personas.

**Consecuencia:** el asesor individual de retención **solo existe en GDO**
(`gdo_inbound.nombre_asesor_retencion` — 25 personas: SHARITH GUEVARA, JESUS GUTIERREZ,
LUISA TORRES, KELLY MORON, YENNIFER MEJIA…; y `gdo_outbound.gestor` — 26 personas).
En CEO, Efigas, Caribe y Surtigas **no hay ninguna columna con el asesor de retención**;
la única persona disponible es `asesor_de_venta` (el asesor que vendió la póliza).

> **Impacto en el modelo:** la dimensión de "asesor" solo puede construirse para GDO.
> Para las otras 4 gaseras, la granularidad disponible es la **empresa operadora**.
> Cualquier KPI de productividad individual es **imposible** en 4 de 5 gaseras.

### 🔴 H-24 — Sangrado de columnas: hay filas donde el valor de una columna cae en otra

**Evidencia** — filas donde `operador` contiene un valor de `tipo_de_contacto`:

| Gasera | Filas afectadas | % |
| :--- | ---: | ---: |
| **Surtigas Inbound** | **1,099** | **11.7%** |
| CEO | 182 | 6.6% |
| Caribe Outbound | 52 | 4.0% |
| Caribe Inbound | 237 | 3.5% |
| Efigas | 19 | 1.9% |
| Surtigas Outbound | 0 | 0.0% |

En Surtigas Inbound el `operador` está poblado en solo 1,165 de 9,423 filas (12.4%), y
**1,099 de esas contienen un tipo de contacto** (`titular/asegurado`, `asegurado`,
`titular`, `tercero`…). Es decir: **en Surtigas Inbound la columna `operador` no existe**
y se está llenando con el valor de la columna vecina.

Otros indicadores de sangrado:

| Gasera | `canal` con valor de otra columna | `aseguradora` = `operador` | `tipo_de_contacto` con valor de estado |
| :--- | ---: | ---: | ---: |
| CEO | 63 (2.3%) | 142 (5.2%) | 83 (3.0%) |
| Caribe Inbound | 78 (1.1%) | 16 (0.2%) | — |
| Caribe Outbound | 2 (0.2%) | 0 | — |
| Surtigas Inbound | 43 (0.5%) | 0 | — |

### 🔴 H-25 — Causa raíz: celdas del Excel con varias columnas pegadas

**Evidencia** — celdas que contienen un tabulador (dos o más columnas en una sola celda):

| Tabla | Columna | Filas | Valor real |
| :--- | :--- | ---: | :--- |
| `ceo_inbound` | `operador` | 5 | `SERVIPROTECCION BPO⇥TELEVENTA` |
| `caribe_inbound` | `aseguradora` | 7 | `SEGUROS DE VIDA ALFA S.AC⇥PRACTISEGURO` |
| `caribe_inbound` | `tipo_de_contacto` | 1 | `titular/asegurado⇥Lisbeth Angel⇥SERVIPROTECCION BP` (3 columnas) |
| `caribe_inbound` | `motivo` | 4 | `NO DESEA CONTINUAR POR MOTIVOS ECONOMICOS ⇥CANCELA…` |
| `surti_inbound` | `tipo_de_contacto` | 1 | `TIULAR/ASEGURADO⇥TELEVENTA` |
| `gdo_outbound` | `plan` | 1 | `SALVA FACTURA⇥PLAN 2 ⇥Seguros Alfa S.A.` |
| `surti_qr` | `observacion_solicitud` | 25 | `CRSF0735832026 Meyling Castro Argumedo⇥CC 45563583` |
| `surti_qr` | `nombre_solicitante` | 1 | `ISABEL ⇥ BERNAL PATERNINA` |

> **La carga se hizo literal, sin validar que cada valor pertenezca a su columna.**
> Por eso un valor de `canal` terminó en `operador`. Es el mismo síntoma que H-24, y
> la detección por tabulador es la forma barata y determinista de cazarlo.

### 🟠 H-26 — Escape `_x000D_` de Excel dentro del texto

Celdas con saltos de línea codificados como texto por Excel:

| Tabla | Columna | Filas con salto de línea |
| :--- | :--- | ---: |
| `surti_qr` | `comentario_orden_trabajo` | 520 |
| `surti_qr` | `observacion_solicitud` | 182 |
| `caribe_inbound` / `caribe_outbound` | `motivo` | 13 / 13 |
| `ceo_inbound` / `surti_inbound` / `efigas_outbound` | `motivo` | 3 / 3 / 2 |
| `caribe_outbound` | `observacion_retencion` | 2 |
| `gdo_inbound` | `observaciones` | 3 |

Ejemplo literal: `'CONTRATO 339303⇥_x000D_\nEMILSE ISABEL ESCOBAR GARC'`.
El texto `_x000D_` es el escape de Excel para un retorno de carro y debe limpiarse
en la ingesta.

### 🟠 H-27 — `base` (FECHA BASE) es la fecha de carga del lote, nunca la de gestión

Regla confirmada con datos de Efigas:

| Lote `base` | Filas | Rango real de `fecha_de_ejecucion` | Ejecuciones fuera del mes del lote |
| :--- | ---: | :--- | ---: |
| `2026-03-02` | 64 | **2026-09-03 → 2026-11-02** | **64 (100%)** |
| `26/01/2026` (texto) | 48 | **2026-03-02 → 2026-05-02** | **48 (100%)** |
| `2026-11-02` | 64 | 2026-11-02 → 2026-12-02 | 34 (53%) |
| `2026-04-20` | 160 | 2026-04-05 → 2026-05-05 | 22 (14%) |
| `2026-05-19` | 105 | 2026-05-05 → 2026-06-05 | 20 (19%) |
| `2026-06-09` | 99 | 2026-03-01 → 2026-07-03 | 4 (4%) |
| `2026-07-21` | 130 | 2026-07-14 → 2026-07-29 | 0 |
| `2026-08-13` | 99 | 2026-08-06 → 2026-08-28 | 0 |
| `2026-01-13` | 85 | 2026-01-03 → 2026-01-29 | 0 |
| `17/02/2026` (texto) | 34 | *(sin fecha de ejecución)* | — |

Además `base` es `varchar` con **formatos mezclados**: `2026-11-02 00:00:00` (timestamp
como texto) y `26/01/2026` / `17/02/2026` (texto puro).

---

## 4. Datos personales (PII) presentes en el esquema

Ley 1581 de 2012 (Colombia). Minimización y control de acceso son obligatorios.

| Dato | Tablas y columnas | Nivel |
| :--- | :--- | :---: |
| Nombre del cliente | `ceo_abandono.nombre_cliente`, `caribe_abandono.nombre_cliente`, `gdo_abandono.nombre_cliente`, `gdo_inbound.nombre_cliente`, `gdo_outbound.nombre_solicitante`, `surti_qr.nombre_solicitante` | 🔴 Alto |
| Documento de identidad | `*.identificacion_usuario`, `*.identificacion_solicitante`, `gdo_inbound.cedula`, `surti_qr.ident_solicitante` | 🔴 Alto |
| Teléfono | `*.telefono`, `*.numbercall`, `*.cel`, `surti_qr.telefono_solicitante/suscriptor` | 🔴 Alto |
| Dirección | `gdo_outbound.direccion`, `*.direccion_orden_trabajo`, `surti_qr.direccion_solicitud` | 🔴 Alto |
| Correo | `gdo_outbound.correo`, `caribe_inbound.correo_reintegro` | 🔴 Alto |
| Datos del funcionario | `gdo_informativo.funcionario`, `.terminal`, `.tabulacion`, `.cel` | 🟠 Medio |
| Contexto laboral | `gdo_informativo.departamento`, `.localidad` | 🟠 Medio |

> **Regla operativa:** ningún reporte publicado debe incluir columnas de este bloque.
> Los reportes usan `contrato` como identificador, nunca el nombre ni el documento.

---

## 5. Inventario por tabla

#### `ceo_inbound` — 2,749 filas

| # | Columna | Nombre original Excel | Tipo | Nulos | Distintos | Significado | Ejemplos |
| ---: | :--- | :--- | :--- | ---: | ---: | :--- | :--- |
| 1 | `id` | **ID** | integer | 0.0% | 2,749 | PK sintética. La carga no conserva un identificador del Excel. | `1` · `2` · `3` |
| 2 | `distribuidora` | DISTRIBUIDORA | character varying(100) | 0.0% | 1 | Gasera a la que pertenece la fila. Constante por tabla. | `CEO` |
| 3 | `aseguradora` | ASEGURADORA | character varying(200) | 3.3% | 22 | Aseguradora que emite la póliza del cliente. | `NO TIENE SEGUROS ACT` · `PROEXEQUIAL SAS` · `PROEXEQUIAL SA` |
| 4 | `medio_de_recepcion` | MEDIO DE RECEPCION | character varying(200) | 100.0% | 0 | Canal físico por donde llegó la solicitud (punto de venta, call center, WhatsApp). | — |
| 5 | `contrato` | CONTRATO | character varying(200) | 1.6% | 1,855 | Número de contrato del cliente. Llave de negocio principal. | `1585983` · `1255658` · `253945` |
| 6 | `localidad` | LOCALIDAD | character varying(200) | 97.3% | 9 | Municipio/ciudad del cliente. | `CARMEN DE BOLIVAR` · `CARTAGENA DE INDIAS` · `COVENAS` |
| 7 | `operador` | OPERADOR | character varying(200) | 38.4% | 23 | **Empresa operadora del contact center** (SERVIPROTECCION, ACCION PLUS, MIGRACION, GNP...). NO es una persona. Ver H-23. | `NO APTO` · `PROEXEQUIAL` · `NO APLICA` |
| 8 | `canal` | CANAL | character varying(200) | 15.1% | 23 | Canal de la llamada: TELEVENTA, SAC, PAP, DOBLE CUPON, PUNTO FIJO. | `NO APTO` · `PROEXEQUIAL` · `NO APLICA` |
| 9 | `producto` | PRODUCTO | character varying(200) | 2.7% | 45 | Producto de seguros del cliente. | `SEGURO FUNERARIO` · `NO APTO` · `PROEXEQUIAL` |
| 10 | `tipo_de_contacto` | TIPO DE CONTACTO | character varying(300) | 3.8% | 41 | Con quién se spoke el asesor. | `NO APTO` · `CONTACTO A TERCERO` · `Madiley Vasquez` |
| 11 | `estado` | ESTADO | character varying(200) | 2.3% | 40 | **Resultado de la gestión** (lo escribe el asesor). Columna crítica → ver cap. de clasificación. | `NO APTO` · `CREDITO BRILLA` · `CANCELADA` |
| 12 | `subtipificacion` | SUBTIPIFICACION | character varying(300) | 100.0% | 0 | Motivo o detalle de la gestión. Vacía en CEO al 100%. | — |
| 13 | `motivo` | MOTIVO | text | 4.6% | 471 | Texto libre con la razón de la gestión. | `porque no tomo la pr` · `MANTINE LA COBERTURA` · `FINALIZO EL CREDITO ` |
| 14 | `fecha_de_ejecucion` | **FECHA_DE_EJECUCION** | date | 5.6% | 164 | **Fecha en que ocurrió la gestión.** Columna temporal canónica. | `2026-08-14` · `2026-05-02` · `2025-11-04` |
| 15 | `base` | FECHA BASE | character varying(200) | 0.1% | 175 | **Fecha de carga del lote en el Excel, NO la de la gestión.** No usar para análisis. (Regla Efigas.) | `2026-07-10 00:00:00` · `2026-06-22 00:00:00` · `2026-05-07 00:00:00` |
| 16 | `fecha_de_venta` | FECHA DE VENTA | date | 39.6% | 574 | Fecha en que se vendió la póliza. Eje temporal distinto al de gestión. | `2025-11-24` · `2025-03-31` · `2023-06-10` |
| 17 | `asesor_de_venta` | ASESOR DE VENTA | character varying(300) | 16.5% | 172 | Asesor que vendió la póliza originalmente. No es el de retención. | `YEXENIA MARIA MONTAL` · `LEIDY YURANI ARANGO ` · `Keinis Lisbeth Herná` |
| 18 | `mes` | MES | character varying(50) | 0.0% | 8 | Mes de la gestión. Formato variable por gasera (ver H-08). | `AGOSTO` · `MARZO` · `FEBRERO` |
| 19 | `cabina` | CABINA | character varying(20) | 0.0% | 1 | INBOUND / OUTBOUND. Constante por tabla. | `INBOUND` |
| 20 | `anio` | ANIO | integer | 61.6% | 6 | **Año de VENTA, no de gestión.** No usar para agregar por periodo. | `2024` · `2025` · `1900` |
| 21 | `fecha_carga` | (agregada por la carga) | timestamp without time zone | 0.0% | 1 | Momento en que la fila se insertó en la BD. No viene del Excel. | `2026-09-15 17:22:38.` |

#### `ceo_abandono` — 4,020 filas

| # | Columna | Nombre original Excel | Tipo | Nulos | Distintos | Significado | Ejemplos |
| ---: | :--- | :--- | :--- | ---: | ---: | :--- | :--- |
| 1 | `id` | **ID** | integer | 0.0% | 4,020 | PK sintética. La carga no conserva un identificador del Excel. | `1` · `2` · `3` |
| 2 | `aseguradora` | ASEGURADORA | character varying(200) | 73.8% | 5 | Aseguradora que emite la póliza del cliente. | `IKE ASISTENCIA COLOM` · `PROXEQUIAL SAS` · `GNP GRUPO NACIONAL` |
| 3 | `nombre_cliente` | NOMBRE CLIENTE | character varying(300) | 69.5% | 1,137 | Nombre del cliente. **Dato sensible.** | `ALCIRA FERNANDEZ AST` · `MARTHA` · `EVELIO   YUDI` |
| 4 | `identificacion_usuario` | IDENTIFICACION USUARIO | bigint | 76.4% | 854 | Documento de identidad. **Dato sensible.** | `36292681` · `25295649` · `25284441` |
| 5 | `contrato` | CONTRATO | bigint | 70.2% | 956 | Número de contrato del cliente. Llave de negocio principal. | `967396` · `300380` · `300833` |
| 6 | `localidad` | LOCALIDAD | character varying(200) | 86.9% | 53 | Municipio/ciudad del cliente. | `TOTORÓ` · `25635080` · `1197735` |
| 7 | `telefono` | TELEFONO | bigint | 0.5% | 1,754 | Teléfono del cliente. | `3206830879` · `3126820912` · `3148064629` |
| 8 | `resultado_llamada` | RESULTADO LLAMADA | character varying(300) | 0.1% | 18 | Resultado del corte de la llamada abandonada. | `CAÍDA EN LA LLAMADA` · `NO APTO` · `SEGURO NO PERTENECE` |
| 9 | `fecha_llamada` | FECHA LLAMADA | date | 62.4% | 51 | **Fecha de la llamada abandonada.** | `2026-04-02` · `2026-06-07` · `2026-01-06` |
| 10 | `hora` | HORA | character varying(30) | 99.2% | 32 | Hora de la llamada, como texto libre (formato `10:01:10 a. m.`). | `10:01:10 a. m.` · `10:14:37 a. m.` · `10:20:24 a. m.` |
| 11 | `fecha_carga` | (agregada por la carga) | timestamp without time zone | 0.0% | 1 | Momento en que la fila se insertó en la BD. No viene del Excel. | `2026-09-15 17:22:39.` |

#### `efigas_outbound` — 999 filas

| # | Columna | Nombre original Excel | Tipo | Nulos | Distintos | Significado | Ejemplos |
| ---: | :--- | :--- | :--- | ---: | ---: | :--- | :--- |
| 1 | `id` | **ID** | integer | 0.0% | 999 | PK sintética. La carga no conserva un identificador del Excel. | `1` · `2` · `3` |
| 2 | `distribuidora` | DISTRIBUIDORA | character varying(100) | 0.0% | 1 | Gasera a la que pertenece la fila. Constante por tabla. | `EFIGAS` |
| 3 | `aseguradora` | ASEGURADORA | character varying(200) | 0.0% | 6 | Aseguradora que emite la póliza del cliente. | `HDI` · `SEGUROS DE VIDA SURA` · `HDI SEGUROS COLOMBIA` |
| 4 | `medio_de_recepcion` | MEDIO DE RECEPCION | character varying(200) | 100.0% | 0 | Canal físico por donde llegó la solicitud (punto de venta, call center, WhatsApp). | — |
| 5 | `contrato` | CONTRATO | character varying(200) | 0.0% | 781 | Número de contrato del cliente. Llave de negocio principal. | `61368` · `358677` · `253168` |
| 6 | `localidad` | LOCALIDAD | character varying(200) | 98.8% | 3 | Municipio/ciudad del cliente. | `CARTAGENA DE INDIAS` · `SINCELEJO` · `TURBACO` |
| 7 | `operador` | OPERADOR | character varying(200) | 37.3% | 14 | **Empresa operadora del contact center** (SERVIPROTECCION, ACCION PLUS, MIGRACION, GNP...). NO es una persona. Ver H-23. | `ASESOR  GENERAL MIGR` · `ACCION PLUS` · `EMERGIA` |
| 8 | `canal` | CANAL | character varying(200) | 0.0% | 8 | Canal de la llamada: TELEVENTA, SAC, PAP, DOBLE CUPON, PUNTO FIJO. | `MASCOTAS` · `DOBLE CUPON` · `SEGURO FUNERARIO` |
| 9 | `producto` | PRODUCTO | character varying(200) | 0.4% | 18 | Producto de seguros del cliente. | `SEGUROFUNERARIO` · `Practiseguro plus` · `PRACTISEGURO` |
| 10 | `tipo_de_contacto` | TIPO DE CONTACTO | character varying(300) | 0.1% | 16 | Con quién se spoke el asesor. | `NO APTO` · `TITULAR` · `TERCERO` |
| 11 | `estado` | ESTADO | character varying(200) | 0.6% | 13 | **Resultado de la gestión** (lo escribe el asesor). Columna crítica → ver cap. de clasificación. | `CANCELADO+REINTEGRO` · `RETENIDA` · `CANCELADO + REINTEGR` |
| 12 | `subtipificacion` | SUBTIPIFICACION | character varying(300) | 51.5% | 8 | Motivo o detalle de la gestión. Vacía en CEO al 100%. | `Cancelación de segur` · `CANCELACIÓN DE SEGUR` · `Cancelacion de segur` |
| 13 | `motivo` | MOTIVO | text | 0.3% | 164 | Texto libre con la razón de la gestión. | `PORQUE YA TIENE UN S` · `USUARIO CUELGA LA LL` · `USUARIO YA CUENTA CO` |
| 14 | `fecha_de_ejecucion` | **FECHA_DE_EJECUCION** | date | 17.2% | 68 | **Fecha en que ocurrió la gestión.** Columna temporal canónica. | `2026-12-02` · `2026-04-08` · `2026-01-03` |
| 15 | `base` | FECHA BASE | character varying(200) | 0.0% | 34 | **Fecha de carga del lote en el Excel, NO la de la gestión.** No usar para análisis. (Regla Efigas.) | `24/02/2026` · `2026-08-21 00:00:00` · `2026-08-27 00:00:00` |
| 16 | `fecha_de_venta` | FECHA DE VENTA | date | 38.3% | 358 | Fecha en que se vendió la póliza. Eje temporal distinto al de gestión. | `2024-05-17` · `2022-10-31` · `2025-05-22` |
| 17 | `asesor_de_venta` | ASESOR DE VENTA | character varying(300) | 0.9% | 144 | Asesor que vendió la póliza originalmente. No es el de retención. | `MARCELA BEATRIZ MONT` · `MATEO ANDRES NAVARRO` · `OMARIS TATIANA FLORE` |
| 18 | `mes` | MES | character varying(50) | 0.0% | 8 | Mes de la gestión. Formato variable por gasera (ver H-08). | `AGOSTO` · `MARZO` · `FEBRERO` |
| 19 | `cabina` | CABINA | character varying(20) | 0.0% | 1 | INBOUND / OUTBOUND. Constante por tabla. | `OUTBOUND` |
| 20 | `anio` | ANIO | integer | 64.2% | 11 | **Año de VENTA, no de gestión.** No usar para agregar por periodo. | `2021` · `2020` · `2023` |
| 21 | `fecha_carga` | (agregada por la carga) | timestamp without time zone | 0.0% | 1 | Momento en que la fila se insertó en la BD. No viene del Excel. | `2026-09-15 17:22:40.` |

#### `caribe_inbound` — 6,797 filas

| # | Columna | Nombre original Excel | Tipo | Nulos | Distintos | Significado | Ejemplos |
| ---: | :--- | :--- | :--- | ---: | ---: | :--- | :--- |
| 1 | `id` | **ID** | integer | 0.0% | 6,797 | PK sintética. La carga no conserva un identificador del Excel. | `4374` · `4375` · `4376` |
| 2 | `distribuidora` | DISTRIBUIDORA | character varying(100) | 100.0% | 0 | Gasera a la que pertenece la fila. Constante por tabla. | — |
| 3 | `aseguradora` | ASEGURADORA | character varying(200) | 29.0% | 22 | Aseguradora que emite la póliza del cliente. | `SEGUROS DE VIDA ALFA` · `HDI SEGUROS COLOMBIA` · `CSEGUROS DE VIDA ALF` |
| 4 | `medio_de_recepcion` | MEDIO DE RECEPCION | character varying(200) | 100.0% | 0 | Canal físico por donde llegó la solicitud (punto de venta, call center, WhatsApp). | — |
| 5 | `contrato` | CONTRATO | character varying(200) | 26.9% | 4,067 | Número de contrato del cliente. Llave de negocio principal. | `1002541.0` · `1035205` · `67710163.0` |
| 6 | `localidad` | LOCALIDAD | character varying(200) | 79.1% | 135 | Municipio/ciudad del cliente. | `PONEDERA` · `CAMPECHE` · `ZONA BANANERA` |
| 7 | `operador` | OPERADOR | character varying(200) | 28.8% | 50 | **Empresa operadora del contact center** (SERVIPROTECCION, ACCION PLUS, MIGRACION, GNP...). NO es una persona. Ver H-23. | `GNP` · `MIGRACION` · `servirpoteccion` |
| 8 | `canal` | CANAL | character varying(200) | 28.7% | 25 | Canal de la llamada: TELEVENTA, SAC, PAP, DOBLE CUPON, PUNTO FIJO. | `TELEENTA` · `NO APTO` · `PROEXEQUIAL` |
| 9 | `producto` | PRODUCTO | character varying(200) | 27.3% | 53 | Producto de seguros del cliente. | `AMPARO DE VIDA + ITP` · `PAZ Y SALVO` · `Futuro protegido` |
| 10 | `tipo_de_contacto` | TIPO DE CONTACTO | character varying(300) | 28.0% | 50 | Con quién se spoke el asesor. | `Titular` · `CANCELADO` · `contacto tercero` |
| 11 | `estado` | ESTADO | character varying(200) | 0.0% | 20 | **Resultado de la gestión** (lo escribe el asesor). Columna crítica → ver cap. de clasificación. | `NO APTO` · `NO APLICA` · `TERCERO` |
| 12 | `subtipificacion` | SUBTIPIFICACION | character varying(300) | 28.5% | 355 | Motivo o detalle de la gestión. Vacía en CEO al 100%. | `NO ESTA INTERESADA` · `MODIFICACION DE COBE` · `NO QUIERE LA PROTECI` |
| 13 | `motivo` | MOTIVO | text | 28.3% | 1,050 | Texto libre con la razón de la gestión. | `NO QUIERE LA PROTECI` · `NO QUIERE EL SERVICI` · `SR LIGIA MANTIENE LA` |
| 14 | `fecha_de_ejecucion` | **FECHA_DE_EJECUCION** | date | 26.1% | 199 | **Fecha en que ocurrió la gestión.** Columna temporal canónica. | `2026-01-13` · `2026-04-08` · `2026-06-10` |
| 15 | `base` | FECHA BASE | character varying(200) | 100.0% | 0 | **Fecha de carga del lote en el Excel, NO la de la gestión.** No usar para análisis. (Regla Efigas.) | — |
| 16 | `fecha_de_venta` | FECHA DE VENTA | date | 40.2% | 1,543 | Fecha en que se vendió la póliza. Eje temporal distinto al de gestión. | `2024-11-28` · `2020-12-15` · `2021-11-13` |
| 17 | `asesor_de_venta` | ASESOR DE VENTA | character varying(300) | 29.2% | 479 | Asesor que vendió la póliza originalmente. No es el de retención. | `MATEO ANDRES NAVARRO` · `SUSAN  SARMIENTO` · `VALENTINA ALEXANDRA ` |
| 18 | `mes` | MES | character varying(50) | 0.0% | 9 | Mes de la gestión. Formato variable por gasera (ver H-08). | `MAYO 2026` · `JULIO 2026` · `SEPTIEMBRE 2026` |
| 19 | `cabina` | CABINA | character varying(20) | 100.0% | 0 | INBOUND / OUTBOUND. Constante por tabla. | — |
| 20 | `anio` | ANIO | integer | 0.0% | 1 | **Año de VENTA, no de gestión.** No usar para agregar por periodo. | `2026` |
| 21 | `fecha_carga` | (agregada por la carga) | timestamp without time zone | 0.0% | 1 | Momento en que la fila se insertó en la BD. No viene del Excel. | `2026-10-01 17:19:22.` |
| 23 | `telefono` | TELEFONO | text | 26.9% | 3,912 | Teléfono del cliente. | `3206862440` · `3012385050` · `3126767149` |
| 24 | `documento` | DOCUMENTO | text | 28.2% | 3,935 | Documento de identidad del cliente. **Dato sensible (Ley 1581).** | `32894411` · `1083454325` · `64695046` |
| 25 | `usuario` | USUARIO | text | 26.6% | 4,161 | Nombre del usuario/cliente. **Dato sensible.** | `DOMINGO PELAYO ROBLE` · `YULEIDIS POLO RUIZ` · `NINFA PANTOJA` |
| 26 | `gestor` | GESTOR | text | 27.3% | 55 | Asesor que gestionó la llamada (GDO y Caribe). | `SERVIPROTECCION BPO` · `Yenifer Mejia` · `kelly` |
| 27 | `correo_reintegro` | CORREO REINTEGRO | text | 98.4% | 100 | Correo para el reintegro. **Dato sensible.** | `????'` · `19390` · `33000108` |
| 28 | `gestion_sac` | GESTION SAC | text | 27.9% | 8 | Resultado registrado en el sistema SAC de la aseguradora. | `NO APTO` · `RETENIDO` · `NO APLICA` |
| 29 | `numero_solicitud` | NUMERO SOLICITUD | text | 27.9% | 3,602 | Radicado de la solicitud. | `246883443` · `242394402` · `240512165` |
| 30 | `observacion_sac` | OBSERVACION SAC | text | 98.8% | 21 | Observación registrada en el SAC. | `245811873` · `CANCELACION DE SEGUR` · `CANCELADO POR JOB` |
| 31 | `fecha_legalizacion` | FECHA LEGALIZACION | date | 68.4% | 82 | Fecha en que se formalizó la póliza. | `2026-06-10` · `2026-09-14` · `2026-08-18` |
| 32 | `resultado_normalizado` | RESULTADO NORMALIZADO | text | 0.0% | 12 | Resultado canónico tras pasar por el catálogo `clasificacion`. | `informativo` · `cancelado previa` · `no aplica` |
| 33 | `clasificacion` | CLASIFICACION | text | 0.0% | 2 | Clasificación de la solicitud. | `NO APTA` · `APTA` |
| 34 | `producto_norm` | PRODUCTO NORM | text | 0.0% | 16 | Producto normalizado (función `normalizar_producto`). | `SEGURO FUNERARIO` · `DEUDOR` · `PROEXEQUIAL` |
| 35 | `aseguradora_norm` | ASEGURADORA NORM | text | 0.0% | 7 | Aseguradora normalizada (función `normalizar_aseguradora`). | `PROEXEQUIAL` · `NO APLICA` · `SIN REGISTRO` |

#### `caribe_outbound` — 1,305 filas

| # | Columna | Nombre original Excel | Tipo | Nulos | Distintos | Significado | Ejemplos |
| ---: | :--- | :--- | :--- | ---: | ---: | :--- | :--- |
| 1 | `id` | **ID** | integer | 0.0% | 1,305 | PK sintética. La carga no conserva un identificador del Excel. | `1277` · `1278` · `1279` |
| 2 | `distribuidora` | DISTRIBUIDORA | character varying(100) | 100.0% | 0 | Gasera a la que pertenece la fila. Constante por tabla. | — |
| 3 | `aseguradora` | ASEGURADORA | character varying(200) | 0.2% | 14 | Aseguradora que emite la póliza del cliente. | `Seguros Alfa S.A.` · `6331-GDGU SEGUROS DE` · `152-HDI SEGUROS COLO` |
| 4 | `medio_de_recepcion` | MEDIO DE RECEPCION | character varying(200) | 100.0% | 0 | Canal físico por donde llegó la solicitud (punto de venta, call center, WhatsApp). | — |
| 5 | `contrato` | CONTRATO | character varying(200) | 0.0% | 1,107 | Número de contrato del cliente. Llave de negocio principal. | `66917945` · `67192182` · `66434952` |
| 6 | `localidad` | LOCALIDAD | character varying(200) | 100.0% | 0 | Municipio/ciudad del cliente. | — |
| 7 | `operador` | OPERADOR | character varying(200) | 3.5% | 28 | **Empresa operadora del contact center** (SERVIPROTECCION, ACCION PLUS, MIGRACION, GNP...). NO es una persona. Ver H-23. | `SERDAN VANTI` · `PUNTOS DE VENTAS SAC` · `COSTELEVENTA` |
| 8 | `canal` | CANAL | character varying(200) | 5.9% | 16 | Canal de la llamada: TELEVENTA, SAC, PAP, DOBLE CUPON, PUNTO FIJO. | `DOBLE CUPÓN` · `CANCELADO POR JOB` · `AC ASOCIADOS` |
| 9 | `producto` | PRODUCTO | character varying(200) | 4.2% | 27 | Producto de seguros del cliente. | `FUTURO PROTEGIDO PLU` · `SEGURO FUERARIO` · `CANCELADO POR JOB` |
| 10 | `tipo_de_contacto` | TIPO DE CONTACTO | character varying(300) | 6.0% | 32 | Con quién se spoke el asesor. | `NO APTO` · `CONTACTO A TERCERO` · `TERCERO` |
| 11 | `estado` | ESTADO | character varying(200) | 0.0% | 30 | **Resultado de la gestión** (lo escribe el asesor). Columna crítica → ver cap. de clasificación. | `NO APTO` · `NO TIENE RECURSOS` · `SIN REGISTRO` |
| 12 | `subtipificacion` | SUBTIPIFICACION | character varying(300) | 2.4% | 95 | Motivo o detalle de la gestión. Vacía en CEO al 100%. | `NO AUTORIZO EL SEGUR` · `Tiene otro seguro` · `TRASLADO DE PREDIO` |
| 13 | `motivo` | MOTIVO | text | 0.1% | 1,024 | Texto libre con la razón de la gestión. | `SEGUN CARTA RECIBIDA` · `NO ESTA INTERESADA` · `SEGUN CARTA WEB RECI` |
| 14 | `fecha_de_ejecucion` | **FECHA_DE_EJECUCION** | date | 1.7% | 97 | **Fecha en que ocurrió la gestión.** Columna temporal canónica. | `2026-07-30` · `2026-06-02` · `2026-06-26` |
| 15 | `base` | FECHA BASE | character varying(200) | 0.0% | 154 | **Fecha de carga del lote en el Excel, NO la de la gestión.** No usar para análisis. (Regla Efigas.) | `2026-07-10 00:00:00` · `2026-06-22 00:00:00` · `2026-05-07 00:00:00` |
| 16 | `fecha_de_venta` | FECHA DE VENTA | date | 28.0% | 624 | Fecha en que se vendió la póliza. Eje temporal distinto al de gestión. | `2025-11-24` · `2019-07-08` · `2019-01-21` |
| 17 | `asesor_de_venta` | ASESOR DE VENTA | character varying(300) | 6.4% | 263 | Asesor que vendió la póliza originalmente. No es el de retención. | `RAUL ALBERTO GARCIA ` · `JENNIFER  PEREA` · `ARIS YULIETH BARRIOS` |
| 18 | `mes` | MES | character varying(50) | 0.0% | 9 | Mes de la gestión. Formato variable por gasera (ver H-08). | `MAYO 2026` · `JULIO 2026` · `SEPTIEMBRE 2026` |
| 19 | `cabina` | CABINA | character varying(20) | 100.0% | 0 | INBOUND / OUTBOUND. Constante por tabla. | — |
| 20 | `anio` | ANIO | integer | 0.0% | 1 | **Año de VENTA, no de gestión.** No usar para agregar por periodo. | `2026` |
| 21 | `fecha_carga` | (agregada por la carga) | timestamp without time zone | 0.0% | 1 | Momento en que la fila se insertó en la BD. No viene del Excel. | `2026-10-01 17:19:22.` |
| 23 | `gestor` | GESTOR | text | 0.6% | 23 | Asesor que gestionó la llamada (GDO y Caribe). | `MADE` · `LIS` · `CANCELADO POR JOB` |
| 24 | `gestion_sac` | GESTION SAC | text | 0.1% | 6 | Resultado registrado en el sistema SAC de la aseguradora. | `NO APTO` · `GESTIONADO` · `CANCELADA` |
| 25 | `numero_solicitud` | NUMERO SOLICITUD | text | 26.0% | 917 | Radicado de la solicitud. | `239468544` · `243178902` · `244212116` |
| 26 | `solicitud` | SOLICITUD | text | 0.0% | 1,274 | Número de solicitud. | `237646000` · `236796128` · `240512165` |
| 27 | `fecha_registro` | FECHA REGISTRO | date | 0.0% | 156 | Fecha de radicación de la solicitud. | `2026-06-10` · `2026-04-22` · `2026-01-29` |
| 28 | `cod_estado` | COD ESTADO | text | 0.1% | 1 | Código de estado según catálogo de la gasera. | `13.0` |
| 29 | `observacion_retencion` | OBSERVACION RETENCION | text | 0.8% | 346 | Observación del proceso de retención. | `usuario solicita la ` · `LA ASEGURADA YA FALL` · `NO TIENE EMPLEO` |
| 30 | `fecha_gestion` | FECHA GESTION | date | 31.7% | 92 | Fecha de la gestión (segunda marca temporal en Caribe Outbound). | `2026-01-20` · `2026-03-16` · `2026-06-10` |
| 31 | `resultado_normalizado` | RESULTADO NORMALIZADO | text | 0.0% | 20 | Resultado canónico tras pasar por el catálogo `clasificacion`. | `telefono apagado` · `no es proteceso de r` · `no tiene resursos` |
| 32 | `clasificacion` | CLASIFICACION | text | 0.0% | 2 | Clasificación de la solicitud. | `NO APTA` · `APTA` |
| 33 | `producto_norm` | PRODUCTO NORM | text | 0.0% | 10 | Producto normalizado (función `normalizar_producto`). | `PROEXEQUIAL` · `PAZ Y SALVO` · `SIN REGISTRO` |
| 34 | `aseguradora_norm` | ASEGURADORA NORM | text | 0.0% | 6 | Aseguradora normalizada (función `normalizar_aseguradora`). | `PROEXEQUIAL` · `SURAMERICANA` · `OTROS` |

#### `caribe_abandono` — 5,064 filas

| # | Columna | Nombre original Excel | Tipo | Nulos | Distintos | Significado | Ejemplos |
| ---: | :--- | :--- | :--- | ---: | ---: | :--- | :--- |
| 1 | `id` | **ID** | integer | 0.0% | 5,064 | PK sintética. La carga no conserva un identificador del Excel. | `1` · `2` · `3` |
| 2 | `aseguradora` | ASEGURADORA | character varying(200) | 69.5% | 5 | Aseguradora que emite la póliza del cliente. | `SEGURO DE VIDA` · `CIA SURAMERICANA DE` · `PROXEQUIAL SAS` |
| 3 | `nombre_cliente` | NOMBRE CLIENTE | character varying(300) | 65.7% | 1,700 | Nombre del cliente. **Dato sensible.** | `GABIANA  ESCORCIA   ` · `ALEXANDER ALVEAR TOR` · `CARMEN SOFIA MOLINA ` |
| 4 | `identificacion_usuario` | IDENTIFICACION USUARIO | bigint | 70.9% | 1,404 | Documento de identidad. **Dato sensible.** | `32832603` · `25296174` · `1129536897` |
| 5 | `contrato` | CONTRATO | bigint | 66.2% | 1,574 | Número de contrato del cliente. Llave de negocio principal. | `48170305` · `17190364` · `66707266` |
| 6 | `localidad` | LOCALIDAD | character varying(200) | 81.9% | 115 | Municipio/ciudad del cliente. | `RODADERO` · `ORIHUECA (Z. B.)` · `PENONCITO (SN ZENON)` |
| 7 | `telefono` | TELEFONO | bigint | 0.9% | 2,735 | Teléfono del cliente. | `3209278203` · `3113845411` · `3205497405` |
| 8 | `resultado_llamada` | RESULTADO LLAMADA | character varying(300) | 4.0% | 15 | Resultado del corte de la llamada abandonada. | `NO APTO` · `Supero el tiempo de ` · `CONTACTO EXITOSO` |
| 9 | `fecha_llamada` | FECHA LLAMADA | date | 0.0% | 116 | **Fecha de la llamada abandonada.** | `2026-08-15` · `2026-06-10` · `2026-09-12` |
| 10 | `hora` | HORA | character varying(30) | 0.0% | 4,734 | Hora de la llamada, como texto libre (formato `10:01:10 a. m.`). | `14:19:53` · `14:17:26` · `14:10:30` |
| 11 | `fecha_carga` | (agregada por la carga) | timestamp without time zone | 0.0% | 2 | Momento en que la fila se insertó en la BD. No viene del Excel. | `2026-09-15 17:22:37.` · `2026-10-01 17:24:56.` |
| 13 | `gestionado_inbound` | GESTIONADO INBOUND | boolean | 0.0% | 2 | Flag: el abandono terminó luego en una gestión Inbound. Solo Caribe. | `False` · `True` |

#### `gdo_inbound` — 4,190 filas

| # | Columna | Nombre original Excel | Tipo | Nulos | Distintos | Significado | Ejemplos |
| ---: | :--- | :--- | :--- | ---: | ---: | :--- | :--- |
| 1 | `id` | **ID** | integer | 0.0% | 4,190 | PK sintética. La carga no conserva un identificador del Excel. | `1` · `2` · `3` |
| 2 | `mes` | MES | text | 0.0% | 6 | Mes de la gestión. Formato variable por gasera (ver H-08). | `Julio` · `Abril` · `Agosto` |
| 3 | `fecha_de_llamada` | FECHA DE LLAMADA | text | 0.0% | 117 |  | `2026-04-30` · `2026-04-21` · `2026-05-21` |
| 4 | `solicitud_de_poliza` | SOLICITUD DE POLIZA | text | 7.0% | 3,851 | Número de la solicitud de póliza. | `159178806` · `163163203` · `161973210` |
| 5 | `fecha_de_legalizacion` | FECHA DE LEGALIZACION | text | 7.6% | 136 | Fecha de formalización de la póliza. | `2026-01-03` · `2026-04-30` · `2026-04-21` |
| 6 | `estado_de_solicitud` | ESTADO DE SOLICITUD | text | 1.1% | 43 | Estado de la solicitud en el sistema de GDO. | `INFORMACION SOBRE LI` · `NO APTO` · `VOLVER A LLAMAR  MAÑ` |
| 7 | `entidad_facturacion` | ENTIDAD DE FACTURACION | text | 2.7% | 6 | Entidad que factura (aseguradora). | `HDI` · `ALFA` · `SURA` |
| 8 | `nombre_distribuidoras` | NOMBRE DISTRIBUIDORAS | text | 0.2% | 6 | Nombre de la fuerza de ventas. | `ALFA` · `SURA` · `NA` |
| 9 | `nombre_cliente` | NOMBRE CLIENTE | text | 0.1% | 3,598 | Nombre del cliente. **Dato sensible.** | `MARTHA` · `LUZMARI` · `RAQUEL HUERTA SOTO` |
| 10 | `identificacion_usuario` | IDENTIFICACION USUARIO | text | 2.3% | 3,426 | Documento de identidad. **Dato sensible.** | `27281967` · `16511527` · `3199135` |
| 11 | `contrato` | CONTRATO | text | 0.1% | 3,471 | Número de contrato del cliente. Llave de negocio principal. | `415159` · `445811` · `902202` |
| 12 | `localidad` | LOCALIDAD | text | 4.2% | 225 | Municipio/ciudad del cliente. | `VILLAPAZ (JAMUNDI)` · `ROSELIN ESTHER ALVAR` · `GUACHINTE ( JAMUNDI ` |
| 13 | `telefono` | TELEFONO | text | 0.4% | 3,427 | Teléfono del cliente. | `3136715146` · `3217866048` · `3018219165` |
| 14 | `tipo_contacto` | TIPO CONTACTO | text | 1.4% | 36 | Con quién se spoke el asesor (GDO). | `NO APTO` · `Asegurada` · `Recuperando datos. E` |
| 15 | `canal` | CANAL | text | 4.3% | 35 | Canal de la llamada: TELEVENTA, SAC, PAP, DOBLE CUPON, PUNTO FIJO. | `NO APTO` · `DOBLE CUPÓN` · `Recuperando datos. E` |
| 16 | `fecha_venta` | FECHA VENTA | text | 8.4% | 1,715 | Fecha de venta de la póliza. | `2024-05-31` · `2022-08-18` · `2021-11-27` |
| 17 | `producto_1` | PRODUCTO | text | 0.8% | 48 | Producto principal. | `SEGURO PROCTECTOR` · `SEGURO FUNERARIO` · `SEGUR PORTECTOR` |
| 18 | `producto_2` | PRODUCTO 2 | text | 99.9% | 2 | Producto secundario. | `NA` · `NO APLICA` |
| 19 | `nombre_asesor_venta` | NOMBRE ASESOR VENTA | text | 2.6% | 454 | Asesor que vendió la póliza. | `VALENTINA  CARVAJAL ` · `NATALIA N PARGA SUAR` · `DAVID FELIPE MONGUA ` |
| 20 | `nombre_asesor_retencion` | NOMBRE ASESOR RETENCION | text | 0.8% | 25 | **Asesor de retención (persona).** Solo GDO registra el asesor individual. | `NO APTO` · `NO APLICA` · `NA` |
| 21 | `categoria` | CATEGORIA | text | 0.3% | 6 | Categoría de la solicitud. | `PETICION` · `1. Solicitud de Canc` · `510413` |
| 22 | `categoria_detalle` | CATEGORIA DETALLE | text | 2.4% | 20 | Detalle de la categoría. | `NO APTO` · `3.1 Solicitud de Inf` · `NA` |
| 23 | `subtipificacion` | SUBTIPIFICACION | text | 2.7% | 52 | Motivo o detalle de la gestión. Vacía en CEO al 100%. | `13.1 Credito finaliz` · `Devolución de prima` · `ASEGURADO FALLECIDO` |
| 24 | `observaciones` | OBSERVACIONES | text | 2.1% | 412 |  | `NO QUIERE EL SEGURO ` · `USUARIA MENCIONA QUE` · `SE APLICA INDENMIZAC` |
| 25 | `number1` | (encabezado inutil) | text | 87.4% | 469 | Sin encabezado útil en el Excel. **Basura de importación.** | `3166116440` · `3014107508` · `3226120123` |
| 26 | `number2` | (encabezado inutil) | text | 86.6% | 495 | Sin encabezado útil en el Excel. **Basura de importación.** | `3104612314` · `3166526155` · `3117901273` |
| 27 | `resultado_final` | RESULTADO FINAL | text | 0.0% | 11 | **Resultado de la gestión (GDO Inbound).** La columna `estado` está vacía al 100%. | `CANCELADO+REINTEGRO` · `SOLICITUD DE DOVOLUC` · `CANCELADO` |
| 28 | `tipo_de_contacto` | TIPO DE CONTACTO | text | 0.0% | 2 | Con quién se spoke el asesor. | `APTO` · `NO APTO` |
| 29 | `respuesta_de_aseguradora` | RESPUESTA DE ASEGURADORA | text | 100.0% | 0 | Respuesta escrita de la aseguradora. | — |
| 30 | `soporte` | SOPORTE | text | 100.0% | 1 | Evidencia adjunta (soporte de la gestión). | `NO` |
| 31 | `observacion` | OBSERVACION | text | 100.0% | 1 | Observación del asesor. | `Usuario no contesta,` |
| 32 | `quien_autoriza` | QUIEN AUTORIZA | text | 100.0% | 0 | Quién autorizó la gestión. | — |
| 33 | `cedula` | CEDULA | text | 100.0% | 0 | Cédula de citizenship. **Dato sensible.** | — |
| 34 | `resposable_del_pago_o_titular_de_la_cuenta` | RESPONSABLE DEL PAGO O TITULAR DE LA CUENTA | text | 100.0% | 0 | Responsable del pago o titular de la cuenta. **Typo en el nombre: "resposable".** | — |
| 35 | `estado` | ESTADO | text | 100.0% | 1 | **Resultado de la gestión** (lo escribe el asesor). Columna crítica → ver cap. de clasificación. | `ENVIADO` |
| 36 | `f_envio` | F ENVIO | text | 100.0% | 1 | Fecha de envío. | `27/03/2026` |
| 37 | `fehca_de_cancelacion` | FECHA DE CANCELACION | text | 100.0% | 0 | Fecha de cancelación. **Typo en el nombre: "fehca".** | — |
| 38 | `ans` | ANS | text | 52.0% | 11 | Días de_answer (Answer Service) entre solicitud y atención. | `0` · `1` · `4` |
| 39 | `dias_de_maduracion` | DIAS DE MADURACION | text | 49.8% | 17 | Días de maduración de la gestión. | `Mayor a 1 año y 3 me` · `1 año y 1 mes` · `8 meses` |

#### `gdo_outbound` — 3,284 filas

| # | Columna | Nombre original Excel | Tipo | Nulos | Distintos | Significado | Ejemplos |
| ---: | :--- | :--- | :--- | ---: | ---: | :--- | :--- |
| 1 | `id` | **ID** | integer | 0.0% | 3,284 | PK sintética. La carga no conserva un identificador del Excel. | `1` · `2` · `3` |
| 2 | `fecha_de_base` | FECHA DE BASE | text | 0.0% | 139 | **Fecha de carga del lote. NO usar para análisis.** | `2026-04-30` · `2026-04-21` · `2026-05-21` |
| 3 | `contrato` | CONTRATO | text | 0.0% | 2,977 | Número de contrato del cliente. Llave de negocio principal. | `312293` · `500264` · `2177003` |
| 4 | `producto` | PRODUCTO | text | 0.1% | 3,220 | Producto de seguros del cliente. | `312293` · `500264` · `71241548` |
| 5 | `plan` | PLAN | text | 6.8% | 45 | Plan comercial. | `practiseguro` · `MODULO C` · `ASISTENCIA SALUD BÁS` |
| 6 | `tipo_de_plan` | TIPO DE PLAN | text | 8.0% | 74 | Tipo de plan. | `plan 2 SALVA FACTURA` · `Paz y salvo` · `PLAN EXEQUIAL` |
| 7 | `aseguradora` | ASEGURADORA | text | 7.5% | 24 | Aseguradora que emite la póliza del cliente. | `GNP` · `PLAN 1` · `SEGURO FUNERARIO` |
| 8 | `tipo_producto` | TIPO PRODUCTO | text | 0.1% | 5 | Tipo de producto. | `NO ES LABOR DE RETEN` · `Seguros Alfa S.A.` · `7053 - Brilla Seguro` |
| 9 | `interaccion` | INTERACCION | text | 0.1% | 3,060 | Tipo de interacción. | `156691944` · `165031263` · `156309026` |
| 10 | `numero_solicitud` | NUMERO SOLICITUD | text | 0.1% | 3,271 | Radicado de la solicitud. | `157340201` · `152147472` · `163889828` |
| 11 | `nombre_solicitud` | NOMBRE SOLICITUD | text | 0.1% | 5 | Descripción corta de la solicitud. | `NO ES LABOR DE RETEN` · `LDC - Solicitudes Va` · `Cancelación de Segur` |
| 12 | `causal_registro_solicitud` | CAUSAL REGISTRO SOLICITUD | text | 10.2% | 23 | Causal con que se registró la solicitud. | `318 - AUDITORIA NEGA` · `389 - RECLAMO DESCUE` · `22 - QUEJA POR GESTI` |
| 13 | `area_causante_solicitud` | AREA CAUSANTE SOLICITUD | text | 71.9% | 9 | Área causante de la solicitud. | `4591 - QR-FNB - HDI ` · `4590 - QR-FNB-ALFA S` · `4589 - QR-FNB-ALFA S` |
| 14 | `area_duena_solicitud` | AREA DUEÑA SOLICITUD | text | 0.1% | 3 | Área que debe resolver. | `NO ES LABOR DE RETEN` · `41 - QR-SER.CLIENTE-` · `40 - QR-FNB` |
| 15 | `area_real_causante` | AREA REAL CAUSANTE | text | 100.0% | 0 | Área realmente causante. | — |
| 16 | `pto_atencion_reg_solicitud` | PTO ATENCION REG SOLICITUD | text | 0.1% | 6 | Punto de atención donde se registró. | `NO ES LABOR DE RETEN` · `145 - QR-SER.CLIENTE` · `41 - QR-SER.CLIENTE-` |
| 17 | `clasificacion_solicitud` | CLASIFICACION SOLICITUD | text | 0.1% | 3 | Clasificación de la solicitud. | `QUEJAS` · `PETICIONES` · `RECLAMOS` |
| 18 | `estado_solicitud` | ESTADO SOLICITUD | text | 0.1% | 2 | Estado de la solicitud. | `NO ES LABOR DE RETEN` · `13 - Registrado` |
| 19 | `medio_de_uso` | MEDIO DE USO | text | 0.1% | 1 | Medio por el que el cliente usa el seguro. | `Externa` |
| 20 | `medio_recepcion` | MEDIO RECEPCION | text | 0.1% | 11 | Medio de recepción de la solicitud. | `64 - Agendamiento Ca` · `NO ES LABOR DE RETEN` · `21 - Virtual-Aten.Cl` |
| 21 | `semana_registro` | SEMANA REGISTRO | text | 0.1% | 40 | Semana de registro (ISO). | `2026-04-03` · `2026-01-03` · `2026-04-01` |
| 22 | `funcionario_registra` | FUNCIONARIO REGISTRA | text | 0.1% | 108 | Funcionario que registró la solicitud. | `16203 - VERSA - SACV` · `148 - GLADYS TATIANA` · `24782 - JHON ANDERSO` |
| 23 | `observacion` | OBSERVACION | text | 0.0% | 3,188 | Observación del asesor. | `SRA AURA NELLY BETAN` · `CL 3163118265 SRA MA` · `REALIZÓ PAGO TOTAL Y` |
| 24 | `fecha_registro_solicitud` | FECHA REGISTRO SOLICITUD | text | 0.0% | 173 | **Fecha de radicación de la solicitud.** | `2026-04-30` · `15/07/2026` · `2026-04-21` |
| 25 | `fecha_atencion` | FECHA ATENCION | text | 100.0% | 0 | Fecha de atención. **98.8% no parseable.** | — |
| 26 | `tipo_respuesta` | TIPO RESPUESTA | text | 100.0% | 0 | Tipo de respuesta dada. | — |
| 27 | `respuesta` | RESPUESTA | text | 100.0% | 0 | Respuesta dada al cliente. | — |
| 28 | `amplicacion_term` | AMPLIACION TERM | text | 63.6% | 1,190 | Ampliación de término. **Typo en el nombre: "amplicacion".** | `17 -  FECHA MÁXIMA R` · `17 -  FECHA MÁXIMA R` · `17 -  FECHA MÁXIMA R` |
| 29 | `ans` | ANS | text | 0.0% | 2 | Días de_answer (Answer Service) entre solicitud y atención. | `10` · `8` |
| 30 | `dias_registro_solicitud` | DIAS REGISTRO SOLICITUD | text | 0.0% | 5 | Días entre registro y atención. | `4` · `6` · `3` |
| 31 | `cumplimiento_ans` | CUMPLIMIENTO ANS | text | 0.0% | 1 | Cumplimiento del ANS. | `CUMPLE` |
| 32 | `nombre_solicitante` | NOMBRE SOLICITANTE | text | 0.1% | 2,973 | Nombre de quien solicita. **Dato sensible.** | `CECILIA MARLENE - RI` · `HECTOR DE JESUS - CA` · `JENNY SOLANGE - CABR` |
| 33 | `identificacion_solicitante` | IDENTIFICACION SOLICITANTE | text | 0.0% | 2,973 | Documento del solicitante. **Dato sensible.** | `59686608` · `42141637` · `29871538` |
| 34 | `direccion` | DIRECCION | text | 0.1% | 2,976 | Dirección. **Dato sensible.** | `KR 2B CL 15 - 1 PISO` · `CORREG GUACHENE VDA ` · `CL 116 KR 26I - 60 A` |
| 35 | `barrio_solicitud` | BARRIO SOLICITUD | text | 0.1% | 761 | Barrio de la solicitud. | `JUAN PABLO II` · `BARRIO PORTALES DE Y` · `COCICOINPA` |
| 36 | `departamento_solicitud` | DEPARTAMENTO SOLICITUD | text | 0.1% | 2 | Departamento de la solicitud. | `VALLE DEL CAUCA` · `CAUCA` |
| 37 | `localidad_solicitud` | LOCALIDAD SOLICITUD | text | 0.1% | 143 | Localidad de la solicitud. | `VILLAPAZ (JAMUNDI)` · `SAN JOSE (SAN PEDRO)` · `18 - CALI` |
| 38 | `ciclo_solicitud` | CICLO SOLICITUD | text | 0.1% | 84 | Ciclo de la solicitud. | `16 - LA FORTALEZA` · `9 - MUNICIPAL` · `166 - VILLAGORGONA` |
| 39 | `numero_orden_trabajo` | NUMERO ORDEN TRABAJO | text | 0.1% | 3,257 | Número de la orden de trabajo. | `438059249` · `436621159` · `432655503` |
| 40 | `tipo_trabajo_orden_trabajo` | TIPO TRABAJO ORDEN TRABAJO | text | 0.1% | 12 | Tipo de trabajo de la orden. | `10405 - PETICIONES M` · `13365 - RECLAMO DESC` · `12597 - QUEJA POR NO` |
| 41 | `unidad_trabajo_orden` | UNIDAD TRABAJO ORDEN | text | 0.1% | 14 | Unidad de trabajo. | `5119 - FNB - IKE ASI` · `4590 - QR-FNB-ALFA S` · `2705 - FNB - ALFA MI` |
| 42 | `area_causante_en_el_registro` | AREA CAUSANTE EN EL REGISTRO | text | 100.0% | 0 | Área causante según el registro. | — |
| 43 | `tipo_unidad_trabajo` | **TIPO_UNIDAD_TRABAJO** | text | 1.5% | 2 |  | `Financiacion No Banc` · `3005 - FINANCIACION ` |
| 44 | `clasificacion_orden_trabajo` | CLASIFICACION ORDEN TRABAJO | text | 1.5% | 3 | Clasificación de la orden de trabajo. | `215 - ORD.QUEJAS` · `222 - FINANCIACIÓN N` · `214 - ORD.RECLAMOS` |
| 45 | `estado_orden_trabajo` | ESTADO ORDEN TRABAJO | text | 1.5% | 1 | Estado de la orden de trabajo. | `5 - Asignada` |
| 46 | `direccion_orden_trabajo` | DIRECCION ORDEN TRABAJO | text | 1.5% | 2,933 | Dirección de la orden. **Dato sensible.** | `KR 2B CL 15 - 1 PISO` · `CORREG GUACHENE VDA ` · `CL 116 KR 26I - 60 A` |
| 47 | `barrio_orden_trabajo` | BARRIO ORDEN TRABAJO | text | 1.5% | 827 | Barrio de la orden. | `2077 - LA MERCED` · `8706 - BARRIO LOS MA` · `5214 - VILLA DEL SOL` |
| 48 | `categoria` | CATEGORIA | text | 0.1% | 2 | Categoría de la solicitud. | `1 - RESIDENCIAL` · `2 - COMERCIAL` |
| 49 | `subcategoria` | SUBCATEGORIA | text | 0.1% | 7 | Subcategoría. | `4 - ESTRATO 4` · `6 - ESTRATO 6` · `3 - ESTRATO 3` |
| 50 | `operador` | OPERADOR | text | 5.5% | 47 | **Empresa operadora del contact center** (SERVIPROTECCION, ACCION PLUS, MIGRACION, GNP...). NO es una persona. Ver H-23. | `MULTINTEGRAL S.A.S` · `MIGRACIÓN` · `PUNTOS DE VENTAS SAC` |
| 51 | `canal` | CANAL | text | 7.8% | 19 | Canal de la llamada: TELEVENTA, SAC, PAP, DOBLE CUPON, PUNTO FIJO. | `NA` · `NO ES UN MICROSEGURO` · `NO TIENE POLIZA` |
| 52 | `producto_2` | PRODUCTO 2 | text | 7.3% | 32 | Producto secundario. | `practiseguro` · `ASISTENCIA SALUD BÁS` · `PRACTISEGURO` |
| 53 | `tipo_de_contacto` | TIPO DE CONTACTO | text | 5.2% | 38 | Con quién se spoke el asesor. | `NO APTO` · `TERCERO` · `CONTACTO A TERCERO` |
| 54 | `motivo` | MOTIVO | text | 3.1% | 247 | Texto libre con la razón de la gestión. | `NO QUIERE LA PROTECI` · `INDDICA QUE LA ASEGU` · `NO ACEPTÓ VALIDACION` |
| 55 | `estado` | ESTADO | text | 7.8% | 30 | **Resultado de la gestión** (lo escribe el asesor). Columna crítica → ver cap. de clasificación. | `NO APTO` · `CONTACTO A TERCERO` · `YA ESTA CANCELADO` |
| 56 | `observacion_2` | OBSERVACION 2 | text | 7.3% | 762 | Observación adicional. | `Sus hijos ya la tien` · `NO QUIERE LA POLZA P` · `usuario solicita la ` |
| 57 | `fecha_ejecucion` | FECHA EJECUCION | text | 7.1% | 136 | **Fecha de ejecución de la llamada (GDO Outbound).** | `2026-01-10` · `21/2/2026` · `13/03/2026` |
| 58 | `fecha_base` | FECHA BASE | text | 3.1% | 152 |  | `2026-04-30` · `2026-04-21` · `2026-05-21` |
| 59 | `fecha_de_venta` | FECHA DE VENTA | text | 7.2% | 1,249 | Fecha en que se vendió la póliza. Eje temporal distinto al de gestión. | `2024-09-23` · `2025-03-11` · `2022-11-05` |
| 60 | `nombre_del_asesor_de_venta` | NOMBRE DEL ASESOR DE VENTA | text | 7.2% | 355 | Asesor que vendió la póliza. | `SHIRLEY SAIR NIÑO TO` · `CAROLAY LINED RAMIRE` · `YINETH CELENY ALVARE` |
| 61 | `llamada_1` | LLAMADA 1 | text | 9.0% | 9 | Campo de llamada (uso no determinado). | `4` · `6` · `3` |
| 62 | `gestor` | GESTOR | text | 6.6% | 26 | Asesor que gestionó la llamada (GDO y Caribe). | `MADE` · `CINDY` · `KATHE` |
| 63 | `tipo_de_contacto_2` | TIPO DE CONTACTO 2 | text | 7.8% | 57 | Segundo tipo de contacto. | `NO APTO` · `TERCERO` · `CONTACTO A TERCERO` |
| 64 | `tipifiacion_de_pqr` | TIPIFICACION DE PQR | text | 8.5% | 184 | Tipificación de la PQR. **184 valores distintos.** | `FINALIZO CREDITO CON` · `NO TENIA CONOCIMIENT` · `ASEGURADO FALLECIDO` |
| 65 | `resultado_de_retencion` | RESULTADO DE RETENCION | text | 8.5% | 15 | **Resultado de la gestión (GDO Outbound).** | `NO APTO` · `NO APLICA` · `NUMERO ERRADO` |
| 66 | `correo` | CORREO | text | 98.8% | 23 | Correo del cliente. **Dato sensible.** | `BASQUESLUCI783@GMAIL` · `claudiaortiz1932@hot` · `cristian.640@hotmail` |
| 67 | `mes` | MES | text | 0.0% | 8 | Mes de la gestión. Formato variable por gasera (ver H-08). | `AGOSTO` · `MARZO` · `FEBRERO` |
| 68 | `cruce` | CRUCE | text | 100.0% | 1 | Marca de cruce con otro registro. | `2` |

#### `gdo_abandono` — 831 filas

| # | Columna | Nombre original Excel | Tipo | Nulos | Distintos | Significado | Ejemplos |
| ---: | :--- | :--- | :--- | ---: | ---: | :--- | :--- |
| 1 | `id` | **ID** | integer | 0.0% | 831 | PK sintética. La carga no conserva un identificador del Excel. | `32` · `33` · `34` |
| 2 | `fecha` | FECHA | text | 0.1% | 76 | Fecha (GDO Abandono). Formato libre y contaminado. | `5/14/2026` · `7/17/2026` · `5/19/2026` |
| 3 | `numbercall` | NUMBERCALL | text | 0.0% | 522 | Número de teléfono de la llamada. | `3235800480` · `3203181156` · `3215986786` |
| 4 | `hora` | **HORA** | text | 20.5% | 350 | Hora de la llamada, como texto libre (formato `10:01:10 a. m.`). | `5:02:00 p. m.` · `2:37:00 p. m.` · `12:17:00 p. m.` |
| 5 | `resultcalldesc` | RESULTCALLDESC | text | 45.4% | 2 | Resultado de la llamada (catálogo del contact center). | `Abandoned` · `NO CONTESTA` |
| 6 | `resultdesc` | RESULTDESC | text | 45.6% | 1 | Descripción del resultado. | `Abandoned` |
| 7 | `fecha_llamada` | **FECHA_LLAMADA** | text | 79.9% | 20 | **Fecha de la llamada abandonada.** | `6/16/2026` · `5/27/2026` · `24/03/2026` |
| 8 | `nombre_cliente` | NOMBRE CLIENTE | text | 89.2% | 48 | Nombre del cliente. **Dato sensible.** | `ALICIA DIAGO` · `JUAN DIEGO ARIAS LON` · `JOSE FERNANDO PINO C` |
| 9 | `identificacion_usuario` | IDENTIFICACION USUARIO | text | 92.3% | 24 | Documento de identidad. **Dato sensible.** | `16588367` · `66992350` · `886743` |
| 10 | `contrato` | CONTRATO | text | 92.1% | 26 | Número de contrato del cliente. Llave de negocio principal. | `249144` · `662401` · `886743` |
| 11 | `producto_1` | PRODUCTO | text | 92.3% | 9 | Producto principal. | `SALVA FACTURA` · `SEGURO FUNERARIO` · `Seguros Alfa S.A.` |
| 12 | `aseguradora` | **ASEGURADORA** | text | 92.8% | 6 | Aseguradora que emite la póliza del cliente. | `HDI` · `SEGUROS DE VIDA ALFA` · `ALFA` |
| 13 | `observaciones` | OBSERVACIONES | text | 82.1% | 70 |  | `ESTA SUSPENDIDO` · `NO TENIA DATOS PARA ` · `UN DAÑO QUE TUVO EN ` |
| 14 | `resultado_final` | RESULTADO FINAL | text | 88.1% | 22 | **Resultado de la gestión (GDO Inbound).** La columna `estado` está vacía al 100%. | `NO APTO` · `PENDIENTE GESTIÓN` · `SINIETRO` |
| 15 | `tipo_de_registro` | **TIPO_DE_REGISTRO** | text | 10.1% | 2 |  | `REGISTRO ÚNICO` · `DUPLICADO` |
| 16 | `resultado_gestion` | RESULTADO GESTION | text | 10.1% | 2 | Resultado de la gestión. | `No gestionado` · `Gestionado por Inbou` |
| 17 | `gestion_canal_inbound` | GESTION CANAL INBOUND | text | 66.2% | 18 | Canal Inbound de la gestión. | `NO APTO` · `NO APLICA` · `DEVOLUCION DE PRIMAS` |
| 18 | `gestor` | **GESTOR** | text | 82.3% | 13 | Asesor que gestionó la llamada (GDO y Caribe). | `Madiley` · `YENNIFER MEJIA` · `CINDY` |

#### `gdo_pqrs` — 747 filas

| # | Columna | Nombre original Excel | Tipo | Nulos | Distintos | Significado | Ejemplos |
| ---: | :--- | :--- | :--- | ---: | ---: | :--- | :--- |
| 1 | `id` | **ID** | integer | 0.0% | 747 | PK sintética. La carga no conserva un identificador del Excel. | `225` · `226` · `227` |
| 2 | `contrato` | CONTRATO | integer | 0.0% | 688 | Número de contrato del cliente. Llave de negocio principal. | `707886` · `345916` · `278536` |
| 3 | `producto` | PRODUCTO | integer | 0.0% | 697 | Producto de seguros del cliente. | `1320963` · `20608` · `77642379` |
| 4 | `tipo_producto` | TIPO PRODUCTO | character varying(50) | 0.0% | 3 | Tipo de producto. | `7053 - Brilla Seguro` · `7055 - Servicios Fin` · `7014 - Gas` |
| 5 | `interaccion` | INTERACCION | integer | 0.0% | 703 | Tipo de interacción. | `158249197` · `158594420` · `158012944` |
| 6 | `numero_solicitud` | NUMERO SOLICITUD | integer | 0.0% | 733 | Radicado de la solicitud. | `161899466` · `162337033` · `158129662` |
| 7 | `nombre_solicitud` | NOMBRE SOLICITUD | character varying(50) | 0.0% | 4 | Descripción corta de la solicitud. | `LDC - Solicitudes Va` · `Reclamos` · `Cancelación de Segur` |
| 8 | `causal_registro_solicitud` | CAUSAL REGISTRO SOLICITUD | character varying(64) | 0.0% | 16 | Causal con que se registró la solicitud. | `22 - QUEJA POR GESTI` · `317 - PAGO TOTAL FIN` · `254 - MALA INFORMACI` |
| 9 | `area_causante_solicitud` | AREA CAUSANTE SOLICITUD | character varying(50) | 0.0% | 12 | Área causante de la solicitud. | `109 - QR-FNB - HDI M` · `4591 - QR-FNB - HDI ` · `5120 - FNB - QR - IK` |
| 10 | `area_duena_solicitud` | AREA DUEÑA SOLICITUD | character varying(50) | 0.0% | 2 | Área que debe resolver. | `41 - QR-SER.CLIENTE-` · `40 - QR-FNB` |
| 11 | `area_real_causante` | AREA REAL CAUSANTE | character varying(50) | 0.0% | 2 | Área realmente causante. | `` · `3 - GERENCIA COMERCI` |
| 12 | `pto_atencion_reg_solicitud` | PTO ATENCION REG SOLICITUD | character varying(50) | 0.0% | 4 | Punto de atención donde se registró. | `41 - QR-SER.CLIENTE-` · `793 - FNB - ADMINIST` · `148 - QR-SER.CLIENTE` |
| 13 | `clasificacion_solicitud` | CLASIFICACION SOLICITUD | character varying(50) | 0.0% | 3 | Clasificación de la solicitud. | `QUEJAS` · `PETICIONES` · `RECLAMOS` |
| 14 | `estado_solicitud` | ESTADO SOLICITUD | character varying(50) | 0.0% | 2 | Estado de la solicitud. | `14 - Atendido` · `13 - Registrado` |
| 15 | `♣` | **♣** | character varying(50) | 0.0% | 1 |  | `Externa` |
| 16 | `medio_recepcion` | MEDIO RECEPCION | character varying(64) | 0.0% | 8 | Medio de recepción de la solicitud. | `10 - Orden de proced` · `65 - WhatsApp - Aten` · `4 - Call center-Aten` |
| 17 | `semana_registro` | SEMANA REGISTRO | character varying(50) | 0.0% | 29 | Semana de registro (ISO). | `3-may` · `2-jul` · `3-jun` |
| 18 | `funcionario_registra` | FUNCIONARIO REGISTRA | character varying(150) | 0.0% | 101 | Funcionario que registró la solicitud. | `16203 - VERSA - SACV` · `148 - GLADYS TATIANA` · `24782 - JHON ANDERSO` |
| 19 | `observacion_solicitud` | OBSERVACION SOLICITUD | text | 0.0% | 725 | Observación de la solicitud. | `ANGELA OCHOA TELF 31` · `SEGURO: (de vida ) -` · `SEGURO: (SALVA FACTU` |
| 20 | `fecha_registro_solicitud` | FECHA REGISTRO SOLICITUD | character varying(50) | 0.0% | 123 | **Fecha de radicación de la solicitud.** | `9/06/2026` · `9/04/2026` · `15/07/2026` |
| 21 | `fecha_atencion` | FECHA ATENCION | character varying(50) | 0.0% | 5 | Fecha de atención. **98.8% no parseable.** | `28/03/2026` · `20/03/2026` · `30/03/2026` |
| 22 | `tipo_respuesta` | TIPO RESPUESTA | character varying(50) | 0.0% | 2 | Tipo de respuesta dada. | `32 - No Accede` · `` |
| 23 | `respuesta` | RESPUESTA | character varying(50) | 0.0% | 3 | Respuesta dada al cliente. | `` · `1551 - NO HUBO FALLA` · `1731 - NO HUBO FALLA` |
| 24 | `amplicacion_term` | AMPLIACION TERM | character varying(128) | 0.0% | 624 | Ampliación de término. **Typo en el nombre: "amplicacion".** | `17 -  FECHA MÁXIMA R` · `17 -  FECHA MÁXIMA R` · `17 -  FECHA MÁXIMA R` |
| 25 | `ans` | ANS | integer | 0.0% | 2 | Días de_answer (Answer Service) entre solicitud y atención. | `8` · `10` |
| 26 | `dias_registro_solicitud` | DIAS REGISTRO SOLICITUD | integer | 0.0% | 9 | Días entre registro y atención. | `8` · `7` · `9` |
| 27 | `cumplimiento_ans` | CUMPLIMIENTO ANS | character varying(50) | 0.0% | 2 | Cumplimiento del ANS. | `CUMPLE` · `NO CUMPLE ANS` |
| 28 | `nombre_solicitante` | NOMBRE SOLICITANTE | character varying(50) | 0.0% | 689 | Nombre de quien solicita. **Dato sensible.** | `MARGARITA   - DAGUA ` · `JUAN RICARDO - CAMAC` · `EDITH - LOSADA MANCH` |
| 29 | `identificacion_solicitante` | IDENTIFICACION SOLICITANTE | integer | 0.0% | 689 | Documento del solicitante. **Dato sensible.** | `66817870` · `1130670450` · `34372020` |
| 30 | `direccion` | DIRECCION | character varying(128) | 0.0% | 688 | Dirección. **Dato sensible.** | `KR 41D CL 48 - 64` · `KR 28F CL 78 - 29 PI` · `CL 2 KR 8 - 76 PISO ` |
| 31 | `barrio_solicitud` | BARRIO SOLICITUD | character varying(50) | 0.0% | 356 | Barrio de la solicitud. | `LOS PARQUES - BARRAN` · `VEREDA DOMINGA ALTA` · `MUNICIPAL` |
| 32 | `departamento_solicitud` | DEPARTAMENTO SOLICITUD | character varying(50) | 0.0% | 2 | Departamento de la solicitud. | `VALLE DEL CAUCA` · `CAUCA` |
| 33 | `localidad_solicitud` | LOCALIDAD SOLICITUD | character varying(50) | 0.0% | 84 | Localidad de la solicitud. | `10733 - QUINAMAYO (J` · `VILLAPAZ (JAMUNDI)` · `CAMPO ALEGRE ( CALI ` |
| 34 | `ciclo_solicitud` | CICLO SOLICITUD | character varying(50) | 0.0% | 78 | Ciclo de la solicitud. | `16 - LA FORTALEZA` · `9 - MUNICIPAL` · `166 - VILLAGORGONA` |
| 35 | `numero_orden_trabajo` | NUMERO ORDEN TRABAJO | integer | 0.0% | 733 | Número de la orden de trabajo. | `447954767` · `444650576` · `443267386` |
| 36 | `tipo_trabajo_orden_trabajo` | TIPO TRABAJO ORDEN TRABAJO | character varying(128) | 0.0% | 10 | Tipo de trabajo de la orden. | `10405 - PETICIONES M` · `12585 - ANULACION/DE` · `12597 - QUEJA POR NO` |
| 37 | `unidad_trabajo_orden` | UNIDAD TRABAJO ORDEN | character varying(50) | 0.0% | 16 | Unidad de trabajo. | `5119 - FNB - IKE ASI` · `5120 - FNB - QR - IK` · `4590 - QR-FNB-ALFA S` |
| 38 | `area_causante_en_el_registro` | AREA CAUSANTE EN EL REGISTRO | character varying(50) | 0.0% | 2 | Área causante según el registro. | `` · `#N/D` |
| 39 | `tipo_unidad_trabajo` | **TIPO_UNIDAD_TRABAJO** | character varying(50) | 0.0% | 1 |  | `3005 - FINANCIACION ` |
| 40 | `clasificacion_orden_trabajo` | CLASIFICACION ORDEN TRABAJO | character varying(50) | 0.0% | 3 | Clasificación de la orden de trabajo. | `215 - ORD.QUEJAS` · `214 - ORD.RECLAMOS` · `222 - FINANCIACIÓN N` |
| 41 | `estado_orden_trabajo` | ESTADO ORDEN TRABAJO | character varying(50) | 0.0% | 2 | Estado de la orden de trabajo. | `8 - Cerrada` · `5 - Asignada` |
| 42 | `direccion_orden_trabajo` | DIRECCION ORDEN TRABAJO | character varying(128) | 0.0% | 688 | Dirección de la orden. **Dato sensible.** | `KR 41D CL 48 - 64` · `KR 28F CL 78 - 29 PI` · `CL 2 KR 8 - 76 PISO ` |
| 43 | `barrio_orden_trabajo` | BARRIO ORDEN TRABAJO | character varying(50) | 0.0% | 354 | Barrio de la orden. | `5120 - BELLAVISTA` · `6450 - LA INMACULADA` · `5186 - SALOMIA` |
| 44 | `categoria` | **CATEGORIA** | character varying(50) | 0.0% | 2 | Categoría de la solicitud. | `1 - RESIDENCIAL` · `2 - COMERCIAL` |
| 45 | `subcategoria` | **SUBCATEGORIA** | character varying(50) | 0.0% | 6 | Subcategoría. | `4 - ESTRATO 4` · `1 - UNICO -COMERCIAL` · `3 - ESTRATO 3` |
| 46 | `fecha_creacion_orden_trabajo` | FECHA CREACION ORDEN TRABAJO | character varying(50) | 0.0% | 721 | Fecha de creación de la orden de trabajo. | `28/07/2026 11:59` · `20/05/2026 11:09` · `22/05/2026 11:59` |
| 47 | `fecha_asignacion_orden_trab` | FECHA ASIGNACION ORDEN TRAB | character varying(50) | 0.0% | 706 |  | `28/07/2026 11:59` · `20/05/2026 11:09` · `22/05/2026 11:59` |
| 48 | `fecha_finali_ejec_ord_trab` | FECHA FINALI EJEC ORD TRAB | character varying(50) | 0.0% | 10 | Fecha de finalización de la orden. | `` · `30/03/2026 16:47` · `30/03/2026 9:29` |
| 49 | `fecha_lega_orden_trabajo` | FECHA LEGA ORDEN TRABAJO | character varying(50) | 0.0% | 10 |  | `26/03/2026 12:33` · `30/03/2026 16:43` · `28/03/2026 9:22` |
| 50 | `dias_ejecucion_ordenes` | DIAS EJECUCION ORDENES | integer | 0.9% | 9 |  | `8` · `10` · `9` |
| 51 | `comentario_orden_trabajo` | COMENTARIO ORDEN TRABAJO | character varying(2048) | 0.0% | 14 | Comentario de la orden de trabajo. **Contiene escapes `_x000D_` de Excel.** | `Legalizacion de la o` · `Teniendo en cuenta q` · `Teniendo en cuenta q` |
| 52 | `causal_legal_ord_trab` | CAUSAL LEGAL ORD TRAB | character varying(128) | 0.0% | 6 |  | `4468 - NO HUBO FALLA` · `9441 - NO SE RECUPER` · `3230 - SERVICIO AL C` |
| 53 | `func_legaliza_orden_trabajo` | FUNC LEGALIZA ORDEN TRABAJO | character varying(50) | 0.0% | 7 | Funcionario que legaliza la orden. | `OPEN` · `` · `FNBCREMARLIM2` |
| 54 | `agendamiento_visita` | AGENDAMIENTO VISITA | character varying(50) | 0.0% | 2 | Agendamiento de visita. | `NO HAY VENTA FNB` · `` |
| 55 | `agendamiento_vta_cruzada` | AGENDAMIENTO VTA CRUZADA | character varying(50) | 0.0% | 2 | Agendamiento de venta cruzada. | `NO HAY VENTA FNB` · `` |
| 56 | `estado_vta` | ESTADO VTA | character varying(50) | 0.0% | 2 | Estado de la venta cruzada. | `NO HAY VENTA FNB` · `` |
| 57 | `dias_agendamiento` | DIAS AGENDAMIENTO | character varying(50) | 0.0% | 2 | Días de agendamiento. | `NO HAY VENTA FNB` · `` |
| 58 | `ORDEN LOCALIDAD` | **ORDEN LOCALIDAD** | character varying(50) | 0.0% | 76 |  | `7017 - BORRERO AYERB` · `18 - CALI` · `2350 - SAN MARCOS ( ` |
| 59 | `estado` | ESTADO | character varying(50) | 0.0% | 3 | **Resultado de la gestión** (lo escribe el asesor). Columna crítica → ver cap. de clasificación. | `##########` · `` · `SEGUROS` |
| 60 | `tipo poliza` | TIPO POLIZA | character varying(50) | 0.0% | 1 |  | `` |
| 61 | `columna1` | (encabezado generico) | character varying(50) | 0.0% | 3 |  | `SURA` · `` · `HDI` |
| 62 | `columna2` | (encabezado generico) | character varying(50) | 0.0% | 3 |  | `SURA` · `` · `HDI` |
| 63 | `column62` | (encabezado generico) | character varying(50) | 0.0% | 1 |  | `` |

#### `gdo_pqrs_escritas` — 86 filas

| # | Columna | Nombre original Excel | Tipo | Nulos | Distintos | Significado | Ejemplos |
| ---: | :--- | :--- | :--- | ---: | ---: | :--- | :--- |
| 1 | `id` | **ID** | integer | 0.0% | 86 | PK sintética. La carga no conserva un identificador del Excel. | `1` · `2` · `3` |
| 2 | `contrato` | CONTRATO | integer | 0.0% | 80 | Número de contrato del cliente. Llave de negocio principal. | `2806149` · `906922` · `648514` |
| 3 | `aseguradora` | ASEGURADORA | text | 0.0% | 5 | Aseguradora que emite la póliza del cliente. | `PROEXEQUIAL` · `SURAMERICANA` · `IKE` |
| 4 | `producto` | PRODUCTO | text | 0.0% | 11 | Producto de seguros del cliente. | `FUTURO PROTEGIDO PLU` · `SEGURO FUTURO PROTEG` · `EXEQUIAL` |
| 5 | `categoria` | CATEGORIA | text | 0.0% | 6 | Categoría de la solicitud. | `Solicitudes varias` · `Queja` · `Peteición` |
| 6 | `tipificacion` | TIPIFICACION | text | 0.0% | 4 | Tipificación de la solicitud. | `Solicitud de siniest` · `Información del segu` · `No cancelación de la` |
| 7 | `queja_escrita` | QUEJA ESCRITA | integer | 0.0% | 1 | Flag: la queja fue radicada por escrito. | `1` |
| 8 | `canal` | CANAL | text | 1.2% | 2 | Canal de la llamada: TELEVENTA, SAC, PAP, DOBLE CUPON, PUNTO FIJO. | `Presencial-Aten.Clie` · `correo electronico` |
| 9 | `radicado_usu_gdo` | RADICADO USU GDO | date | 11.6% | 46 | **Fecha de radicación del usuario en GDO.** | `2026-07-02` · `2026-06-13` · `2026-08-15` |
| 10 | `fecha_gdo_xuma` | FECHA GDO XUMA | date | 0.0% | 48 | Fecha de radicación en Xuma. | `2026-06-10` · `2026-07-11` · `2026-06-23` |
| 11 | `ans_notificacion_gdo_xuma` | ANS NOTIFICACION GDO XUMA | integer | 11.6% | 16 | Días ANS de la notificación GDO→Xuma. | `14` · `3` · `17` |
| 12 | `fecha_xuma_aseg` | FECHA XUMA ASEG | date | 11.6% | 43 | Fecha de radicación en la aseguradora. | `2026-06-10` · `2026-06-23` · `2026-06-30` |
| 13 | `fecha_respuesta_aseguradora` | FECHA RESPUESTA ASEGURADORA | date | 16.3% | 37 | Fecha de respuesta de la aseguradora. | `2026-08-15` · `2026-06-10` · `2026-06-23` |
| 14 | `ans_respuesta_aseguradora` | ANS RESPUESTA ASEGURADORA | integer | 24.4% | 14 | Días ANS de respuesta de la aseguradora. | `4` · `14` · `3` |
| 15 | `numero_radicado` | NUMERO RADICADO | text | 12.8% | 69 | Número de radicado ante la aseguradora. | `260722-000656` · `SE ENVIO CORREO` · `260714-000581` |
| 16 | `respuesta` | RESPUESTA | text | 16.3% | 70 | Respuesta dada al cliente. | `Cordial saludo, seño` · `Para Seguros de Vida` · `No obstante, en aten` |
| 17 | `estado` | ESTADO | text | 0.0% | 3 | **Resultado de la gestión** (lo escribe el asesor). Columna crítica → ver cap. de clasificación. | `GESTIONADA` · `SINIESTRO` · `PENDIENTE` |
| 18 | `observacion` | OBSERVACION | text | 79.1% | 9 | Observación del asesor. | `RADICARON PQR TAMBIE` · `Cordial saludo, seño` · `Hemos revisado su ca` |
| 19 | `mes` | MES | text | 0.0% | 4 | Mes de la gestión. Formato variable por gasera (ver H-08). | `Julio` · `Agosto` · `Mayo` |
| 20 | `orden_mes` | ORDEN MES | integer | 0.0% | 4 | Orden del mes (1-12) para ordenar reportes. | `8` · `7` · `6` |

#### `gdo_informativo` — 4,191 filas

| # | Columna | Nombre original Excel | Tipo | Nulos | Distintos | Significado | Ejemplos |
| ---: | :--- | :--- | :--- | ---: | ---: | :--- | :--- |
| 1 | `id` | **ID** | integer | 0.0% | 4,191 | PK sintética. La carga no conserva un identificador del Excel. | `1` · `2` · `3` |
| 2 | `solicitud` | SOLICITUD | bigint | 22.3% | 3,214 | Número de solicitud. | `165004535` · `163169445` · `161893083` |
| 3 | `id_tipo_solicitud` | ID TIPO SOLICITUD | integer | 22.3% | 1 | ID del tipo de solicitud. | `100214` |
| 4 | `desc_tipo_solicitud` | DESC TIPO SOLICITUD | text | 22.3% | 1 | Descripción del tipo de solicitud. | `Solicitud de Informa` |
| 5 | `punto_atencion` | PUNTO ATENCION | integer | 22.3% | 2 | ID del punto de atención. | `148` · `41` |
| 6 | `nombre_punto_atencion` | NOMBRE PUNTO ATENCION | text | 22.3% | 2 | Nombre del punto de atención. | `QR-SER.CLIENTE-CALL ` · `QR-SER.CLIENTE-FRONT` |
| 7 | `id_tipo_recepcion` | ID TIPO RECEPCION | integer | 22.3% | 9 | ID del tipo de recepción. | `19` · `10` · `1` |
| 8 | `desc_tipo_recepcion` | DESC TIPO RECEPCION | text | 22.3% | 9 | Descripción del tipo de recepción. | `Orden de procedimien` · `Página web-Aten.Clie` · `Internet-Aten.Client` |
| 9 | `fecha_regi` | FECHA REGI | text | 22.3% | 264 | Fecha de registro. **Tres formatos distintos en la misma columna.** | `26/08/2026  11:17:17` · `25/08/2026  9:42:47 ` · `31/08/2026  11:00:08` |
| 10 | `hora_regi` | HORA REGI | text | 56.3% | 1,806 | Hora de registro. | `13:13:58 a.7./p.7.` · `15:08:22 a.7./p.7.` · `15:29:51 a.6./p.6.` |
| 11 | `contrato` | CONTRATO | text | 19.8% | 2,979 | Número de contrato del cliente. Llave de negocio principal. | `1558277` · `1565815` · `614531` |
| 12 | `observacion` | OBSERVACION | text | 6.5% | 3,375 | Observación del asesor. | `GLORIA INES GARZON N` · `SOLICITAR FORMALMENT` · `3185405545  TL SRA H` |
| 13 | `clase_comentario` | CLASE COMENTARIO | text | 22.3% | 2 | Clase del comentario. | `127` · `Informacion de Segur` |
| 14 | `desc_clase_comentario` | DESC CLASE COMENTARIO | text | 22.3% | 10 | Descripción de la clase de comentario. | `Informacion de Segur` · `1512` · `1510` |
| 15 | `tipo_comentario` | TIPO COMENTARIO | text | 22.3% | 23 | Tipo de comentario. | `REITERATIVO POR TRAS` · `TRASLADO POR COMPETE` · `REITERATIVO POR TRAS` |
| 16 | `desc_tipo_comentario` | DESC TIPO COMENTARIO | text | 22.3% | 74 | Descripción del tipo de comentario. | `17450 - LINA MARIA C` · `15158 - VERSA - SACV` · `16206 - VERSA - SACV` |
| 17 | `funcionario` | FUNCIONARIO | text | 22.4% | 104 | Funcionario que registra. **Dato sensible.** | `15145 - VERSA - SACV` · `16214 - VERSA - SACV` · `18916 - VERSA - SACV` |
| 18 | `departamento` | DEPARTAMENTO | text | 22.9% | 46 | Departamento del funcionario. | `47 - TULUA` · `13 - SANTANDER DE QU` · `35 - JAMUNDI` |
| 19 | `localidad` | LOCALIDAD | text | 22.8% | 169 | Municipio/ciudad del cliente. | `18 - CALI` · `COAZRVDAGDO104` · `4571 - SALONICA ( RI` |
| 20 | `terminal` | TERMINAL | text | 28.2% | 37 | Terminal de tabs del funcionario. **Dato sensible.** | `COYMB38GDO1EHE` · `COCLO38GDOCM0S` · `COCTG38GDOCMRH` |
| 21 | `tabulacion` | TABULACION | text | 28.2% | 11 | Tabulación del funcionario. **Dato sensible.** | `IKE` · `GNP` · `HDI` |
| 22 | `cel` | CEL | text | 32.7% | 2,357 | Celular del funcionario. **Dato sensible.** | `3154466630` · `3118807756` · `3155577961` |
| 23 | `gestion` | GESTION | text | 28.2% | 4 | Indicador de si el abandono fue gestionado. | `PQRS REGISTRADA` · `NO ENCONTRADA` · `GESTIÓN INBOUND` |
| 24 | `tipo_registro` | TIPO DE REGISTRO | text | 28.2% | 2 | Marca de duplicado: REGISTRO ÚNICO / REGISTRO DUPLICADO. | `REGISTRO DUPLICADO` · `REGISTRO ÚNICO` |
| 25 | `estado_inf` | ESTADO INF | text | 28.2% | 867 | **Bitácora de seguimiento**: PRIMER REGISTRO / 2 REGISTRO - N DÍAS. | `3 REGISTRO - 1 DÍAS` · `3 REGISTRO - 0 DÍAS` · `702 REGISTRO - 57 DÍ` |
| 26 | `validacion_pqrs` | VALIDACION PQRS | text | 93.7% | 4 | Tipo de PQRS validada (Reclamos, LDC, Cancelación de Seguros). | `LDC - Solicitudes Va` · `Cancelación de Segur` · `Reclamos` |
| 27 | `resultado` | RESULTADO | text | 28.7% | 2 | Resultado de la gestión (nombre genérico). | `Comunicación con usu` · `No registra llamadas` |
| 28 | `campo_v1` | CAMPO V1 | text | 86.7% | 74 | Campo variable sin definición. | `72` · `106` · `8` |
| 29 | `antiguedad_registro` | ANTIGUEDAD REGISTRO | text | 28.3% | 97 | Antigüedad del registro. | `3er registro - 69 dí` · `3er registro - 21 dí` · `2do registro - 91 dí` |

#### `surti_inbound` — 9,423 filas

| # | Columna | Nombre original Excel | Tipo | Nulos | Distintos | Significado | Ejemplos |
| ---: | :--- | :--- | :--- | ---: | ---: | :--- | :--- |
| 1 | `id` | **ID** | bigint | 0.0% | 9,423 | PK sintética. La carga no conserva un identificador del Excel. | `1` · `2` · `3` |
| 2 | `distribuidora` | DISTRIBUIDORA | text | 0.0% | 1 | Gasera a la que pertenece la fila. Constante por tabla. | `SURTIGAS` |
| 3 | `aseguradora` | ASEGURADORA | text | 2.0% | 9 | Aseguradora que emite la póliza del cliente. | `N/A` · `IKE` · `GNP` |
| 4 | `medio_de_recepcion` | MEDIO DE RECEPCION | text | 100.0% | 0 | Canal físico por donde llegó la solicitud (punto de venta, call center, WhatsApp). | — |
| 5 | `suscripcion` | SUSCRIPCION | text | 0.2% | 6,865 | Número de suscripción (Surtigas usa esta denominación en vez de "contrato"). | `259419` · `4929955` · `4553548` |
| 6 | `localidad` | LOCALIDAD | text | 57.4% | 116 | Municipio/ciudad del cliente. | `SANTA ANA` · `SAN ANTERO` · `CARTAGENA DE INDIAS` |
| 7 | `operador` | OPERADOR | text | 87.6% | 28 | **Empresa operadora del contact center** (SERVIPROTECCION, ACCION PLUS, MIGRACION, GNP...). NO es una persona. Ver H-23. | `FRANCIS GARAVITO RAM` · `NO APTO` · `asegudado` |
| 8 | `canal` | CANAL | text | 2.9% | 75 | Canal de la llamada: TELEVENTA, SAC, PAP, DOBLE CUPON, PUNTO FIJO. | `salva factura` · `GNP` · `MIGRACION` |
| 9 | `producto` | PRODUCTO | text | 0.9% | 66 | Producto de seguros del cliente. | `FUTUROM PROTEGIDO PL` · `FAMILIA PROTEGIDA` · `NO APTO` |
| 10 | `tipo_de_contacto` | TIPO DE CONTACTO | text | 1.2% | 40 | Con quién se spoke el asesor. | `LINK MARKETING` · `BENEFICIARIO` · `3132104874` |
| 11 | `estado` | ESTADO | text | 0.6% | 18 | **Resultado de la gestión** (lo escribe el asesor). Columna crítica → ver cap. de clasificación. | `NO APTO` · `NUEVA VENTA` · `NO APLICA` |
| 12 | `subtipificacion` | SUBTIPIFICACION | text | 70.7% | 135 | Motivo o detalle de la gestión. Vacía en CEO al 100%. | `Se contacta al usuar` · `4.2 Dudas en la pres` · `NO ESTA INTERESADA` |
| 13 | `motivo` | MOTIVO | text | 2.5% | 1,249 | Texto libre con la razón de la gestión. | `NO QUIERE LA PROTECI` · `INDICA QUE ES MUY CO` · `no esta interesada e` |
| 14 | `fecha_de_ejecucion` | **FECHA_DE_EJECUCION** | text | 0.0% | 181 | **Fecha en que ocurrió la gestión.** Columna temporal canónica. | `2026-04-30` · `2026-01-10` · `2026-04-21` |
| 15 | `base` | FECHA BASE | text | 0.0% | 182 | **Fecha de carga del lote en el Excel, NO la de la gestión.** No usar para análisis. (Regla Efigas.) | `2026-04-30` · `2026-01-10` · `2026-04-21` |
| 16 | `fecha_de_venta` | FECHA DE VENTA | text | 14.7% | 2,040 | Fecha en que se vendió la póliza. Eje temporal distinto al de gestión. | `26/12/2022` · `2019-06-26` · `2017-08-10` |
| 17 | `asesor_de_venta` | ASESOR DE VENTA | text | 3.2% | 566 | Asesor que vendió la póliza originalmente. No es el de retención. | `MARCELA BEATRIZ MONT` · `AURA ESTELA ARRIETA ` · `MATEO ANDRES NAVARRO` |
| 18 | `mes` | MES | text | 0.0% | 8 | Mes de la gestión. Formato variable por gasera (ver H-08). | `AGOSTO` · `MARZO` · `FEBRERO` |
| 19 | `cabina` | CABINA | text | 0.0% | 1 | INBOUND / OUTBOUND. Constante por tabla. | `INBOUND` |
| 20 | `ano_venta` | AÑO VENTA | text | 35.8% | 14 | **Año de VENTA, no de gestión.** | `2021` · `2014` · `1900` |
| 21 | `validacion` | VALIDACION | text | 0.0% | 2 | **Control de calidad del dato**, no taxonomía de negocio: VÁLIDO / REVISAR. | `VÁLIDO` · `REVISAR` |
| 22 | `tipo_contacto_homolog` | TIPO CONTACTO HOMOLOG | text | 0.0% | 7 | Tipo de contacto ya homogeneizado. **Precedente del proyecto.** | `TITULAR` · `NO APLICA` · `TITULAR/ASEGURADO` |
| 23 | `maduracion_desde_la_venta_queja` | MADURACION DESDE LA VENTA QUEJA | text | 0.0% | 19 | Cohorte de maduración entre la venta y la queja. | `NO REGISTRA` · `#NUM!` · `25 - 35 meses` |
| 24 | `asesor_venta_val` | ASESOR VENTA VAL | text | 3.2% | 549 | Asesor de venta validado. | `MARCELA BEATRIZ MONT` · `AURA ESTELA ARRIETA ` · `MATEO ANDRES NAVARRO` |

#### `surti_outbound` — 299 filas

| # | Columna | Nombre original Excel | Tipo | Nulos | Distintos | Significado | Ejemplos |
| ---: | :--- | :--- | :--- | ---: | ---: | :--- | :--- |
| 1 | `id` | **ID** | bigint | 0.0% | 299 | PK sintética. La carga no conserva un identificador del Excel. | `1` · `2` · `3` |
| 2 | `distribuidora` | DISTRIBUIDORA | text | 0.0% | 1 | Gasera a la que pertenece la fila. Constante por tabla. | `SURTIGAS` |
| 3 | `aseguradora` | ASEGURADORA | text | 0.3% | 7 | Aseguradora que emite la póliza del cliente. | `HDI SEGUROS COLOMBIA` · `HDI` · `ALFA` |
| 4 | `medio_de_recepcion` | MEDIO DE RECEPCION | text | 100.0% | 0 | Canal físico por donde llegó la solicitud (punto de venta, call center, WhatsApp). | — |
| 5 | `suscripcion` | SUSCRIPCION | text | 16.4% | 221 | Número de suscripción (Surtigas usa esta denominación en vez de "contrato"). | `3224309` · `5232576` · `339390` |
| 6 | `localidad` | LOCALIDAD | text | 94.3% | 4 | Municipio/ciudad del cliente. | `CARTAGENA DE INDIAS` · `MONTERIA` · `SAN LUIS DE SINCE` |
| 7 | `operador` | OPERADOR | text | 35.5% | 14 | **Empresa operadora del contact center** (SERVIPROTECCION, ACCION PLUS, MIGRACION, GNP...). NO es una persona. Ver H-23. | `SERVIPROTECCION BPO/` · `ACCION PLUS` · `LINKMARTKETING` |
| 8 | `canal` | CANAL | text | 0.0% | 9 | Canal de la llamada: TELEVENTA, SAC, PAP, DOBLE CUPON, PUNTO FIJO. | `PUNTO FIJO` · `TELEVENTA/PAP` · `2042878` |
| 9 | `producto` | PRODUCTO | text | 1.0% | 37 | Producto de seguros del cliente. | `PROTEGIDO PLUS` · `Practiseguro plus` · `PAP` |
| 10 | `tipo_de_contacto` | TIPO DE CONTACTO | text | 0.0% | 13 | Con quién se spoke el asesor. | `ASEGURDO` · `NO APTO` · `TITULAR DE FCATURA/` |
| 11 | `estado` | ESTADO | text | 0.3% | 7 | **Resultado de la gestión** (lo escribe el asesor). Columna crítica → ver cap. de clasificación. | `NO APTO` · `RETENIDO` · `CANCELADA +VENTA` |
| 12 | `subtipificacion` | SUBTIPIFICACION | text | 98.3% | 5 | Motivo o detalle de la gestión. Vacía en CEO al 100%. | `CONTINUA CON LA PROT` · `FINALIZACION DEL CRE` · `Modificacion de la p` |
| 13 | `motivo` | MOTIVO | text | 0.3% | 97 | Texto libre con la razón de la gestión. | `NO HUBO CONTACTO CON` · `RETENCION EXITOSA DE` · `TITULAR DE FACTURA N` |
| 14 | `fecha_de_ejecucion` | **FECHA_DE_EJECUCION** | text | 0.3% | 96 | **Fecha en que ocurrió la gestión.** Columna temporal canónica. | `2026-08-13` · `2026-09-07` · `2026-05-21` |
| 15 | `base` | FECHA BASE | text | 0.0% | 123 | **Fecha de carga del lote en el Excel, NO la de la gestión.** No usar para análisis. (Regla Efigas.) | `13/03/2026` · `2026-07-22` · `2026-01-21` |
| 16 | `fecha_de_venta` | FECHA DE VENTA | text | 3.7% | 222 | Fecha en que se vendió la póliza. Eje temporal distinto al de gestión. | `2025-02-13` · `2023-11-04` · `2026-04-30` |
| 17 | `asesor_de_venta` | ASESOR DE VENTA | text | 0.3% | 96 | Asesor que vendió la póliza originalmente. No es el de retención. | `KAREN ANDREA NEGRETE` · `ROSELIN ESTHER ALVAR` · `JANURYTH  PINA CUNHA` |
| 18 | `mes` | MES | text | 0.0% | 8 | Mes de la gestión. Formato variable por gasera (ver H-08). | `AGOSTO` · `MARZO` · `FEBRERO` |
| 19 | `cabina` | CABINA | text | 0.0% | 2 | INBOUND / OUTBOUND. Constante por tabla. | `outbound` · `OUTBOUND` |
| 20 | `ano_venta` | AÑO VENTA | text | 11.7% | 12 | **Año de VENTA, no de gestión.** | `2019` · `2025` · `2021` |
| 21 | `validacion` | VALIDACION | text | 0.0% | 2 | **Control de calidad del dato**, no taxonomía de negocio: VÁLIDO / REVISAR. | `VÁLIDO` · `REVISAR` |
| 22 | `tipo_contacto_homolog` | TIPO CONTACTO HOMOLOG | text | 0.0% | 6 | Tipo de contacto ya homogeneizado. **Precedente del proyecto.** | `ASEGURADO` · `TITULAR` · `NO APLICA` |
| 23 | `maduracion_desde_la_venta_queja` | MADURACION DESDE LA VENTA QUEJA | text | 0.0% | 18 | Cohorte de maduración entre la venta y la queja. | `NO REGISTRA` · `25 - 35 meses` · `8 meses` |
| 24 | `asesor_venta_val` | ASESOR VENTA VAL | text | 0.3% | 96 | Asesor de venta validado. | `KAREN ANDREA NEGRETE` · `KELLY IRREÑO` · `ROSELIN ESTHER ALVAR` |

#### `surti_abandono` — 2,795 filas

| # | Columna | Nombre original Excel | Tipo | Nulos | Distintos | Significado | Ejemplos |
| ---: | :--- | :--- | :--- | ---: | ---: | :--- | :--- |
| 1 | `id` | **ID** | bigint | 0.0% | 2,795 | PK sintética. La carga no conserva un identificador del Excel. | `1` · `2` · `3` |
| 2 | `fecha_llamada` | FECHA LLAMADA | text | 0.0% | 2,788 | **Fecha de la llamada abandonada.** | `17/04/2026 9:54:09 a` · `23/04/2026 4:10:33 p` · `22/04/2026 10:49:53 ` |
| 3 | `telefono` | TELEFONO | text | 0.0% | 1,254 | Teléfono del cliente. | `3206692581` · `3002074402` · `3208722308` |
| 4 | `resultado` | RESULTADO | text | 0.0% | 1 | Resultado de la gestión (nombre genérico). | `Abandono` |
| 5 | `gestion` | GESTION | text | 0.0% | 2 | Indicador de si el abandono fue gestionado. | `No Gestionado` · `Gestionado por Inbou` |

#### `surti_qr` — 1,256 filas

| # | Columna | Nombre original Excel | Tipo | Nulos | Distintos | Significado | Ejemplos |
| ---: | :--- | :--- | :--- | ---: | ---: | :--- | :--- |
| 1 | `id` | **ID** | bigint | 0.0% | 1,256 | PK sintética. La carga no conserva un identificador del Excel. | `1` · `2` · `3` |
| 2 | `numero_solicitud` | NUMERO SOLICITUD | text | 0.0% | 1,255 | Radicado de la solicitud. | `176853609` · `177326354` · `186526220` |
| 3 | `producto` | PRODUCTO | text | 0.0% | 16 | Producto de seguros del cliente. | `FNB` · `PROEXEQUIAL` · `PROTEGIDO PLUS` |
| 4 | `resultado` | RESULTADO | text | 2.2% | 9 | Resultado de la gestión (nombre genérico). | `FNB` · `retenida` · `fnb` |
| 5 | `tipificacion` | TIPIFICACION | text | 0.0% | 10 | Tipificación de la solicitud. | `siniestro` · `FNB` · `usuario no autorizo` |
| 6 | `aseguradora` | ASEGURADORA | text | 0.0% | 6 | Aseguradora que emite la póliza del cliente. | `GNP` · `IKE ASISTENCIA` · `HDI` |
| 7 | `nombre_solicitud` | NOMBRE SOLICITUD | text | 0.0% | 2 | Descripción corta de la solicitud. | `Reclamos` · `Registro de Quejas` |
| 8 | `soporte` | SOPORTE | text | 86.9% | 3 | Evidencia adjunta (soporte de la gestión). | `SI` · `NO` · `NO/ SI` |
| 9 | `fecha_registro_solicitud` | FECHA REGISTRO SOLICITUD | text | 0.0% | 1,255 | **Fecha de radicación de la solicitud.** | `2026-06-27 12:06:24` · `2026-07-28 13:17:42` · `2026-07-03 16:33:47` |
| 10 | `semana_de_registro` | SEMANA DE REGISTRO | text | 0.0% | 38 | Semana de registro. | `5 - MAYO` · `1 - MAYO` · `5 - JULIO` |
| 11 | `fecha_de_atencion` | FECHA DE ATENCION | text | 5.9% | 1,181 | Fecha de atención de la solicitud. | `2026-08-21 11:56:21` · `2026-02-25 10:33:03` · `2026-07-06 16:11:08` |
| 12 | `codigo_contrato` | CODIGO CONTRATO | text | 0.0% | 1,185 | Código de contrato. | `230317` · `2090908` · `4316454` |
| 13 | `ident_solicitante` | IDENT SOLICITANTE | text | 0.0% | 1,192 | Identificación del solicitante. **Dato sensible.** | `5000000962` · `23243561` · `78729854` |
| 14 | `nombre_solicitante` | NOMBRE SOLICITANTE | text | 0.0% | 1,193 | Nombre de quien solicita. **Dato sensible.** | `FERMINA DEL CARMEN  ` · `LUIS ENRIQUE MARQUEZ` · `JUAN G GUZMAN PEREZ` |
| 15 | `clasificacion_solicitud` | CLASIFICACION SOLICITUD | text | 0.0% | 2 | Clasificación de la solicitud. | `RECLAMOS` · `QUEJAS` |
| 16 | `medio_de_uso` | MEDIO DE USO | text | 0.0% | 1 | Medio por el que el cliente usa el seguro. | `Externa` |
| 17 | `estado_solicitud` | ESTADO SOLICITUD | text | 0.0% | 2 | Estado de la solicitud. | `14 - Atendido` · `13 - Registrado` |
| 18 | `area_duena_solicitud` | AREA DUEÑA SOLICITUD | text | 0.0% | 4 | Área que debe resolver. | `FNB` · `FNB.BRILLA` · `SEGUROS` |
| 19 | `punto_atencion_reg_solicitud` | PTO ATENCION REG SOLICITUD | text | 0.0% | 13 | Punto de atención del registro. | `1527 - QR-SER.CLIENT` · `1532 - QR-SER.CLIENT` · `148 - QR-SER.CLIENTE` |
| 20 | `medio_recepcion` | MEDIO RECEPCION | text | 0.0% | 12 | Medio de recepción de la solicitud. | `3 - Internet-Aten.Cl` · `47 - Redes Sociales` · `26 - Call center-Ate` |
| 21 | `funcionario_registra` | FUNCIONARIO REGISTRA | text | 0.0% | 89 | Funcionario que registró la solicitud. | `13611 - PAOLA ANDREA` · `29866 - KEVIN ALFONS` · `25158 - ORION - ORIO` |
| 22 | `observacion_solicitud` | OBSERVACION SOLICITUD | text | 0.0% | 1,252 | Observación de la solicitud. | `Reclamo por cobro de` · `El usuario presenta ` · `SR FELIX BALOY IBARR` |
| 23 | `direccion_solicitud` | DIRECCION SOLICITUD | text | 0.0% | 1,185 | Dirección de la solicitud. **Dato sensible.** | `URB FLOR DEL CAMPO  ` · `KR 17 CL 19 - 13` · `KR 11 CL 11 - 17` |
| 24 | `departamento_solicitud` | DEPARTAMENTO SOLICITUD | text | 0.0% | 4 | Departamento de la solicitud. | `ANTIOQUIA` · `SUCRE` · `BOLIVAR` |
| 25 | `localidad_solicitud` | LOCALIDAD SOLICITUD | text | 0.0% | 66 | Localidad de la solicitud. | `SAN ANTERO` · `OVEJAS` · `CARTAGENA DE INDIAS` |
| 26 | `ciclo_solicitud` | CICLO SOLICITUD | text | 0.0% | 110 | Ciclo de la solicitud. | `1164 - CC 1164 MAGAN` · `2252 - CC 2252 SAHAG` · `1051 - CC 1051 BAYUN` |
| 27 | `barrio_solicitud` | BARRIO SOLICITUD | text | 0.0% | 672 | Barrio de la solicitud. | `SAN  MIGUEL ( MONTER` · `DIVINO NI?O ( SINCEL` · `LOMA FRESCA ( CAUCAS` |
| 28 | `numero_orden_trabajo` | NUMERO ORDEN TRABAJO | text | 0.0% | 1,256 | Número de la orden de trabajo. | `307292620` · `298403593` · `304283676` |
| 29 | `tipo_trabajo_orden_trabajo` | TIPO TRABAJO ORDEN TRABAJO | text | 0.0% | 9 | Tipo de trabajo de la orden. | `12552 - RECLAMO COBR` · `12593 - QUEJA POR AT` · `12606 - QUEJA POR MÉ` |
| 30 | `estado_orden_trabajo` | ESTADO ORDEN TRABAJO | text | 0.0% | 2 | Estado de la orden de trabajo. | `5 - Asignada` · `8 - Cerrada` |
| 31 | `unidad_de_trabajo_orden` | UNIDAD DE TRABAJO ORDEN | text | 0.0% | 5 | Unidad de trabajo de la orden. | `1622 - GC PETICIONES` · `294 - QR-FNB.SEGUROS` · `4154 - QR-FNB- SEGUR` |
| 32 | `tipo_unidad_de_trabajo` | TIPO UNIDAD DE TRABAJO | text | 0.0% | 2 | Tipo de unidad de trabajo. | `3004 - GESTION CON E` · `3005 - FINANCIACION ` |
| 33 | `clasificacion` | CLASIFICACION | text | 0.0% | 3 | Clasificación de la solicitud. | `215 - ORD.QUEJAS` · `214 - ORD.RECLAMOS` · `237 - ORD.SOLICITUDE` |
| 34 | `direccion_orden_trabajo` | DIRECCION ORDEN TRABAJO | text | 0.0% | 1,185 | Dirección de la orden. **Dato sensible.** | `URB FLOR DEL CAMPO  ` · `KR 17 CL 19 - 13` · `KR 11 CL 11 - 17` |
| 35 | `fecha_creacion_orden_trabajo` | FECHA CREACION ORDEN TRABAJO | text | 0.0% | 188 | Fecha de creación de la orden de trabajo. | `2026/07/25 00:00:00` · `2026/07/31 00:00:00` · `2026/03/24 00:00:00` |
| 36 | `fecha_asignacion_orden_trabajo` | FECHA ASIGNACION ORDEN TRABAJO | text | 0.0% | 188 | Fecha de asignación de la orden. | `2026/07/25 00:00:00` · `2026/07/31 00:00:00` · `2026/03/24 00:00:00` |
| 37 | `fecha_plan_ejec_ord_trab` | FECHA PLAN EJEC ORD TRAB | text | 0.0% | 188 | Fecha planificada de ejecución. | `2026/07/25 00:00:00` · `2026/07/31 00:00:00` · `2026/03/24 00:00:00` |
| 38 | `fech_lega_orden_trabajo` | FECHA LEGA ORDEN TRABAJO | text | 5.9% | 179 | Fecha de llegada de la orden. **Typo en el nombre: "fech_lega".** | `2026/03/14 00:00:00` · `2026/07/25 00:00:00` · `2026/07/31 00:00:00` |
| 39 | `fech_ini_ejec_orden_trabajo` | FECHA INI EJEC ORDEN TRABAJO | text | 5.9% | 185 | Fecha de inicio de ejecución de la orden. | `2026/07/25 00:00:00` · `2026/07/31 00:00:00` · `2026/03/24 00:00:00` |
| 40 | `fecha_finali_ejec_ord_trab` | FECHA FINALI EJEC ORD TRAB | text | 5.9% | 179 | Fecha de finalización de la orden. | `2026/03/14 00:00:00` · `2026/07/25 00:00:00` · `2026/07/31 00:00:00` |
| 41 | `dias_de_ejecucion_de_ordenes` | DIAS DE EJECUCION DE ORDENES | text | 0.0% | 17 | Días de ejecución de las órdenes. | `29` · `1` · `4` |
| 42 | `comentario_orden_trabajo` | COMENTARIO ORDEN TRABAJO | text | 5.8% | 924 | Comentario de la orden de trabajo. **Contiene escapes `_x000D_` de Excel.** | `CASOS SURA PERIODO D` · `PROEXEQUIAL:en respu` · `SEÑOR CASAS: con la ` |
| 43 | `caus_legal_ord_trab` | CAUS LEGAL ORD TRAB | text | 5.9% | 13 | Causal legal de la orden. **Nombre truncado.** | `9290 - FALLA EN EL C` · `9291 - NO HUBO FALLA` · `3758 - FALLA CAUSADA` |
| 44 | `func_legaliza_orden_trabajo` | FUNC LEGALIZA ORDEN TRABAJO | text | 5.9% | 7 | Funcionario que legaliza la orden. | `SADIDH` · `SUSANAV` · `DANNAG` |
| 45 | `agendamiento_visita` | AGENDAMIENTO VISITA | text | 0.0% | 1 | Agendamiento de visita. | `NO HAY VENTA FNB` |
| 46 | `agendamiento_vta_cruzada` | AGENDAMIENTO VTA CRUZADA | text | 0.0% | 1 | Agendamiento de venta cruzada. | `NO HAY VENTA FNB` |
| 47 | `estado_vta` | ESTADO VTA | text | 0.0% | 1 | Estado de la venta cruzada. | `NO HAY VENTA FNB` |
| 48 | `dias_agendamiento` | DIAS AGENDAMIENTO | text | 0.0% | 1 | Días de agendamiento. | `NO HAY VENTA FNB` |
| 49 | `interaccion` | INTERACCION | text | 0.0% | 1,248 | Tipo de interacción. | `182931122` · `184256241` · `182823584` |
| 50 | `telefono_solicitante` | TELEFONO SOLICITANTE | text | 10.0% | 1,070 | Teléfono del solicitante. **Dato sensible.** | `3146740054` · `3107479657 - 3107479` · `3137552198 - 3137552` |
| 51 | `telefono_suscriptor` | TELEFONO SUSCRIPTOR | text | 9.6% | 1,068 | Teléfono del suscriptor. **Dato sensible.** | `- 3226500008` · `3146740054` · `- 3117265059 - 0 - 3` |
| 52 | `fecha_de_venta` | FECHA DE VENTA | text | 62.0% | 383 | Fecha en que se vendió la póliza. Eje temporal distinto al de gestión. | `2026-04-30` · `2025-11-04` · `2022-03-31` |
| 53 | `minutos` | MINUTOS | text | 86.9% | 51 | Duración de la llamada en minutos. | `Usuario acepta los c` · `Usuario no contesta,` · `Usuario acepta los c` |
| 54 | `quien_autorizo` | QUIEN AUTORIZO | text | 98.4% | 18 | Quién autorizó la gestión. | `ANA MARIA CASTRO LOB` · `ANGEL CRESPO ROMERO` · `BETTY DEL CARMEN MAR` |

#### `clasificacion` — 40 filas

| # | Columna | Nombre original Excel | Tipo | Nulos | Distintos | Significado | Ejemplos |
| ---: | :--- | :--- | :--- | ---: | ---: | :--- | :--- |
| 1 | `gasera` | **GASERA** | text | 0.0% | 1 | Gasera a la que aplica la variante del catálogo. | `GasCaribe` |
| 2 | `variante` | **VARIANTE** | text | 0.0% | 40 | Texto tal como lo escribe el asesor. Clave del catálogo. | `no apto` · `sin registro` · `retenido` |
| 3 | `resultado_normalizado` | RESULTADO NORMALIZADO | text | 0.0% | 27 | Resultado canónico tras pasar por el catálogo `clasificacion`. | `no apto` · `sin registro` · `retenido` |
| 4 | `clasificacion` | CLASIFICACION | text | 0.0% | 2 | Clasificación de la solicitud. | `APTA` · `NO APTA` |

---

## 6. Catálogos de tipificación (dominios completos)

### 6.1 Resultado de la gestión (`estado` y equivalentes) por gasera

Cada gasera usa una columna distinta para el resultado, y **todas comparten el mismo
vocabulario de fondo** con diferencias de escritura:

| Gasera | Columna de resultado | Distintos | APTA (filas) | NO APTA (filas) | Sin catalogar (filas) | Nulos |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: |
| CEO | `ceo_inbound.estado` | 40 | 2.392 | 228 | **65** | 64 |
| Efigas | `efigas_outbound.estado` | 13 | 590 | 398 | **5** | 6 |
| Caribe Inbound | `caribe_inbound.estado` | 20 | 4.753 | 2.044 | **0** ✅ | 0 |
| Caribe Outbound | `caribe_outbound.estado` | 30 | 564 | 741 | **0** ✅ | 0 |
| GDO Inbound | `gdo_inbound.resultado_final` | 11 | 3.941 | 198 | **51** | 0 |
| GDO Outbound | `gdo_outbound.resultado_de_retencion` | 15 | 1.427 | 1.563 | **15** | 279 |
| Surtigas Inbound | `surti_inbound.estado` | 18 | 9.049 | 219 | **100** | 55 |
| Surtigas Outbound | `surti_outbound.estado` | 7 | 221 | 77 | **0** ✅ | 1 |

**Variantes distintas sin catalogar** (no filas): CEO **22**, Efigas **1**, Caribe **0** ✅
en ambas cabinas, GDO **4** (Inbound) y **5** (Outbound), Surtigas **11** (Inbound) y
**0** (Outbound). **Total: 43 variantes** que no resuelven contra el catálogo.

> En total quedan **236 filas** (65 + 5 + 51 + 15 + 100) cuyo resultado no se clasifica
> con el catálogo actual. Un 0.5% del volumen, pero **concentrado en CEO y Surtigas**,
> que son las gaseras con más tráfico.

> La columna `estado` de GDO Inbound está **100% vacía**: el resultado real está en
> `resultado_final`. Lo mismo aplica a `gdo_outbound.estado` (7.8% nulo) frente a
> `resultado_de_retencion` (8.5% nulo).

#### 6.1.1 Los 4 resultados APTA canónicos (decisión D-01, ya implementada)

> ⚠️ **Los 4 son CONCEPTOS, no cadenas de texto.** Son un conjunto **cerrado** de 4.
> Las **variantes** (las formas en que el asesor lo escribe) son un conjunto **abierto**
> e ilimitado: `cancelada`, `cancelad`, `cncelado`, `canceladoo`… El catálogo de
> abajo es una **foto del 19-oct-2026**, no un universo. Ver `09_Normalizacion_y_Clasificacion.md` §1.2.

La tabla `clasificacion` ya distingue **exactamente 4 resultados canónicos** entre sus
17 variantes APTA registradas hasta hoy — que son exactamente los 4 definidos en la
decisión **D-01**:

| Resultado canónico | Variantes que colapsan en él | Filas afectadas |
| :--- | :---: | ---: |
| `cancelado` | 2 | ~1,900 |
| `cancelado + venta` | 6 | ~1,100 |
| `cancelado + reintegro` | 6 | ~950 |
| `retenido` | 3 | ~3,100 |
| **Total** | **17** | — |

> **D-01 y D-02 están implementadas en la base de datos.** La columna
> `resultado_normalizado` de `gestion_diaria.clasificacion` produce exactamente estos
> 4 valores, y `Retenido` y `Cancelado` son valores separados. Ver el documento
> `09_Normalizacion_y_Clasificacion.md` para el algoritmo propuesto.

#### 6.1.2 Asimetría de la normalización actual

| Clasificación | Variantes | Corregidas | Literales (typo conservado) |
| :--- | ---: | ---: | ---: |
| **APTA** | 17 | **13** | 4 |
| **NO APTA** | 23 | **0** | **23** |

**El catálogo corrige los errores de escritura solo en los resultados APTA.** En los NO
APTA el typo se conserva tal cual: `no tiene resursos`, `no tiene resursus`,
`no es proteceso de retencion`, `retnido` (este sí corregido, por ser APTA).

> Esto es coherente con el objetivo de **D-03** (un error no puede convertir una llamada
> apta en no apta): el esfuerzo se puso donde el error era costoso. El lado NO APTA
> quedó sin normalizar, y por eso los NO APTA tienen 23 normalizados distintos en vez
> de un catálogo cerrado.

#### 6.1.3 Variantes que casi caen en el catálogo (fallos por un espacio o una letra)

> **Muestra del día, no lista cerrada.** El espacio de variantes es abierto (§1.2 del
> doc 09): estas son las que se detectaron hoy, y mañana habrá otras. Lo relevante no
> es enumerarlas, sino que el mecanismo de detección y aprendizaje las absorba.

Estas **no están en el catálogo** pese a que el concepto sí existe catalogado:

| Variante no catalogada | Gasera | Filas | Concepto catalogado equivalente |
| :--- | :--- | ---: | :--- |
| `cancelado/reintegro` | CEO | 26 | `cancelado /reintegro` (con espacios) — **mismo concepto, falla por el `/`** |
| `cancelado/reintegro` | GDO Outbound | 1 | idem |
| `cancelada + reintegro` | CEO | 3 | `cancelado + reintegro` |
| `cancelada previa` | CEO | 4 | `cancelado previa` / `cancelacion previa` |
| `retnida` | Efigas | 5 | `retenida` / `retnido` |
| `no es proteceso de retención` | Caribe Outbound | 2 | `no es proceso de retencion` |
| `venta nueva` / `nueva venta` | Surtigas | 51 + 6 | — (mismo concepto, dos textos) |
| `llamada caida` / `caida de llamada` | CEO / Surtigas | 4 / 1 / 6 | — (mismo concepto, tres textos) |
| `datos incompletos` / `datos incompleto` / `datos incompeto` | CEO | 5 / 1 / 1 | — |

> **El caso `cancelado/reintegro` es el más grave:** 26 filas de CEO que deberían ser
> APTA quedan sin clasificar **solo por un espacio alrededor de la barra**. `normalizar_texto`
> normaliza el `+` pero no la `/`.

#### 6.1.4 Conceptos APTA que el algoritmo de corrección debe tratar con cuidado

| Variante ambigua | Gasera | Gasera | Por qué es ambigua |
| :--- | :--- | ---: | :--- |
| `cancelacion` | CEO | 2 | ¿"cancelación previa" (NO APTA) o "cancelado" (APTA)? |
| `reintegro` | CEO | 1 | ¿"cancelado + reintegro" (APTA) o un reintegro suelto? |
| `devolucion` | CEO | 1 | ¿"cancelado + devolución de primas" (NO APTA)? |
| `cancelado/devolucion de primas` | Surtigas | 14 | NO APTA, pero se parece a `cancelado + reintegro` (APTA) |

> **Zona de peligro para la corrección automática:** estos cuatro conceptos son los
> que el Paso 5 del algoritmo (coincidencia aproximada por componentes) puede convertir
> erróneamente. Deben ir a `POR_REVISAR`, no resolverse solos.

#### 6.1.5 Estados con negación (riesgo R-04)

| Gasera | Valores con negación | Filas |
| :--- | :--- | ---: |
| CEO | `NO APTO`, `NO APLICA`, `NO ATENDEMOS EL SEGURO`, `NO TIENE SEGUROS ACTIVOS`, `NO PTO` | 104, 30, 1, 1, 1 |
| Efigas | `NO APTO`, `NO APLICA`, `NO CONTACTO` | 9, 1, 387 |
| Caribe | `NO APTO`, `NO APLICA`, `SIN REGISTRO`, `NO CONTACTO`, `NO ES PROCESO DE RETENCION`, `NO TIENE…` | 84, 97, 1.818, 577, 32, … |
| GDO | `NO APTO`, `NO APLICA`, `NO CONTACTO`, `NUNCA DESEA ADQUIRIR EL SEGURO` | 73, 88, 1.507, 3 |
| Surtigas | `NO APTO`, `NO APLICA` | 101, 80 |

> Todos los valores con negación **ya están en el catálogo como NO APTA**, salvo
> `NO ATENDEMOS EL SEGURO`, `NO TIENE SEGUROS ACTIVOS`, `NO PTO` (1 fila cada uno en CEO).
> Como el catálogo los resuelve en el **Paso 2 (búsqueda exacta)**, nunca llegan al
> Paso 4 de bloqueo de negaciones. Eso confirma que el orden del algoritmo propuesto
> en el documento 09 es correcto.

### 6.1.6 Nota sobre la cardinalidad de los catálogos

| Catálogo | Cardinalidad | Naturaleza |
| :--- | :--- | :--- |
| Resultados APTA (D-01) | **4** | Conceptos. **Cerrado**, definido por el negocio |
| Resultados NO APTA | ~26 | Conceptos. **Cerrado** (aunque hoy el catálogo los tenga como literales sin consolidar) |
| Variantes de un resultado | **Ilimitadas** | Formas escritas. **Abierto**: se descubre y se aprende |
| Motivos (`gdo_inbound.subtipificacion`) | 52 hoy | **Abierto**: cada gasera aporta conceptos nuevos |

> El número "43 variantes sin catalogar" del §4.3 y del doc 04 es un **snapshot**: mide
> el rezago del catálogo frente a lo escrito **hasta hoy**, no el tamaño del problema.

### 6.2 Maestro de motivos (`gdo_inbound.subtipificacion`, 52 valores)

Es el **único catálogo de motivos jerárquico y numerado** que existe en la base de datos
y el mejor candidata para ser el vocabulario unificado del proyecto.

| Motivo | Filas |
| :--- | ---: |
| 1.11 Usuario no le interesa la cobertura | 2.143 |
| 1.3 Sin capacidad económica | 385 |
| 13.1 Credito finalizado | 352 |
| 1.12 Desconocimiento de la protección factura… | 338 |
| Credito finalizado | 267 |
| 3.1 Solicitud de Información adicional del s… | 156 |
| 4.1 Información de siniestro | 80 |
| 1.2 Tiene otro seguro | 58 |
| 1.1 Inconformidad en el servicio | 49 |
| 1.10 Traslado de predio | 47 |
| NA | 35 |
| NO APTO | 20 |
| 2.1 Cancelación / Devolución de prima - Irrevocable | 19 |
| INFORMACION DEL SEGURO | 18 |
| Cancelación de seguro / Crédito finalizado | 15 |
| 1.7 Afiliación autorizada por tercero | 10 |
| NO APLICA | 10 |
| SEGURO NO AUTORIZADO | 7 |
| MODIFICACION DE POLIZA | 7 |
| Devolución de prima - Irrevocable | 7 |
| 4.2 Dudas en la prestación de servicio | 6 |
| CREDITO FINALIZADO | 4 |
| Cancelación de seguro / Usuario no autorizó | 3 |
| no lo autorizo | 3 |
| ASEGURADO FALLECIDO | 3 |
| 3. Información sobre seguro activo | 2 |
| N/A | 2 |
| Asegurado fallecido | 2 |
| VOLVER A LLAMAR | 2 |
| Traslado de predio | 2 |
| 1.4 Aumento de tarifa | 2 |
| 1.5 Mala información del asesor | 2 |
| Inconformidad con el seguro | 2 |
| MANTIENE LA PROTECCION | 2 |
| SOLICITUD DE SINIESTRO | 1 |
| Devolución de prima | 1 |
| SE LE EXPLICA LA COBERTURA Y MANTIENE LA PR… | 1 |
| USUARIO NUNCA TOMO LA POLIZA Y NO SABIA QUE… | 1 |
| 1.10 traslado de predio | 1 |
| Usuario no autorizó | 1 |
| NO TIENE RESURSOS | 1 |
| Continua con la proteccion | 1 |
| 1.1 Finalizo credito | 1 |
| CANCELACION PREVIA\| | 1 |
| REPORTE DE SINIESTRO | 1 |
| 1.9 No conoce al asegurado | 1 |
| PAGO DE SINIESTRO // RADICADO 680174 //ABRIL | 1 |
| Demora en respuesta de siniestro | 1 |
| Cancelación de seguro / Tiene otro seguro | 1 |
| 5.1 Interesado en compra de seguro | 1 |
| 510413 | 1 |
| FINALIZACION DE CREDITO | 1 |

> **Observación:** el catálogo mezcla el código numérico (`1.11`) con su texto
> (`1.11 Usuario no le interesa la cobertura`) y con la versión sin código
> (`Credito finalizado`). Hay **duplicados semánticos**:
> `1.10 Traslado de predio` / `Traslado de predio`,
> `1.1 Inconformidad en el servicio` / `1.1 Finalizo credito` (código reasignado),
> `2.1 Cancelación / Devolución de prima - Irrevocable` / `Devolución de prima - Irrevocable`,
> `ASEGURADO FALLECIDO` / `Asegurado fallecido`, `NA` / `N/A`.
> Limpiar este catálogo es la tarea previa a usarlo como maestro.

### 6.3 Motivos en texto libre (sin catálogo)

| Gasera | Columna | Distintos | Nulos | Observación |
| :--- | :--- | ---: | ---: | :--- |
| Caribe | `subtipificacion` | 355 | 28.5% | Texto libre. Valores dominantes: `MANTIENE LA COBERTURA` (657), `NO QUIERE EL SERVICIO` (665), `NO ESTA INTERESADO` (196)… con variantes de mayúsculas y tildes |
| GDO Outbound | `tipifiacion_de_pqr` | 184 | 8.5% | Demasiado granular para ser un maestro |
| GDO Informativo | `desc_clase_comentario` | 10 | 22.3% | Aplicable |
| GDO Informativo | `desc_tipo_comentario` | 74 | 22.3% | Aplicable |
| Surtigas QR | `clasificacion` | 3 | 0% | Aplicable |

> Los 355 valores de `caribe_inbound.subtipificacion` **se pueden mapear al catálogo de
> GDO** (que tiene 52): `MANTIENE LA COBERTURA` → equivalente a `MANTIENE LA PROTECCION`;
> `NO QUIERE EL SERVICIO` → `1.11 Usuario no le interesa la cobertura`;
> `NO TIENE RECURSOS` → `1.3 Sin capacidad económica`;
> `TIENE OTRO SEGURO` → `1.2 Tiene otro seguro`. Es el mapeo que propone P-19.

### 6.4 `gestion_diaria.clasificacion` — catálogo completo

| Columna | Tipo | Descripción |
| :--- | :--- | :--- |
| `gasera` | text | Gasera a la que aplica la variante. **Solo contiene `GasCaribe`** (40 de 40 filas) |
| `variante` | text | Texto tal como lo escribe el asesor, ya normalizado con `normalizar_texto` |
| `resultado_normalizado` | text | Valor canónico. 27 valores distintos (4 APTA + 23 NO APTA literales) |
| `clasificacion` | text | `APTA` (17) / `NO APTA` (23) |

**Llave primaria:** `(gasera, variante)` — confirmada con el DDL real.

**Mapa completo variante → normalizado → clasificación:**

| Variante | Normalizado | Clasificación |
| :--- | :--- | :---: |
| `cancelada` | `cancelado` | APTA |
| `cancelado` | `cancelado` | APTA |
| `cancelacion + reintegro` | `cancelado + reintegro` | APTA |
| `cancelacion+reintegro` | `cancelado + reintegro` | APTA |
| `cancelado + reintegro` | `cancelado + reintegro` | APTA |
| `cancelado +reintegro` | `cancelado + reintegro` | APTA |
| `cancelado /reintegro` | `cancelado + reintegro` | APTA |
| `cancelado+reintegro` | `cancelado + reintegro` | APTA |
| `cancelada + venta` | `cancelado + venta` | APTA |
| `cancelada +venta` | `cancelado + venta` | APTA |
| `cancelada+venta` | `cancelado + venta` | APTA |
| `cancelado + venta` | `cancelado + venta` | APTA |
| `cancelado +venta` | `cancelado + venta` | APTA |
| `cancelado+venta` | `cancelado + venta` | APTA |
| `retenida` | `retenido` | APTA |
| `retenido` | `retenido` | APTA |
| `retnido` | `retenido` | APTA |
| `cancelacion previa` | *(literal)* | NO APTA |
| `cancelado + reembolso` | *(literal)* | NO APTA |
| `cancelado por job` | *(literal)* | NO APTA |
| `cancelado previa` | *(literal)* | NO APTA |
| `informacion` | *(literal)* | NO APTA |
| `informacion errada` | *(literal)* | NO APTA |
| `informativo` | *(literal)* | NO APTA |
| `no aplica` | *(literal)* | NO APTA |
| `no apto` | *(literal)* | NO APTA |
| `no contacto` | *(literal)* | NO APTA |
| `no contesta` | *(literal)* | NO APTA |
| `no es proceso de retencion` | *(literal)* | NO APTA |
| `no es proteceso de retencion` | *(literal)* | NO APTA |
| `no hubo contacto` | *(literal)* | NO APTA |
| `no tiene activos seguros` | *(literal)* | NO APTA |
| `no tiene recursos` | *(literal)* | NO APTA |
| `no tiene resursos` | *(literal)* | NO APTA |
| `no tiene resursus` | *(literal)* | NO APTA |
| `numero equivocado` | *(literal)* | NO APTA |
| `sin registro` | *(literal)* | NO APTA |
| `telefono apagado` | *(literal)* | NO APTA |
| `tercero` | *(literal)* | NO APTA |
| `ya fue cancelado` | *(literal)* | NO APTA |

---

## 7. Resumen de hallazgos del diccionario

| # | Hallazgo | Severidad | Dónde | Volumen |
| ---: | :--- | :---: | :--- | ---: |
| H-23 | `operador` es la empresa operadora, no una persona; el asesor individual solo existe en GDO | 🔴 | 6 tablas | 43.398 filas afectadas |
| H-24 | Sangrado de columnas: valores de una columna en otra | 🔴 | 5 tablas | 1.589 filas |
| H-25 | Causa raíz: celdas del Excel con columnas pegadas por tabulador | 🔴 | 5 tablas | 45 celdas |
| H-26 | Escape `_x000D_` de Excel dentro del texto | 🟠 | 7 tablas | 740 celdas |
| H-27 | `base` es la fecha de carga del lote, nunca la de gestión | 🟠 | 3 tablas | 999 filas Efigas |
| H-28 | `subtipificacion` vacía al 100% en CEO | 🟠 | `ceo_inbound` | 2.749 filas |
| H-29 | `estado` vacía al 100% en GDO Inbound (el resultado está en `resultado_final`) | 🟠 | `gdo_inbound` | 4.190 filas |
| H-30 | `localidad` vacía al 97–100% en CEO, Efigas y Caribe Outbound | 🟠 | 3 tablas | 9.968 filas |
| H-31 | 43 variantes de estado sin catalogar (22 CEO, 11 Surtigas, 9 GDO, 1 Efigas) | 🔴 | 4 tablas | 236 filas |
| H-32 | `normalizar_texto` no normaliza la `/` → 27 filas APTA quedan sin clasificar | 🔴 | CEO, GDO | 27 filas |
| H-34 | No existe entorno de pruebas ni el usuario tiene permiso de escritura | 🟠 | instancia | 48.036 filas en riesgo |
| H-35 | Columnas de PII en 13 tablas | 🔴 | 13 tablas | — |

---

## 8. Impacto en otros documentos

| Documento | Cambio requerido |
| :--- | :--- |
| **02 Mapeo Origen-Destino** | Validar el mapeo **por archivo**, no asumirlo: el sangrado de H-24/H-25 demuestra que la posición de las columnas cambia entre gaseras |
| **03 Modelo de Datos (ERD)** | La dimensión de asesor solo aplica a GDO; para las otras 4 la granularidad es la empresa operadora. `anio` debe separarse en `anio_gestion` y `anio_venta` |
| **Normalizacion_y_Clasificacion** | §11 "Datos pendientes" queda **cerrado**: los 4 resultados APTA ya existen, el DDL real está verificado y la lista de no aptos está completa |
| **010 Registro de Decisiones** | Cerrar A-09 (clasificación por gasera: el catálogo es por gasera pero la clasificación es idéntica) y S-03 (columnas por hoja) |
