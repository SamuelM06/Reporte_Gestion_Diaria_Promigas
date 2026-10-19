# 📋 Plan 03: Definición de KPIs

**Proyecto:** Gestión Diaria Promigas
**Estado:** ⬜ **Pendiente de redactar con el negocio**
**Alcance previsto:** definición formal de los indicadores del reporte de gestión diaria
**Fecha de creación:** 19 de octubre de 2026

---

## 1. Por qué este documento existe

El modelo de datos (doc 03) y el mapeo de ingesta (doc 02) ya están definidos. Falta lo
que convierte esos datos en **indicadores de gestión**: la fórmula exacta, la fuente, la
 granularidad y el destinatario de cada KPI.

> **Este documento no se puede redactar solo con evidencia técnica.** Cada KPI requiere
> una decisión de negocio sobre qué se quiere medir. La sección §3 deja preparado el
> andamiaje.

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

## 3. Andamiaje de KPIs (propuesta a discutir)

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

## 4. Reglas que todo KPI debe cumplir

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

## 5. Qué se necesita del negocio para cerrarlo

1. ¿Cuáles son los **5-8 indicadores** que la jefatura mira hoy en Power BI? (K-07 del doc 010)
2. ¿Cómo se calcula cada uno exactamente? (fórmula y denominador)
3. ¿Quién los consume y con qué periodicidad?
4. ¿Qué se hace cuando el KPI de una gasera **no es comparable** con otra?
5. ¿Hay umbrales o metas por gasera?

---

## 6. Impacto en otros documentos

| Documento | Relación |
| :--- | :--- |
| `03_Modelo_Datos.md` | Define de dónde se saca cada KPI |
| `09_Normalizacion_y_Clasificacion.md` | Define `POR_REVISAR` y su efecto en los KPIs |
| `010_Registro_Decisiones_Riesgos.md` | Las decisiones A-11…A-14 se registran aquí al cerrarse |
