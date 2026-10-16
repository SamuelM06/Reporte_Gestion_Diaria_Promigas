# 🏛️ Estructura de Datos Técnica y Operativa - Promigas

> **Fuente Oficial:** Documento de Especificación Técnica & Operativa - *Estructura de Datos y Flujo de Gestión Diaria Promigas*.  
> **Objetivo:** Definir la matriz de fuentes, tipología de cabinas, libros, hojas y campos clave para la unificación y posterior migración a Base de Datos.

---

## 1. Matriz General de Cabinas y Reglas Operativas

| Concepto Operativo | Definición Técnica | Aplica a | Regla de Negocio / Calidad |
| :--- | :--- | :--- | :--- |
| **Cabina / Cabinas** | Término que engloba conjuntamente las operaciones de **INBOUND** (entrantes) y **OUTBOUND** (salientes). | Operación General Promigas | Diferenciar siempre el tipo de tráfico telefónico. |
| **Inbound** | Recepción de llamadas entrantes por parte del equipo de asesores de retención. | CEO, Gas Caribe, GDO, Surtigas | Requiere auditar tiempos de atención y tasa de abandono. *(Efigas NO tiene Inbound)*. |
| **Outbound** | Gestión de llamadas salientes realizadas por el asesor hacia el usuario. | Efigas, Gas Caribe, GDO, Surtigas | La fecha válida es la de ejecución del contacto. *(CEO NO tiene Outbound)*. |
| **Abandono** | Llamadas entrantes que se cortan antes de ser atendidas por un asesor. | Exclusivo de Cabina Inbound | No tiene asesor asignado; se usa para métricas de nivel de servicio. |
| **PQRS / Informativo** | Peticiones, Quejas, Reclamos y Solicitudes radicadas por escrito. | GDO | La pestaña `informativo` es conceptualmente PQRS y debe homologarse. |

---

## 2. Inventario Detallado de Fuentes por Gasera

### 🏢 1. CEO (Compañía Energética del Cauca)
* **Cabina:** Exclusivamente **Inbound** (no maneja Outbound).
* **Ruta / Carpeta:** Carpeta `CEO` (SharePoint).
* **Archivo Principal:** `Gestion diaria CEO.xlsx`
* **Estructura de Hojas:**
  1. `Gestion Diaria Inbound Ceo`: Registros de atención de llamadas entrantes.
  2. `Abandono`: Registros de llamadas no contestadas / cortadas.
* **Campo Clave Temporal:** `FECHA INGRESO LLAMADA` (columna obligatoria para consolidar totales mensuales).

---

### 🏢 2. Efigas
* **Cabina:** Exclusivamente **Outbound** (no maneja Inbound ni abandono).
* **Ruta / Carpeta:** Carpeta `Efigas` (SharePoint).
* **Archivo Principal:** `Gestion Diaria Outbound - Efigas.xlsx`
* **Estructura de Hojas:**
  1. `base efigas`: Hoja única de gestión saliente.
* **Reglas Críticas de Fechas:**
  * ✅ **Usar:** `FECHA DE EJECUCION` (indica el momento real en que se efectuó la llamada saliente).
  * ⚠️ **IGNORAR:** `FECHA BASE` (únicamente refleja la fecha en que se cargó el listado al sistema, no la gestión).

---

### 🏢 3. Gas Caribe (Gases del Caribe)
* **Cabina:** **Ambas Cabinas** (Inbound y Outbound).
* **Ruta / Carpeta:** Carpeta `Gas Caribe` (SharePoint). Se debe enfocar **únicamente en los 2 libros principales**:
* **Libros de Trabajo:**
  1. **Cabina Inbound:** `Gestion diaria Inbound -gases del caribe.xlsx`
     * *Estructura de Hojas:* Organizado en pestañas por mes (ej. `Enero 2026`) + hoja `abandono`.
     * *Columna de Agrupación:* `FECHA DE ATENCION` o sufijo de año en el nombre de la pestaña (`2026`).
  2. **Cabina Outbound:** `gestión diaria outbound-gases del caribe.xlsx`
     * *Estructura de Hojas:* Hoja `outbound`.
     * *Columna de Agrupación:* Columna directa `MES` para agrupación rápida.

---

### 🏢 4. GDO (Gases de Occidente) - Registro En Vivo
* **Cabina:** **Ambas Cabinas + PQRS Escritas**.
* **Condición Especial:** Archivo independiente conectado directamente con los asesores (operación en vivo).
* **Archivo:** `VALIDACION INFORMACION GDO- 24 de Junio 2026.xlsx` (en SharePoint).
* **Estructura de Hojas:**
  1. `gestión inbound`
  2. `out`
  3. `prqs escritas`
  4. `informativo`
  5. `abandono`
* **Regla de Limpieza y Homologación:**
  * La hoja `informativo` corresponde técnicamente a **PQRS** y debe renombrarse/unificarse bajo la tipología de PQRS durante la ingesta a la base de datos.

---

### 🏢 5. Surtigas
* **Cabina:** **Ambas Cabinas** (Inbound y Outbound).
* **Ruta / Carpeta:** Carpeta `SURTIGAS` (SharePoint).
* **Particularidad de Inbound (Fragmentación Histórica vs Continuidad):**
  1. **Inbound Histórico (Enero - Junio):**
     * Archivo: `SURTIGAS ARCHIVO RECUPERADO - Copia.xlsx` *(Sustituye archivo que sufrió daño)*.
     * Hojas: `Enero a Marzo`, `abrl` [sic], `mayo`, `junio`.
  2. **Inbound Continuidad (Julio - Octubre y subsiguientes):**
     * Ubicación: Subcarpeta `JULIO - AGOSTO 2026`.
     * Archivo: `Gestión diaria Inbound Surtigas.xlsx` (incluye hoja `ABANDONO`).
  3. **Cabina Outbound:**
     * Ubicación: Carpeta `SURTIGAS`.
     * Archivo: `gestión diaria outbound surtugas.xlsx`.
* **Columna Clave Temporal:** `FECHA DE LLAMADA` (aplica uniformemente a ambas cabinas).

---

## 3. Matriz Comparativa de Homologación de Fuentes

| Gasera | Cabina Inbound | Cabina Outbound | PQRS / Otros | Abandono | Columna Fecha Maestra | Ubicación / Archivo(s) |
| :--- | :---: | :---: | :---: | :---: | :--- | :--- |
| **CEO** | Sí | No | No | Sí | `FECHA INGRESO LLAMADA` | `CEO / Gestion diaria CEO.xlsx` |
| **Efigas** | No | Sí | No | No | `FECHA DE EJECUCION` *(ignorar FECHA BASE)* | `Efigas / Gestion Diaria Outbound - Efigas.xlsx` |
| **Gas Caribe** | Sí | Sí | No | Sí | `FECHA DE ATENCION` (Inb) / `MES` (Out) | 2 libros: `Gestion diaria Inbound...` y `gestión diaria outbound...` |
| **GDO** | Sí | Sí | Sí (`prqs escritas` + `informativo`) | Sí | Fecha de registro en vivo | 1 libro en vivo: `VALIDACION INFORMACION GDO...` |
| **Surtigas** | Sí | Sí | No | Sí | `FECHA DE LLAMADA` | 3 libros: Histórico Ene-Jun, Continuidad Jul-Oct, Outbound |

---

## 4. Rutas Oficiales en SharePoint

* **Ruta Madre (CEO, Efigas, Gas Caribe, Surtigas):**  
  `https://chariotandcastle.sharepoint.com/:f:/s/teamexperienciaalcliente/IgCMliHwe9GjTZbIUZDTZdpoAY0MFBoTaxKnLBbmFNDX7Gg?e=yCdsBa`
* **Ruta Archivo en Vivo (GDO):**  
  `https://chariotandcastle.sharepoint.com/:x:/r/sites/teamexperienciaalcliente/_layouts/15/doc2.aspx?sourcedoc=%7B89E8CBEE-0646-4F78-B9C8-4B2B8B0A86D6%7D&file=VALIDACION%20INFORMACION%20GDO-%2024%20de%20Junio%202026.xlsx`

---

## 5. Puntos Críticos y Cuestionamientos para Análisis (Reunión del Lunes)

1. **Homogeneidad de Columnas por Hoja:**
   * ¿Cada pestaña mensual de Gas Caribe y Surtigas conserva exactamente el mismo orden y nombre de columnas, o hay variaciones en tildes, minúsculas o nombres (`abrl` vs `Abril`)?
2. **Definición de Clave Primaria (PK):**
   * Al no venir de un sistema transaccional único, ¿cuál es la llave única? ¿Combinación de `(Gasera + Tipo_Cabina + Fecha + Contrato/Cuenta + Asesor)` o se generará un Hash ID / UUID autogenerado?
3. **Estrategia con la Base Local Desactualizada:**
   * ¿La base local contiene datos previos a 2026? ¿Se va a limpiar y cargar como histórico estático o se reemplaza totalmente leyendo los archivos recuperados de SharePoint?
4. **Ventana de Transición a OCM:**
   * ¿Cuándo entra formalmente OCM para cada gasera? (Esto define la vigencia del script de sincronización con SharePoint).
