"""
Inspección del esquema de DataCenter_Promigas (esquema gestion_diaria).

Herramienta de auditoría para la fase de análisis. NO modifica datos:
solo consulta el catálogo de PostgreSQL y perfila las tablas de origen.

Uso:
    python database/inspeccion_esquema.py                 # resumen por defecto
    python database/inspeccion_esquema.py --tablas        # inventario + row counts
    python database/inspeccion_esquema.py --columnas       # detalle de columnas
    python database/inspeccion_esquema.py --calidad        # perfil de calidad
    python database/inspeccion_esquema.py --vistas         # definiciones de vistas
    python database/inspeccion_esquema.py --todo           # todas las secciones
    python database/inspeccion_esquema.py --esquema ocm_retencion
"""

import argparse
import sys
from pathlib import Path

import pandas as pd
from sqlalchemy import text

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from conexion_template import DB_SCHEMA, get_db_engine  # noqa: E402


# --------------------------------------------------------------------------
# Consultas de catálogo
# --------------------------------------------------------------------------
SQL_INVENTARIO = """
SELECT table_schema, table_name, table_type
FROM information_schema.tables
WHERE table_schema = :schema
ORDER BY table_type, table_name
"""

SQL_COLUMNAS = """
SELECT table_name, ordinal_position, column_name, data_type,
       character_maximum_length AS largo, is_nullable, column_default
FROM information_schema.columns
WHERE table_schema = :schema
ORDER BY table_name, ordinal_position
"""

SQL_CONSTRAINTS = """
SELECT tc.table_name, tc.constraint_type, tc.constraint_name,
       string_agg(kcu.column_name, ', ' ORDER BY kcu.ordinal_position) AS columnas
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu
  ON kcu.constraint_name = tc.constraint_name
 AND kcu.table_schema = tc.table_schema
WHERE tc.table_schema = :schema
GROUP BY 1, 2, 3
ORDER BY tc.table_name, tc.constraint_type
"""

SQL_FKS = """
SELECT tc.table_name AS tabla_origen, kcu.column_name AS columna_origen,
       ccu.table_name AS tabla_destino, ccu.column_name AS columna_destino,
       tc.constraint_name
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu ON kcu.constraint_name = tc.constraint_name
JOIN information_schema.constraint_column_usage ccu ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_schema = :schema
ORDER BY tc.table_name
"""

SQL_INDICES = """
SELECT tablename AS tabla, indexname AS indice, indexdef AS definicion
FROM pg_indexes
WHERE schemaname = :schema
ORDER BY tablename, indexname
"""

# Columna de fecha principal por tabla (para perfil de cobertura temporal)
COLUMNA_FECHA = {
    "ceo_inbound": "fecha_de_ejecucion",
    "ceo_abandono": "fecha_llamada",
    "efigas_outbound": "fecha_de_ejecucion",
    "caribe_inbound": "fecha_de_ejecucion",
    "caribe_outbound": "fecha_de_ejecucion",
    "caribe_abandono": "fecha_llamada",
    "gdo_inbound": "fecha_de_llamada",
    "gdo_outbound": "fecha_ejecucion",
    "gdo_abandono": "fecha_llamada",
    "gdo_pqrs": "fecha_registro_solicitud",
    "gdo_pqrs_escritas": "radicado_usu_gdo",
    "gdo_informativo": "fecha_regi",
    "surti_inbound": "fecha_de_ejecucion",
    "surti_outbound": "fecha_de_ejecucion",
    "surti_abandono": "fecha_llamada",
    "surti_qr": "fecha_registro_solicitud",
}


def q(sql, **params):
    with get_db_engine().connect() as conn:
        return pd.read_sql(text(sql), conn, params=params or None)


def _safe(sql, **params):
    try:
        return q(sql, **params)
    except Exception as exc:  # noqa: BLE001
        print(f"    [error] {exc}")
        return pd.DataFrame()


def seccion_titulo(titulo: str) -> None:
    print("\n" + "=" * 100)
    print(titulo)
    print("=" * 100)


def inventario(schema: str) -> None:
    seccion_titulo(f"1. INVENTARIO DE OBJETOS - esquema {schema}")
    df = _safe(SQL_INVENTARIO, schema=schema)
    if df.empty:
        print("    (sin objetos)")
        return
    tablas = df[df.table_type == "BASE TABLE"].table_name.tolist()
    for t in tablas:
        n = _safe(f'SELECT count(*) AS n FROM "{schema}"."{t}"')
        filas = int(n.n.iloc[0]) if not n.empty else -1
        print(f"    {t:<38} {filas:>10,} filas")
    extras = df[df.table_type != "BASE TABLE"]
    if not extras.empty:
        print("\n    -- otros objetos --")
        for _, r in extras.iterrows():
            print(f"    {r.table_name:<38} {r.table_type}")


def columnas(schema: str) -> None:
    seccion_titulo(f"2. COLUMNAS - esquema {schema}")
    df = _safe(SQL_COLUMNAS, schema=schema)
    if df.empty:
        print("    (sin columnas)")
        return
    for tabla, grupo in df.groupby("table_name"):
        print(f"\n### {tabla}")
        for _, r in grupo.iterrows():
            ln = f"({int(r.largo)})" if pd.notna(r.largo) else ""
            nul = "NULL" if r.is_nullable == "YES" else "NOT NULL"
            print(f"  {int(r.ordinal_position):>2}. {r.column_name:<38} {r.data_type}{ln} {nul}")


def restricciones(schema: str) -> None:
    seccion_titulo(f"3. RESTRICCIONES - esquema {schema}")
    df = _safe(SQL_CONSTRAINTS, schema=schema)
    if df.empty:
        print("    (sin restricciones)")
        return
    for tabla, grupo in df.groupby("table_name"):
        print(f"\n### {tabla}")
        for _, r in grupo.iterrows():
            print(f"    [{r.constraint_type:<12}] {r.constraint_name:<38} ({r.columnas})")
    fks = _safe(SQL_FKS, schema=schema)
    print("\n    -- foreign keys --")
    if fks.empty:
        print("    (ninguna)")
    else:
        for _, r in fks.iterrows():
            print(f"    {r.tabla_origen}.{r.columna_origen} -> {r.tabla_destino}.{r.columna_destino}")


def indices(schema: str) -> None:
    seccion_titulo(f"4. INDICES - esquema {schema}")
    df = _safe(SQL_INDICES, schema=schema)
    if df.empty:
        print("    (sin indices)")
        return
    for tabla, grupo in df.groupby("tabla"):
        print(f"\n### {tabla}")
        for _, r in grupo.iterrows():
            print(f"    {r.indice:<38} {r.definicion[:90]}")


def calidad(schema: str) -> None:
    seccion_titulo("5. PERFIL DE CALIDAD - cobertura de la columna temporal principal")
    for tabla, col in COLUMNA_FECHA.items():
        df = _safe(f"""
            SELECT count(*) AS total,
                   count("{col}") AS con_valor,
                   min("{col}"::text) AS minimo,
                   max("{col}"::text) AS maximo
            FROM "{schema}"."{tabla}"
        """)
        if df.empty:
            continue
        r = df.iloc[0]
        pct = (r.con_valor / r.total * 100) if r.total else 0
        print(f"    {tabla:<22} {col:<24} {r.total:>7,} filas | con_fecha={r.con_valor:>7,} "
              f"({pct:5.1f}%) | [{str(r.minimo)[:26]} .. {str(r.maximo)[:26]}]")


def vistas(schema: str) -> None:
    seccion_titulo(f"6. VISTAS - esquema {schema}")
    df = _safe("""
        SELECT table_name FROM information_schema.views
        WHERE table_schema = :schema ORDER BY table_name
    """, schema=schema)
    if df.empty:
        print("    (sin vistas)")
        return
    for v in df.table_name:
        print(f"\n--- {schema}.{v} ---")
        d = _safe(f"SELECT pg_get_viewdef('{schema}.{v}'::regclass, true) AS d")
        if not d.empty:
            print(d.d.iloc[0])


def funciones(schema: str) -> None:
    seccion_titulo(f"7. FUNCIONES - esquema {schema}")
    df = _safe("""
        SELECT p.proname AS nombre, pg_get_function_identity_arguments(p.oid) AS argumentos
        FROM pg_proc p JOIN pg_namespace n ON n.oid = p.pronamespace
        WHERE n.nspname = :schema ORDER BY p.proname
    """, schema=schema)
    if df.empty:
        print("    (sin funciones)")
        return
    for _, r in df.iterrows():
        print(f"    {r.nombre}({r.argumentos})")


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspección del esquema DataCenter_Promigas")
    parser.add_argument("--esquema", default=DB_SCHEMA, help="esquema a inspeccionar")
    parser.add_argument("--tablas", action="store_true", help="inventario y row counts")
    parser.add_argument("--columnas", action="store_true", help="detalle de columnas")
    parser.add_argument("--restricciones", action="store_true", help="PK, unique y FK")
    parser.add_argument("--indices", action="store_true", help="indices definidos")
    parser.add_argument("--calidad", action="store_true", help="perfil de calidad temporal")
    parser.add_argument("--vistas", action="store_true", help="definiciones de vistas")
    parser.add_argument("--funciones", action="store_true", help="funciones del esquema")
    parser.add_argument("--todo", action="store_true", help="todas las secciones")
    args = parser.parse_args()

    if args.todo or not any(
        [args.tablas, args.columnas, args.restricciones, args.indices,
         args.calidad, args.vistas, args.funciones]
    ):
        args.tablas = args.columnas = args.restricciones = True
        args.indices = args.calidad = args.vistas = args.funciones = True

    print(f"Esquema objetivo: {args.esquema}")
    if args.tablas:
        inventario(args.esquema)
    if args.columnas:
        columnas(args.esquema)
    if args.restricciones:
        restricciones(args.esquema)
    if args.indices:
        indices(args.esquema)
    if args.calidad:
        calidad(args.esquema)
    if args.vistas:
        vistas(args.esquema)
    if args.funciones:
        funciones(args.esquema)


if __name__ == "__main__":
    main()
