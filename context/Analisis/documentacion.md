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
| *SRC-01* | *Por definir* | *Gasera 1* | *Excel* | *Diaria* | *Operación* | *Pendiente ruta y hojas* |
| *SRC-02* | *Por definir* | *Gasera 2* | *Excel* | *Diaria* | *Operación* | *Pendiente ruta y hojas* |
| *SRC-03* | *Por definir* | *BD Transaccional* | *Consolidado* | *Base de Datos* | *Automático* | *Pendiente credenciales* |

---

## 4. Preguntas Clave de Exploración y Auditoría
Para cada fuente o archivo compartido, resolveremos:
1. **Granularidad:** ¿Qué representa una sola fila? (¿Una gestión, un cliente, un contrato, un ticket de llamada?).
2. **Llave Primaria / Identificador Único:** ¿Existe un ID único confiable (ID_Gestion, Contrato, Cuenta, Radicado)?
3. **Temporalidad:** ¿Qué campos de fecha existen? (Fecha de asignación, fecha de gestión, fecha de cierre, fecha de corte).
4. **Clasificación de Registros:** ¿Cuáles son los estados finales de la gestión? (Retenido, No Retenido, En Proceso, No Contactado, Ilocalizable).
5. **Diferencias entre Gaseras:** ¿Cada gasera maneja los mismos nombres de columnas y catálogos, o requieren un diccionario de homologación?

---

## 5. Bitácora de Hallazgos y Decisiones
* **Fecha:** *Inicio de proyecto*
  * Creación del repositorio y estructura base analítica.
  * Definición de lineamientos para análisis previo a desarrollo.
