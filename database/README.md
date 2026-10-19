# 🗄️ Módulo de Base de Datos / Conexión

Utilidades para la conexión a `DataCenter_Promigas` (PostgreSQL 16.14) y la auditoría
del esquema `gestion_diaria`.

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
| `reportes` | `reporte_promi` (31,122) + backup GDO (8,813) | **Principal** — capa core consolidada |
| `ocm_retencion` | Réplica OCM: `log_calls` (338,254), agentes, campañas, sync | **Secundario** — verdad de llamadas y abandonos |
| `siniestros` | 28,882 casos, bitácora de cargas | Fuera de alcance (proyecto paralelo) |
| `auditoria` | `retencion` (54 col.) + 4 vistas | ⚗️ **Requiere `GRANT USAGE`** (P-17) |

> Detalle completo en `context/Analisis/03_Modelo_Datos.md`.

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
* El usuario de conexión **no es superusuario** y no tiene permiso de escritura
  sobre los esquemas de producción verificados.
* `ocm_retencion.agent.pass` contiene credenciales de agentes en texto plano
  (hash base64 reversible): **no extraer ni copiar ese campo** a ningún artefacto
  del proyecto.
* Los datos personales (nombre, documento, teléfono, dirección) están presentes en
  varias tablas: aplicar el principio de minimización al exponerlos en reportes.
