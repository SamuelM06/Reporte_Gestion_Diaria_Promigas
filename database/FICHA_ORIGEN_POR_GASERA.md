# 📋 Ficha de Origen por Gasera — Verificada contra los Archivos

**Proyecto:** Reporte de Gestión Diaria - Retención Promigas
**Verificado contra:** archivos reales del equipo (21-oct-2026)
**Estado:** ✅ **Estructura verificada.** Pendiente solo la decisión de estrategia de carga (A-16).

> 🔴 **Regla de oro:** el origen es **Excel en OneDrive/SharePoint**, escrito a mano por
> los asesores. La base de datos debe conservar **la misma estructura** que los Excel
> (D-13): una tabla por libro+hoja, con las mismas columnas.
>
> 📌 Detalle técnico columna por columna: `context/Analisis/14_Estructura_Origen_Excel.md`.

---

## 0. Ruta madre

```text
<OneDrive>\Team Experiencia al Cliente - Promigas\
  └─ Retención\Promigas\
       └─ Gestión diaria Promigas Inb -Outbound\      ← 📂 RUTA MADRE (5 gaseras)
```

| Subcarpeta | Contenido | Estado |
| :--- | :--- | :--- |
| `CEO\` | Archivo de gestión diaria + carpeta `INFORME` | ✅ |
| `EFIGAS\` | Archivo de gestión diaria | ✅ |
| `GAS CARIBE\` | Inbound + Outbound + `Activas Caribe\` + `Gestion Mes\` | ✅ |
| `GDO\` | `Informe\` (archivo vivo), `Gestión Inbound-Outbound\`, `Solicitud de cancelación...\` | ✅ |
| `SURTIGAS\` | Inbound (2 libros) + Outbound + `JULIO - AGOSTO 2026\` + `Informe\` | ✅ |
| *(raíz)* | `Abandono 2-10-2026.xlsx`, `TARIFA VALOR COMPLETOS (1).xlsx` | 🔴 No documentado, ver §7 |
| `Valores de Protecciones\` | `TARIFA VALOR COMPLETOS.xlsx`, `VALOR DE PROTECCIONES SERVIPROTECCIÓN.xlsx` | 🔴 Maestros de tarifa |
| `Tendencia LLamadas OCM\` | `Base.xlsx` | 🔴 Fuera del alcance actual |

---

## 1. CEO — Compañía Energética del Cauca

**Cabina:** solo **INBOUND** · **Archivo:** `CEO\Gestion diaria CEO.xlsx`
(1.496.311 bytes · modificado 21-oct-2026 16:25)

| Hoja | Columna fecha (guía mes) | Columna resultado | Contrato | Destino BD | Cargar |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Gestion Diaria Inbound Ceo` | **`FECHA INGRESO LLAMADA`** | **`Resultado de retencion`** | `CONTRATO` | `ceo_inbound` | ✅ 2026 |
| `Abandono` | **`Fecha de llamada`** | `RESULTADO FINAL` | `CONTRATO` | `ceo_abandono` | ✅ 2026 |
| `enero a mayo 2025` | `FECHA DE LLAMADA` | `ESTADO` | `CONTRATO` | — | ❌ **solo 2025** |
| `Hoja1` | `FECHA INGRESO LLAMADA` | `Resultado de retencion` | `CONTRATO` | — | ⚠️ **verificar**: 20 cols vs 30 de la hoja principal, datos de 2026-09-09 |
| `Datos` | — | — | — | — | 📖 catálogo de `RESULTADO RETENCIÓN` |
| `CANAL , OPERADORES, TIPIFICACIO` | — | — | — | — | 📖 catálogos (PQR / Retención / Canales) |
| `SINIESTRO CEO `, `LINEAS DE ATENCION`, `PRACTISEGURO`, `APLICATIVOS`, `ACOMULADO`, `Hoja2` | — | — | — | — | ❌ no son gestión diaria |

**Estructura de `Gestion Diaria Inbound Ceo`** (30 encabezados, 54 columnas — hay 2 columnas
vacías entre la fecha y `CONTRATO`):

```text
FECHA INGRESO LLAMADA | (vacía) | (vacía) | CONTRATO | TELEFONO | DOCUMENTO | USUARIO |
ASEGURADORA | PRODUCTO | OBSERVACIÓN | Resultado de retencion | PROCESOS EXTERNOS |
TIPO DE CONTACTO | Gestor de retencion | Operador | Canal | Fecha de venta | Asesor de venta |
Tipifiacion de la retencion | RESPUESTA DE GESTION | (vacía) | Soporte | OBSERVACIÓN (2ª) |
QUIEN AUTORIZA | CEDULA | RESPONSABLE DEL PAGO O TITULAR DE LA CUENTA | ESTADO |
FEHCA DE CANCELACION | ANS | DEVOLUCION DE PRIMAS
```

> ⚠️ **CEO tiene las 3 columnas de resultado**: `Resultado de retencion` (la buena),
> `ESTADO` (que hoy se llena con "NO APTO") y `Tipifiacion de la retencion`.
> **Usar `Resultado de retencion`.**
> 💡 `Gestor de retencion` = **asesor persona** (Sharith Guevara, Madiley Vasquez…).
> `Operador` = empresa.

---

## 2. EFIGAS

**Cabina:** solo **OUTBOUND** · **Archivo:** `EFIGAS\Gestión Diaria Outbound-Efigas.xlsx`
(3.347.386 bytes · modificado 21-oct-2026 16:29)

| Hoja | Columna fecha (guía mes) | Columna resultado | Contrato | Destino BD | Cargar |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Base` | **`FECHA DE EJECUCION`** | **`ESTADO`** | `CODIGO CONTRATO` | `efigas_outbound` | ✅ 2026 |
| `Hoja1` | `FECHA DE BASE g` | `ESTADO` | `CODIGO CONTRATO` | — | ⚠️ verificar (117 filas, datos abr-2026) |
| `activos` | — | — | `CONTRATO` | — | ❌ **maestro de pólizas activas** (9.565 filas), no es gestión |
| `CANAL,TIPIFICA, ` | — | — | — | — | 📖 catálogos |
| `ACUMULADO`, `Hoja2` | — | — | — | — | ❌ vacías |

**Estructura de `Base`** (66 columnas; las 31 primeras):

```text
FECHA DE BASE | No. SOLICITUD | CODIGO CONTRATO | No. PRODUCTO | ASEGURADORA | LINEA PRODUCTO |
# POLIZA | VALOR PRIMA | No. CEDULA ASEGURADO | TITULAR FACTURA | No. CEDULA TITULAR |
OBSERVACIÓN | TELEFONO 1 | DIRECCIÓN | DEPARTAMENTO | CIUDAD | Tipifiacion de PQR |
ASEGURADORA | OPERADOR | CANAL | PRODUCTO | TIPO DE CONTACTO | MOTIVO | ESTADO | OBSERVACION |
FECHA DE EJECUCION | FECHA DE VENTA | ASESOR DE VENTA | LLAMADA #1 | GESTOR | CORREO | …(35 más)
```

> 🔴 **`FECHA DE BASE` es la fecha de carga del lote, NO la de gestión.** ✅ **Confirmado por
> negocio (21-oct-2026, D-16):** la fecha de gestión es **`FECHA DE EJECUCION`** (el
> momento de la llamada). Evidencia en el archivo:
> * 1.595 de 1.764 filas (90.5%) tienen `BASE` ≠ `EJECUCION`; el desfase llega a **273 días**.
> * 72 lotes distintos en `FECHA DE BASE`, con formatos mezclados (`2026-04-20 00:00:00`,
>   `13/01/2026`, `01/092025`).
> * Usar `FECHA DE BASE` **movería 526 filas (29.8%) al mes equivocado**: el mes más
>   cargado por ejecución es **sep-2026 (169)**; por base sería **oct-2025 (157)**.
>
> ⚠️ Efigas trae **3 columnas de resultado**: `ESTADO` (la buena), `MOTIVO` (motivo en
> texto libre) y `Tipifiacion de PQR` (PQR, no retención).

---

## 3. GDO — Gases de Occidente

**Cabina:** INBOUND + OUTBOUND + PQRS + ABANDONO
**Archivo vivo:** `GDO\Informe\VALIDACION INFORMACION GDO- 24 de Junio 2026.xlsx`
(10.855.422 bytes · modificado 21-oct-2026 16:31)

| Hoja | Columna fecha (guía mes) | Columna resultado | Contrato | Destino BD | Cargar |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `GESTIÓN INBOUND` | **`FECHA DE LLAMADA`** (+ `Mes`) | **`RESULTADO FINAL`** | `CONTRATO` | `gdo_inbound` | ✅ 2026 |
| `OUT` | **`FECHA EJECUCION`** (+ `MES`) | **`Resultado de retencion`** | `CONTRATO` | `gdo_outbound` | ✅ 2026 |
| `INFORMATIVO` | `FECHA REGI` (+ `Hora`) | `Resultado` | `CONTRATO` | `gdo_informativo` | ⚠️ **es bitácora, no maestro PQRS** |
| `PQR HDI - SURA-ALFA` | `FECHA REGISTRO SOLICITUD` | — | `CONTRATO` | `gdo_pqrs` | ✅ 2026 |
| `PQRS ESCRITAS` | `FECHA DE RAD,SOLICITANTE-GDO` | `ESTADO` | `CONTRATO ` | `gdo_pqrs_escritas` | ✅ 2026 (modelo de referencia: ANS completo) |
| `abandono` | `Fecha de llamada` (+ `Mes`) | `RESULTADO FINAL` | `CONTRATO` | `gdo_abandono` | ⚠️ calidad desigual |
| `TD Inbound`, `TD INB 2`, `Hoja2`, `TD aseguradora`, `Informativos vs pqrs`, `Td infr`, `Td informativo falta BI`, `Tabulación`, `Hoja1` | — | — | — | — | ❌ **tablas dinámicas, no son datos** |

**GDO es la gasera mejor estructurada** y la única con `NOMBRE_ASESOR_RETENCION`
(persona). `SUBTIPIFICACION` (52 valores) es el **vocabulario maestro de motivos**.

**Otros archivos de GDO** (fuera del archivo vivo):

| Archivo | Hojas | ¿Cargar? |
| :--- | :--- | :--- |
| `GDO\Gestión Inbound-Outbound\GESTION_INBOUND_GDO_TRASLADO_POR_COMPETENCIA.xlsx` | `ACOMULADO Inb-Out` (17 cols, 1.526 filas), `Hoja1`, `Informativos reiterativo`, `INFORMACION` | ⚠️ traslados por competencia — **fuera del alcance actual** |
| `GDO\Gestión Inbound-Outbound\Gestión de Abandono GDO 2026.xlsx` | `ABANDONO Inb` (1.762), `ABANDONO FUERA DE HORARIO` (12), `Prueba - No Usar` | ⚠️ solo `ABANDONO Inb`; `Prueba - No Usar` está explícitamente descartada |
| `GDO\Gestión Inbound-Outbound\Acomulado Mes\01_Marzo.xlsx` … `06_Agosto.xlsx` | acumulado mensual | ⚠️ duplican `GESTIÓN INBOUND` |
| `GDO\BASE ACTIVAS.xlsx` | maestro de pólizas | ❌ |
| `GDO\Informe\VALIDACION INFORMACION GDO- 22 Abril 2026.xlsx` | versión anterior | ❌ sustituida |

---

## 4. GAS CARIBE

### 4.1 Inbound — `GAS CARIBE\Gestión diaria Inbound Caribe.xlsx`
(2.761.624 bytes · modificado 21-oct-2026 16:45)

| Hoja | Columna fecha (guía mes) | Columna resultado | Contrato | Cargar |
| :--- | :--- | :--- | :--- | :--- |
| `ENERO 2026` | `fecha de atencion` | `ESTADO` | `CONTRATO` | ✅ 2026 |
| `FEBRERO 2026` | `fecha de atencion` | `Resultado de retencion` | `CONTRATO` | ✅ 2026 |
| `MARZO 2026` | `fecha de atencion` | `Resultado de retencion` | `CONTRATO` | ✅ 2026 |
| `ABRIL 2026` | `FECHA DE ATENCION` | `RESULTADO DE RETENCION` | `CONTRATO` | ✅ 2026 |
| `MAYO 2026` | `FECHA DE ATENCION` | `RESULTADO DE RETENCION` | `CONTRATO` | ✅ 2026 |
| `JUNIO 2026` | `FECHA DE ATENCION` | `RESULTADO DE RETENCION` | `CONTRATO` | ✅ 2026 |
| `JULIO 2026` | `FECHA DE ATENCION` | `RESULTADO DE RETENCION` | `CONTRATO` | ✅ 2026 |
| `AGOSTO 2026` | `FECHA DE ATENCION` | `RESULTADO DE RETENCION` | `CONTRATO` | ✅ 2026 |
| `SEPTIEMBRE 2026 ` | `FECHA DE ATENCION` | `RESULTADO DE RETENCION` | `CONTRATO` | ✅ 2026 |
| `OCTUBRE 2026 ` | `FECHA DE ATENCION` | `RESULTADO DE RETENCION` | `CONTRATO` | ✅ 2026 |
| `ABANDONO` | `Fecha de llamada` | `RESULTADO FINAL` | `CONTRATO` | ✅ 2026 |
| `enero`…`noviembre `, `Diciembre` *(solo mes = 2025)* | `FECHA DE LLAMADA` / `fecha de atencion` | `ESTADO` | `CONTRATO` | ❌ **2025** |
| `Rellamadas` | `FECHA DE LLAMADA` | `ESTADO FINAL ` | `CONTRATO` | ⚠️ subconjunto de llamadas |
| `Datos`, `CANALES , OPERADORES, TIPIFICAC`, `SINIESTRO CARIBE `, `Hoja1` | — | — | — | ❌ catálogos / no es gestión |

> 🔴 **El nombre de la columna fecha y de la columna resultado CAMBIAN entre hojas**
> (`fecha de atencion` vs `FECHA DE ATENCION`; `ESTADO` vs `RESULTADO DE RETENCION`).
> El lector debe resolverlos **por hoja**, no por analogía.
>
> 🔴 **`AGOSTO 2026`: la columna `LOCALIDAD` trae `#VALUE!`** (error de Excel heredado).
>
> 📌 **El nombre de la hoja no siempre coincide con el mes del dato**: la hoja
> `ENERO A MARZO` de Surtigas contiene datos de diciembre 2025. **El filtro es por
> columna de fecha**, no por nombre de hoja.

### 4.2 Outbound — `GAS CARIBE\Gestión diaria Outbound-Gases del caribe.xlsx`
(697.088 bytes · modificado 21-oct-2026 16:43)

| Hoja | Columna fecha (guía mes) | Columna resultado | Contrato | Cargar |
| :--- | :--- | :--- | :--- | :--- |
| `Outbound` | **`Fecha de llamada`** (también `FECHA DE LLAMADA`) | **`Resultado de retencion`** | `CONTRATO` | ✅ 2026 |
| `Tipificaciones` | — | — | — | ❌ catálogos |

Además trae `MES` como columna directa → el mes es inmediato sin parsear la fecha.

---

## 5. SURTIGAS

### 5.1 Inbound — enero a junio

**Archivo:** `SURTIGAS\SURTIGAS ARCHIVO RECUPERADO - Copia.xlsx`
(1.582.374 bytes · modificado 16-oct-2026 15:45) — *sustituye al archivo que se dañó*

| Hoja | Columna fecha (guía mes) | Columna resultado | Contrato | Cargar |
| :--- | :--- | :--- | :--- | :--- |
| `ENERO A MARZO ` | **`FECHA DE LLAMADA`** | **`RESULTADO FINAL`** | `CONTRATO` | ✅ 2026 |
| `ABRIL` | **`FECHA DE LLAMADA`** | **`RESULTADO FINAL`** | `CONTRATO` | ✅ 2026 |
| `MAYO ` | **`FECHA DE LLAMADA`** | **`RESULTADO FINAL`** | `CONTRATO` | ✅ 2026 |
| `JUNIO` | **`FECHA DE LLAMADA`** | **`RESULTADO FINAL`** | `CONTRATO` | ✅ 2026 |

Estructura tipo GDO: `CABINA`, `FECHA DE LLAMADA`, `SOLICITUD DE POLIZA`,
`FECHA DE LEGALIZACION`, `ESTADO DE SOLICITUD`, `Medio de ejecución `,
`ENTIDAD_FACTURACION`, `NOMBRE_CLIENTE`, `IDENTIFICACION_USUARIO`, `CONTRATO`,
`LOCALIDAD`, `TELEFONO1`, `TIPO_CONTACTO`, `CANAL`, `FECHA_VENTA`, `PRODUCTO_1`,
`NOMBRE_ASESOR_RETENCION`, `CATEGORIA`, `CATEGORIA_DETALLE`, `SUBTIPIFICACION`,
`OBSERVACIONES`, **`RESULTADO FINAL`**, `CORREO`, `ESTADO`, `FEHCA DE CANCELACION`,
`ANS`, `DEVOLUCION DE PRIMAS`.

> 💡 `CABINA` viene **poblada** (`Inbound`) — en Surtigas sí sirve para filtrar.

### 5.2 Inbound — julio en adelante

**Archivo:** `SURTIGAS\JULIO - AGOSTO 2026\Gestión diaria Inbound Surtigas.xlsx`
(1.273.472 bytes · modificado 21-oct-2026 16:51)

| Hoja | Columna fecha (guía mes) | Columna resultado | Contrato | Cargar |
| :--- | :--- | :--- | :--- | :--- |
| `JULIO` | **`FECHA DE LLAMADA`** | **`RESULTADO FINAL`** | `CONTRATO` | ✅ 2026 |
| `Agosto` | **`FECHA DE LLAMADA`** | **`RESULTADO FINAL`** | `CONTRATO` | ✅ 2026 |
| `SEPTIEMBRE` | **`FECHA DE LLAMADA`** | **`RESULTADO FINAL`** | `CONTRATO` | ✅ 2026 |
| `OCTUBRE` | **`FECHA DE LLAMADA`** | **`RESULTADO FINAL`** | `CONTRATO` | ✅ 2026 |
| `ABANDONO` | `Fecha de llamada` | `RESULTADO FINAL` | `CONTRATO` | ✅ 2026 |
| `Filtros`, `LINEAS - REINTEGROS DE PRIMAS`, `Hoja1` | — | — | — | ❌ catálogos / guiones |

> ⚠️ `OCTUBRE`: la columna 5 se llama **`CA`** en vez de `ESTADO DE SOLICITUD`.
> ⚠️ `Agosto`: dos columnas **sin nombre** (posiciones 33 y 34).
> 📌 La carpeta se llama `JULIO - AGOSTO 2026` pero el archivo ya trae **septiembre y
> octubre**: la carpeta no refleja el contenido.

### 5.3 Outbound — `SURTIGAS\Gestión diaria Outbound SURTIGAS.xlsx`
(3.000.936 bytes · modificado 21-oct-2026 16:51)

| Hoja | Columna fecha (guía mes) | Columna resultado | Contrato | Cargar |
| :--- | :--- | :--- | :--- | :--- |
| `salva factura ` | `fecha de lllamada` *(typo)* | `ESTADO` | `Código Contrato` | ✅ 2026 |
| `reclamos` | `Fecha de llamada` | `Estado` | `Código Contrato` | ✅ 2026 |
| `cancelaciones ` | `Fecha de llamada` | `Resultado de retencion` | `CONTRATO` | ✅ 2026 |
| `tipificacion , CANALES`, `Hoja1` | — | — | — | ❌ catálogos |

### 5.4 QR — `SURTIGAS\Informe\Gestión Inbound -Outbound-QR.xlsx`
(9.580.606 bytes · modificado 22-sep-2026 10:03)

| Hoja | Columna fecha | Columna resultado | Contrato | Cargar |
| :--- | :--- | :--- | :--- | :--- |
| `Base` | `FECHA DE EJECUCION` (+ `BASE`) | `ESTADO` | `SUSCRIPCION` | ✅ 2026 |
| `QR` | `Fecha Registro Solicitud` | `RESULTADO` | `Código Contrato` | ✅ 2026 |
| `Abandono` | `Fecha Llamada` | `Resultado` | — | ✅ 2026 |
| `Gestion`, `Acomulado` | `FECHA DE LLAMADA` | `RESULTADO FINAL` | `CONTRATO` | ⚠️ subconjuntos |
| `Hoja4`, `TD QR`, `Listado de homologación` | — | — | — | ❌ TD / catálogo de homologación (40 filas) |

> 🔴 **Hallazgo de trazabilidad:** la tabla `gestion_diaria.surti_inbound` de la base
> actual tiene **exactamente las 23 columnas de la hoja `Base` de este archivo**
> (`DISTRIBUIDORA`, `SUSCRIPCION`, `Validación`, `TIPO CONTACTO HOMOLOG`,
> `Maduración desde la venta -queja`, `ASESOR VENTA VAL`…). Es decir, **la tabla
> `surti_inbound` se construyó desde el archivo de QR, no desde los libros oficiales de
> Inbound**. Hay que decidir si se reconstruye con el origen real (H-27/H-29).

### 5.5 Los archivos de 461 MB

`SURTIGAS\Gestión diaria Inbound SURTIGAS.xlsx` y `... - copia.xlsx` (461 MB c/u,
22-jul-2026) contienen las hojas `llamada no aptas`, `MAYO 2026`, `ABRIL 2026 `,
`JUNIO 2026`, `JULIO 2026`, `Petición`, `Guión Sura`, `ABANDONO`, `SINIESTRO SURTIGAS`,
`observacion de OSF`, `Lineas -reintegro de prima `.

> ⚠️ Es el **archivo grande que se dañó**. **No usarlo como fuente principal** (pesado,
> obsoleto a jul-2026 y con datos de mayo–julio que la vía oficial ya cubre con
> `SURTIGAS ARCHIVO RECUPERADO - Copia` + `JULIO - AGOSTO 2026`).

---

## 6. Reglas transversales confirmadas

| Regla | Estado verificado |
| :--- | :--- |
| **Filtrar por la columna de fecha, no por el nombre de la hoja** | 🔴 Necesario: la hoja `ENERO A MARZO` de Surtigas trae datos de dic-2025 |
| Ventana a cargar | **2026-01-01 en adelante** (a la fecha: 21-oct-2026) |
| La mayoría de los libros Inbound traen hoja `ABANDONO` / `Abandono` | ✅ CEO, Caribe, GDO, Surtigas. Efigas no tiene Inbound |
| Efigas `FECHA DE BASE` = fecha de carga del lote | 🔴 No usarla como guía de mes |
| GDO `ESTADO` = columna de estado manual ("NO APTO") | 🔴 El resultado real está en `RESULTADO FINAL` / `Resultado de retencion` |
| GDO `SUBTIPIFICACION` = 52 valores | ✅ Vocabulario maestro de motivos del proyecto |
| GDO `NOMBRE_ASESOR_RETENCION` = persona | ✅ Único caso con asesor individual |
| Surtigas `CABINA` = `Inbound` | ✅ Sirve para filtrar (a diferencia de Caribe/GDO) |
| Surtigas usa `SUSCRIPCION` / `Código Contrato`, no `CONTRATO` | ✅ |
| Hojas de tabulación dinámica (`TD *`, `Tabulación`, `Hoja4`) | ❌ No son datos |
| Hojas de catálogos (`Datos`, `Filtros`, `CANALES...`, `tipificacion...`, `Listado de homologación`) | ❌ No son datos (son la fuente del catálogo `clasificacion`) |
| Maestros (`activos`, `BASE ACTIVAS`, `Activas Caribe`, `Valores de Protecciones`) | ❌ No son gestión diaria |

---

## 7. Archivos encontrados en la ruta que **no** están documentados

| Archivo | Qué es | Decisión |
| :--- | :--- | :--- |
| `Abandono 2-10-2026.xlsx` (52 KB, raíz) | Abandono **cross-gasera** con corte 2-oct-2026 | 🔴 **Definir si entra al modelo** (¿duplica las hojas de abandono?) |
| `GAS CARIBE\Activas Caribe*.xlsx` (7 archivos, 20 MB c/u) | Maestro de pólizas activas | ❌ Fuera del alcance |
| `GAS CARIBE\Informe.xlsx`, `Gestion Mes\Enero.xlsx` | Supportes | ❌ |
| `Tendencia LLamadas OCM\Base.xlsx` | Tendencias de llamadas OCM | 🔴 Ver si alimenta el KPI de abandono |
| `Valores de Protecciones\*` | Tarifas y valores de protección | 🔴 Necesario para un KPI de valor (primas) |
| `GDO\Solicitud de cancelación enviado a Leidy\*.xlsx` | Base de solicitudes de cancelación | ❌ |
| `GDO\Informe\comentario Gdo retención.xlsx` | Comentarios manuales | ❌ |
| `SURTIGAS\Informe\Validación Monteria\*.xlsx` | Validación | ❌ |

---

## 8. Volumetría 2026 verificada (barrido 21-oct-2026)

Criterio: **fecha de la fila ∈ [2026-01-01, 2026-10-21]**, sobre la columna fecha real
de cada hoja.

| Gasera | Familia | Filas 2026 | Nota |
| :--- | :--- | ---: | :--- |
| **CEO** | Inbound | 3.599 | + `Hoja1` 75 (¿duplicado?) |
| | Abandono | 642 | fecha en col 1 `FECHA` |
| **Efigas** | Outbound | 1.155 | + `Hoja1` 116 (¿duplicado?) |
| **Caribe** | Inbound (10 hojas) | 5.408 | |
| | Outbound | 1.341 | |
| | Abandono | 903 | fecha en col 1 `fecha` |
| **GDO** | Inbound | 5.709 | |
| | Outbound | 3.212 | 237 filas sin fecha |
| | PQRS (`PQR HDI - SURA-ALFA`) | 896 | |
| | PQRS (`PQRS ESCRITAS`) | 116 | modelo de referencia (ANS) |
| | Informativo (bitácora) | 4.174 | no es maestro PQRS |
| | Abandono | 482 | fecha en col 2 `fecha` |
| **Surtigas** | Inbound (origen real) | 11.648 | RECUPERADO + JUL-AGOSTO |
| | Inbound (consolidado QR `Base`) | 9.716 | ⚠️ **alternativa**, no aditiva |
| | Outbound (3 hojas) | 173 | mayoritariamente 2025 |
| | QR (hoja `QR`) | 1.256 | |
| | Abandono (oficial) | 1.356 | fecha en col 1 `fecha` |
| | Abandono (hoja `Abandono` del QR) | 2.795 | alternativa cross-gasera |
| **TOTAL 2026 a cargar** | | **≈ 42.070** | +191 de las `Hoja1` dudosas |

> 📊 La base actual tiene 48.036 filas de un snapshot parcial. Cargar 2026 completo
> desde el origen real la deja en **~42.000 filas**.

---

## 9. Checklist de cierre

- [x] Ruta raíz y subcarpetas por gasera
- [x] Libro y hojas por gasera y cabina
- [x] Columna fecha y columna resultado por hoja
- [x] Regla de filtrado (por fecha, no por nombre de hoja) y ventana 2026
- [x] Hojas de abandonment y PQRS identificadas
- [x] Archivos extra no documentados inventariados
- [x] **Efigas: `FECHA DE EJECUCION` confirmada por negocio (D-16)** ✅
- [ ] ⬜ **Estrategia de persistencia: A / B / C (A-16)** — con el conteo de filas 2026
- [ ] ⬜ **Decidir qué hacer con `Abandono 2-10-2026.xlsx` y los archivos master**
- [ ] ⬜ **Confirmar si `Hoja1` de CEO y de Efigas son hojas vivas o duplicados**
- [ ] ⬜ **Definir el día de cierre de Excel (A-18)**
- [ ] ⬜ **Llave de casamiento Excel ↔ OCM (A-17)**
- [ ] ⬜ **Confirmar si `surti_inbound` se reconstruye desde el origen real** (§5.4)
