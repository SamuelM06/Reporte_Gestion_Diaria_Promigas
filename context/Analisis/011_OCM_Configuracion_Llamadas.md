# 11. Configuración OCM — Retención

**Proyecto:** Gestión Diaria Promigas
**Origen:** `Matriz_Distribuidoras_Configuracion_Llamadas.xlsx` (matriz oficial de configuración de canales OCM)
**Fecha de creación:** 19 de octubre de 2026
**Estado:** ✅ Documentado

---

## 1. Propósito

Cuando una llamada **entra (inbound)**, OCM debe detectar automáticamente a qué gasera
pertenece para tipificarla. Esta matriz es la **configuración oficial** de:

- Qué gaseras manejan **inbound**, **outbound** o ambas
- Las **líneas telefónicas** de inbound por gasera
- Los **skills de inbound y outbound** asignados

> ⚠️ **Vanti NO es gasera Promigas.** Está en el archivo pero se excluye de todo este
> documento y de cualquier análisis.

---

## 2. Matriz de Configuración de Llamadas

> Fuente: hoja `Matriz Distribuidoras` del archivo `Matriz_Distribuidoras_Configuracion_Llamadas.xlsx`.
> Vanti excluida.

| Distribuidora | Inbound | Outbound | Línea Inbound | Skill Inbound | Skill Outbound |
| :--- | :---: | :---: | :--- | :--- | :--- |
| **Gas Caribe** | ✅ | ✅ | 3185606558 | `RETENCIONGAS` | *(sin skill)* |
| **Gas Caribe** (línea 2) | ✅ | ✅ | 3152564863 | `RETENCIONGAS` | *(sin skill)* |
| **CEO** | ✅ | — | 317 3280989 | `RETENCION_GASCARIBE` | *(sin skill)* |
| **Efigas** | — | ✅ | *(sin línea)* | *(sin skill)* | `RETENCION_PROMIGAS` |
| **Surtigas** | ✅ | ✅ | 3177105886 | `TRASLADO_POR_COMPETENCIA` | *(sin skill)* |
| **GDO** | ✅ | ✅ | 3186142478 | *(sin skill)* | *(sin skill)* |

---

## 3. Resumen por Tipo de Gestión

### Solo Inbound

| Gasera | Línea | Skill Inbound |
| :--- | :--- | :--- |
| CEO | 317 3280989 | `RETENCION_GASCARIBE` |
| Gas Caribe | 3185606558 / 3152564863 | `RETENCIONGAS` |
| Surtigas | 3177105886 | `TRASLADO_POR_COMPETENCIA` |
| GDO | 3186142478 | *(sin skill asignado)* |

### Solo Outbound

| Gasera | Skill Outbound |
| :--- | :--- |
| Efigas | `RETENCION_PROMIGAS` |

### Inbound + Outbound

| Gasera | Línea Inbound | Skill Inbound | Skill Outbound |
| :--- | :--- | :--- | :--- |
| Gas Caribe | 3185606558 / 3152564863 | `RETENCIONGAS` | — |
| Surtigas | 3177105886 | `TRASLADO_POR_COMPETENCIA` | — |
| GDO | 3186142478 | — | — |

> **Nota:** Gas Caribe tiene **dos líneas inbound** (3185606558 y 3152564863) con el mismo
> skill `RETENCIONGAS`. CEO también aparece dos veces en la matriz original: una con
> `RETENCION_GASCARIBE` (inbound) y otra con `RETENCION_PROMIGAS` (outbound). Ver §5.

---

## 4. Gaseras Sin Inbound

| Gasera | Observación |
| :--- | :--- |
| **Efigas** | Solo **outbound** (`RETENCION_PROMIGAS`). No recibe llamadas inbound. |
| **Guajira** | No aplica para inbound ni outbound. Sin línea ni skill. |

---

## 5. Datos Atípicos de la Matriz Original

Estos puntos **no son errores de esta documentación**, sino características del archivo
original que conviene tener en cuenta:

| Observación | Detalle |
| :--- | :--- |
| **CEO aparece dos veces** | 1) Inbound: línea `317 3280989`, skill `RETENCION_GASCARIBE`. 2) Outbound: skill `RETENCION_PROMIGAS`, sin línea. |
| **GDO sin skills** | Tiene inbound (línea 3186142478) y outbound, pero **sin skill asignado** en la matriz. |
| **Surtigas con skill de traslado** | El skill inbound es `TRASLADO_POR_COMPETENCIA`, no `RETENCION_*`. Indica que las llamadas pueden redirigirse por competencia. |
| **Efigas sin línea** | Solo outbound, pero no tiene línea inbound registrada. |
| **Guajira "No aplica"** | Marcada como no aplica para inbound ni outbound. |

---

## 6. Relación con el Modelo de Datos

Esta matriz es la **llave de detección automática** de gasera para llamadas inbound:

```
Llamada entrante → OCM valida la línea → Asigna skill → Tipifica gasera
```

| Paso | Regla |
| :--- | :--- |
| 1 | La línea entrante coincide con una de la §2 |
| 2 | OCM asigna el **skill inbound** de esa gasera |
| 3 | El resultado se registra en la tabla de hechos con su gasera |

> **Efecto en el reporte:** el KPI de "Total Inbound" por gasera **solo puede incluir
> las gaseras con línea inbound configurada** (Gas Caribe, CEO, Surtigas, GDO). Efigas y
> Guajira no pueden aparecer en ese KPI.

---

## 7. Decisión Pendiente

| Decisión | Pregunta |
| :--- | :--- |
| **GDO sin skill** | ¿GDO usa un skill de inbound que no está en la matriz, o se tipifica solo por línea? |
| **CEO outbound** | ¿La segunda fila de CEO (`RETENCION_PROMIGAS`) implica que CEO también hace outbound? |
| **Surtigas traslado** | ¿Las llamadas con skill `TRASLADO_POR_COMPETENCIA` cuentan como retención o como redirección? |
