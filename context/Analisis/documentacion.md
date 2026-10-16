# 📊 Documentación de Análisis de Datos - Reporte Gestión Diaria Promigas

## 1. Contexto del Negocio y Alcance
* **Organización:** Promigas.
* **Área:** Retención.
* **Entidades / Gaseras involucradas:** 5 a 6 empresas distribuidoras de gas asociadas a Promigas.
* **Objetivo General:** Diseñar y construir un sistema de reportería y dashboard diario para la gestión de retención, garantizando calidad, consistencia y trazabilidad de los datos recolectados día a día.

---

## 2. Enfoque Metodológico (Modo Analista de Datos)
Antes de construir interfaces o arquitecturas de backend, este proyecto sigue una fase analítica estricta:
1. **Comprensión del Dato en Origen:** Identificar fuentes, formatos, periodicidad, consistencia y volumetría.
2. **Auditoría y Calidad de Datos:** Evaluar duplicados, valores nulos, discrepancias en tipificación y formatos entre gaseras.
3. **Estandarización y Homologación:** Mapear reglas de negocio para unificar catálogos (estados, tipologías, motivos de retención, causales de pérdida/éxito).
4. **Validación con Stakeholders:** Confirmar que los indicadores y agrupaciones reflejen la realidad operativa.

---

## 3. Matriz de Fuentes de Datos (En Construcción)
| ID Fuente | Nombre Archivo / Tabla | Gasera / Unidad | Tipo (Excel / DB / CSV) | Periodicidad | Responsable / Origen | Observaciones |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| *SRC-01* | **Base Acumulada** | Todas las gaseras | Local / Descarga antigua | Histórica (Estática) | Descarga previa local | **Hallazgo crítico:** Contiene histórico de todas las gaseras pero actualmente **NO está conectada a la gestión diaria**. |
| *SRC-02* | **Gestión Diaria** | Por gasera / Consolidada | Excel / Operación diaria | Diaria | Operación de Retención | Registros del día a día que deben conciliarse/empalmarse con el acumulado. |
| *SRC-03* | *BD Transaccional* | *Consolidado* | *Base de Datos* | *Automático* | *Sistemas* | *Pendiente credenciales y validación de tablas*. |

---

## 4. Preguntas Clave de Exploración y Auditoría
Para cada fuente o archivo compartido, resolveremos:
1. **Granularidad:** ¿Qué representa una sola fila? (¿Una gestión, un cliente, un contrato, un ticket de llamada?).
2. **Llave Primaria / Identificador Único:** ¿Existe un ID único confiable (ID_Gestion, Contrato, Cuenta, Radicado)?
3. **Temporalidad:** ¿Qué campos de fecha existen? (Fecha de asignación, fecha de gestión, fecha de cierre, fecha de corte).
4. **Clasificación de Registros:** ¿Cuáles son los estados finales de la gestión? (Retenido, No Retenido, En Proceso, No Contactado, Ilocalizable).
5. **Diferencias entre Gaseras:** ¿Cada gasera maneja los mismos nombres de columnas y catálogos, o requieren un diccionario de homologación?
6. **Empalme Histórico vs Diario:** ¿Cómo se relacionan los registros de la Base Acumulada con los que entran en la gestión diaria? ¿La gestión diaria actualiza un estado previo de la base acumulada o son eventos/gestiones nuevas?

---

## 5. Bitácora de Hallazgos y Decisiones
* **Hallazgo 01 (Arquitectura de Datos - Fuentes Desconectadas):**
  * **Situación:** Todas las gaseras provienen actualmente de una base histórica descargada localmente llamada **"Base Acumulada"**.
  * **Problema identificado:** Las tablas de la Base Acumulada están **completamente desconectadas de la gestión diaria**.
  * **Impacto analítico:** Existe un riesgo alto de desactualización, doble conteo o pérdida de trazabilidad si no se define una llave común y un proceso de actualización (CDC/Upsert o Append) para vincular el historial con el flujo diario.
* **Fecha:** *Inicio de proyecto*
  * Creación del repositorio y estructura base analítica.
  * Definición de lineamientos para análisis previo a desarrollo.
