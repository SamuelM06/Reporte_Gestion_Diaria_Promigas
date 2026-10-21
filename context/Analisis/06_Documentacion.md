# 📊 Documentación del Proyecto - Reporte Gestión Diaria Promigas

**Proyecto:** Gestión Diaria Promigas
**Alcance:** esquema `gestion_diaria` de `DataCenter_Promigas` (PostgreSQL 16.14)
**Estado:** Fase 1 completada — auditoría de datos en origen ejecutada el 19-oct-2026
**Última actualización:** 19 de octubre de 2026

---

## 1. Contexto del Negocio y Alcance
* **Organización:** Promigas.
* **Área:** Retención y Experiencia al Cliente.
* **Entidades / Gaseras Confirmadas (5):**
  1. **CEO** (Compañía Energética del Cauca) — *Solo Inbound*
  2. **Efigas** — *Solo Outbound*
  3. **Gas Caribe** (Gases del Caribe) — *Inbound y Outbound*
  4. **GDO** (Gases de Occidente) — *Registro En Vivo: Inbound, Outbound, PQRS*
  5. **Surtigas** — *Inbound (Histórico + Continuidad) y Outbound*
* **Objetivo General:** Diseñar y construir un sistema de reportería y dashboard diario para la gestión de retención, garantizando calidad, consistencia y trazabilidad de los datos recolectados día a día, facilitando la transición desde planillas Excel en SharePoint hacia una Base de Datos centralizada e integración definitiva con la plataforma **OCM (Omnichannel Contact Manager)**.

### 1.1 Alcance técnico del proyecto

| Aspecto | Definición |
| :--- | :--- |
| **Base de datos** | `DataCenter_Promigas` (PostgreSQL 16.14) — host, puerto y usuario en `database/.env` |
| **Esquema de trabajo** | `gestion_diaria` — 18 tablas, 5 vistas (4 legibles con el usuario actual), 4 funciones, 17 secuencias |
| **Volumen analizado** | **48.036 filas** de datos (29.046 atenciones · 12.710 abandono · 6.280 PQRS) |
| **Fuentes** | 13 libros de Excel en SharePoint, 5 gaseras |
| **Fuera de alcance** | Los demás esquemas de la instancia (`ocm_retencion`, `reportes`, `siniestros`, `auditoria`) no pertenecen a este proyecto. OCM aparece **solo como destino de la transición**, no como fuente de datos. |

---

## 2. Estado Actual

**Fase:** Fase 1 completada — Auditoría de datos en origen.

| Logro | Evidencia |
| :--- | :--- |
| ✅ Base de datos conectada y validada | 18 tablas, 5 vistas, 4 funciones inventariadas |
| ✅ 16 tablas fuente perfiladas | 48.036 filas: nulos, cardinalidad, dominios, ejemplos |
| ✅ Dominios de tipificación completos | 7 columnas de resultado × 5 gaseras, con volumetría |
| ✅ Reglas de negocio verificadas con datos | Efigas `FECHA BASE`, GDO `informativo`, Surtigas fragmentado |
| ✅ 35 hallazgos documentados | Con evidencia SQL reproducible (`04_Hallazgos_y_Backlog.md`) |
| ✅ 20 reglas de validación definidas | `05_Calidad_de_Datos.md` §8 |
| ✅ 5 decisiones de negocio identificadas | Bloqueantes para el KPI (`010_Registro_Decisiones_Riesgos.md` §1.3) |

### 2.1 Conclusión central de la auditoría

> El sistema **no tiene un problema de construcción de datos: tiene un problema de
> gobierno del dato.** La capa de datos está construida y cargada; el catálogo de
> homologación y las 4 funciones de normalización existen. Lo que falta es que las
> piezas **se concilien entre sí**.

**Los 4 bloqueos críticos:**

| # | Bloqueo | Hallazgo |
| ---: | :--- | :--- |
| 1 | **`APTA` no significa "retención"**: 3 de los 4 resultados APTA implican cancelación, y `CANCELADO` es el 63.6% de las filas | H-22 |
| 2 | **`operador` es la empresa operadora, no el asesor**: la productividad individual solo es calculable en GDO | H-23 |
| 3 | **Sangrado de columnas**: 1.589 filas tienen en `operador` un valor de `tipo_de_contacto` | H-24, H-25 |
| 4 | **43 variantes de resultado sin catalogar** (236 filas), y `normalizar_texto` no normaliza la `/` → 27 filas APTA de CEO sin clasificar | H-31, H-32 |

---

## 3. Mapa de Documentación

| # | Documento | Contenido | Estado |
| ---: | :--- | :--- | :---: |
| 01 | `planes/01_Plan_Estructura.md` | Hoja de ruta por fases, puertas de calidad, riesgos | ✅ |
| 02 | `planes/02_Plan_Migracion_y_Estrategia_DB.md` | Estrategia de datos, cuestionario del lunes respondido, plan de acción | ✅ |
| 03 | `Analisis/01_Diccionario_de_Datos.md` | **Inventario columna por columna** de las 17 tablas: nombre original del Excel, tipo, nulos, distintos, significado, ejemplos + catálogos de tipificación | ✅ **Nuevo** |
| 04 | `Analisis/02_Mapeo_Origen_Destino.md` | **Especificación de la ingesta**: cada columna del Excel → tabla y campo destino, con su transformación | ✅ **Nuevo** |
| 05 | `Analisis/03_Modelo_Datos.md` | **Modelo en estrella**: vista actual, vista objetivo, migraciones SQL M0–M8 con criterios de aceptación | ✅ **Nuevo** |
| 06 | `planes/03_Definicion_de_KPIs.md` | Definición de KPIs con el negocio — 7 KPIs comunes definidos y confirmados | ✅ **Definido** |
| 07 | `planes/04_Transicion_a_OCM.md` | Casamiento OCM×planilla y plan de apagado de Excel — delegado al compañero | 🟡 Delegado |
| 08 | `Analisis/010_Registro_Decisiones_Riesgos.md` | Decisiones (D-01…D-10), propuestas (P-01…P-14), abiertas (A-01…A-15), inconsistencias, supuestos, riesgos, preguntas | ✅ Actualizado |
| 09 | `Analisis/09_Normalizacion_y_Clasificacion.md` | Algoritmo de normalización, cola de revisión, DDL del catálogo maestro | ✅ Actualizado |
| 10 | `Analisis/04_Hallazgos_y_Backlog.md` | 35 hallazgos con evidencia + backlog B-01…B-35 | ✅ **Nuevo** |
| 11 | `Analisis/05_Calidad_de_Datos.md` | Perfil de calidad por tabla + 20 reglas de validación | ✅ **Nuevo** |
| 12 | `Analisis/011_OCM_Configuracion_Llamadas.md` | **Matriz oficial de configuración OCM**: qué gaseras manejan inbound/outbound, líneas telefónicas y skills asignados | ✅ **Nuevo** |
| 13 | `Analisis/012_Asesores_Gestion_Diaria.md` | **Listado de asesores de gestión diaria**: nombres, gaseras asociadas y roles por distribuidora | ✅ **Nuevo** |
| 14 | `Analisis/13_ERD_Estado_Actual.md` | **ERD estado actual**: diagrama entidad-relación lógico del esquema `gestion_diaria` + diagnóstico de integridad (compañero textual del PDF visual) | ✅ **Nuevo** |
| — | `Analisis/06_Documentacion.md` | Este índice | ✅ |
| — | `Analisis/07_Estructura_de_datos.md` | Inventario por gasera: hojas, campos clave, reglas operativas | ✅ |
| — | `Analisis/08_Flujo_De_Datos.md` | Arquitectura de flujo de datos y flujo objetivo | ✅ |
| — | `database/` | Conexión, plantilla de credenciales y herramienta de inspección | ✅ |

---

## 4. Convenciones del proyecto

| Prefijo | Significado |
| :--- | :--- |
| **H-01 … H-35** | Hallazgos (doc 04) |
| **B-01 … B-35** | Acciones del backlog (doc 04) |
| **D-01 … D-10** | Decisiones tomadas (doc 010) |
| **P-01 … P-14** | Propuestas pendientes de aprobar (doc 010) |
| **A-01 … A-15** | Decisiones abiertas (doc 010) |
| **R-01 … R-20** | Reglas de validación (doc 05) |
| **L-01 … L-07** | Reglas de limpieza de texto (doc 02) |
| **M0 … M8** | Migraciones SQL (doc 03) |

---

## 5. Cómo reproducir la verificación

```bash
# Prueba de conexión
python database/conexion_template.py

# Inventario, columnas, restricciones, índices, calidad, vistas y funciones
python database/inspeccion_esquema.py --todo

# Solo un esquema
python database/inspeccion_esquema.py --esquema gestion_diaria --calidad
```

Todas las cifras de la documentación son reproducibles con estas consultas y con las
que están citadas en cada documento.

---

## 6. 🔒 Estándar de Seguridad del Proyecto

> **Esta sección NO va en el README público.** Es una referencia interna para el equipo.
>
> **Origen:** requisito de la junta directiva — *todo proyecto debe tener una brecha de
> seguridad altísima*. Aplica a documentación, conexión a DB y cualquier artefacto futuro.

### 6.1 Reglas base (credenciales y acceso)

| # | Regla | Detalle |
| ---: | :--- | :--- |
| S-01 | **`.env` está en `.gitignore`** | Verificar con `git check-ignore -v database/.env` antes de cualquier commit. |
| S-02 | **El usuario de conexión no es superusuario** | No tiene permiso de escritura sobre los esquemas de producción verificados. |
| S-03 | **`ocm_retencion.agent.pass` contiene credenciales en texto plano** | Hash base64 reversible. **No extraer ni copiar** ese campo a ningún artefacto del proyecto. |
| S-04 | **Datos personales en varias tablas** | Nombre, documento, teléfono y dirección están presentes. Aplicar el **principio de minimización** al exponerlos en reportes. |
| S-05 | **Escaneo de secretos antes de cada commit** | Verificar que el diff no contenga host, usuario, contraseña, tokens ni rutas internas. |
| S-06 | **Solo placeholders en artefactos públicos** | README y docs muestran `<motor>`, `<host>`, `<usuario>`. Nunca valores reales. |

### 6.2 Caché y control de acceso a datos

| # | Regla | Detalle |
| ---: | :--- | :--- |
| S-07 | **Nunca cachear datos sensibles en el cliente** | Respuestas HTTP con `Cache-Control: no-store, no-cache, must-revalidate` para cualquier endpoint que devuelva datos personales o de gestión. |
| S-08 | **Headers de seguridad obligatorios** | `Strict-Transport-Security`, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Content-Security-Policy`. |
| S-09 | **Sin datos sensibles en URLs** | Nunca pasar PII ni credenciales por query params. |
| S-10 | **Sesiones y tokens con expiración corta** | Refresh tokens rotativos; access tokens con TTL mínimo. |
| S-11 | **Principio de mínimo privilegio** | Cada rol solo ve las tablas y columnas que necesita. Ningún rol compartido. |

### 6.3 Cifrado y transmisión

| # | Regla | Detalle |
| ---: | :--- | :--- |
| S-12 | **Solo conexiones cifradas** | PostgreSQL con `sslmode=require`. Nunca contraseñas o datos en texto plano por HTTP. |
| S-13 | **Cifrado en reposo** | Las copias de seguridad y los dumps deben ir cifrados. |
| S-14 | **No loguear datos personales** | Los logs no contienen nombre, documento, teléfono ni dirección de usuarios. |

### 6.4 Datos personales y reportes

| # | Regla | Detalle |
| ---: | :--- | :--- |
| S-15 | **Minimización en reportes** | Mostrar solo lo necesario. Si un KPI no necesita el nombre del usuario, no se expone. |
| S-16 | **Seudonimización cuando sea posible** | Reemplazar identificadores directos por IDs en reportes agregados. |
| S-17 | **Derecho al olvido** | Definir procedimiento para atender solicitudes de supresión (Ley 1581 de 2012). |

### 6.5 Verificación

```bash
# Antes de cada commit: verificar que .env está ignorado
git check-ignore -v database/.env

# Antes de cada push: verificar que no haya secretos en el diff
git diff --cached | grep -E "(password|host|token|api[_-]?key|secret)" \
  && echo "ALERTA: posible secreto en el diff" || echo "OK"

# Verificar que el README no contiene valores reales
grep -E "(DataCenter_Promigas|20\.7\.15\.40|samuel_mena|5432)" README.md \
  && echo "ALERTA: valor real en README" || echo "OK"
```

---

## 7. Próximo paso

**Resolver A-11** (¿el reporte mide productividad por empresa operadora o por asesor?) y
**cerrar la cola de 43 variantes** del catálogo (≈4-5 h de revisión humana).

Ambas están en `010_Registro_Decisiones_Riesgos.md` §1.3 y en el guion de la reunión.
