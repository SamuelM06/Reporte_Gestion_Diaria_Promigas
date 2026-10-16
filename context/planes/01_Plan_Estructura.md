# 📋 Plan 01: Estructura del Proyecto y Fases de Trabajo

## 1. Visión del Plan
Este documento establece la hoja de ruta integral para la ejecución del proyecto **Reporte de Gestión Diaria - Retención Promigas**. Sigue una metodología orientada a datos (*Data-First*), donde cada fase depende de la total compresión de la fase anterior.

---

## 2. Cronograma de Fases

### 🔷 Fase 0: Preparación y Gobernanza (Actual)
* **Objetivo:** Disponer del entorno de trabajo, repositorios y estándares de documentación.
* **Entregables:**
  * [x] Repositorio Git vinculado con GitHub.
  * [x] Estructura de carpetas analíticas (`context/Analisis`, `context/planes`, `database`).
  * [x] Documentos iniciales de flujo y análisis de requerimientos.
  * [x] Plantilla base de conexión a base de datos segura.

### 🔷 Fase 1: Inmersión y Auditoría de Datos en Origen
* **Objetivo:** Comprender al 100% cada archivo Excel, cada hoja, cada columna y la conexión a la base de datos antes de proponer código o transformaciones.
* **Actividades Clave:**
  * Recepción y catalogación de rutas de archivos Excel por gasera.
  * Análisis de estructura: dimensiones (filas x columnas), tipos de datos inferidos vs reales.
  * Identificación de la semántica de cada hoja y posibles campos calculados manuales.
  * Definición de preguntas analíticas por cada fuente.
* **Entregable:** Matriz de Insumos y Diccionario de Datos Preliminar.

### 🔷 Fase 2: Homologación y Reglas de Negocio Multigasera
* **Objetivo:** Resolver la dispersión de criterios entre las 5 o 6 gaseras.
* **Actividades Clave:**
  * Comparación de catálogos: ¿Cómo tipifica cada gasera las gestiones de retención?
  * Reglas para determinar "Gestión Exitosa", "Retención Fallida", "En Seguimiento", etc.
  * Mapeo de equivalencias cruzadas entre gaseras.
* **Entregable:** Catálogo Maestro Homologado de Retención.

### 🔷 Fase 3: Conexión y Automatización de la Data (Capa ETL/ELT)
* **Objetivo:** Configuración de la conexión real a base de datos y scripts de extracción/unificación.
* **Actividades Clave:**
  * Configuración segura de variables de entorno (`.env`).
  * Validación de conectividad a la BD con la plantilla creada.
  * Pipeline de ingesta diaria automatizada (Excel + BD).
* **Entregable:** Scripts modulares de extracción y consolidación de datos con logs de auditoría.

### 🔷 Fase 4: Modelado Analítico y Métricas
* **Objetivo:** Estructurar el dataset final con los KPIs que la dirección de Promigas y Retención necesitan.
* **Actividades Clave:**
  * Conteo de gestiones por gasera/agente/fecha.
  * Tasa de retención (% efectividad).
  * Distribución de motivos de retiro.
* **Entregable:** Modelo de datos analítico (tablas agregadas y dimensionales).

### 🔷 Fase 5: Desarrollo de Backend y Dashboard Visual
* **Objetivo:** Construcción de la interfaz gráfica y reportes interactivos finales.
* **Actividades Clave:**
  * Arquitectura backend para servir los datos filtrados y agregados.
  * Dashboard con alta estética visual, filtros por gasera, fecha y estado de gestión.
  * Exportación de reportes operativos.
* **Entregable:** Tablero en producción validado por el área de retención.

---

## 3. Criterio de Control: "No avanzar sin entender la Data"
> **Regla de oro:** No se programará ninguna interfaz ni se cerrará ningún backend sin haber revisado exhaustivamente cada hoja de cálculo, cada tabla y cada caso atípico en la data.
