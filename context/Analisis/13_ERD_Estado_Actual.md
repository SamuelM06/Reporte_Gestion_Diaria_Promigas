# 13. ERD Estado Actual — Esquema `gestion_diaria` (staging)

**Proyecto:** Gestión Diaria Promigas  
**Esquema:** `gestion_diaria` de `DataCenter_Promigas` (PostgreSQL 16.14)  
**Fecha:** 19 de octubre de 2026  
**Fuente visual:** `context/Analisis/Data_Db/gestion_diaria_documentacion.pdf` (ERD exportado)  
**Fuente de datos:** `01_Diccionario_de_Datos.md`, `03_Modelo_Datos.md`, `04_Hallazgos_y_Backlog.md`, `05_Calidad_de_Datos.md`, `07_Estructura_de_datos.md`

> **Compañero textual del PDF:** este documento es la versión versionable, buscable y editable
> en Git del diagrama ERD visual. El PDF sirve para presentaciones; este `.md` sirve para
> trabajo diario y para que el equipo pueda referenciarlo desde otros documentos.

---

## 1. Resumen ejecutivo (métricas del esquema actual)

| Métrica | Valor | Fuente |
| :--- | ---: | :--- |
| Tablas totales en el esquema | **18** | `03_Modelo_Datos.md` §3.2 |
| Tablas con datos | **16** | `07_Estructura_de_datos.md` §6 |
| Filas totales | **48.036** | `01_Diccionario` §2.2 |
| Foreign Keys declaradas | **0** | `03_Modelo` §3.2 |
| Índices de negocio | **0** | `07_Estructura` §6 |
| Filas con sangrado de columnas | **1.589** | `04_Hallazgos` H-24 |
| Variantes de resultado sin catalogar | **43** (236 filas) | `04_Hallazgos` H-31 |
| Formatos distintos de `mes` | **5** | `04_Hallazgos` H-08 |
| Funciones de normalización | **4** | `07_Estructura` §6 |
| Vistas | **5** (4 legibles) | `07_Estructura` §6 |

---

## 2. ERD — Diagrama entidad-relación lógico (estado actual)

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
    gdo_gestion_diaria { int id PK | int filas = 0 }

    ceo_inbound }o..o| clasificacion : "por estado (LEFT JOIN manual)"
    efigas_outbound }o..o| clasificacion : ""
    caribe_inbound }o..o| clasificacion : ""
    gdo_inbound }o..o| clasificacion : ""
    surti_inbound }o..o| clasificacion : ""
```

> **Importante:** todas las relaciones son **lógicas**, no físicas. No hay FKs declaradas.
> El join con `clasificacion` solo funciona para GasCaribe (única gasera en el catálogo).

---

## 3. Mapa por familias

### 3.1 Familia ATENCIÓN — 8 tablas · 29.046 filas

| Tabla | Gasera | Cabina | Filas | PK | FK | Índices negocio |
| :--- | :--- | :--- | ---: | :--- | :---: | :---: |
| `ceo_inbound` | CEO | Inbound | 2.749 | `id` | 0 | 0 |
| `efigas_outbound` | Efigas | Outbound | 999 | `id` | 0 | 0 |
| `caribe_inbound` | Caribe | Inbound | 6.797 | `id` | 0 | 0 |
| `caribe_outbound` | Caribe | Outbound | 1.305 | `id` | 0 | 0 |
| `gdo_inbound` | GDO | Inbound | 4.190 | `id` | 0 | 0 |
| `gdo_outbound` | GDO | Outbound | 3.284 | `id` | 0 | 0 |
| `surti_inbound` | Surtigas | Inbound | 9.423 | `id` | 0 | 0 |
| `surti_outbound` | Surtigas | Outbound | 299 | `id` | 0 | 0 |

**Patrón de columnas (común con variaciones por gasera):**

| Columna | Tipo | Presente en | Nota |
| :--- | :--- | :--- | :--- |
| `id` | serial/bigint | Todas | PK sintética, no viene del Excel |
| `distribuidora` | varchar | Todas (excepto Caribe, GDO) | Constante por tabla |
| `contrato` / `suscripcion` | varchar/bigint | Todas | Llave de negocio principal. Surtigas usa `suscripcion` |
| `fecha_de_ejecucion` / `fecha_*` | date/text | Todas | Fecha de gestión. 4 formatos distintos entre tablas |
| `estado` / `resultado_final` / `resultado_de_retencion` | varchar/text | Todas | Resultado crudo del asesor. GDO usa `resultado_final` (Inbound) y `resultado_de_retencion` (Outbound) |
| `operador` | varchar/text | Todas | **Empresa BPO, no persona** (H-23). 87.6% nulo en Surtigas |
| `canal` | varchar/text | Todas | TELEVENTA, SAC, PAP, DOBLE CUPON, PUNTO FIJO |
| `producto`, `aseguradora`, `tipo_de_contacto`, `subtipificacion`, `motivo` | varchar/text | La mayoría | Contexto de la gestión |
| `fecha_de_venta`, `asesor_de_venta` | date/varchar | La mayoría | Fecha/asesor de la venta original (eje distinto) |
| `anio` | integer | La mayoría | **Año de VENTA, no de gestión** (H-07) |
| `mes` | varchar | Todas | 5 formatos distintos según gasera (H-08) |
| `cabina` | varchar | Algunas | INBOUND/OUTBOUND. Constante por tabla |
| `fecha_carga` | timestamp | Solo 6 tablas | Snapshot único en todas |
| `nombre_asesor_retencion` | text | Solo `gdo_inbound` | **Única columna con asesor persona** (H-23) |
| `gestor` | text | Solo `gdo_outbound` | **Única columna con asesor persona** (H-23) |

---

### 3.2 Familia ABANDONO — 4 tablas · 12.710 filas

| Tabla | Gasera | Filas | Fecha utilizable | Contrato utilizable | Veredicto |
| :--- | :--- | ---: | :--- | :--- | :--- |
| `ceo_abandono` | CEO | 4.020 | 37.6% (2.508 sin fecha) | 29.8% | 🟠 Parcial |
| `caribe_abandono` | Caribe | 5.064 | 100% ✅ | 33.8% | ✅ Mejor estructurada |
| `gdo_abandono` | GDO | 831 | 20.1% (664 sin fecha) | 7.9% | 🔴 No confiable (A-12) |
| `surti_abandono` | Surtigas | 2.795 | 0% (100% no parseable) | ❌ Sin columna | 🔴 No confiable |

**Problema estructural:** el abandono vive en tablas sueltas con esquemas de columnas
distintos, sin un destino común con la atención. No hay forma de hacer un reporte
transversal de "llamadas del día" sin `UNION ALL` de 4 tablas con 3 plantillas de
columnas diferentes (H-02).

---

### 3.3 Familia PQRS — 4 tablas · 6.280 filas

| Tabla | Gasera | Filas | Columnas | Granularidad | Veredicto |
| :--- | :--- | ---: | ---: | :--- | :--- |
| `gdo_pqrs` | GDO | 747 | 63 | Maestro de solicitud | 🟠 Columna `♣` (U+2663) + `columna1/2/62` |
| `gdo_pqrs_escritas` | GDO | 86 | 20 | Maestro con ANS completo | ✅ Modelo de referencia (trazabilidad ANS) |
| `gdo_informativo` | GDO | 4.191 | 29 | **Bitácora de seguimiento** | 🔴 No es maestro PQRS (A-13) |
| `surti_qr` | Surtigas | 1.256 | 54 | Solicitud + orden de trabajo | 🟠 520 celdas con salto de línea |

**Solapamiento:** 142 contratos de `gdo_informativo` están en `gdo_pqrs`; 61 en
`gdo_pqrs_escritas`. No se pueden cargar los tres como "PQRS" a la vez (A-13).

---

### 3.4 Catálogo — `clasificacion` (40 filas)

| Aspecto | Valor |
| :--- | :--- |
| Columnas | 4, todas `text` |
| Llave primaria | `(gasera, variante)` compuesta |
| Gaseras cubiertas | **1 sola: `GasCaribe`** (H-04) |
| Valores de `clasificacion` | `APTA` (17 variantes), `NO APTA` (23 variantes) |
| Valores de `resultado_normalizado` | **27** (4 APTA + 23 NO APTA literales) |
| Índices | Solo PK. Sin índice por `resultado_normalizado` ni por `clasificacion` |
| Variantes sin catalogar | **43** (236 filas) en las otras 4 gaseras (H-31) |

**Relación lógica (no física) con las tablas de atención:**

```
clasificacion JOIN por (gasera, variante)
  donde variante = normalizar_texto(estado / resultado_final / resultado_de_retencion)
```

> El join solo resuelve para GasCaribe hoy. Las 43 variantes pendientes de las otras
> gaseras quedan sin clasificar (H-31, H-32).

---

### 3.5 Artefacto — `gdo_gestion_diaria` (0 filas)

| Aspecto | Valor |
| :--- | :--- |
| Columnas | 1 |
| Filas | 0 |
| Tamaño | 8 KB |
| Veredicto | 🔴 Diseño de vista materializada que nunca se completó (H-18). **Eliminar** (M8). |

---

## 4. Relaciones lógicas (no físicas)

El esquema actual **no tiene relaciones declaradas**. Las relaciones son todas inferidas
por el analista a partir de las columnas comunes:

| Relación lógica | Columna(s) compartida(s) | Estado |
| :--- | :--- | :--- |
| Atención ↔ Abandono | `gasera`, `cabina`, `contrato`, `fecha` | Solo Caribe tiene `gestionado_inbound` (flag) |
| Atención ↔ PQRS | `contrato`, `gasera` | 142 contratos de `informativo` en `gdo_pqrs` |
| Atención ↔ `clasificacion` | `(gasera, normalizar_texto(estado))` | Solo GasCaribe catalogado |
| Atención ↔ `dim_operador` (futuro) | `operador` (empresa BPO) | Sin dimensión creada aún |
| Abandono ↔ Atención | `contrato`, `fecha` | Solo Caribe tiene fecha y hora al 100% |

---

## 5. Semántica crítica a preservar

> Estas 4 reglas **no son negociables** y deben quedar explícitas en cualquier modelo,
> dashboard o reporte que se construya sobre este esquema.

| # | Regla | Motivo | Hallazgo |
| :---: | :--- | :--- | :--- |
| 1 | **`anio` es el año de VENTA, no de gestión** | `ceo_inbound.anio`: 1900→110, 2022→22, 2023→74, 2024→132, 2025→484, 2026→233, NULL→1.694. Nunca usar para agregaciones temporales | H-07 |
| 2 | **`operador` es la empresa operadora del BPO, no una persona** | Dominio: SERVIPROTECCION BPO, ACCION PLUS, MIGRACION, GNP, CREAMOS MARKETING, etc. El asesor individual solo existe en GDO (`nombre_asesor_retencion`, `gestor`) | H-23 |
| 3 | **`gdo_informativo` es una bitácora, no un maestro de PQRS** | `tipo_registro` = REGISTRO ÚNICO/DUPLICADO; `estado_inf` = PRIMER REGISTRO/2º REGISTRO - N DÍAS. 1.180 filas (28.1%) sin tipo ni resultado | H-21, A-13 |
| 4 | **`APTA` ≠ "retención"** | 3 de los 4 resultados APTA implican cancelación. Total Retenciones = `retenido` + `cancelado + venta` (2 de los 4 APTA). `CANCELADO` (sin venta) es el resultado más común | H-22, D-01, D-02 |

---

## 6. Diagnóstico de integridad (resumen de salud del esquema)

| Dimensión | Estado | Veredicto | Fuente |
| :--- | :--- | :---: | :--- |
| Completitud de identificadores (contrato, estado, fecha) | 73–100% | 🟢 Aceptable | `05_Calidad` §2 |
| Completitud de contexto (localidad, operador, motivo) | 57–100% nulos | 🔴 Crítico | `05_Calidad` §2 |
| Validez temporal | 4 fechas imposibles; 63–100% no parseables en 4 tablas | 🔴 Crítico | `05_Calidad` §3 |
| Consistencia de catálogo | 43 variantes sin catalogar; normalización asimétrica | 🔴 Crítico | `05_Calidad` §4 |
| Unicidad | 3.114 grupos duplicados (20.2%) | 🔴 Crítico | `05_Calidad` §5 |
| Integridad de columna | 1.589 filas con valores de otra columna | 🔴 Crítico | `05_Calidad` §6 |
| Trazabilidad origen→fila | Inexistente (sin bitácora ni hash) | 🔴 Crítico | `05_Calidad` §1 |
| Codificación | UTF-8 correcto en todo el servidor | 🟢 Correcto | `04_Hallazgos` H-19 |
| Integridad referencial | 0 FKs, 0 índices de negocio | 🟠 Riesgo medio | `07_Estructura` §6 |
| Actualización | Cargas manuales por snapshot, sin ingesta automatizada | 🟠 Alto | `02_Plan` §1 |

---

## 7. Relación con otros documentos

| Documento | Qué aporta sobre este esquema |
| :--- | :--- |
| `01_Diccionario_de_Datos.md` | Inventario columna por columna (511+ líneas) con nulos, distintos, ejemplos, PII |
| `02_Mapeo_Origen_Destino.md` | Especificación de ingesta: cada columna Excel → tabla/campo destino |
| `03_Modelo_Datos.md` | ERD actual (§3.1), inventario (§3.2), modelo objetivo (§4) y migraciones (§6) |
| `04_Hallazgos_y_Backlog.md` | 36 hallazgos con evidencia SQL y 35 acciones de remediación |
| `05_Calidad_de_Datos.md` | Perfil de calidad por tabla y 20 reglas de validación (R-01 a R-20) |
| `07_Estructura_de_datos.md` | Inventario por gasera: hojas, campos clave, reglas operativas |
| `08_Flujo_De_Datos.md` | Arquitectura de flujo actual y objetivo |
| `09_Normalizacion_y_Clasificacion.md` | Algoritmo de normalización, cola de revisión, DDL del catálogo maestro |
| `10_Registro_Decisiones_Riesgos.md` | Decisiones (D-01…D-10), abiertas (A-01…A-15), riesgos (R-01…R-16) |
| `context/Analisis/Data_Db/gestion_diaria_documentacion.pdf` | **Versión visual exportada** de este ERD (one-pager técnico) |

---

## 8. Cómo reproducir / verificar

```bash
# Inventario completo + columnas + restricciones + índices + vistas + funciones + calidad
python database/inspeccion_esquema.py --todo

# Solo un esquema
python database/inspeccion_esquema.py --esquema gestion_diaria --calidad

# Conexión de prueba
python database/conexion_template.py
```

Todas las cifras de este documento son reproducibles con estas consultas y con las
que están citadas en cada documento fuente.

---

> 💡 **Para actualizar:** si el esquema cambia (nuevas tablas, columnas, migraciones
> aplicadas), actualiza este documento, el PDF visual y registra el cambio en
> `010_Registro_Decisiones_Riesgos.md` (sección de decisiones/inconsistencias).