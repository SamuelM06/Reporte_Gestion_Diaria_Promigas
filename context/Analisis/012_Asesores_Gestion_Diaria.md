# 12. Asesores de Gestión Diaria — Promigas

**Proyecto:** Gestión Diaria Promigas  
**Área:** Retención y Experiencia al Cliente  
**Origen:** listado de asesores enviado para documentación  
**Fecha de creación:** 21 de octubre de 2026  
**Estado:** ✅ Documentado

---

## 1. Propósito

Este documento registra el listado de asesores de gestión diaria por gasera, para tener una referencia centralizada de quiénes están asignados a cada distribuidora y en qué entidad o línea operan. Sirve de apoyo para:

- Vincular atenciones y resultados a un asesor individual (cuando el dato `operador` esté disponible por gasera).
- Consultas operativas y de seguimiento por gasera.
- Validar la cobertura de asesores entre las 5 gaseras del alcance (CEO, Efigas, Gas Caribe, GDO, Surtigas).

---

## 2. Listado de Asesores

| # | Asesor | Gasera / Entidad | Rol o línea asociada | Observaciones |
|---|:---|:---|:---|:---|
| 1 | Yennifer Paola Mejia Quiñonez | GDO | Cancela | — |
| 2 | Sharith Melisa Guevara Tovar | GDO / Alfa | Cancela | Aparece asociada a dos entidades (GDO y Alfa) |
| 3 | Kelly Johanna Moron Macias | Surtigas | — | — |
| 4 | Lisbeth Cecilia Ángel Jiménez | Surtigas | — | — |
| 5 | Luisa Fernanda Torres Guerrero | GDO / Alfa | — | Aparece asociada a dos entidades (GDO y Alfa) |
| 6 | Yeison Javier Santiago Salguedo | Occidente / Sura | — | Asesor vinculado a Occidente Sura |
| 7 | Cindy Johana Palmera Torres | CEO | — | — |
| 8 | Madiley Isabel Vasquez Solano | Surtigas / CEO | — | Aparece asociada a dos entidades (Surtigas y CEO) |
| 9 | Jesus Danilo Gutierrez Varela | GDO / HDI | — | Aparece asociado a dos entidades (GDO y HDI) |

**Total de asesores registrados:** 9  
**Total de filas:** 9 (algunos asesores aparecen con más de una gasera/entidad asociada)

---

## 3. Resumen por Gasera / Entidad

| Gasera / Entidad | Asesores asociados | Cantidad |
|:---|:---|---:|
| **GDO** | Yennifer Paola Mejia Quiñonez, Sharith Melisa Guevara Tovar, Luisa Fernanda Torres Guerrero, Jesus Danilo Gutierrez Varela | 4 |
| **Surtigas** | Kelly Johanna Moron Macias, Lisbeth Cecilia Ángel Jiménez, Madiley Isabel Vasquez Solano | 3 |
| **CEO** | Cindy Johana Palmera Torres, Madiley Isabel Vasquez Solano | 2 |
| **Alfa** | Sharith Melisa Guevara Tovar, Luisa Fernanda Torres Guerrero | 2 |
| **HDI** | Jesus Danilo Gutierrez Varela | 1 |
| **Occidente / Sura** | Yeison Javier Santiago Salguedo | 1 |

> **Nota:** varios asesores aparecen asociados a más de una gasera o entidad (GDO/Alfa, Surtigas/CEO, GDO/HDI). Esto puede indicar que operan en varias líneas o que el listado fuente no distingue exclusivamente una gasera por asesor. Validar antes de usar para cálculo de productividad individual.

---

## 4. Relación con el modelo de datos

En la auditoría de la fase 1 se identificó (hallazgo **H-23**) que la columna `operador` de la base de datos representa la **empresa operadora**, no necesariamente al asesor individual, y que la productividad por asesor solo es calculable de forma confiable en **GDO**.

Este listado es de referencia operativa y no debe usarse como fuente de verdad para KPIs de productividad individual hasta que se confirme que la columna `operador` (o un campo equivalente) almacene el nombre del asesor por gasera.

Ver también: `context/Analisis/06_Documentacion.md` §2.1 (bloqueo #2) y `context/Analisis/010_Registro_Decisiones_Riesgos.md` (abierta A-11).

---

## 5. Decisiones pendientes

| Decisión | Pregunta |
|:---|:---|
| **Asesores multi-entidad** | ¿Sharith Guevara, Luisa Torres, Madiley Vasquez y Jesus Gutierrez operan realmente en varias gaseras, o el listado fuente tiene duplicados por entidad? |
| **Entidades no Promigas** | ¿Alfa, HDI y Occidente/Sura son gaseras del alcance o clientes externos que deben excluirse de los KPIs de retención Promigas? |
| **Productividad por asesor** | ¿Existe un campo confiable de asesor por gasera para calcular productividad individual fuera de GDO? |

---

> 💡 **Cómo actualizar:** si recibes un listado nuevo o corregido de asesores, edita esta tabla, actualiza el resumen por gasera y registra el cambio en `context/Analisis/010_Registro_Decisiones_Riesgos.md`.
