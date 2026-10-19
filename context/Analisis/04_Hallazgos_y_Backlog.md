# 04. Hallazgos y Backlog Analítico

**Proyecto:** Gestión Diaria Promigas
**Alcance:** esquema `gestion_diaria` de `DataCenter_Promigas` (PostgreSQL 16.14)
**Fecha del análisis:** 19 de octubre de 2026
**Método:** conexión directa a la BD + introspección de catálogo + perfilado estadístico

| Meta | Valor |
| :--- | :--- |
| Objetos inspeccionados | 18 tablas, 5 vistas (4 legibles), 4 funciones, 17 secuencias |
| Filas perfiladas | **48.036** |
| Hallazgos | **36** (8 críticos, 14 altos, 6 medios, 8 bajos) |
| Acciones | **35** (B-01 … B-35) + 15 decisiones abiertas (A-01 … A-15) |
| Reproducibilidad | `python database/inspeccion_esquema.py --todo` |

---

## 1. Resumen ejecutivo

> **El sistema no tiene un problema de construcción de datos: tiene un problema de
> gobierno del dato.** La capa de datos está construida y cargada; el catálogo de
> homologación y las funciones de normalización existen. Lo que falta es que las piezas
> **se concilien entre sí**: un catálogo que solo cubre una gasera, un normalizador que
> no cubre el símbolo que separa dos conceptos, columnas que guardan valores de otras
> columnas, y un modelo donde el abandono y los PQRS no tienen lugar.

### Distribución por severidad

| Severidad | Cantidad | Hallazgos |
| :--- | ---: | :--- |
| 🔴 Crítico | 8 | H-01, H-02, H-03, H-05, H-22, H-23, H-24, H-31, H-32, H-34 |
| 🟠 Alto | 14 | H-04, H-06, H-09, H-13, H-14, H-15, H-17, H-26, H-25, H-27, H-28, H-29, H-33, H-34, H-35 |
| 🟡 Medio | 6 | H-07, H-08, H-10, H-11, H-12, H-16 |
| 🔵 Bajo | 4 | H-18, H-19, H-20, H-21 |

### Hallazgos fuera de alcance (contexto histórico)

| H | Tema | Estado |
| ---: | :--- | :--- |
| ~~H-17 (versión anterior)~~ | OCM ya tiene el modelo de datos | 📌 Reencuadrado como destino de la transición, no como fuente. Ver plan 02, Pilar 3 |
| ~~H-18 (versión anterior)~~ | El esquema `auditoria` existe pero no tiene acceso | 📌 Fuera de alcance: no pertenece a `gestion_diaria` |

---

## 2. Hallazgos críticos

### 🔴 H-01 — La documentación del repositorio está desfasada respecto a la realidad

| Elemento | Estado en la documentación | Estado real (19-oct-2026) |
| :--- | :--- | :--- |
| Base de datos central | *"Diseñar el esquema Target (Core)"* — futuro | **Ya existe**: 18 tablas, 48.036 filas |
| Catálogo de homologación | *"Catálogo Maestro Homologado"* — a construir | **Existe parcial**: 40 filas, **solo GasCaribe** |
| Normalización | no existía | **Ya existen 4 funciones** + 5 vistas |
| Auditoría | no existía | **Existe** el esquema `auditoria` (fuera de alcance) |
| Ingesta automatizada | *"Fase 3"* | **No existe.** Cargas manuales por snapshot |

**Impacto** Planificar sobre esa base duplica trabajo ya hecho y subestima el esfuerzo de
gobernanza. **Acción:** B-01. **Resuelto:** ✅

---

### 🔴 H-02 — Abandono y PQRS no tienen un modelo de hechos común

| Fuente | Filas | Tabla |
| :--- | ---: | :--- |
| Abandono | **12.710** | `ceo_abandono` (4.020), `caribe_abandono` (5.064), `gdo_abandono` (831), `surti_abandono` (2.795) |
| PQRS | **6.280** | `gdo_pqrs` (747), `gdo_pqrs_escritas` (86), `gdo_informativo` (4.191), `surti_qr` (1.256) |

El modelo de gestión (8 tablas de atención/outbound, 29.046 filas) **no tiene dónde
alojar el abandono ni los PQRS**, que viven en 8 tablas más con esquemas de columnas
distintos.

**Impacto** Ningún reporte transversal de "llamadas del día" es posible sin un `UNION ALL`
de 4 tablas con 3 plantillas de columnas diferentes. Y el abandono **no tiene ni
asignación de fecha confiable** (ver H-06, H-10).

**Acción:** B-02 (modelo de hechos único con `subtipo_gestion`). **Resuelto:** ❌ Pendiente

---

### 🔴 H-03 — Taxonomía de clasificación fragmentada

**Evidencia** — `resultado_normalizado` de la tabla `clasificacion`:

| Gasera | Filas con resultado | Valores APTA/NO APTA | Variantes APTA | En catálogo |
| :--- | ---: | ---: | ---: | ---: |
| CEO | 2.685 | 2.620 (97.6%) | 13 de 40 | ❌ 22 sin catalogar |
| Efigas | 993 | 988 (99.5%) | 9 de 13 | ❌ 1 sin catalogar |
| Caribe Inbound | 6.797 | 6.797 (100%) | 15 de 20 | ✅ 0 sin catalogar |
| Caribe Outbound | 1.305 | 1.305 (100%) | 26 de 30 | ✅ 0 sin catalogar |
| GDO Inbound | 4.190 | 4.139 (98.8%) | 11 de 11 | ❌ 4 sin catalogar |
| GDO Outbound | 3.005 | 2.990 (99.5%) | 14 de 15 | ❌ 5 sin catalogar |
| Surtigas Inbound | 9.368 | 9.268 (98.9%) | 18 de 18 | ❌ 11 sin catalogar |
| Surtigas Outbound | 298 | 298 (100%) | 7 de 7 | ✅ 0 sin catalogar |

**Impacto** 236 filas quedan sin clasificar (0.5% del volumen), concentradas en CEO y
Surtigas, que son las gaseras con más tráfico. **Acción:** B-03 (cola de revisión).

---

### 🔴 H-05 — 20.2% de las filas están en grupos duplicados

**Evidencia** — llave `(gasera, cabina, contrato, fecha, estado, asesor)`:

| Gasera / cabina | Grupos duplicados |
| :--- | ---: |
| SURTIGAS / INBOUND | 1.436 |
| CEO / INBOUND | 530 |
| CARIBE / INBOUND | 393 |
| GDO / INBOUND | 322 |
| GDO / OUTBOUND | 139 |
| EFIGAS / OUTBOUND | 137 |
| CARIBE / OUTBOUND | 132 |
| SURTIGAS / OUTBOUND | 23 |
| **Total** | **3.114 grupos · 6.297 filas** |

En las fuentes, con llave `(contrato/suscripcion, fecha, estado)`:

| Tabla | Grupos | Filas | % de la tabla |
| :--- | ---: | ---: | ---: |
| `caribe_inbound` | 509 | 2.821 | **41.5%** |
| `ceo_inbound` | 475 | 966 | 35.1% |
| `surti_inbound` | 1.472 | 2.984 | 31.7% |
| `efigas_outbound` | 135 | 281 | 28.1% |
| `gdo_inbound` | 328 | 667 | 15.9% |

**Causa raíz ambigua:** un mismo contrato, mismo día y mismo estado puede ser (a) doble
carga, (b) dos asesores que atendieron al mismo cliente, o (c) multipoliza. (b) y (c) son
**legítimas** y borrarlas destruye información.

**Acción:** B-04 (llave con `fecha_carga` en el hash), B-05 (calificar duplicados). **Resuelto:** ❌

---

### 🔴 H-22 — `APTA` no significa "retención"

**Evidencia** — la decisión D-01 define 4 resultados APTA, y **3 de los 4 implican
cancelación**:

| Resultado APTA | Filas aproximadas | Lectura de negocio |
| :--- | ---: | :--- |
| `cancelado` | ~1.900 | El usuario canceló el servicio |
| `cancelado + venta` | ~1.100 | Canceló **y** se concretó una venta → sí hay retención de cartera |
| `cancelado + reintegro` | ~950 | Canceló **y** se gestionó un reintegro |
| `retenido` | ~3.100 | El usuario fue retenido |

`CANCELADO` es el **63.6% de las filas**. Mezclar "canceló" con "se quedó" en la misma
etiqueta y llamarla "retención" **invierte el indicador**.

**Impacto** Es el riesgo de comunicación más alto del proyecto (R-10 en el doc 010).
**Acción:** B-06 (documentar la semántica literal en el dashboard). **Resuelto:** 📌 Aclarado por D-01/D-02

---

### 🔴 H-23 — `operador` es la empresa operadora, no el asesor

**Evidencia** — dominio completo: `SERVIPROTECCION BPO` (CEO 818, Caribe 2.176, Efigas 436,
Surtigas Out 98), `SERVIPROTECCION`, `ACCION PLUS`, `MIGRACION`, `GNP`, `CREAMOS MARKETING`,
`CYS SERVICIOS INTEGRALES`, `PUNTOS DE VENTAS SAC`, `AC ASOCIADOS`, `COS TELEVENTA`,
`EMERGIA`, `INTELCIA SAS`, `SERDAN`, `LINK MARKETING`, `TELEVENTA VERSA`, `ANDICALL`.

**El asesor individual de retención solo existe en GDO**: `gdo_inbound.nombre_asesor_retencion`
(25 personas) y `gdo_outbound.gestor` (26 personas). En las otras 4 gaseras la única
persona disponible es `asesor_de_venta` (el que vendió la póliza).

**Impacto** La productividad por asesor **no es calculable en 4 de 5 gaseras**. La
granularidad disponible es la empresa de tercerización.
**Acción:** B-07 (dimensión con `tipo` ∈ {EMPRESA, PERSONA}), B-08 (resolver A-11). **Resuelto:** 📌 D-08

---

### 🔴 H-25 — Causa raíz del sangrado: celdas del Excel con columnas pegadas

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

**Impacto** La carga se hizo literal, sin validar que cada valor pertenezca a su
columna. Por eso un valor de `canal` terminó en `operador`. La detección por tabulador
es la forma barata y determinista de cazarlo.
**Acción:** B-18. **Resuelto:** ❌

---

### 🔴 H-24 — Sangrado de columnas: valores de una columna caen en otra

**Evidencia** — filas donde `operador` contiene un valor de `tipo_de_contacto`:

| Gasera | Filas | % |
| :--- | ---: | ---: |
| **Surtigas Inbound** | **1.099** | **11.7%** |
| CEO | 182 | 6.6% |
| Caribe Outbound | 52 | 4.0% |
| Caribe Inbound | 237 | 3.5% |
| Efigas | 19 | 1.9% |
| Surtigas Outbound | 0 | 0.0% |

En Surtigas Inbound `operador` está poblado en solo 1.165 de 9.423 filas (12.4%), y
**1.099 de esas contienen un tipo de contacto**: la columna no existe en el origen.

Otros: `canal` con valor de otra columna (CEO 63, Caribe In 78, Surtigas 43, Caribe Out 2);
`aseguradora` = `operador` (CEO 142); `tipo_de_contacto` con valor de estado (CEO 83).

**Impacto** Cualquier análisis de `operador` o `canal` sobre esas filas es ruido.
**Acción:** B-09 (validación de dominio por columna en la ingesta). **Resuelto:** ❌

---

### 🔴 H-31 — 43 variantes de resultado sin catalogar (236 filas)

> ⚠️ **Cifra de un snapshot, no un techo.** El espacio de variantes es abierto e
> ilimitado (doc 09 §1.2): 43 es lo que había sin catalogar el 19-oct-2026, y la
> cola se seguirá alimentando. El hallazgo real no es "faltan 43", sino que **no
> existe un mecanismo continuo de descubrimiento y aprendizaje** — por eso el §6.1 del
> doc 09 propone el ciclo variante → revisión → aprendizaje, y la acción B-03 incluye
> un criterio de **tiempo de vaciado de la cola**, no de tamaño final.

| Gasera | Variantes | Filas | Ejemplos |
| :--- | ---: | ---: | :--- |
| CEO | **22** | 65 | `cancelado/reintegro` (26), `cancelada + reintegro` (3), `cancelada previa` (4), `datos incompletos` (5), `no atendemos el seguro` (1) |
| Surtigas | **11** | 100 | `venta nueva` (51), `cancelado/devolucion de primas` (14), `datos incompletos` (7), `llamada caida` (6) |
| GDO Outbound | **5** | 15 | `numero errado` (6), `nunca desea adquirir el seguro` (3), `contacto a tercero` (3) |
| GDO Inbound | **4** | 51 | `informacion de siniestro` (23), `cancelado/imposibilidad operativa` (21) |
| Efigas | **1** | 5 | `retnida` (5) |

**Acción:** B-03 (cola de revisión). **Resuelto:** ❌ — **4-5 horas de trabajo humano**

---

### 🔴 H-32 — `normalizar_texto` no normaliza la `/`

**Evidencia** — el catálogo tiene `cancelado /reintegro` (con espacios) → `cancelado + reintegro`
(APTA). Pero `normalizar_texto` solo normaliza el `+`:

| Variante | Gasera | Filas | Resultado |
| :--- | :--- | ---: | :--- |
| `cancelado /reintegro` | — | (catalogada) | ✅ APTA |
| `cancelado/reintegro` | CEO | **26** | ❌ **sin clasificar** |
| `cancelado/reintegro` | GDO Outbound | 1 | ❌ sin clasificar |

**27 filas que deberían ser APTA y hoy no clasifican, por un espacio alrededor de la barra.**

**Acción:** B-10 (corregir `normalizar_texto`). **Resuelto:** ❌ — corrección de una línea

---

#### H-32 (segunda mitad) — La normalización actual es asimétrica

| Clasificación | Variantes | Corregidas | Literales |
| :--- | ---: | ---: | ---: |
| **APTA** | 17 | **13** | 4 |
| **NO APTA** | 23 | **0** | **23** |

El catálogo corrige typos **solo en el lado APTA** (`retenida`→`retenido`, `retnido`→`retenido`,
`cancelada`→`cancelado`), y deja los typos NO APTA tal cual (`no tiene resursos`,
`no tiene resursus`, `no es proteceso de retencion`).

Es coherente con D-03 (el error caro es convertir un APTA en NO APTA), pero deja el lado
NO APTA como una lista de 23 literales sin consolidar: `resultado_normalizado` tiene
**27 valores distintos** en vez de un catálogo cerrado.

**Acción:** B-11 (consolidar los NO APTA en el catálogo maestro). **Resuelto:** ❌

---

## 3. Hallazgos altos

| H | Hallazgo | Evidencia | Impacto | Acción |
| ---: | :--- | :--- | :--- | :--- |
| **H-04** | El catálogo solo cubre GasCaribe | 40 de 40 filas con `gasera='GasCaribe'` | 4 gaseras sin diccionario propio | B-03 |
| **H-06** | Fechas imposibles | `ceo_inbound` → **3748-11-16** (1), `caribe_outbound` → **1970-01-01** (2), `surti_outbound` → **2023-08-13** (1) | Rompen `MIN()`, `MAX()` y los agregados por año | B-12 |
| **H-09** | `fn_parse_fecha` no parsea el 63–100% de 4 columnas | `surti_abandono` 2.795/2.795 (100%), `gdo_informativo` 3.246/3.255 (99.7%), `gdo_pqrs.fecha_atencion` 738/747 (98.8%), `gdo_abandono` 106/167 (63.5%) | 4 tablas no analizables por fecha | B-13 |
| **H-13** | Carga manual por snapshot | `fecha_carga` con **1 solo valor** en 6 tablas; las 7 restantes sin la columna | Sin reproducibilidad ni actualización | B-14, B-15 |
| **H-14** | Sin trazabilidad origen→fila | No hay `sha256`, ni nombre de archivo, ni hoja de origen | Una fila no es rastreable a su Excel | B-15 |
| **H-15** | Dimensiones con alto % de nulos | `localidad` 97.3% (CEO) / 98.8% (Efigas) / 100% (Caribe Out); `operador` 87.6% (Surtigas); `subtipificacion` 100% (CEO) | Sin reporte geográfico ni por motivo en 3 gaseras | B-16 |
| **H-17** | 0 FKs y 0 índices de negocio | Solo las PK en las 18 tablas | Seq scan por fecha o contrato | B-17 |
| **H-26** | Escape `_x000D_` de Excel | 520 filas en `surti_qr.comentario_orden_trabajo`, 182 en `observacion_solicitud`, 13 en `caribe_*.motivo` | Ruido en el texto libre | B-18 |
| **H-25** | Causa raíz del sangrado: celdas con columnas pegadas | `ceo_inbound.operador` = `'SERVIPROTECCION BPO⇥TELEVENTA'` (5); `caribe_inbound.tipo_de_contacto` = `'titular/asegurado⇥Lisbeth Angel⇥SERVIPROTECCION BP'` (1); `surti_qr.observacion_solicitud` = 25 | 45 celdas | B-18 |
| **H-27** | `base` = fecha de carga del lote | Lote `2026-03-02` (64 filas) con ejecuciones del 2026-09-03 al 2026-11-02 (100% fuera) | Usar `base` como fecha de gestión desplaza el periodo | B-19 |
| **H-28** | `subtipificacion` 100% vacía en CEO | 2.749 de 2.749 | CEO no registra motivo de gestión | B-16 |
| **H-29** | `estado` 100% vacía en GDO Inbound | 4.189 de 4.190 nulas | Un dashboard que use `estado` para GDO no retorna nada | B-20 |
| **H-33** | 4 conceptos intrínsecamente ambiguos | `cancelacion` (2), `reintegro` (1), `devolucion` (1), `cancelado/devolucion de primas` (14) | La corrección automática puede invertir la clasificación | B-21 |
| **H-34** | Sin entorno de pruebas ni permiso de escritura | 1 solo esquema; el usuario tiene lectura y no escritura | Las migraciones se probarían sobre 48.036 filas reales | B-22 |
| **H-35** | PII en 13 tablas | Nombre, documento, teléfono, dirección, correo, datos de funcionario | Ley 1581 | B-23 |

---

## 4. Hallazgos medios

| H | Hallazgo | Evidencia |
| ---: | :--- | :--- |
| **H-07** | `anio` es el **año de venta**, no de gestión | CEO: 1900→110, 2022→22, 2023→74, 2024→132, 2025→484, 2026→233, NULL→1.694. Surtigas `ano_venta`: 2014→2 … 2026→1.862, NULL→3.369 |
| **H-08** | 5 formatos de mes | Caribe `"ABRIL 2026"` (con año), GDO In `"Abril"`, GDO Out `"AGOSTO"`, resto `"ABRIL"`, consolidado `"ABRIL"` |
| **H-10** | `gdo_abandono` es un volcado sin delimitar | `contrato` 92.1% nulo, `fecha_llamada` 79.9% nulo, `resultado_final` 88.1% nulo, `gestor` 82.3% nulo, y el campo fecha contiene **nombres de personas** (`"CARLOS DIAZ"`) |
| **H-11** | 3 fuentes PQRS en GDO con solapamiento parcial | `gdo_informativo` (4.191, bitácora) · `gdo_pqrs` (747, maestro de solicitud) · `gdo_pqrs_escritas` (86, maestro con ANS completo). 142 contratos de `informativo` están en `gdo_pqrs`; 61 en `gdo_pqrs_escritas` |
| **H-12** | Columnas con nombres inválidos | `♣` (U+2663, pos. 15 en `gdo_pqrs`), `ORDEN LOCALIDAD`, `tipo poliza`, `columna1/2/62`, `resposable_del_pago_...`, `fehca_de_cancelacion`, `amplicacion_term`, `fech_lega_orden_trabajo` |
| **H-16** | `canal` y `medio_de_recepcion` no están normalizados | `medio_recepcion` mezcla `"6 - Presencial-Aten.Client"`, `"65 - WhatsApp - Aten. Clie"` (truncado), `"TELEVENTA"`, `"PAP"`; 40% es NULL |

---

## 5. Hallazgos bajos (contexto positivo)

| H | Hallazgo | Detalle |
| ---: | :--- | :--- |
| **H-18** | `gdo_gestion_diaria` es un artefacto vacío | 1 columna, 0 filas, 8 KB. Un diseño de vista materializada que nunca se completó |
| **H-19** | La codificación UTF-8 del servidor es **correcta** | Verificado a nivel de bytes: `CANCELACIÓN PREVIA` = `c393` (UTF-8 válido de `Ó`); `normalizar_texto` lo resuelve a `cancelacion previa` ✅. **No diagnosticar codificación desde la salida de consola** |
| **H-20** | Surtigas ya trae columnas de homologación | `validacion` (VÁLIDO 8.160 / REVISAR 1.263), `tipo_contacto_homolog` (7 canónicos), `maduracion_desde_la_venta_queja` (13), `asesor_venta_val` — todas al 100% pobladas. **Es el precedente del proyecto** |
| **H-21** | `gdo_informativo` es una bitácora, no un maestro | `tipo_registro` = REGISTRO ÚNICO (2.392) / DUPLICADO (619); `estado_inf` = PRIMER REGISTRO (1.420) / 2º REGISTRO - N DÍAS. 1.180 filas (28.1%) sin `tipo_registro` ni `resultado`, de las cuales 160 (3.8%) tienen todas las columnas nulas |

---

## 6. Backlog de acciones

### 6.1 Bloque 0 — Decisiones (bloquean todo)

| ID | Decisión | Opciones | Responsable | Estado |
| ---: | :--- | :--- | :--- | :--- |
| **A-11** | ¿El reporte mide productividad por **empresa** o por **asesor**? | (a) Solo empresa; (b) Solo asesor (imposible fuera de GDO); (c) Ambos, con la granularidad explícita en cada panel | Negocio + jefatura | **ABIERTA** |
| **A-12** | ¿El abandono de GDO se incluye, se reprocesa o se declara no confiable? | (a) No confiable, no se carga; (b) Reprocesar con GDO; (c) Cargar con la fecha que exista | GDO + equipo de datos | **ABIERTA** |
| **A-13** | ¿`gdo_informativo` se carga como bitácora o se descarta? | (a) Bitácora aparte; (b) Resolver a estado final por solicitud; (c) Descartar | Equipo de datos | **ABIERTA** |
| **A-14** | ¿Qué campos son obligatorios por gasera? | Lista mínima + fecha de compromiso | Negocio + gaseras | **ABIERTA** |
| **A-15** | ¿El catálogo de normalización sobrevive al corte a OCM? | (a) Sí, para el histórico; (b) Se congela | Equipo de datos + OCM | **ABIERTA** |

### 6.2 Bloque 1 — Desbloqueo inmediato (esfuerzo S, sin dependencias)

| ID | Acción | H | Esf. | Criterio de aceptación |
| ---: | :--- | ---: | :---: | :--- |
| **B-01** | Reescribir los documentos de plan desde el estado real | H-01 | S | ✅ Hecho (plan 01 y 02 reformulados) |
| **B-02** | Modelar el abandono y PQRS en el modelo de hechos común | H-02 | M | `fact_gestion` con `subtipo_gestion` y `fact_pqrs` (doc 03 §6.3–M3/M4) |
| **B-03** | Cerrar la cola de 43 variantes y extender `clasificacion` a las 5 gaseras, **e instalar el ciclo de aprendizaje continuo** | H-03, H-04, H-31 | M | 0 estados sin catalogar hoy en las 5 gaseras **y** cola con vaciado < 7 días |
| **B-04** | Implementar la llave `id_gestion` + `clave_natural` (md5) con `es_duplicado` | H-05 | M | Índice único parcial aplicado; 0 filas perdidas |
| **B-05** | Calificar los duplicados (multigestión vs. doble carga) | H-05 | S | Matriz por gasera con el conteo de cada caso |
| **B-06** | Documentar la semántica literal de `APTA` en el dashboard y en el diccionario de KPIs | H-22 | S | Texto "Apta = a la llamada se le puede hacer gestión" visible en el reporte |
| **B-07** | Crear `dim_operador` con `tipo` ∈ {EMPRESA, PERSONA} | H-23 | S | Los 35 valores de empresa clasificados; 51 personas de GDO con `tipo='PERSONA'` |
| **B-08** | Resolver A-11 con la jefatura | H-23 | S | Acta con la granularidad acordada |
| **B-09** | Validar el dominio de cada columna en la ingesta y mandar a cuarentena lo que no aplique | H-24 | M | 0 filas con sangrado en la siguiente carga |
| **B-10** | Corregir `normalizar_texto` para normalizar la `/` | H-32 | S | `cancelado/reintegro` clasifica como APTA; 27 filas resueltas |
| **B-03b** | **Implementar el ciclo de descubrimiento continuo**: fuzzy contra conceptos + cola permanente + aprendizaje de variantes | H-31 | M | Toda variante nueva se resuelve por aproximación o entra a la cola; el tiempo de vaciado de la cola se mide semanalmente |
| **B-11** | Consolidar los 23 NO APTA literales en el catálogo maestro | H-34 | M | `resultado_normalizado` con ≤ 15 valores distintos |
| **B-12** | Regla de rango de fechas `[2025-01-01, hoy+1]` + cuarentena | H-06 | M | Las 4 fechas imposibles van a cuarentena, no al modelo |
| **B-13** | Extender `fn_parse_fecha` (4 formatos) y validarla contra las 48.036 filas | H-09 | M | ≥ 99% de las fechas de las 9 columnas texto son parseables |
| **B-14** | Crear `dim_carga` y `dim_origen` (bitácora con `sha256`) | H-13, H-14 | M | Cada fila cargada es rastreable a su archivo y lote |
| **B-15** | Reingerir de forma reproducible y cuadrar con el actual | H-13, H-14 | L | Cuadre 100% o diferencia documentada y explicada |
| **B-16** | Negociar campos obligatorios por gasera y cuantificar nulos | H-15, H-28 | M | Tabla de compromisos por gasera firmada |
| **B-17** | Crear los índices de negocio del modelo nuevo | H-17 | S | `EXPLAIN` de la consulta mensual no hace seq scan |
| **B-18** | Limpieza de artefactos de Excel en la ingesta (L-01…L-03) | H-26, H-25 | M | 0 celdas con tabulador, `_x000D_` o salto de línea en el destino |
| **B-19** | Marcar `base` como "no usar para análisis" en el mapeo | H-27 | S | La regla está en el doc 02 y en el diccionario de datos |
| **B-20** | Mapear el resultado de GDO desde `resultado_final` / `resultado_de_retencion` | H-29 | S | El mapeo del doc 02 §5.4 aplicado y verificado |
| **B-21** | Guardia de conceptos ambiguos en el algoritmo de normalización | H-33 | S | `devolucion`, `reintegro` y `previa` nunca se corrigen solos |
| **B-22** | Habilitar un entorno de pruebas (o una copia para migraciones) | H-34 | S | Las migraciones M0–M8 se probaron sin riesgo |
| **B-23** | Minimización de PII: vistas de consumo sin datos personales | H-35 | S | 0 columnas de PII en las vistas de reporte |
| **B-24** | Eliminar `gdo_gestion_diaria` | H-18 | S | La tabla no existe (0 filas) |
| **B-25** | Pedir a cada gasera el layout real de cada pestaña de Excel | H-15 | M | Mapa de columnas por archivo; resuelve el bloque de 27% sin datos de Caribe |
| **B-26** | Confirmar si existen septiembre y octubre de Surtigas Inbound | H-15 | S | Respuesta escrita de Surtigas |
| **B-27** | Solicitar permiso de escritura acotado sobre `gestion_diaria` | H-34 | S | El rol de ingesta puede escribir solo en ese esquema |
| **B-28** | Adoptar el catálogo de 52 motivos de GDO como `dim_motivo` | H-15 | M | `dim_motivo` con cobertura ≥ 90% de los motivos de las 5 gaseras |
| **B-29** | Extender a las 4 gaseras restantes el modelo de Surtigas (`validacion`, `tipo_contacto_homolog`) | H-20 | M | Las 5 gaseras con las 2 columnas al ≥ 90% |
| **B-30** | Consolidar los 3 catálogos de motivo en texto libre (355 de Caribe, 184 de GDO) | H-15 | L | `dim_motivo` con ≤ 80 filas y cobertura ≥ 90% |
| **B-31** | Redactar el doc 06 (Definición de KPIs) con el negocio | — | M | KPIs aprobados con su fórmula y su fuente |
| **B-32** | Redactar el doc 07 (Transición a OCM): casamiento y plan de apagado | — | M | % de casamiento OCM×planilla medido |
| **B-33** | Implementar la vista de consumo `v_gestion_diaria` (M7) | H-02 | S | La vista responde y cuadra con el staging |
| **B-34** | Panel de calidad del dato en el dashboard | H-13 | S | Cargas, rechazos, `POR_REVISAR` y cobertura visibles |
| **B-35** | Separar `anio_gestion` de `anio_venta` | H-07 | S | `anio_gestion = EXTRACT(YEAR FROM fecha_gestion)` en el 100% |

### 6.3 Esfuerzo

| Esfuerzo | Acciones | % |
| :--- | ---: | ---: |
| **S** (< 1 día) | 13 | 37% |
| **M** (1-2 semanas) | 16 | 46% |
| **L** (> 1 mes) | 6 | 17% |
| **Total estimado** | **35** | **~9-11 semanas-persona** |

---

## 7. Matriz de trazabilidad

| H | Severidad | Acciones | Decisión |
| ---: | :--- | :--- | :--- |
| H-01 | 🔴 | B-01 | — |
| H-02 | 🔴 | B-02, B-33 | — |
| H-03 | 🔴 | B-03 | — |
| H-04 | 🟠 | B-03 | — |
| H-05 | 🔴 | B-04, B-05 | A-03 |
| H-06 | 🟠 | B-12 | — |
| H-07 | 🟡 | B-35 | — |
| H-08 | 🟡 | B-19 | — |
| H-09 | 🟠 | B-13 | — |
| H-10 | 🟡 | — | A-12 |
| H-11 | 🟡 | — | A-13 |
| H-12 | 🟡 | B-17 (parcial) | — |
| H-13 | 🟠 | B-14, B-15, B-34 | — |
| H-14 | 🟠 | B-14, B-15 | — |
| H-15 | 🟠 | B-16, B-25, B-28, B-30 | A-14 |
| H-16 | 🟡 | B-17 (parcial) | — |
| H-17 | 🟠 | B-17 | — |
| H-18 | 🔵 | B-24 | — |
| H-19 | 🔵 | B-32 (referencia) | — |
| H-20 | 🔵 | B-29 | — |
| H-21 | 🔵 | — | A-13 |
| H-22 | 🔴 | B-06, B-31 | — |
| H-23 | 🔴 | B-07, B-08 | **A-11** |
| H-24 | 🔴 | B-09 | — |
| H-25 | 🔴 | B-18 | — |
| H-26 | 🟠 | B-18 | — |
| H-25 | 🟠 | B-18 | — |
| H-27 | 🟠 | B-19 | — |
| H-28 | 🟠 | B-16 | A-14 |
| H-29 | 🟠 | B-20 | — |
| H-31 | 🔴 | B-03, B-03b | — |
| H-32 | 🔴 | B-10 | — |
| H-33 | 🟠 | B-21 | — |
| H-34 | 🔴 | B-11 | — |
| H-34 | 🟠 | B-22, B-27 | — |
| H-35 | 🟠 | B-23 | — |

---

## 8. Definición de "Listo"

Una acción está **cerrada** cuando:

1. ✅ Está implementada y **verificada con una consulta reproducible** contra la BD.
2. ✅ Se cumple el criterio de aceptación de la tabla del ítem.
3. ✅ El impacto está documentado en el doc 01 (diccionario), 04 (mapeo) o 05 (modelo).
4. ✅ Si cambió un catálogo o una regla, se actualizó `gestion_diaria.clasificacion` y su vista de auditoría.
5. ✅ No se introdujeron regresiones: `python database/inspeccion_esquema.py --todo` corre limpio.

> **Regla de oro vigente:** ninguna acción se cierra sin evidencia consultable en la
> base de datos. Un cierre basado en la suposición no es un cierre.
