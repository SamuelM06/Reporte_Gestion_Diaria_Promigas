# 📋 Plan 03: Definición de KPIs

**Proyecto:** Gestión Diaria Promigas
**Estado:** 🟡 **Parcialmente definido** — 7 KPIs comunes definidos por el negocio (§3); fórmulas pendientes de % Retención y Total Retenciones
**Alcance previsto:** definición formal de los indicadores del reporte de gestión diaria
**Fecha de creación:** 19 de octubre de 2026

---

## 1. Por qué este documento existe

El modelo de datos (doc 03) y el mapeo de ingesta (doc 02) ya están definidos. Falta lo
que convierte esos datos en **indicadores de gestión**: la fórmula exacta, la fuente, la
 granularidad y el destinatario de cada KPI.

> **Este documento no se puede redactar solo con evidencia técnica.** Cada KPI requiere
> una decisión de negocio sobre qué se quiere medir. La sección §3 deja preparado el
> andamiaje, y la §4 registra los que el negocio ya definió.

> ⚠️ **No hay alcance de front ni de back definido todavía.** No se sabe si será un portal
> por gasera, una vista por gasera o un aplicativo por gasera. **Este documento solo define
> indicadores**; cualquier decisión sobre la interfaz queda fuera de alcance hasta que el
> negocio la defina.

---

## 2. Dependencias

| Dependencia | Estado | Bloquea |
| :--- | :--- | :--- |
| **D-P1 / A-11** — semántica de `APTA` y granularidad del reporte | 🔴 Abierta | Todos los KPIs de retención y de operador |
| **A-12** — abandono de GDO confiable o no | 🔴 Abierta | KPIs de nivel de servicio |
| **A-13** — `gdo_informativo`: bitácora o maestro | 🔴 Abierta | KPIs de PQRS |
| **A-14** — campos obligatorios por gasera | 🟠 Abierta | KPIs que dependan de `localidad`, `operador` o motivo |
| Doc 03 (modelo) | ✅ Listo | — |
| Doc 02 (mapeo) | ✅ Listo | — |
| Doc 09 (normalización) | ✅ Listo, con `POR_REVISAR` pendiente | — |

---

## 3. KPIs comunes a TODAS las gaseras (definidos por el negocio — 19-oct-2026) ✅

> Fuente de esta definición: el equipo de negocio, en conversación directa del
> 19-oct-2026. Son los **indicadores que toda gasera reporta por igual**, aunque cada
> gasera maneja **gráficos distintos** sobre ellos.

| # | KPI (nombre del negocio) | ¿Qué mide? | Fórmula | Fuente propuesta | Estado |
| ---: | :--- | :--- | :--- | :--- | :--- |
| **1** | **Total general** | Total de gestiones registradas en el periodo | `COUNT(*)` de gestiones | `fact_gestion` | 🟡 Falta confirmar el filtro de periodo y qué tipos de gestión entran |
| **2** | **Total Inbound** | Gestiones de entrada (el cliente o la cabina originan la llamada) | `COUNT(*) WHERE sentido = 'IN'` | `fact_gestion` | 🟡 Falta confirmar si Inbound+Outbound = Total general |
| **3** | **Total Outbound** | Gestiones de salida (la cabina llama al cliente) | `COUNT(*) WHERE sentido = 'OUT'` | `fact_gestion` | 🟡 idem |
| **4** | **Registros Aptos** | Gestiones cuyo resultado es un resultado APTA | `COUNT(*) WHERE es_apto = TRUE` | `fact_gestion` → `dim_resultado` | 🟠 Requiere cerrar la cola de `POR_REVISAR` (B-03b) |
| **5** | **Registros No Aptos** | Gestiones cuyo resultado NO es apto | `COUNT(*) WHERE es_apto = FALSE` | `fact_gestion` → `dim_resultado` | 🟠 idem |
| **6** | **Total Retenciones** | Gestiones que terminaron en retención | ⚠️ **Ver nota 1** | `fact_gestion` → `resultado_normalizado = 'retenido'` | 🔴 **Semántica por confirmar** (H-22) |
| **7** | **% Retención** | Proporción de gestiones retenidas | **El negocio tiene la fórmula; se compartirá cuando se aborde back/front** | — | 🔴 **Pendiente la fórmula** |

### ⚠️ Notas de análisis que el negocio debe confirmar (no bloqueadas, pero críticas)

> **Nota 1 — «Total Retenciones» NO es lo mismo que «Registros Aptos» (H-22).**
> Este es el punto más importante de todo el documento. De los **4 resultados APTA**, solo
> **1** es una retención real (`retenido`). Los otros 3 implican **cancelación**:
>
> | Resultado APTA (D-01) | ¿Es retención? | Peso en los datos de hoy |
> | :--- | :---: | ---: |
> | `retenido` | ✅ Sí | ~16% de los registros aptos |
> | `cancelado` | ❌ No | 63.6% de todas las filas |
> | `cancelado + venta` | ❌ No | minoritario |
> | `cancelado + reintegro` | ❌ No | minoritario |
>
> **Consecuencia:** `Registros Aptos` (KPI 4) y `Total Retenciones` (KPI 6) son **dos
> números distintos** y ambos se publican. Si alguien presenta «Registros Aptos» como
> «Retenciones», el reporte está equivocado. **La fórmula exacta del KPI 6 la tiene el
> negocio** y se registrará aquí cuando la comparta.

> **Nota 2 — los tres totales deben cuadrar entre sí.**
> `Total general` debería ser igual a `Total Inbound + Total Outbound`. **Pero hoy no
> necesariamente es así**, porque existen tipos de gestión que no son ni inbound ni
> outbound: `gdo_informativo` (la bitácora), los **abandonos** y las **PQRS**.
> **Pregunta pendiente:** ¿el Total general incluye abandonos y PQRS, o solo llamadas?
> Eso cambia el denominador de todo lo demás.

> **Nota 3 — % Retención necesita su denominador (regla K-06).**
> Cuando el negocio comparta la fórmula, hay que verificar qué hay en el denominador:
> ¿Total general? ¿Registros Aptos? ¿Inbound? Un % Retención calculado sobre denominadores
> distintos produce números que **no se pueden comparar entre gaseras**.

> **Nota 4 — APTA y NO APTA deben sumar el total, sin hueco.**
> `Registros Aptos + Registros No Aptos` debe ser igual a `Total general`. Si existe
> `POR_REVISAR` sin clasificar, **la suma no cuadra** y el KPI 4 y 5 se subreportan. Por
> eso la acción B-03b (ciclo de aprendizaje continuo) es un prerequisito de estos dos KPIs.

---

## 4. Andamiaje de KPIs (propuesta a discutir)

| # | KPI | Concepto canónico | Fuente | Granularidad | Estado |
| ---: | :--- | :--- | :--- | :--- | :--- |
| 1 | Volumen de gestiones | — | `fact_gestion` | gasera × cabina × mes | 🟢 Calculable ya |
| 2 | Distribución de resultado | `dim_resultado` | `fact_gestion` | gasera × mes | 🟢 Calculable ya |
| 3 | Resultado apto | `dim_resultado.es_apto` | `fact_gestion` | gasera × mes | 🟡 Requiere D-P1 |
| 4 | Tasa de abandono | — | `fact_gestion` (ABANDONO) | gasera × hora | 🟡 Requiere A-12 |
| 5 | Motivos de pérdida | `dim_motivo` | `fact_gestion` | motivo × mes | 🟡 Requiere B-28 |
| 6 | Productividad por operador | `dim_operador` | `fact_gestion` | operador × mes | 🟠 Requiere A-11 |
| 7 | Cobertura de clasificación | `metodo_normalizacion` | `fact_gestion` | gasera × mes | 🟢 Calculable ya |
| 8 | Calidad de la ingesta | `dim_carga` + cuarentena | `dim_carga` | lote | 🟢 Calculable ya |
| 9 | Radicación de PQRS | `fact_pqrs` | `fact_pqrs` | gasera × mes | 🟠 Requiere A-13 |
| 10 | Cumplimiento de ANS | `fact_pqrs.ans_*` | `fact_pqrs` | gasera × mes | 🟡 Requiere A-13 |

> **KPI 7 (cobertura de clasificación) es el que menos se ha visto y el que más importa
> para la credibilidad del reporte:** mide qué porcentaje del histórico se clasificó por
> coincidencia exacta, por aproximación o quedó en `POR_REVISAR`.

---

## 5. Reglas que todo KPI debe cumplir

| Regla | Descripción |
| :--- | :--- |
| K-01 | Cada KPI declara su **fuente exacta** (tabla + columna) y su **fórmula** |
| K-02 | Cada KPI se puede calcular **con la data de hoy**, sin trabajo manual |
| K-03 | Los KPIs de retention **no** se publican si hay `POR_REVISAR` sin reportar |
| K-04 | Todo KPI se puede desagregar por gasera **y** su nivel de comparabilidad se declara |
| K-05 | Ningún KPI usa `anio` (año de venta) para un periodo de gestión |
| K-06 | Todo KPI de porcentaje declara su **denominador** explícitamente |
| K-07 | Los KPIs que dependan de `operador` declaran si es **empresa o persona** |

---

## 6. Qué pendía vs. qué ya está resuelto

### ✅ Resuelto por el negocio (19-oct-2026)

1. ✅ **¿Cuáles son los indicadores?** — los 7 de la §3 (Total general, Total Inbound,
   Total Outbound, Registros Aptos, Registros No Aptos, Total Retenciones, % Retención).
2. ✅ **¿Son comunes a todas las gaseras?** — sí, son los mismos 7 en las 5 gaseras,
   aunque cada gasera use gráficos distintos sobre ellos.

### 🔴 Aún pendiente del negocio

1. **Fórmula exacta de «Total Retenciones»** — ver Nota 1 de la §3.
2. **Fórmula y denominador de «% Retención»** — el negocio la tiene y la compartirá
   cuando se aborde back/front.
3. **¿Total general = Inbound + Outbound?** — ¿entran abandono y PQRS en el total?
   (Nota 2).
4. **¿Hay umbrales o metas por gasera?** — por ejemplo: «% Retención objetivo ≥ X%».
5. **¿Quién consume cada KPI y con qué periodicidad?** — diario, semanal, mensual.

### 🟠 Decisiones que siguen abiertas (registro)

| Decisión | Estado | Bloquea |
| :--- | :---: | :--- |
| **A-11** — productividad por empresa o por asesor | 🔴 | KPIs de operador (§4, KPI 6) |
| **A-12** — abandono de GDO confiable | 🔴 | KPI de abandono |
| **A-13** — `gdo_informativo`: bitácora o maestro | 🔴 | KPIs de PQRS |
| **A-14** — campos obligatorios por gasera | 🟠 | KPIs con `localidad` / motivo |

---

## 7. Impacto en otros documentos

| Documento | Relación |
| :--- | :--- |
| `03_Modelo_Datos.md` | Define de dónde se saca cada KPI |
| `09_Normalizacion_y_Clasificacion.md` | Define `POR_REVISAR` y su efecto en los KPIs |
| `010_Registro_Decisiones_Riesgos.md` | Las decisiones A-11…A-14 se registran aquí al cerrarse |
