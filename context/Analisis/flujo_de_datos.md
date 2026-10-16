# 🔄 Flujo de Datos - Reporte Gestión Diaria Promigas

Este documento define el ciclo de vida del dato desde su captura en las diferentes gaseras hasta su visualización en el reporte diario de gestión de retención.

---

## 1. Diagrama Conceptual del Flujo de Datos

```mermaid
flowchart TD
    subgraph Orígenes ["1. Fuentes de Datos (Insumos)"]
        subgraph Historico ["Histórico Desconectado"]
            BA["Base Acumulada (Descarga Local Antigua - Todas las Gaseras)"]
        end
        subgraph Diario ["Gestión Diaria (Operación)"]
            G1["Gasera 1 (Gestión Diaria)"]
            G2["Gasera 2 (Gestión Diaria)"]
            G3["Gasera 3 (Gestión Diaria)"]
            G4["Gasera 4 (Gestión Diaria)"]
            G5["Gasera 5 (Gestión Diaria)"]
            G6["Gasera 6 (Gestión Diaria)"]
        end
        BD["Base de Datos Centralizada (Futura/En Proceso)"]
    end

    subgraph Ingestion ["2. Ingesta y Captura"]
        LoadBA["Lectura y Perfilado de Base Acumulada"]
        RawExcel["Lectura Hojas / Rangos Gestión Diaria"]
        DBSync["Conexión y Extracción BD"]
    end

    subgraph Conciliacion ["3. Empalme y Reconciliación"]
        MergeKey["Cruce por Llave Común (ID_Contrato / ID_Gestion / Cliente)"]
        CheckGap["Identificación de Desfase Temporal / Brecha de Datos"]
    end

    subgraph Auditoria ["4. Capa de Validación y Calidad"]
        ValFormat["Validación de Estructura y Tipos"]
        CheckDups["Detección de Duplicados e Inconsistencias"]
        CheckNulls["Gestión de Registros Nulos / Vacíos"]
    end

    subgraph Transformacion ["5. Homologación y Transformación"]
        StdCat["Estandarización de Catálogos (Estados / Motivos)"]
        MapGaseras["Etiquetado y Mapeo por Gasera"]
        CalcMetrics["Cálculo de Métricas y KPIs Diarios"]
    end

    subgraph Storage ["6. Capa Analítica / Consolidado"]
        Staging["Tablas Consolidadas (Histórico + Diario Unificado)"]
    end

    subgraph Consumo ["7. Salidas y Visualización"]
        DashDaily["Dashboard de Retención Diario"]
        RepMgmt["Reportes Operativos y Gerenciales"]
    end

    BA --> LoadBA
    G1 --> RawExcel
    G2 --> RawExcel
    G3 --> RawExcel
    G4 --> RawExcel
    G5 --> RawExcel
    G6 --> RawExcel
    BD --> DBSync

    LoadBA --> MergeKey
    RawExcel --> MergeKey
    DBSync --> MergeKey
    MergeKey --> CheckGap --> ValFormat
    ValFormat --> CheckDups --> CheckNulls
    CheckNulls --> StdCat --> MapGaseras --> CalcMetrics
    CalcMetrics --> Staging
    Staging --> DashDaily
    Staging --> RepMgmt
```

---

## 2. Etapas Detalladas del Flujo

### Fase 1: Ingesta (Data Ingestion)
* **Fuentes:** Archivos Excel locales o compartidos por cada gasera + consultas a base de datos.
* **Frecuencia:** Diaria.
* **Riesgos analíticos a controlar:**
  * Variabilidad en el nombre de las columnas entre versiones de archivo.
  * Presencia de encabezados múltiples o filas combinadas en Excel.
  * Cambios de codificación (UTF-8, Latin-1, ANSI).

### Fase 2: Validación y Limpieza (Data Quality & Cleansing)
* **Validaciones obligatorias:**
  * Formato de fechas consistente (evitar ambigüedad DD/MM vs MM/DD).
  * Limpieza de strings (espacios extras, caracteres especiales, mayúsculas/minúsculas).
  * Unicidad de registros según la clave de gestión definida.

### Fase 3: Homologación de Negocio (Business Mapping)
* Unificación de conceptos entre las 5 o 6 gaseras:
  * ¿Cómo llama cada gasera al estado "Retenido"? (Ej: "Éxito", "Efectivo", "Retención Lograda").
  * ¿Cómo clasifica a los no contactados?
  * Homologación de motivos de retiro / reclamo.

### Fase 4: Almacenamiento y Salida (Data Serving)
* Generación del dataset maestro unificado para alimentar el tablero de control sin duplicidad de esfuerzo.

---

## 3. Matriz de Control de Calidad del Dato
* [ ] Auditoría de integridad referencial.
* [ ] Conteo de registros input vs output por gasera.
* [ ] Registro de logs de rechazo o inconsistencias (registros con error para retroalimentación operativa).
