# 📋 Plan 02: Estrategia de Migración a Base de Datos y Transición a OCM

> **Referencia:** Plan de Migración y Estrategia Futura (Sección 7 de la Documentación Técnica Promigas).  
> **Objetivo:** Definir la hoja de ruta técnica y el cuestionario analítico para la reunión de trabajo del **Lunes**.

---

## 1. Los Tres Pilares Estratégicos del Proyecto

```text
[Fase 1: Análisis y Estrategia DB] ──▶ [Fase 2: Ingesta Temporal SharePoint] ──▶ [Fase 3: Integración Final OCM]
      (Reunión del Lunes)                     (Contingencia en Python)                 (Telefonía Cloud - Sin Excel)
```

### 🔹 Pilar 1: Análisis y Estrategia de la Base de Datos Central (Prioridad Lunes)
* **Objetivo:** Definir la arquitectura de almacenamiento relacional para consolidar las 5 gaseras.
* **Decisión Crítica sobre la Base Local Desactualizada:**
  * **Opción A (Truncar / Descartar):** Si la base local tiene inconsistencias graves o fue construida con criterios viejos, se parte de cero cargando directamente los archivos recuperados de SharePoint (Ene 2026 - Presente).
  * **Opción B (Modificar / Sanear):** Conservar la estructura previa y aplicarle un script de limpieza y mapeo para alinearla con el nuevo esquema unificado.
  * **Opción C (Reemplazar con Histórico Homologado):** Diseñar un esquema nuevo en la DB y migrar únicamente los registros auditables de la base local previa.
* **Diseño del Esquema Target (Core):**
  * Modelo relacional con separación de hechos (`Fact_Gestion_Diaria`) y dimensiones (`Dim_Gasera`, `Dim_Cabina`, `Dim_Tipo_Gestion`, `Dim_Asesor`, `Dim_Motivo_Retencion`).

---

### 🔹 Pilar 2: Automatización Temporal de Ingesta (Contingencia SharePoint)
* **Objetivo:** Garantizar la continuidad operativa mientras los asesores sigan registrando en Excel.
* **Componentes del Pipeline:**
  1. Conector a SharePoint vía Microsoft Graph API / Office365 REST API o descarga local sincronizada.
  2. Lectores especializados por gasera:
     * Lector CEO (`Gestion diaria CEO.xlsx`)
     * Lector Efigas (`Gestion Diaria Outbound - Efigas.xlsx`) con regla de descarte de `FECHA BASE`.
     * Lector Gas Caribe (Iterador de pestañas mensuales en Inbound + Outbound).
     * Lector GDO (Conexión al libro de validación en vivo con homologación de `informativo`).
     * Lector Surtigas (Conciliador de archivo recuperado Ene-Jun + archivo continuidad Jul-Oct + Outbound).
  3. Proceso de Upsert / Deduplicación para no duplicar llamadas registradas en días previos.

---

### 🔹 Pilar 3: Integración Definitiva con OCM (Omnichannel Contact Manager)
* **Objetivo:** Desconexión y cierre del uso de planillas Excel.
* **Hitos:**
  1. Habilitación de la API / Data Export de la plataforma **OCM**.
  2. Sustitución de los conectores Excel por el flujo directo cloud `OCM -> DB Central`.
  3. Archivo y congelamiento de las planillas de SharePoint como histórico no editable.
  4. Reducción a 0% de errores de tipeo o pérdida de fórmulas en hojas de cálculo.

---

## 2. Guía de Cuestionamiento y Análisis para el Lunes (Modo Analista)

Para la sesión de trabajo y análisis del lunes, debemos resolver y validar los siguientes puntos:

### ❓ Bloque 1: Calidad y Continuidad de la Data Histórica
1. **Volumetría y Periodo de la Base Local:**
   * ¿Qué rango de fechas exacto cubre la "Base Acumulada" local? ¿Tiene datos anteriores al 1 de enero de 2026?
   * ¿Existen solapamientos entre la Base Acumulada y los archivos de SharePoint de 2026?
2. **Caso Especial Surtigas:**
   * En el archivo histórico de Surtigas (`SURTIGAS ARCHIVO RECUPERADO`), ¿las hojas `Enero a Marzo`, `abrl`, `mayo` y `junio` tienen exactamente las mismas columnas y nombres de cabecera?
   * En la transición a `JULIO - AGOSTO 2026`, ¿cambió algún criterio de tipificación?
3. **Manejo de Llamadas de Abandono:**
   * ¿Las hojas de `Abandono` (CEO, Gas Caribe, GDO, Surtigas) tienen la misma granularidad que las llamadas atendidas, o solo traen número de teléfono, fecha y hora de desconexión?

### ❓ Bloque 2: Reglas de Homologación Multigasera
4. **Unificación de Estados de Retención:**
   * ¿Cuáles son los valores permitidos para catalogar el resultado de la gestión? (¿"Retenido", "No Retenido", "En Proceso", etc.?). ¿Varía el texto entre gaseras?
5. **GDO - Hoja "Informativo":**
   * ¿Qué columnas específicas tiene la hoja `informativo` frente a `prqs escritas` para diseñar la regla exacta de fusión en la base de datos?
6. **Gas Caribe - Pestañas Mensuales:**
   * ¿En qué columna exacta se ubica `FECHA DE ATENCION` dentro de cada pestaña mensual de Gas Caribe? ¿El nombre de la hoja sigue estrictamente la convención `Mes Año`?

### ❓ Bloque 3: Infraestructura y Acceso a Base de Datos
7. **Motor de Base de Datos Seleccionado:**
   * ¿La base de datos central será PostgreSQL, Microsoft SQL Server, MySQL o una instancia en la nube (Azure SQL, AWS RDS)?
8. **Credenciales y Entorno:**
   * ¿Disponemos de un esquema/ambiente de pruebas (Dev/Staging) para realizar las cargas masivas preliminares sin afectar producción?

---

## 3. Plan de Acción Inmediato para la Semana
* [ ] **Lunes mañana:** Revisión conjunta de `estructura_de_datos.md` y resolución del cuestionario analítico.
* [ ] **Lunes tarde:** Análisis de muestras reales de cada hoja Excel para validar tipos de datos y nulos.
* [ ] **Martes:** Definición del script DDL (creación de tablas en la BD central).
* [ ] **Miércoles:** Construcción del módulo extractor de contingencia para SharePoint.
* [ ] **Jueves:** Carga histórica inicial masiva y auditoría de cuadre de cifras (totales por mes y gasera).
