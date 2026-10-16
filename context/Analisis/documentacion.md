# 📊 Documentación de Análisis de Datos - Reporte Gestión Diaria Promigas

## 1. Contexto del Negocio y Alcance
* **Organización:** Promigas.
* **Área:** Retención y Experiencia al Cliente.
* **Entidades / Gaseras Confirmadas (5):**
  1. **CEO** (Compañía Energética del Cauca) - *Solo Inbound*
  2. **Efigas** - *Solo Outbound*
  3. **Gas Caribe** (Gases del Caribe) - *Inbound y Outbound*
  4. **GDO** (Gases de Occidente) - *Registro En Vivo: Inbound, Outbound, PQRS*
  5. **Surtigas** - *Inbound (Histórico + Continuidad) y Outbound*
* **Objetivo General:** Diseñar y construir un sistema de reportería y dashboard diario para la gestión de retención, garantizando calidad, consistencia y trazabilidad de los datos recolectados día a día, facilitando la transición desde planillas Excel en SharePoint hacia una Base de Datos centralizada e integración definitiva con la plataforma **OCM (Omnichannel Contact Manager)**.

---

## 2. Enfoque Metodológico (Modo Analista de Datos)
Antes de construir interfaces o arquitecturas de backend, este proyecto sigue una fase analítica estricta:
1. **Comprensión del Dato en Origen:** Identificar fuentes, formatos, periodicidad, consistencia y volumetría.
2. **Auditoría y Calidad de Datos:** Evaluar duplicados, valores nulos, discrepancias en tipificación y formatos entre gaseras.
3. **Estandarización y Homologación:** Mapear reglas de negocio para unificar catálogos (estados, tipologías, motivos de retención, causales de pérdida/éxito).
4. **Validación con Stakeholders:** Confirmar que los indicadores y agrupaciones reflejen la realidad operativa.

---

## 3. Matriz Oficial de Fuentes de Datos

| ID Fuente | Gasera / Entorno | Archivo(s) / Ruta | Tipo de Cabina | Columna Temporal Clave | Regla Crítica |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **SRC-CEO** | CEO | `CEO / Gestion diaria CEO.xlsx` | Inbound + Abandono | `FECHA INGRESO LLAMADA` | Consolidar totales mensuales con fecha de ingreso. |
| **SRC-EFI** | Efigas | `Efigas / Gestion Diaria Outbound - Efigas.xlsx` | Solo Outbound | `FECHA DE EJECUCION` | **Ignorar obligatoriamente `FECHA BASE`**. |
| **SRC-GCA** | Gas Caribe | `Gas Caribe / Gestion diaria Inbound...` y `gestión diaria outbound...` | Inbound + Outbound | `FECHA DE ATENCION` (Inb) / `MES` (Out) | Hojas organizadas por mes en Inbound. |
| **SRC-GDO** | GDO | `VALIDACION INFORMACION GDO- 24 de Junio 2026.xlsx` | En Vivo (Inb + Out + PQRS + Abandono) | Fecha en vivo | **Homologar hoja `informativo` a `PQRS`**. |
| **SRC-SUR** | Surtigas | `SURTIGAS ARCHIVO RECUPERADO` + `JULIO - AGOSTO` + `outbound surtugas.xlsx` | Inbound + Outbound | `FECHA DE LLAMADA` | Inbound fragmentado en histórico recuperado y continuidad. |
| **SRC-HIS** | Consolidado Histórico | Base Acumulada Local previa | Histórico todas las gaseras | Por evaluar | Desconectada de la gestión diaria; decidir si truncar, sanear o reemplazar. |
| **SRC-OCM** | Plataforma Futura | OCM Cloud (Omnichannel Contact Manager) | Telefonía Cloud Unificada | Timestamp de llamada en vivo | Sustituirá definitivamente los archivos Excel en SharePoint. |

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
  * Todas las gaseras provienen históricamente de una base local descargada desactualizada.
* **Hallazgo 02 (Especificación Oficial Promigas Procesada):**
  * Se identificaron las 5 gaseras reales (CEO, Efigas, Gas Caribe, GDO, Surtigas) con sus respectivos libros en SharePoint.
  * Se descubrió la condición en vivo de GDO y las reglas particulares (ignorar `FECHA BASE` en Efigas, homologar `informativo` en GDO, y unir histórico recuperado en Surtigas).
  * Se documentó la transición obligatoria a **OCM (Omnichannel Contact Manager)** como destino final estratégico para apagar el uso operativo de Excel.
