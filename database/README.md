# 🗄️ Módulo de Base de Datos / Conexión

Utilidades para la conexión a `DataCenter_Promigas` (PostgreSQL 16.14) y la auditoría
del esquema `gestion_diaria`.

> 🔴 **Estado crítico (21-oct-2026):** el contenido actual de `gestion_diaria` es un
> **snapshot estático de una descarga manual de Excel de SharePoint** (dos fechas de
> carga: 15-sep y 01-oct-2026). Está desactualizado y hay que reemplazarlo por la
> gestión diaria real.
>
> **NO se trunca nada todavía (D-11).** Hasta que se defina el día de cierre de Excel,
> los registros de 2026 de las 5 gaseras deben quedar registrados en la base. La
> estrategia —truncado + recarga, esquema paralelo o carga incremental— sigue abierta
> (**A-16**). Los registros de OCM también deben persistirse (**D-12**).
> Ver **`PROCEDENCIA_Y_REINGESTA.md`**.

---

## 📌 Configuración

1. **Archivo `.env`** — ya existe en `database/.env` con las credenciales reales.
   Está en el `.gitignore` del repositorio: **no se versiona**.
   Para replicar el entorno en otra máquina, copia `.env.example` y complétalo:

   ```bash
   cp database/.env.example database/.env
   ```

2. **Variables de entorno**

   | Variable | Valor | Notas |
   | :--- | :--- | :--- |
   | `DB_TYPE` | `postgresql` | Soporta `postgresql`, `mssql`, `mysql`, `oracle` |
   | `DB_HOST` | `<host>` | |
   | `DB_PORT` | `<puerto>` | |
   | `DB_NAME` | `DataCenter_Promigas` | |
   | `DB_SCHEMA` | `gestion_diaria` | Esquema de trabajo por defecto |
   | `DB_USER` | `<usuario>` | |
   | `DB_PASSWORD` | *(en `.env`)* | **Nunca versionar** |
   | `DB_ODBC_DRIVER` | `ODBC Driver 17 for SQL Server` | Solo para MSSQL |

---

## 🚀 Uso

### 1. Probar la conexión

```bash
pip install sqlalchemy pandas python-dotenv psycopg2-binary
python database/conexion_template.py
```

Salida esperada:

```text
Iniciando prueba de conexión con la plantilla de configuración...
✅ Conexión exitosa a la base de datos (postgresql). Resultado test: 1

Esquema de trabajo: gestion_diaria
  table_schema          table_name                 table_type
  gestion_diaria       caribe_abandono            BASE TABLE
  ...
```

### 2. Auditar el esquema

```bash
python database/inspeccion_esquema.py --tablas        # inventario + row counts
python database/inspeccion_esquema.py --columnas       # detalle de columnas
python database/inspeccion_esquema.py --restricciones  # PK, unique y FK
python database/inspeccion_esquema.py --indices        # índices definidos
python database/inspeccion_esquema.py --calidad        # perfil de calidad temporal
python database/inspeccion_esquema.py --vistas         # definiciones de vistas
python database/inspeccion_esquema.py --funciones      # funciones del esquema
python database/inspeccion_esquema.py --todo           # todo
python database/inspeccion_esquema.py --esquema ocm_retencion  # otro esquema
```

> La herramienta es **de solo lectura**: consulta el catálogo de PostgreSQL y perfila
> las tablas. No escribe ni modifica datos.

### 3. Usar el módulo desde Python

```python
from database.conexion_template import get_db_engine, query_to_dataframe, list_tables
from sqlalchemy import text

df = query_to_dataframe("""
    SELECT gasera_norm, count(*) AS n
    FROM reportes.reporte_promi
    GROUP BY 1 ORDER BY 2 DESC
""")

with get_db_engine().connect() as conn:
    for fila in conn.execute(text("SELECT version()")):
        print(fila[0])
```

---

## 🗂️ Qué hay en cada esquema

| Esquema | Contenido | Uso en el proyecto |
| :--- | :--- | :--- |
| `gestion_diaria` | 17 tablas fuente + `clasificacion`, 5 vistas, 4 funciones | **Principal** — datos por gasera × cabina |
| `reportes` | `reporte_promi` (29.222) + backup GDO (8.813) | **Principal** — capa core consolidada |
| `ocm_retencion` | Réplica OCM: `log_calls` (339.499), agentes, campañas, sync | **Secundario** — verdad de llamadas y abandonos |
| `siniestros` | 28.882 casos, bitácora de cargas | Fuera de alcance (proyecto paralelo) |
| `auditoria` | `retencion` (54 col.) + 4 vistas | ⚗️ **Requiere `GRANT USAGE`** (P-17) |

> Detalle completo en `context/Analisis/03_Modelo_Datos.md`.

---

## 🔎 Origen de los datos (procedencia)

> Evidencia SQL y plan de reingesta: **`database/PROCEDENCIA_Y_REINGESTA.md`**

| Capa | Origen físico | ¿Automático? |
| :--- | :--- | :--- |
| `gestion_diaria` (48.036 filas) | **Libros Excel de SharePoint** (13 libros, 5 gaseras) | ❌ Manual, snapshot 15-sep / 01-oct-2026 |
| `gestion_diaria.clasificacion` (40) | Catálogo interno (solo GasCaribe) | ❌ Manual |
| `reportes.reporte_promi` (29.222) | Consolidado del universo Excel (reconstruido 21-oct 15:57) | ❌ Externo al repo |
| `ocm_retencion` (339.499 llamadas) | **Plataforma OCM** | ✅ Automático, ~2 min |

* No hay **Excel local versionado**: `.gitignore` excluye `*.xlsx`/`*.xls`/`*.csv`;
  las descargas van a `data/raw/` (ignorado por Git).
* No hay **ETL**: cero triggers, cero procedimientos, cero jobs en la BD. Los únicos
  scripts del repo son de **solo lectura**.
* Las 5 vistas del esquema sobreviven a un `TRUNCATE` pero quedan vacías.

### Documentos del módulo

| Documento | Contenido |
| :--- | :--- |
| `PROCEDENCIA_Y_REINGESTA.md` | Procedencia verificada, evidencia del snapshot y plan de persistencia (truncado / esquema paralelo / incremental) |
| `FICHA_ORIGEN_POR_GASERA.md` | **Rutas, libros, hojas y columnas guía por gasera** (verificadas contra los archivos) + volumetría 2026 |
| `perfilador_excel.py` | Perfila libros Excel: hojas, columnas, nulos y roles. No imprime valores (PII excluida) |

### Verificación rápida del origen

```bash
python database/perfilador_excel.py --ruta data/raw --muestra
# -> context/Analisis/14_Perfil_Excel_Por_Gasera.md
```

Inventario técnico completo del origen (9 libros, 41 hojas, 17 hallazgos):
`context/Analisis/14_Estructura_Origen_Excel.md`.

---

## 📚 Librerías

| Motor | Driver |
| :--- | :--- |
| **PostgreSQL** | `psycopg2-binary` ✅ (instalado y en uso) |
| SQL Server | `pyodbc` |
| MySQL | `pymysql` |
| Oracle | `cx_Oracle` / `oracledb` |

Comunes: `sqlalchemy`, `pandas`, `python-dotenv`.

---

## 🔒 Seguridad

* `.env` está en `.gitignore` (`*.env`, `.env.*.local`). Verificar con
  `git check-ignore -v database/.env` antes de cualquier commit.
* El usuario de conexión (`<usuario_conexion>`) **no es superusuario**, pero **es owner de las
  tablas** de `gestion_diaria` y `reportes`: tiene `INSERT/UPDATE/DELETE/TRUNCATE`
  (verificado 21-oct-2026). Esto contradice la versión anterior de este README, que
  decía que no había permiso de escritura. Consecuencia: **cualquier `TRUNCATE` es
  irreversible y solo se respalda si antes se ejecuta la Fase 0 del plan de reingesta**
  (`PROCEDENCIA_Y_REINGESTA.md` §5.2). Para automatizar la ingesta con otra cuenta,
  delegar permisos explícitos al rol de ingesta.
* `ocm_retencion.agent.pass` contiene credenciales de agentes en texto plano
  (hash base64 reversible): **no extraer ni copiar ese campo** a ningún artefacto
  del proyecto.
* Los datos personales (nombre, documento, teléfono, dirección) están presentes en
  varias tablas: aplicar el principio de minimización al exponerlos en reportes.
