# 05. Calidad de Datos

**Proyecto:** Gestión Diaria Promigas
**Alcance:** esquema `gestion_diaria` de `DataCenter_Promigas` (16 tablas de datos, 48.036 filas)
**Fecha:** 19 de octubre de 2026
**Reproducibilidad:** `python database/inspeccion_esquema.py --calidad`

---

## 1. Resumen de calidad

| Dimensión | Estado | Veredicto |
| :--- | :--- | :---: |
| **Completitud de identificadores** (contrato, estado, fecha) | 73–100% | 🟢 Aceptable |
| **Completitud de contexto** (localidad, operador, motivo) | 57–100% nulos | 🔴 Crítico |
| **Validez temporal** | 4 fechas imposibles; 63–100% de fechas no parseables en 4 tablas | 🔴 Crítico |
| **Consistencia de catálogo** | 43 variantes sin catalogar; normalización asimétrica | 🔴 Crítico |
| **Unicidad** | 3.114 grupos duplicados (20.2%) | 🔴 Crítico |
| **Integridad de columna** | 1.589 filas con valores de otra columna | 🔴 Crítico |
| **Trazabilidad origen→fila** | Inexistente (sin bitácora ni hash) | 🔴 Crítico |
| **Codificación** | UTF-8 correcto en todo el servidor | 🟢 Correcto |
| **Integridad referencial** | 0 FKs, 0 índices de negocio | 🟠 Riesgo medio |
| **Actualización** | Cargas manuales por snapshot, sin ingesta automatizada | 🟠 Alto |

---

## 2. Completitud por tabla

### 2.1 `ceo_inbound` (2.749) — CEO Inbound

| Columna | Nulos | % | Severidad |
| :--- | ---: | ---: | :--- |
| `subtipificacion` | 2.749 | **100.0%** | 🔴 Columna vacía (H-28) |
| `localidad` | 2,676 | **97.3%** | 🔴 (H-30) |
| `anio` | 1,694 | **61.6%** | 🔴 (H-07) |
| `fecha_de_venta` | 1,088 | 39.6% | 🟠 |
| `operador` | 1,055 | 38.4% | 🟠 (H-23, H-24) |
| `asesor_de_venta` | 454 | 16.5% | 🟡 |
| `canal` | 416 | 15.1% | 🟡 (H-24) |
| `fecha_de_ejecucion` | 153 | 5.6% | 🟡 (H-06) |
| `tipo_de_contacto` | 104 | 3.8% | 🟡 |
| `aseguradora` | 90 | 3.3% | 🟢 |
| `producto` | 75 | 2.7% | 🟢 |
| `estado` | 64 | 2.3% | 🟢 |
| `contrato` | 43 | 1.6% | 🟢 |
| `medio_de_recepcion` | 2,749 | **100.0%** | 🔴 Columna vacía |
| `mes`, `cabina`, `base` | 0 | 0.0% | 🟢 |

> **CEO no registra motivo de gestión** y **no registra locality**. Es la gasera con más
> contexto faltante entre las que sí tienen volumen.

### 2.2 `efigas_outbound` (999) — Efigas Outbound

| Columna | Nulos | % | Severidad |
| :--- | ---: | ---: | :--- |
| `localidad` | 987 | **98.8%** | 🔴 |
| `anio` | 641 | **64.2%** | 🔴 |
| `subtipificacion` | 514 | **51.5%** | 🔴 |
| `fecha_de_venta` | 383 | 38.3% | 🟠 |
| `operador` | 373 | 37.3% | 🟠 |
| `fecha_de_ejecucion` | 172 | **17.2%** | 🟠 |
| `estado` | 6 | 0.6% | 🟢 |
| `producto` | 4 | 0.4% | 🟢 |
| `tipo_de_contacto` | 1 | 0.1% | 🟢 |
| `contrato`, `canal`, `aseguradora`, `base`, `mes` | 0 | 0.0% | 🟢 |

> Efigas es la **más limpia en identificadores** y la que más contexto lacks. 172 filas
> (17.2%) no son ubicables en el tiempo.

### 2.3 `caribe_inbound` (6.797) — Gas Caribe Inbound

| Columna | Nulos | % | Severidad |
| :--- | ---: | ---: | :--- |
| `localidad` | 5,374 | **79.1%** | 🔴 |
| `fecha_de_venta` | 2,733 | 40.2% | 🟠 |
| `aseguradora` | 1,973 | 29.0% | 🟠 |
| `asesor_de_venta` | 1,986 | 29.2% | 🟠 |
| `subtipificacion` | 1,934 | 28.5% | 🟠 |
| `canal` | 1,953 | 28.7% | 🟠 |
| `documento` | 1,920 | 28.2% | 🟠 PII |
| `usuario` | 1,809 | 26.6% | 🟠 PII |
| `telefono` | 1,825 | 26.9% | 🟠 PII |
| `gestor` | 1,855 | 27.3% | 🟠 |
| `contrato` | 1,828 | **26.9%** | 🟠 |
| `fecha_de_ejecucion` | 1,774 | **26.1%** | 🟠 |
| `tipo_de_contacto` | 1,900 | 28.0% | 🟠 |
| `producto` | 1,856 | 27.3% | 🟠 |
| `estado`, `mes`, `anio` | 0 | 0.0% | 🟢 |

> 🔴 **Bloque de ~27% sin datos**: 1.774 sin fecha **y** 1.828 sin contrato **y** 1.825
> sin teléfono **y** 1.953 sin canal. El patrón sugiere **filas con otro layout de
> columnas** dentro del mismo Excel. Requiere el layout real de cada pestaña (B-25).

### 2.4 `caribe_outbound` (1.305) — Gas Caribe Outbound

| Columna | Nulos | % | Severidad |
| :--- | ---: | ---: | :--- |
| `localidad` | 1,305 | **100.0%** | 🔴 Columna vacía |
| `fecha_gestion` | 414 | 31.7% | 🟠 |
| `fecha_de_venta` | 365 | 28.0% | 🟠 |
| `asesor_de_venta` | 83 | 6.4% | 🟡 |
| `tipo_de_contacto` | 78 | 6.0% | 🟡 |
| `canal` | 77 | 5.9% | 🟡 |
| `producto` | 55 | 4.2% | 🟡 |
| `operador` | 46 | 3.5% | 🟢 |
| `subtipificacion` | 31 | 2.4% | 🟢 |
| `fecha_de_ejecucion` | 22 | 1.7% | 🟡 |
| `contrato`, `estado`, `mes`, `anio`, `aseguradora` | 0 | 0.0% | 🟢 |

### 2.5 `surti_inbound` (9.423) — Surtigas Inbound

| Columna | Nulos | % | Severidad |
| :--- | ---: | ---: | :--- |
| `operador` | 8,258 | **87.6%** | 🔴 (H-24: el 12.4% poblado no es operador) |
| `subtipificacion` | 6,666 | **70.7%** | 🔴 |
| `localidad` | 5,407 | **57.4%** | 🔴 |
| `ano_venta` | 3,369 | 35.8% | 🟠 (H-07) |
| `fecha_de_venta` | 1,381 | 14.7% | 🟡 |
| `asesor_de_venta` | 303 | 3.2% | 🟡 |
| `canal` | 275 | 2.9% | 🟢 |
| `aseguradora` | 193 | 2.0% | 🟢 |
| `tipo_de_contacto` | 113 | 1.2% | 🟢 |
| `estado` | 55 | 0.6% | 🟢 |
| `fecha_de_ejecucion` | 4 | 0.0% | 🟢 |
| `suscripcion`, `mes`, `validacion`, `tipo_contacto_homolog` | 0 | 0.0% | 🟢 |

> **La gasera con más volumen y menos contexto.** Sin `operador` real no hay
> productividad por empresa. Sin `subtipificacion` no hay motivo de pérdida.
> Lo que sí está completo: `validacion` y `tipo_contacto_homolog` (H-20, el precedente).

### 2.6 `gdo_inbound` (4.190) — GDO Inbound

| Columna | Nulos | % | Severidad |
| :--- | ---: | ---: | :--- |
| `estado` | 4,189 | **100.0%** | 🔴 Columna vacía (H-29) |
| `localidad` | 177 | 4.2% | 🟡 |
| `canal` | 180 | 4.3% | 🟡 |
| `entidad_facturacion` | 114 | 2.7% | 🟡 |
| `subtipificacion` | 112 | 2.7% | 🟡 |
| `categoria_detalle` | 99 | 2.4% | 🟡 |
| `tipo_contacto` | 59 | 1.4% | 🟢 |
| `producto_1` | 34 | 0.8% | 🟢 |
| `nombre_asesor_retencion` | 34 | 0.8% | 🟢 |
| `contrato` | 6 | 0.1% | 🟢 |
| `resultado_final`, `fecha_de_llamada`, `mes` | 0 | 0.0% | 🟢 |

> **GDO es la gasera mejor estructurada y el estándar de calidad del proyecto.**
> `resultado_final`, `fecha_de_llamada`, `mes`, `contrato` y `subtipificacion`
> prácticamente completos. Es la única con el asesor de retención individual (H-23).

### 2.7 `gdo_outbound` (3.284) — GDO Outbound

| Columna | Nulos | % |
| :--- | ---: | ---: |
| `resultado_de_retencion` | 279 | 8.5% |
| `tipifiacion_de_pqr` | 278 | 8.5% |
| `estado` | 257 | 7.8% |
| `canal` | 255 | 7.8% |
| `aseguradora` | 246 | 7.5% |
| `fecha_ejecucion` | 234 | 7.1% |
| `gestor` | 218 | 6.6% |
| `contrato`, `producto`, `categoria`, `subcategoria`, `ciclo_solicitud`, `nombre_solicitante`, `localidad_solicitud`, `mes` | ≤1 | ≤0.1% |

### 2.8 Tablas de abandono

| Tabla | Filas | Columnas críticas con nulo |
| :--- | ---: | :--- |
| `ceo_abandono` | 4.020 | `hora` **99.2%**, `contrato` **70.2%**, `fecha_llamada` **62.4%**, `localidad` 86.9%, `nombre_cliente` 69.5% |
| `caribe_abandono` | 5.064 | `localidad` 81.9%, `nombre_cliente` 65.7%, `contrato` 66.2%; **`fecha_llamada` y `hora` al 100%** ✅ |
| `gdo_abandono` | 831 | `contrato` **92.1%**, `nombre_cliente` 89.2%, `resultado_final` 88.1%, `gestor` 82.3%, `fecha_llamada` **79.9%** (H-10) |
| `surti_abandono` | 2.795 | Sin nulos, pero **sin columna `contrato`** y con fecha 100% no parseable (H-09) |

> **Conclusión sobre abandono:** solo `caribe_abandono` tiene fecha y hora utilizables.
> **2.508 abandonos de CEO y 2.131 de GDO no tienen fecha utilizable** (21.2% del total).

---

## 3. Validez temporal

### 3.1 Fechas imposibles (tipadas como `date`)

| Tabla | Columna | Rango | Fuera de [2025-01-01, 2026-12-31] |
| :--- | :--- | :--- | ---: |
| `ceo_inbound` | `fecha_de_ejecucion` | 2025-04-08 → **3748-11-16** | 1 |
| `caribe_outbound` | `fecha_de_ejecucion` | **1970-01-01** → 2026-12-03 | 2 |
| `surti_outbound` | `fecha_de_ejecucion` | **2023-08-13** → 2026-09-07 | 1 |

### 3.2 Fechas en texto no parseables (H-09)

| Tabla | Columna | Con valor | Parseables | No parseables | % |
| :--- | :--- | ---: | ---: | ---: | ---: |
| `surti_abandono` | `fecha_llamada` | 2,795 | **0** | 2,795 | **100.0%** |
| `gdo_informativo` | `fecha_regi` | 3,255 | 9 | 3,246 | **99.7%** |
| `gdo_pqrs` | `fecha_atencion` | 747 | 9 | 738 | **98.8%** |
| `gdo_abandono` | `fecha_llamada` | 167 | 61 | 106 | **63.5%** |
| `gdo_outbound` | `fecha_ejecucion` | 3,050 | 3,048 | 2 | 0.1% |
| `gdo_inbound` | `fecha_de_llamada` | 4,190 | 4,190 | 0 | 0.0% |
| `gdo_pqrs` | `fecha_registro_solicitud` | 747 | 747 | 0 | 0.0% |
| `surti_qr` | `fecha_registro_solicitud` | 1,256 | 1,256 | 0 | 0.0% |

**Formatos reales no soportados por `fn_parse_fecha`:**

| Formato | Origen | Ejemplo |
| :--- | :--- | :--- |
| `DD/MM/YYYY HH:MM:SS a. m.` | `surti_abandono.fecha_llamada` | `10/06/2026 10:05:04 a. m.` |
| `MMM-YY` | `gdo_informativo.fecha_regi` | `jun-26` (2.811 filas) |
| `MM/DD/YYYY` | `gdo_informativo.fecha_regi` | `8/18/2026` (208 filas) |
| `DD/MM/YYYY HH:MM:SS a.8./p` | `gdo_informativo.fecha_regi` | `23/08/2026 8:28:48 a.8./p` |
| Texto libre | `gdo_abandono.fecha_llamada` | `CARLOS DIAZ` |

---

## 4. Consistencia de catálogo

### 4.1 Cobertura por gasera (H-03, H-31)

| Gasera | Estados distintos | Catalogados | **Sin catalogar** | Filas afectadas |
| :--- | ---: | ---: | ---: | ---: |
| CEO | 40 | 18 | **22** | 65 |
| Efigas | 13 | 12 | **1** | 5 |
| Caribe Inbound | 20 | 20 | **0** ✅ | 0 |
| Caribe Outbound | 30 | 30 | **0** ✅ | 0 |
| GDO Inbound | 11 | 7 | **4** | 51 |
| GDO Outbound | 15 | 10 | **5** | 15 |
| Surtigas Inbound | 18 | 7 | **11** | 100 |
| Surtigas Outbound | 7 | 7 | **0** ✅ | 0 |
| **Total** | | | **43** | **236** |

### 4.2 Normalización asimétrica (H-32)

| Clasificación | Variantes | Corregidas | Literales |
| :--- | ---: | ---: | ---: |
| **APTA** | 17 | **13** | 4 |
| **NO APTA** | 23 | **0** | **23** |

### 4.3 Fallos por un solo carácter (H-32)

| Variante | Gasera | Filas | Concepto catalogado |
| :--- | :--- | ---: | :--- |
| `cancelado/reintegro` | CEO | 26 | `cancelado /reintegro` (difiere en un espacio) |
| `cancelado/reintegro` | GDO Outbound | 1 | idem |
| `cancelada + reintegro` | CEO | 3 | `cancelado + reintegro` |
| `cancelada previa` | CEO | 4 | `cancelado previa` |
| `retnida` | Efigas | 5 | `retenida` |
| `NO ES PROTECESO DE RETENCIÓN` | Caribe Outbound | 2 | `no es proceso de retencion` |

### 4.4 Conceptos ambiguos para la corrección automática (H-33)

| Variante | Gasera | Filas | Ambigüedad |
| :--- | :--- | ---: | :--- |
| `cancelacion` | CEO | 2 | ¿"cancelación previa" (NO APTA) o "cancelado" (APTA)? |
| `reintegro` | CEO | 1 | ¿"cancelado + reintegro" (APTA)? |
| `devolucion` | CEO | 1 | ¿"cancelado + devolución de primas" (NO APTA)? |
| `cancelado/devolucion de primas` | Surtigas | 14 | NO APTA, pero se parece a un APTA |

---

## 5. Unicidad y duplicados (H-05)

| Gasera / cabina | Grupos duplicados (llave de 6 campos) |
| :--- | ---: |
| SURTIGAS / INBOUND | 1.436 |
| CEO / INBOUND | 530 |
| CARIBE / INBOUND | 393 |
| GDO / INBOUND | 322 |
| GDO / OUTBOUND | 139 |
| EFIGAS / OUTBOUND | 137 |
| CARIBE / OUTBOUND | 132 |
| SURTIGAS / OUTBOUND | 23 |
| **Total** | **3.114 grupos · 6.297 filas (20.2%)** |

Por tabla fuente, con llave `(contrato/suscripcion, fecha, estado)`:

| Tabla | Grupos | Filas | % de la tabla |
| :--- | ---: | ---: | ---: |
| `caribe_inbound` | 509 | 2.821 | **41.5%** |
| `ceo_inbound` | 475 | 966 | 35.1% |
| `surti_inbound` | 1.472 | 2.984 | 31.7% |
| `efigas_outbound` | 135 | 281 | 28.1% |
| `gdo_inbound` | 328 | 667 | 15.9% |

---

## 6. Integridad de columna (H-23, H-24, H-25, H-26)

| Chequeo | Resultado |
| :--- | --- |
| `operador` con valor de `tipo_de_contacto` | **1.589 filas** (Surtigas 1.099 · CEO 182 · Caribe In 237 · Caribe Out 52 · Efigas 19) |
| `canal` con valor de otra columna | **186 filas** (Caribe In 78 · CEO 63 · Surtigas 43 · Caribe Out 2) |
| `aseguradora` = `operador` | **158 filas** (CEO 142 · Caribe In 16) |
| `tipo_de_contacto` con valor de estado | **83 filas** (CEO) |
| Celdas con tabulador (2+ columnas pegadas) | **45 celdas** en 8 tablas |
| Celdas con escape `_x000D_` | **740 celdas** en 7 tablas |
| Celdas con salto de línea | **740 celdas** en 7 tablas |

Detalle de los tabuladores y los escapes: doc 01 §3.

---

## 7. PII (H-35)

| Dato | Columnas | Nivel |
| :--- | :--- | :---: |
| Nombre del cliente | `ceo_abandono`, `caribe_abandono`, `gdo_abandono`, `gdo_inbound`, `gdo_outbound`, `surti_qr` | 🔴 Alto |
| Documento | `*.identificacion_usuario`, `*.identificacion_solicitante`, `gdo_inbound.cedula` | 🔴 Alto |
| Teléfono | `*.telefono`, `*.numbercall`, `*.cel`, `surti_qr.telefono_*` | 🔴 Alto |
| Dirección | `gdo_outbound.direccion`, `*.direccion_orden_trabajo`, `surti_qr.direccion_solicitud` | 🔴 Alto |
| Correo | `gdo_outbound.correo`, `caribe_inbound.correo_reintegro` | 🔴 Alto |
| Datos del funcionario | `gdo_informativo.funcionario`, `.terminal`, `.tabulacion`, `.cel` | 🟠 Medio |

> **Regla operativa:** ningún reporte publicado debe incluir estas columnas. Los reportes
> usan `contrato` como identificador. (B-23)

---

## 8. Reglas de validación a implementar

| # | Regla | Dimensión | Severidad | Origen |
| ---: | :--- | :--- | :--- | :--- |
| R-01 | `fecha_gestion` en `[2025-01-01, CURRENT_DATE + 1]` | Rango | Error | H-06 |
| R-02 | `fecha_gestion` NOT NULL en la tabla de hechos | Completitud | Error | H-15 |
| R-03 | `contrato` NOT NULL | Completitud | Error | H-15 |
| R-04 | `estado` ∈ catálogo maestro (5 gaseras) | Validez | Error | H-03, H-31 |
| R-05 | `mes` ∈ {ENERO…DICIEMBRE} | Dominio | Error | H-08 |
| R-06 | `mes` no contiene el año | Formato | Error | H-08 |
| R-07 | `anio_gestion = EXTRACT(YEAR FROM fecha_gestion)` | Consistencia | Error | H-07 |
| R-08 | `clasificacion` derivada por función determinista | Consistencia | Error | H-03 |
| R-09 | `subtipo_gestion` ∈ {ATENCION, ABANDONO, PQRS} | Dominio | Error | H-02 |
| R-10 | Unicidad de `(gasera, cabina, contrato, fecha, estado, tipo_contacto_norm)` | Unicidad | Advertencia | H-05 |
| R-11 | `telefono` con formato E.164 | Formato | Advertencia | H-35 |
| R-12 | `localidad`, `operador` y `subtipificacion` NOT NULL | Completitud | Advertencia | H-15, H-28, H-30 |
| R-13 | `subtipificacion` ∈ maestro de motivos (52 de GDO) | Dominio | Advertencia | H-15 |
| R-14 | `base` nunca se usa como fecha de análisis | Lógica | Error | H-27 |
| R-15 | `operador` ∈ dominio de empresas;D-8 con `tipo='PERSONA'` | Dominio | Error | H-23 |
| R-16 | `canal` ∈ {TELEVENTA, SAC, PAP, DOBLE CUPON, PUNTO FIJO, …} | Dominio | Error | H-24 |
| R-17 | Ningún valor contiene tabulador, `\n`, `\r` ni `_x000D_` | Formato | Error | H-25, H-26 |
| R-18 | `resultado_original` nunca vacío | Completitud | Error | H-22 |
| R-19 | Registro de carga con conteo de filas y hash del archivo | Trazabilidad | Error | H-13, H-14 |
| R-20 | Quarantine de registros rechazados (nunca borrado silencioso) | Trazabilidad | Advertencia | H-13 |

---

## 9. Métricas de aceptación para el dashboard

| KPI | Meta | Medición |
| :--- | :--- | :--- |
| Cuadre staging → `fact_gestion` | 100% | `EXCEPT` en ambas direcciones |
| Taxonomía unificada | 1 esquema de resultado para las 5 gaseras | `COUNT(DISTINCT clasificacion_norm)` |
| Estados sin catalogar | 0 | `v_valores_sin_mapear` extendido a 5 gaseras |
| Registros en `POR_REVISAR` | < 0.5% **y visibles** | `resultado_pendiente` |
| Cobertura de abandono | 100% con fecha válida | `COUNT(fecha_gestion)/COUNT(*)` |
| Duplicados | < 2% | grupos duplicados / total |
| Completitud de contexto | `operador` < 20% nulos, `localidad` < 30% nulos | perfil por gasera |
| Filas con sangrado | 0 | R-15, R-16, R-17 |
| Cargas con bitácora completa | 100% | `dim_carga` |
| Actualización | Diaria con `id_carga` | `max(fecha_carga)` |
