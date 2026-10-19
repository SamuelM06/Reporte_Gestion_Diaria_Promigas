"""
Módulo de Conexión a Base de Datos - Reporte Gestión Diaria Promigas

Conexión a `DataCenter_Promigas` (PostgreSQL 16.14) con credenciales en variables
de entorno, para no almacenar contraseñas en código fuente.

Configuración:
    1. Copiar `database/.env.example` a `database/.env` y completar los valores.
    2. `python database/conexion_template.py` para probar la conexión.
    3. `python database/inspeccion_esquema.py --todo` para la auditoría del esquema.

Esquemas disponibles en la instancia: `gestion_diaria` (esquema de trabajo),
`ocm_retencion` (réplica OCM), `reportes` (capa core), `siniestros`, `auditoria`
(requiere `GRANT USAGE`), `public`.
"""

import os
import sys
import urllib.parse
from pathlib import Path
from typing import Optional
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

# Evitar UnicodeEncodeError en consolas Windows (cp1252) al imprimir emojis/acentos
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Cargar variables de entorno desde el archivo .env (en la carpeta de este módulo)
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
load_dotenv(BASE_DIR.parent / ".env")

DB_TYPE = os.getenv("DB_TYPE", "postgresql").lower()
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "")
DB_SCHEMA = os.getenv("DB_SCHEMA", "gestion_diaria")
DB_USER = os.getenv("DB_USER", "")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_ODBC_DRIVER = os.getenv("DB_ODBC_DRIVER", "ODBC Driver 17 for SQL Server")


def build_connection_url() -> str:
    """
    Construye la URL de conexión SQLAlchemy según el motor configurado.
    """
    encoded_password = urllib.parse.quote_plus(DB_PASSWORD)

    if DB_TYPE in ["mssql", "sqlserver"]:
        params = urllib.parse.quote_plus(
            f"DRIVER={{{DB_ODBC_DRIVER}}};"
            f"SERVER={DB_HOST},{DB_PORT};"
            f"DATABASE={DB_NAME};"
            f"UID={DB_USER};"
            f"PWD={DB_PASSWORD};"
            "TrustServerCertificate=yes;"
        )
        return f"mssql+pyodbc:///?odbc_connect={params}"

    elif DB_TYPE in ["postgres", "postgresql"]:
        return f"postgresql+psycopg2://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    elif DB_TYPE in ["mysql"]:
        return f"mysql+pymysql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    elif DB_TYPE in ["oracle"]:
        return f"oracle+cx_oracle://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/?service_name={DB_NAME}"

    else:
        raise ValueError(f"Motor de base de datos '{DB_TYPE}' no soportado en la plantilla.")


def get_db_engine() -> Engine:
    """
    Crea y retorna un Engine de SQLAlchemy.
    """
    connection_url = build_connection_url()
    return create_engine(connection_url, pool_pre_ping=True)


def test_connection() -> bool:
    """
    Valida la conexión ejecutando una consulta simple (SELECT 1).
    """
    try:
        engine = get_db_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).scalar()
            print(f"✅ Conexión exitosa a la base de datos ({DB_TYPE}). Resultado test: {result}")
            return True
    except Exception as e:
        print(f"❌ Error al conectar a la base de datos: {e}")
        return False


def query_to_dataframe(sql_query: str, params: Optional[dict] = None) -> pd.DataFrame:
    """
    Ejecuta una consulta SQL y retorna los datos en un DataFrame de pandas.
    """
    engine = get_db_engine()
    with engine.connect() as conn:
        df = pd.read_sql(text(sql_query), conn, params=params)
    return df


def list_tables(schema: Optional[str] = None) -> pd.DataFrame:
    """
    Lista las tablas de un esquema con su número de filas estimado.
    """
    schema = schema or DB_SCHEMA
    sql = f"""
        SELECT table_schema, table_name, table_type
        FROM information_schema.tables
        WHERE table_schema = :schema
        ORDER BY table_name
    """
    return query_to_dataframe(sql, params={"schema": schema})


if __name__ == "__main__":
    print("Iniciando prueba de conexión con la plantilla de configuración...")
    if test_connection():
        print(f"\nEsquema de trabajo: {DB_SCHEMA}")
        print(list_tables().to_string(index=False))
