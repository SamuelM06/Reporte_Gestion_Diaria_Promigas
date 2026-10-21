# 14. Estructura Real del Origen Excel

**Proyecto:** Reporte de Gestión Diaria - Retención Promigas
**Verificado contra:** los archivos del equipo, en la máquina del analista (21-oct-2026)
**Complementa:** `database/FICHA_ORIGEN_POR_GASERA.md` (vista operativa) y
`context/Analisis/02_Mapeo_Origen_Destino.md` (mapeo campo a campo)

> 🎯 **Este documento reemplaza toda suposición sobre la estructura de origen.**
> Cada hoja, cada columna guía y cada anomalía están verificados contra el archivo real,
> no inferidos de la documentación previa.

---

## 1. Ruta raíz y cómo se llega al origen

```text
OneDrive (Chariot & Castle Seguros SAS)
└─ Team Experiencia al Cliente - Promigas
   └─ Retención\Promigas\
      └─ Gestión diaria Promigas Inb -Outbound\      ← 📂 RUTA MADRE
         ├─ CEO\          Gestion diaria CEO.xlsx
         ├─ EFIGAS\       Gestión Diaria Outbound-Efigas.xlsx
         ├─ GAS CARIBE\   Gestión diaria Inbound Caribe.xlsx
         │                Gestión diaria Outbound-Gases del caribe.xlsx
         ├─ GDO\          Informe\VALIDACION INFORMACION GDO- 24 de Junio 2026.xlsx
         │                Gestión Inbound-Outbound\...
         └─ SURTIGAS\     SURTIGAS ARCHIVO RECUPERADO - Copia.xlsx
                          Gestión diaria Outbound SURTIGAS.xlsx
                          JULIO - AGOSTO 2026\Gestión diaria Inbound Surtigas.xlsx
                          Informe\Gestión Inbound -Outbound-QR.xlsx
```

> 📌 La sincronización con OneDrive/SharePoint es la **misma carpeta** que el negocio
> usa a diario. Una copia local en `data/raw/` (ignorada por Git) es el insumo del
> conector de ingesta.

---

## 2. Inventario de archivos de gestión (los que se cargan)

| # | Archivo | Bytes | Modificado | Hojas de datos |
| ---: | :--- | ---: | :--- | ---: |
| 1 | `CEO\Gestion diaria CEO.xlsx` | 1.496.311 | 21-oct 16:25 | 3 |
| 2 | `EFIGAS\Gestión Diaria Outbound-Efigas.xlsx` | 3.347.386 | 21-oct 16:29 | 2 |
| 3 | `GAS CARIBE\Gestión diaria Inbound Caribe.xlsx` | 2.761.624 | 21-oct 16:45 | 12 |
| 4 | `GAS CARIBE\Gestión diaria Outbound-Gases del caribe.xlsx` | 697.088 | 21-oct 16:43 | 1 |
| 5 | `GDO\Informe\VALIDACION INFORMACION GDO- 24 de Junio 2026.xlsx` | 10.855.422 | 21-oct 16:31 | 6 |
| 6 | `SURTIGAS\SURTIGAS ARCHIVO RECUPERADO - Copia.xlsx` | 1.582.374 | 16-oct 15:45 | 4 |
| 7 | `SURTIGAS\JULIO - AGOSTO 2026\Gestión diaria Inbound Surtigas.xlsx` | 1.273.472 | 21-oct 16:51 | 5 |
| 8 | `SURTIGAS\Gestión diaria Outbound SURTIGAS.xlsx` | 3.000.936 | 21-oct 16:51 | 3 |
| 9 | `SURTIGAS\Informe\Gestión Inbound -Outbound-QR.xlsx` | 9.580.606 | 22-sep 10:03 | 5 |

### 2.1 Archivos presentes que NO son fuente de gestión

| Archivo | Bytes | Qué es | Decisión |
| :--- | ---: | :--- | :--- |
| `SURTIGAS\Gestión diaria Inbound SURTIGAS.xlsx` (+`- copia`) | 461.412.357 | Versión grande "dañada": `MAYO 2026`, `ABRIL 2026`, `JUNIO 2026`, `JULIO 2026`, `Petición`, `ABANDONO`, guiones | ❌ No es fuente principal (obsoleta a jul-2026, 461 MB) |
| `GAS CARIBE\Activas Caribe*.xlsx` (7) | ~21 MB c/u | Maestro de pólizas activas | ❌ |
| `EFIGAS\…-Efigas.xlsx` hoja `activos` | 9.565 filas | Maestro de pólizas activas | ❌ |
| `GDO\BASE ACTIVAS.xlsx` | 8.349.611 | Maestro de pólizas | ❌ |
| `GDO\Gestión Inbound-Outbound\Gestión de Abandono GDO 2026.xlsx` | 372.306 | `ABANDONO Inb` (1.762) + `ABANDONO FUERA DE HORARIO` + `Prueba - No Usar` | ⚠️ Solo `ABANDONO Inb`; `Prueba - No Usar` descartada por nombre |
| `GDO\Gestión Inbound-Outbound\Acomulado Mes\01_Marzo..06_Agosto.xlsx` | 25–276 KB | Acumulado mensual | ⚠️ Duplica `GESTIÓN INBOUND` |
| `GDO\Gestión Inbound-Outbound\GESTION_INBOUND_GDO_TRASLADO_POR_COMPETENCIA.xlsx` | 4.605.983 | `ACOMULADO Inb-Out` + traslados por competencia | ⚠️ Fuera del alcance actual |
| `GDO\Informe\VALIDACION INFORMACION GDO- 22 Abril 2026.xlsx` | 575.313 | Versión anterior del archivo vivo | ❌ |
| `Abandono 2-10-2026.xlsx` (raíz) | 52.009 | Abandono **cross-gasera** con corte 2-oct-2026 | 🔴 **Decidir si entra al modelo** |
| `Tendencia LLamadas OCM\Base.xlsx` | 2.660.251 | Tendencias de llamadas OCM | 🔴 Ver si alimenta el KPI de abandono |
| `Valores de Protecciones\*` | ~1–2 MB | Tarifas y valores de protección | 🔴 Necesario para KPI de valor |
| `GAS CARIBE\Gestion Mes\Enero.xlsx`, `GDO\Solicitud de cancelación…`, `SURTIGAS\Informe\Validación Monteria\…` | — | Soportes | ❌ |

---

## 3. Inventario por hoja

### 3.1 CEO — `Gestion diaria CEO.xlsx`

| Hoja | Cols | Columna fecha (guía mes) | Columna resultado | Clave | Tabla destino |
| :--- | ---: | :--- | :--- | :--- | :--- |
| `Gestion Diaria Inbound Ceo` | 30 (54 con vacías) | ` FECHA INGRESO LLAMADA` | **`Resultado de retencion`** | `CONTRATO` | `ceo_inbound` |
| `Abandono` | 22 | `Fecha de llamada` | `RESULTADO FINAL` | `CONTRATO` | `ceo_abandono` |
| `enero a mayo 2025` | 13 | `FECHA DE LLAMADA` | `ESTADO` | `CONTRATO` | — (2025) |
| `Hoja1` | 20 | ` FECHA INGRESO LLAMADA` | `Resultado de retencion` | `CONTRATO` | ⚠️ duplicado parcial |

**Columnas de `Gestion Diaria Inbound Ceo`:**

```text
 FECHA INGRESO LLAMADA | | | CONTRATO | TELEFONO | DOCUMENTO | USUARIO | ASEGURADORA |
PRODUCTO | OBSERVACIÓN | Resultado de retencion | PROCESOS EXTERNOS | TIPO DE CONTACTO |
Gestor de retencion | Operador | Canal | Fecha de venta | Asesor de venta |
Tipifiacion de la retencion | RESPUESTA DE GESTION | | Soporte | OBSERVACIÓN | QUIEN AUTORIZA |
CEDULA | RESPONSABLE DEL PAGO O TITULAR DE LA CUENTA | ESTADO | FEHCA DE CANCELACION | ANS |
DEVOLUCION DE PRIMAS
```

**Columnas de `Abandono`:**

```text
fecha | numbercall | resultcalldesc | resultdesc | Comunicación posterior | Cantidad de intentos |
Fecha de llamada | NOMBRE_CLIENTE | IDENTIFICACION_USUARIO | CONTRATO | PRODUCTO_1 | OBSERVACIONES |
SOLICITUD DE POLIZA | fecha de legalizacion | CATEGORIA | CATEGORIA_DETALLE | SUBTIPIFICACION |
RESULTADO FINAL | GESTOR | Columna21 | Resultado gestión Inbound | Gestión canal Inbound
```

> 💡 `numbercall`, `resultcalldesc`, `resultdesc`, `Comunicación posterior`,
> `Cantidad de intentos` son **nombres de OCM**: la hoja de abandono ya es un
> export de OCM pegado en Excel. Eso abre la puerta al casamiento directo (A-17).

**Hojas auxiliares:** `Datos` (catálogo `RESULTADO RETENCIÓN`),
`CANAL , OPERADORES, TIPIFICACIO` (catálogos PQR/Retención/Canales),
`SINIESTRO CEO `, `LINEAS DE ATENCION`, `PRACTISEGURO`, `APLICATIVOS`, `ACOMULADO` (vacía),
`Hoja2`.

---

### 3.2 EFIGAS — `Gestión Diaria Outbound-Efigas.xlsx`

| Hoja | Cols | Columna fecha (guía mes) | Columna resultado | Clave | Tabla destino |
| :--- | ---: | :--- | :--- | :--- | :--- |
| `Base` | 66 | **`FECHA DE EJECUCION`** | **`ESTADO`** | `CODIGO CONTRATO` | `efigas_outbound` |
| `Hoja1` | 66 | `FECHA DE BASE g` | `ESTADO` | `CODIGO CONTRATO` | ⚠️ verificar |

**Columnas de `Base` (31 primeras):**

```text
FECHA DE BASE | No. SOLICITUD | CODIGO CONTRATO | No. PRODUCTO | ASEGURADORA | LINEA PRODUCTO |
# POLIZA | VALOR PRIMA | No. CEDULA ASEGURADO | TITULAR FACTURA | No. CEDULA TITULAR |
OBSERVACIÓN | TELEFONO 1 | DIRECCIÓN | DEPARTAMENTO | CIUDAD | Tipifiacion de PQR |
ASEGURADORA | OPERADOR | CANAL | PRODUCTO | TIPO DE CONTACTO | MOTIVO | ESTADO | OBSERVACION |
FECHA DE EJECUCION | FECHA DE VENTA | ASESOR DE VENTA | LLAMADA #1 | GESTOR | CORREO | …(35 más)
```

> 🔴 `FECHA DE BASE` = **fecha de carga del lote**. El lote `2026-03-02` contiene
> ejecuciones de septiembre–noviembre (verificado). **La guía de mes es
> `FECHA DE EJECUCION`** (D-16, confirmado por negocio el 21-oct-2026).
> Evidencia: 90.5% de las filas tienen base ≠ ejecución, desfase máximo **273 días**,
> 72 lotes con formatos mezclados, y usar `BASE` **mueve 526 filas (29.8%) al mes
> equivocado** (sep-2026 ↔ oct-2025).
> 🔴 `ASEGURADORA` aparece **dos veces** (posiciones 5 y 18).

**Hojas auxiliares:** `activos` (9.565 filas, 49 cols — maestro),
`CANAL,TIPIFICA, ` (catálogos), `ACUMULADO` (vacía), `Hoja2` (vacía).

---

### 3.3 GDO — `VALIDACION INFORMACION GDO- 24 de Junio 2026.xlsx` (archivo vivo)

| Hoja | Cols | Columna fecha (guía mes) | Columna resultado | Clave | Tabla destino |
| :--- | ---: | :--- | :--- | :--- | :--- |
| `GESTIÓN INBOUND` | 38 | **`FECHA DE LLAMADA`** (+`Mes`) | **`RESULTADO FINAL`** | `CONTRATO` | `gdo_inbound` |
| `OUT` | 82 | **`FECHA EJECUCION`** (+`MES`) | **`Resultado de retencion`** | `CONTRATO` | `gdo_outbound` |
| `INFORMATIVO` | 28 | `FECHA REGI` (+`Hora`) | `Resultado` | `CONTRATO` | `gdo_informativo` (bitácora) |
| `PQR HDI - SURA-ALFA` | 62 | `FECHA_REGISTRO_SOLICITUD` | — | `CONTRATO` | `gdo_pqrs` |
| `PQRS ESCRITAS` | 17 | `FECHA DE RAD,SOLICITANTE-GDO` | `ESTADO` | `CONTRATO ` | `gdo_pqrs_escritas` |
| `abandono` | 23 | `Fecha de llamada` (+`Mes`) | `RESULTADO FINAL` | `CONTRATO` | `gdo_abandono` |

**Columnas de `GESTIÓN INBOUND` (las 38):**

```text
Mes | FECHA DE LLAMADA | SOLICITUD DE POLIZA | FECHA DE LEGALIZACION | ESTADO DE SOLICITUD |
ENTIDAD_FACTURACION | NOMBRE_DISTRIBUIDORAS | NOMBRE_CLIENTE | IDENTIFICACION_USUARIO |
CONTRATO | LOCALIDAD | TELEFONO | TIPO_CONTACTO | CANAL | FECHA_VENTA | PRODUCTO_1 | PRODUCTO_2 |
NOMBRE_ASESOR_VENTA | NOMBRE_ASESOR_RETENCION | CATEGORIA | CATEGORIA_DETALLE | SUBTIPIFICACION |
OBSERVACIONES | number1 | number2 | RESULTADO FINAL | TIPO DE CONTACTO | RESPUESTA DE ASEGURADORA |
Soporte | OBSERVACIÓN | QUIEN AUTORIZA | CEDULA | RESPONSABLE DEL PAGO O TITULAR DE LA CUENTA |
ESTADO | F. ENVIO | FEHCA DE CANCELACION | ANS | Dias de Maduración
```

> ⚠️ `ESTADO` (col 35) es la columna que el asesor marca "NO APTO"; el resultado real
> está en `RESULTADO FINAL` (col 26). Mismo problema que se documentó como H-29.
> 💡 `NOMBRE_ASESOR_RETENCION` = **asesor persona** (única gasera con ese dato).
> 💡 `SUBTIPIFICACION` = 52 valores = **vocabulario maestro de motivos**.

**Hojas de tabulación (NO son datos):** `TD Inbound`, `TD INB 2`, `TD aseguradora`,
`Informativos vs pqrs`, `Td infr`, `Td informativo falta BI`, `Tabulación`, `Hoja2`, `Hoja1`.

---

### 3.4 GAS CARIBE — Inbound

| Hoja | Cols | Columna fecha | Columna resultado | Clave | 2026 |
| :--- | ---: | :--- | :--- | :--- | :---: |
| `ENERO 2026` | 19 | `fecha de atencion` | `ESTADO` | `CONTRATO` | ✅ |
| `FEBRERO 2026` | 20 | `fecha de atencion` | `Resultado de retencion` | `CONTRATO` | ✅ |
| `MARZO 2026` | 20 | `fecha de atencion` | `Resultado de retencion` | `CONTRATO` | ✅ |
| `ABRIL 2026` | 20 | `FECHA DE ATENCION` | `RESULTADO DE RETENCION` | `CONTRATO` | ✅ |
| `MAYO 2026` | 20 | `FECHA DE ATENCION` | `RESULTADO DE RETENCION` | `CONTRATO` | ✅ |
| `JUNIO 2026` | 21 | `FECHA DE ATENCION` | `RESULTADO DE RETENCION` | `CONTRATO` | ✅ |
| `JULIO 2026` | 22 | `FECHA DE ATENCION` | `RESULTADO DE RETENCION` | `CONTRATO` | ✅ |
| `AGOSTO 2026` | 22 | `FECHA DE ATENCION` | `RESULTADO DE RETENCION` | `CONTRATO` | ✅ |
| `SEPTIEMBRE 2026 ` | 22 | `FECHA DE ATENCION` | `RESULTADO DE RETENCION` | `CONTRATO` | ✅ |
| `OCTUBRE 2026 ` | 22 | `FECHA DE ATENCION` | `RESULTADO DE RETENCION` | `CONTRATO` | ✅ |
| `ABANDONO` | 23 | `Fecha de llamada` | `RESULTADO FINAL` | `CONTRATO` | ✅ |
| `enero`…`noviembre `, `Diciembre` | 12–18 | `FECHA DE LLAMADA` | `ESTADO` | `CONTRATO` | ❌ 2025 |
| `Rellamadas` | 17 | `FECHA DE LLAMADA` | `ESTADO FINAL ` | `CONTRATO` | ⚠️ subconjunto |

**Columnas de `ABANDONO`:**

```text
fecha | numbercall | resultcalldesc | resultdesc | Comunicación posterior | Cantidad de intentos |
Fecha de llamada | NOMBRE_CLIENTE | IDENTIFICACION_USUARIO | CONTRATO | PRODUCTO_1 | OBSERVACIONES |
SOLICITUD DE POLIZA | fecha de legalizacion | CATEGORIA | CATEGORIA_DETALLE | SUBTIPIFICACION |
RESULTADO FINAL | # LLAMADAS | Resultado gestión Inbound | Gestión canal Inbound | Estado final
```

**Evolución del esquema por mes** (de 19 a 22 columnas):

| Columna | Desde |
| :--- | :--- |
| `LOCALIDAD` | `JULIO 2026` |
| `FECHA DE LEGALIZACION` | `JUNIO 2026` |
| `CORREO PARA REINTEGRO` | `FEBRERO 2026` |
| `GESTION SAC `, `NUMERO DE SOLICITUD `, `OBSERVACION  SAC ` | `ENERO 2026` |

> 🔴 **`AGOSTO 2026`: la columna `LOCALIDAD` trae `#VALUE!`** (error heredado de Excel).
> 🔴 **El nombre de la columna fecha y de la de resultado cambia entre hojas** →
> el lector debe resolverse **por hoja**.

---

### 3.5 GAS CARIBE — Outbound

| Hoja | Cols | Columna fecha | Columna resultado | Clave |
| :--- | ---: | :--- | :--- | :--- |
| `Outbound` | 28+ | **`Fecha de llamada`** (y `FECHA DE LLAMADA`) | **`Resultado de retencion`** | `CONTRATO` |

```text
fecha de base | SOLICITUD | FECHA REGISTRO | T SOLICITUD | COD ESTADO | ASEGURADORA | CONTRATO |
COD MED RECEPCION | OBSERVACION | Tipifiacion de PQR | Aseguradora | Operador | Canal | Producto |
Tipo de contacto | Tipifiacion de la retencion | Resultado de retencion | Observacion de retencion |
Fecha de llamada | Fecha de venta | Asesor de venta | Gestor de retencion | MES | FECHA DE LLAMADA |
GESTION SAC | FECHA DE GESTION | NUMERO DE SOLICITUD | OBSERVACION
```

> 💣 `MES` viene como columna directa → el mes no requiere parsear la fecha.
> Hoja auxiliar: `Tipificaciones` (catálogos).

---

### 3.6 SURTIGAS — Inbound (enero a junio)

**Archivo:** `SURTIGAS ARCHIVO RECUPERADO - Copia.xlsx`

| Hoja | Cols | Columna fecha | Columna resultado | Clave |
| :--- | ---: | :--- | :--- | :--- |
| `ENERO A MARZO ` | 40 | **`FECHA DE LLAMADA`** | **`RESULTADO FINAL`** | `CONTRATO` |
| `ABRIL` | 41 | **`FECHA DE LLAMADA`** | **`RESULTADO FINAL`** | `CONTRATO` |
| `MAYO ` | 41 | **`FECHA DE LLAMADA`** | **`RESULTADO FINAL`** | `CONTRATO` |
| `JUNIO` | 37 | **`FECHA DE LLAMADA`** | **`RESULTADO FINAL`** | `CONTRATO` |

```text
CABINA | FECHA DE LLAMADA | SOLICITUD DE POLIZA | FECHA DE LEGALIZACION | ESTADO DE SOLICITUD |
Medio de ejecución | ENTIDAD_FACTURACION | NOMBRE_DISTRIBUIDORAS | NOMBRE_CLIENTE |
IDENTIFICACION_USUARIO | CONTRATO | LOCALIDAD | TELEFONO1 | TIPO_CONTACTO | CANAL | FECHA_VENTA |
PRODUCTO_1 | PRODUCTO_2 | NOMBRE_ASESOR_VENTA | NOMBRE_ASESOR_RETENCION | CATEGORIA |
CATEGORIA_DETALLE | SUBTIPIFICACION | OBSERVACIONES | RESULTADO FINAL | CORREO | Fecha de venta |
OBSERVACION DISTRIBUIDORA | RESPUESTA DE ASEGURADORA | Soporte | OBSERVACIÓN | QUIEN AUTORIZA | CEDULA |
RESPOSABLE DEL PAGO O TITULAR DE LA CUENTA | ESTADO | FEHCA DE CANCELACION | ANS | DEVOLUCION DE PRIMAS
```

> 💡 `CABINA` viene **poblada** (`Inbound`) → en Surtigas sí sirve para filtrar.
> 📌 La hoja `ENERO A MARZO ` contiene datos de **diciembre 2025** (fila 2: 10-dic-2025).
> **El filtro es por columna de fecha, nunca por nombre de hoja.**

### 3.7 SURTIGAS — Inbound (julio en adelante)

**Archivo:** `JULIO - AGOSTO 2026\Gestión diaria Inbound Surtigas.xlsx`

| Hoja | Cols | Columna fecha | Columna resultado | Clave |
| :--- | ---: | :--- | :--- | :--- |
| `JULIO` | 37 | **`FECHA DE LLAMADA`** | **`RESULTADO FINAL`** | `CONTRATO` |
| `Agosto` | 39 | **`FECHA DE LLAMADA`** | **`RESULTADO FINAL`** | `CONTRATO` |
| `SEPTIEMBRE` | 37 | **`FECHA DE LLAMADA`** | **`RESULTADO FINAL`** | `CONTRATO` |
| `OCTUBRE` | 37 | **`FECHA DE LLAMADA`** | **`RESULTADO FINAL`** | `CONTRATO` |
| `ABANDONO` | 22 | `Fecha de llamada` | `RESULTADO FINAL` | `CONTRATO` |

> ⚠️ `OCTUBRE`: la columna 5 se llama **`CA`** en vez de `ESTADO DE SOLICITUD`.
> ⚠️ `Agosto`: dos columnas **sin nombre** (posiciones 33 y 34).
> 📌 La carpeta dice `JULIO - AGOSTO 2026` pero el archivo ya trae **septiembre y octubre**.
> Hojas auxiliares: `Filtros` (catálogo), `LINEAS - REINTEGROS DE PRIMAS`, `Hoja1`.

### 3.8 SURTIGAS — Outbound

**Archivo:** `Gestión diaria Outbound SURTIGAS.xlsx`

| Hoja | Cols | Columna fecha | Columna resultado | Clave |
| :--- | ---: | :--- | :--- | :--- |
| `salva factura ` | 29 | `fecha de lllamada` *(typo)* | `ESTADO` | `Código Contrato` |
| `reclamos` | 35 | `Fecha de llamada` | `Estado` | `Código Contrato` |
| `cancelaciones ` | 29 | `Fecha de llamada` | `Resultado de retencion` | `CONTRATO` |

### 3.9 SURTIGAS — QR

**Archivo:** `Informe\Gestión Inbound -Outbound-QR.xlsx`

| Hoja | Cols | Columna fecha | Columna resultado | Clave |
| :--- | ---: | :--- | :--- | :--- |
| `Base` | 23 | `FECHA DE EJECUCION` (+`BASE`) | `ESTADO` | `SUSCRIPCION` |
| `QR` | 53 | `Fecha Registro Solicitud` | `RESULTADO` | `Código Contrato` |
| `Abandono` | 4 | `Fecha Llamada` | `Resultado` | — |
| `Gestion` | 8 | `FECHA DE LLAMADA` | `RESULTADO FINAL` | `CONTRATO` |
| `Acomulado` | 40 | `FECHA DE LLAMADA` | `RESULTADO FINAL` | `CONTRATO` |

**Columnas de `Base` (las 23):**

```text
DISTRIBUIDORA | ASEGURADORA | MEDIO DE RECEPCION | SUSCRIPCION | LOCALIDAD | OPERADOR | CANAL |
PRODUCTO | TIPO DE CONTACTO | ESTADO | SUBTIPIFICACION | MOTIVO | FECHA DE EJECUCION | BASE |
fecha de venta | asesor de venta | Mes | Cabina | AÑO VENTA | Validación | TIPO CONTACTO HOMOLOG |
Maduración desde la venta -queja | ASESOR VENTA VAL
```

> 🔴 **Hallazgo de trazabilidad:** la tabla `gestion_diaria.surti_inbound` de la base
> actual tiene **exactamente estas 23 columnas**. Es decir, **`surti_inbound` se
> construyó desde este archivo de QR, no desde los libros oficiales de Inbound**
> (que traen `CABINA`, `FECHA DE LLAMADA`, `RESULTADO FINAL`, `SUBTIPIFICACION` con
> jerarquía `1.1`…). Hay que decidir si se reconstruye con el origen real.

---

## 4. Hallazgos de estructura (verificados)

| # | Hallazgo | Impacto |
| ---: | :--- | :--- |
| 1 | 🔴 **El nombre de la columna fecha y de la de resultado cambia entre hojas** (Caribe, CEO, Surtigas Outbound) | El lector debe resolverse **por hoja**, no por analogía (H-24) |
| 2 | 🔴 **El nombre de la hoja no coincide con el mes del dato** (`ENERO A MARZO` de Surtigas trae dic-2025; `MARZO 2026` de Caribe trae feb-2026) | **Filtrar por columna de fecha**, nunca por nombre de hoja |
| 3 | 🔴 **Los archivos evolucionan**: `OUT` de GDO hoy tiene 82 columnas; la tabla `gdo_outbound` de la BD tiene 68 (cargada el 01-oct) | El snapshot en BD **ya no coincide** con el archivo |
| 4 | 🔴 **Las hojas de abandono son exports de OCM** (`numbercall`, `resultcalldesc`, `resultdesc`, `Comunicación posterior`, `Cantidad de intentos`) | Casamiento directo OCM↔Excel posible (A-17) |
| 5 | 🔴 `surti_inbound` (BD) tiene las columnas del archivo de **QR**, no del Inbound oficial | Origen de la tabla mal documentado |
| 6 | 🟠 **Fechas imposibles**: CEO llega a `6185-09-22`; hay celdas con serial fuera de rango (`O676`, `O979`, `Q665`…) | Regla R-01 (rango) |
| 7 | 🟠 **Fechas futuras** respecto del 21-oct-2026: Caribe Outbound hasta 2026-12-03, GDO Out hasta 2026-11-09, Surtigas Out hasta 2028-08-28 | Regla R-01 |
| 8 | 🟠 **`AGOSTO 2026` de Caribe: `LOCALIDAD` = `#VALUE!`** | 560 filas con error de Excel |
| 9 | 🟠 **Celdas con formato fecha pero serial inválido** (openpyxl las reporta como error) | Parser debe tolerarlas |
| 10 | 🟠 **Hojas `Hoja1` en CEO (75 filas) y Efigas (116 filas)** con datos 2026 que **podrían duplicar** la hoja principal | Verificar antes de cargar |
| 11 | 🟠 **`FECHA DE BASE` en Efigas** = fecha de carga del lote (no de gestión) | Regla H-27 |
| 12 | 🟠 **GDO `ESTADO` = "NO APTO"**; el resultado real está en `RESULTADO FINAL` / `Resultado de retencion` | H-29 |
| 13 | 🟠 **Efigas `ASEGURADORA` duplicada** (posiciones 5 y 18) | Deduplicar en el mapeo |
| 14 | 🟡 **Columnas sin nombre** en `Agosto` de Surtigas (pos. 33-34) | Descartar o renombrar |
| 15 | 🟡 **Typos de origen**: `fecha de lllamada` (3 l), `FEHCA DE CANCELACION`, `FECHA DE BASE g`, `Arbil`, `prqs escritas`, `surtugas` | Normalizar en la carga (L-01..L-07) |
| 16 | 🟡 **Caribe `ABANDONO`**: 898 de 903 filas con `Fecha de llamada` vacía → la fecha real está en la col 1 | Usar la **primera columna** como fecha |
| 17 | 🟡 **Surtigas `ABANDONO`**: 1.357 filas con `Fecha de llamada` vacía | Igual que arriba |
| 18 | 🔴 **`Hoja1` en CEO (75 filas, sep-2026) y Efigas (116 filas, abr-2026)** con datos 2026 que **podrían duplicar** la hoja principal | ⚠️ Verificar antes de cargar: ¿mes en curso o duplicado? |

---

## 5. Volumetría de 2026 a cargar (barrido verificado 21-oct-2026)

**Criterio:** fecha de la fila ∈ [2026-01-01, 2026-10-21]. Se cuenta sobre la columna
fecha **de la fila**, nunca sobre el nombre de la hoja.

### 5.1 Atención / Outbound

| Gasera | Libro | Hoja | Filas datos | **Filas 2026** | Rango de fecha |
| :--- | :--- | :--- | ---: | ---: | :--- |
| CEO | `Gestion diaria CEO.xlsx` | `Gestion Diaria Inbound Ceo` | 5.808 | **3.599** | 2005-06-11 → 6185-09-22 ⚠️ |
| CEO | | `Hoja1` | 75 | 75 | 2026-09-02 → 2026-09-14 ⚠️ posible duplicado |
| Efigas | `…-Efigas.xlsx` | `Base` | 1.848 | **1.155** | 2025-01-10 → 2026-10-20 |
| Efigas | | `Hoja1` | 116 | 116 | 2026-04-01 → 2026-04-27 ⚠️ posible duplicado |
| Caribe | `Inbound Caribe.xlsx` | `ENERO 2026` | 552 | 547 | 2025-01-03 → 2026-08-01 |
| Caribe | | `FEBRERO 2026` | 544 | 544 | 2026-02-02 → 2026-02-27 |
| Caribe | | `MARZO 2026` | 618 | 617 | 2026-02-03 → 2026-03-31 |
| Caribe | | `ABRIL 2026` | 503 | 503 | 2026-04-01 → 2026-04-30 |
| Caribe | | `MAYO 2026` | 539 | 539 | 2026-04-20 → 2026-05-30 |
| Caribe | | `JUNIO 2026` | 475 | 475 | 2026-05-15 → 2026-06-30 |
| Caribe | | `JULIO 2026` | 572 | 572 | 2026-07-01 → 2026-07-31 |
| Caribe | | `AGOSTO 2026` | 560 | 560 | 2026-08-03 → 2026-08-31 |
| Caribe | | `SEPTIEMBRE 2026 ` | 635 | 635 | 2026-09-01 → 2026-09-29 |
| Caribe | | `OCTUBRE 2026 ` | 418 | 416 | 2026-10-01 → 2026-10-21 |
| Caribe | `Outbound-Gases del caribe.xlsx` | `Outbound` | 2.569 | **1.341** | 2024-08-05 → 2026-12-03 ⚠️ |
| GDO | `VALIDACION INFORMACION GDO…xlsx` | `GESTIÓN INBOUND` | 5.709 | **5.709** | 2026-03-16 → 2026-10-09 |
| GDO | | `OUT` | 3.452 | **3.212** | 2020-08-31 → 2026-11-09 ⚠️ (237 sin fecha) |
| Surtigas | `SURTIGAS ARCHIVO RECUPERADO - Copia.xlsx` | `ENERO A MARZO ` | 3.836 | **3.574** | 2025-12-10 → 2026-03-31 |
| Surtigas | | `ABRIL` | 941 | 941 | 2026-03-05 → 2026-05-02 |
| Surtigas | | `MAYO ` | 1.051 | 1.051 | 2026-04-09 → 2026-05-30 |
| Surtigas | | `JUNIO` | 1.136 | 1.136 | 2026-06-01 → 2026-06-30 |
| Surtigas | `JULIO - AGOSTO 2026\…Inbound Surtigas.xlsx` | `JULIO` | 1.463 | 1.429 | 2026-07-01 → 2026-07-31 (34 sin fecha) |
| Surtigas | | `Agosto` | 1.451 | 1.299 | 2026-07-16 → 2026-08-31 (152 sin fecha) |
| Surtigas | | `SEPTIEMBRE` | 1.410 | 1.410 | 2026-09-01 → 2026-09-30 |
| Surtigas | | `OCTUBRE` | 1.151 | 808 | 2026-10-01 → 2026-10-21 (343 sin fecha) |
| Surtigas | `Gestión diaria Outbound SURTIGAS.xlsx` | `salva factura ` | 1.331 | 17 | 2025-02-12 → 2026-12-02 |
| Surtigas | | `reclamos` | 2.214 | 116 | 2025-01-12 → 2026-12-08 |
| Surtigas | | `cancelaciones ` | 3.474 | 40 | 2002-10-14 → 2028-08-28 ⚠️ |
| Surtigas | `Gestión Inbound -Outbound-QR.xlsx` | `Base` | 9.724 | 9.716 | 2023-08-13 → 2026-09-07 |
| Surtigas | | `QR` | 1.256 | 1.256 | 2026-01-02 → 2026-08-28 |

### 5.2 Abandono

| Gasera | Libro | Hoja | Col fecha real | Filas | **2026** | Rango |
| :--- | :--- | :--- | :--- | ---: | ---: | :--- |
| CEO | `Gestion diaria CEO.xlsx` | `Abandono` | **`FECHA` (col 1)** | 642 | **642** | 2026-05-19 → 2026-09-23 |
| Caribe | `Inbound Caribe.xlsx` | `ABANDONO` | **`fecha` (col 1)** | 903 | **903** | 2026-06-19 → 2026-09-23 |
| GDO | `VALIDACION…GDO.xlsx` | `abandono` | **`fecha` (col 2)** | 482 | **482** | 2026-03-16 → 2026-07-30 |
| Surtigas | `…Inbound Surtigas.xlsx` | `ABANDONO` | **`fecha` (col 1)** | 1.357 | 1.356 | 2020-10-21 → 2026-09-23 |
| Surtigas | `…-Outbound-QR.xlsx` | `Abandono` | `Fecha Llamada` | 2.795 | 2.795 | 2026-04-16 → 2026-08-31 |

> 🔴 **Corrección importante:** en las hojas de abandono la fecha **NO** está en
> `Fecha de llamada` (esa columna viene vacía en la mayoría de las filas) sino en la
> **primera columna** (`FECHA` / `fecha` / `Mes`+`fecha`). Con la columna equivocada el
> 100% de las filas queda "sin fecha". Verificado con datos.

### 5.3 PQRS

| Gasera | Hoja | Columna fecha | Filas | **2026** |
| :--- | :--- | :--- | ---: | ---: |
| GDO | `INFORMATIVO` | `FECHA REGI` | 4.174 | 4.174 (bitácora, no maestro) |
| GDO | `PQR HDI - SURA-ALFA` | `FECHA_REGISTRO_SOLICITUD` | 896 | **896** |
| GDO | `PQRS ESCRITAS` | `FECHA DE RAD,SOLICITANTE-GDO` | 126 | **116** (10 sin fecha) |

### 5.4 Totales de 2026 a cargar

**Escenario recomendado** (Surtigas Inbound desde el origen real; QR aparte):

| Familia | Filas 2026 |
| :--- | ---: |
| Atención / Outbound (CEO 3.599 + Efigas 1.155 + Caribe 6.749 + GDO 8.921 + Surtigas 11.821 + Surtigas QR 1.256) | **33.501** |
| Abandono (CEO 642 + Caribe 903 + GDO 482 + Surtigas 1.356) | **3.383** |
| PQRS (GDO informativo 4.174 + GDO pqrs 896 + GDO pqrs_escritas 116) | **5.186** |
| **Total 2026** | **≈ 42.070** |
| + las 2 hojas `Hoja1` dudosas (CEO 75 + Efigas 116) | 42.261 |

**Escenario alternativo** (Surtigas Inbound desde el consolidado QR): 33.501 − 11.648 +
9.716 → **≈ 40.138**.

> 📊 **La base actual tiene 48.036 filas de un snapshot parcial.** Cargar 2026 completo
> desde el origen real la deja en **~42.000 filas** (más el histórico que se conserve,
> si se conserva). La decisión de estrategia (A-16) define si el snapshot se reemplaza
> o convive.

> ⚠️ **Surtigas Inbound tiene dos fuentes candidatas y NO son acumulables:**
> * **(a) Origen real** (`RECUPERADO` + `JULIO-AGOSTO`): **11.648 filas 2026** con
>   `CABINA`, `FECHA DE LLAMADA`, `RESULTADO FINAL` y `SUBTIPIFICACION` jerárquica.
> * **(b) Consolidado QR** (`Base`): **9.716 filas 2026** con `Validación`,
>   `TIPO CONTACTO HOMOLOG`, `Maduración desde la venta -queja`, `ASESOR VENTA VAL`.
>
> Son **el mismo negocio en dos formatos**. La tabla actual `surti_inbound` se construyó
> desde (b). **Recomendación:** cargar (a) como verdad y usar (b) para enriquecer
> (cruce por `CONTRATO` + fecha) o para extraer las columnas de homologación.

---

## 6. Cómo regenerar esta información

```bash
# Perfil de estructura de un libro (hojas, columnas, nulos, roles)
python database/perfilador_excel.py --ruta data/raw --muestra

# Salida por defecto: context/Analisis/14_Perfil_Excel_Por_Gasera.md
```

El profiler **no imprime valores de datos** (solo estructura, nulos y distintos) y
excluye del muestreo las columnas PII (documento, teléfono, correo, nombre, dirección).

---

## 7. Documentos relacionados

| Documento | Contenido |
| :--- | :--- |
| `database/FICHA_ORIGEN_POR_GASERA.md` | Vista operativa: rutas, hojas, columnas guía y destino |
| `database/PROCEDENCIA_Y_REINGESTA.md` | Procedencia verificada y plan de persistencia |
| `context/Analisis/02_Mapeo_Origen_Destino.md` | Mapeo columna a columna (⚠️ desactualizado en nombres de hoja) |
| `context/Analisis/01_Diccionario_de_Datos.md` | Diccionario de las tablas de la BD |
| `context/Analisis/07_Estructura_de_datos.md` | Inventario por gasera (versión previa a la verificación) |
