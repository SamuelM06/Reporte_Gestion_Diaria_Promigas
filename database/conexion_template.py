"""
Módulo de Conexión a Base de Datos - Plantilla Base
Reporte Gestión Diaria - Promigas

Este script servirá como plantilla de conexión cuando se reciban las credenciales formales.
Utiliza variables de entorno para evitar almacenar contraseñas en código fuente.
"""

import os
import urllib.parse
from typing import Optional
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

# Cargar variables de entorno desde el archivo .env
load_dotenv()

DB_TYPE = os.getenv("DB_TYPE", "mssql").lower()
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "1433")
DB_NAME = os.getenv("DB_NAME", "")
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


if __name__ == "__main__":
    print("Iniciando prueba de conexión con la plantilla de configuración...")
    test_connection()
