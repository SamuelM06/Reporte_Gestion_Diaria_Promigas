# 📈 Reporte de Gestión Diaria - Retención Promigas

Repositorio centralizado para el análisis, ingesta, estandarización y reportería de la gestión diaria del **Área de Retención** para las gaseras de Promigas (5 distribuidoras).

---

## 🎯 Objetivo del Proyecto
Diseñar un sistema unificado y robusto de analítica y reportería diaria que permita comprender, monitorear y optimizar los indicadores de retención de clientes en las distintas gaseras asociadas a Promigas.

---

## 🧭 Enfoque de Trabajo: *Data Analyst First*
1. **Auditoría de Insumos:** Entender cada archivo Excel, cada hoja y cada registro recibido. ✅
2. **Homologación de Criterios:** Estandarizar estados y tipificaciones entre las 5 gaseras. ⏳
3. **Calidad y Validación:** Control de nulos, duplicados y reglas de negocio. ✅
4. **Automatización:** Conexión a bases de datos y scripts de transformación. ✅ (conexión) / ⏳ (automatización)
5. **Dashboard:** Presentación ejecutiva y operativa. ⏳

---

## 🗄️ Base de Datos Conectada

| Parámetro | Valor |
| :--- | :--- |
| **Motor** | PostgreSQL 16.14 |
| **Host / Puerto** | Definidos en `database/.env` (no versionados) |
| **Base de datos** | `DataCenter_Promigas` |
| **Esquema de trabajo** | `gestion_diaria` |
| **Usuario** | Definido en `database/.env` (no versionado) |
| **Estado** | ✅ **Conectada y auditada** (19-oct-2026) |

**Alcance del proyecto:** 18 tablas, 5 vistas (4 legibles), 4 funciones y **48.036 filas de
datos** (29.046 atenciones · 12.710 abandono · 6.280 PQRS) en el esquema `gestion_diaria`.
Los demás esquemas de la instancia no pertenecen a este proyecto.

**Velocidad de arranque:**

```bash
pip install sqlalchemy pandas python-dotenv psycopg2-binary
python database/conexion_template.py          # prueba de conexión
python database/inspeccion_esquema.py --todo  # auditoría completa del esquema
```

Las credenciales reales están en `database/.env` (**ignorado por Git**).
`database/.env.example` es la **plantilla versionada**, sin valores reales.

---

## 📂 Estructura del Repositorio

```text
├── context/
│   ├── Analisis/
│   │   ├── 01_Diccionario_de_Datos.md          # Inventario columna por columna de las 17 tablas
│   │   ├── 02_Mapeo_Origen_Destino.md         # Especificación de la ingesta, campo por campo
│   │   ├── 03_Modelo_Datos.md                 # Modelo en estrella + migraciones SQL M0–M8
│   │   ├── 04_Hallazgos_y_Backlog.md           # 35 hallazgos + 35 acciones priorizadas
│   │   ├── 05_Calidad_de_Datos.md             # Perfil por tabla + 20 reglas de validación
│   │   ├── 06_Documentacion.md                # Índice, contexto y estado
│   │   ├── 07_Estructura_de_datos.md          # Inventario por gasera: hojas y campos clave
│   │   ├── 08_Flujo_De_Datos.md               # Arquitectura de flujo de datos
│   │   ├── 09_Normalizacion_y_Clasificacion.md # Algoritmo de normalización y cola de revisión
│   │   └── 010_Registro_Decisiones_Riesgos.md # Decisiones, riesgos y preguntas abiertas
│   └── planes/
│       ├── 01_Plan_Estructura.md              # Hoja de ruta por fases
│       ├── 02_Plan_Migracion_y_Estrategia_DB.md # Estrategia + cuestionario respondido
│       ├── 03_Definicion_de_KPIs.md           # 🟡 7 KPIs definidos; fórmulas pendientes
│       └── 04_Transicion_a_OCM.md             # 🟡 Delegado al compañero del equipo
├── database/
│   ├── .env                                   # Credenciales reales (NO versionar)
│   ├── .env.example                           # Plantilla versionada
│   ├── conexion_template.py                   # Módulo de conexión (SQLAlchemy/pandas)
│   ├── inspeccion_esquema.py                  # Herramienta de auditoría del esquema
│   └── README.md                              # Guía de configuración y uso
├── .gitignore                                 # Protección de credenciales y datos pesados
└── README.md
```

---

## 🚀 Estado Actual

**Fase:** Fase 1 completada — Auditoría de datos en origen sobre la base de datos real.

| Logro | Evidencia |
| :--- | :--- |
| ✅ Base de datos conectada y validada | 18 tablas, 5 vistas, 4 funciones |
| ✅ 16 tablas fuente perfiladas | 48.036 filas: nulos, cardinalidad, dominios |
| ✅ Dominios de tipificación completos | 7 columnas de resultado × 5 gaseras |
| ✅ Reglas de negocio verificadas con datos | Efigas `FECHA BASE`, GDO `informativo`, Surtigas |
| ✅ 35 hallazgos documentados | Con evidencia SQL reproducible |
| ✅ 20 reglas de validación definidas | `05_Calidad_de_Datos.md` |
| ✅ 5 decisiones de negocio pendientes | Bloqueantes para todo KPI |

### ⚠️ Conclusión Central de la Auditoría

> El sistema **no tiene un problema de construcción de datos: tiene un problema de
> gobierno del dato.** La capa de datos está construida y cargada, el catálogo de
> homologación y las funciones de normalización existen — pero cada pieza fue
> construida con reglas distintas y hoy no se concilian entre sí.

**Los 4 bloqueos críticos:**

| # | Bloqueo | Hallazgo |
| ---: | :--- | :--- |
| 1 | **`APTA` no significa "retención"**: 3 de los 4 resultados APTA implican cancelación, y `CANCELADO` es el 63.6% de las filas | H-22 |
| 2 | **`operador` es la empresa operadora, no el asesor**: la productividad individual solo es calculable en GDO | H-23 |
| 3 | **Sangrado de columnas**: 1.589 filas tienen en `operador` un valor de `tipo_de_contacto` | H-24, H-25 |
| 4 | **43 variantes de resultado sin catalogar**, y `normalizar_texto` no normaliza la `/` → 27 filas APTA de CEO sin clasificar | H-31, H-32 |

> **Nota sobre el #4:** el número 43 es un *snapshot* del 19-oct-2026, no un techo. El
> espacio de variantes es **abierto** (ver `09_Normalizacion_y_Clasificacion.md` §1.2):
> lo que hay que construir no es un catálogo cerrado, sino el mecanismo de
> descubrimiento y aprendizaje continuo.

**Próximo paso:** resolver **A-11** (¿el reporte mide productividad por empresa o por
asesor?) y cerrar la **cola de 43 variantes** del catálogo (≈4-5 h de revisión humana).
Detalle en `010_Registro_Decisiones_Riesgos.md` §1.3.
