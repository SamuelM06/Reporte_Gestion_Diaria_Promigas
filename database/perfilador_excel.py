"""
Profiler de libros Excel de origen - Reporte Gestión Diaria Promigas

Lee los .xlsx descargados de SharePoint y produce el inventario real de cada
libro/hoja: hojas, encabezados, filas, nulos y candidatos a columna clave.

Por qué: la documentación de origen (database/FICHA_ORIGEN_POR_GASERA.md) se
alimenta de la estructura REAL de los archivos, no de la memoria.

Uso:
    python database/perfilador_excel.py                     # todo data/raw/<gasera>/
    python database/perfilador_excel.py --ruta data/raw/ceo  # una gasera
    python database/perfilador_excel.py --archivo "D:/x.xlsx"
    python database/perfilador_excel.py --salida context/Analisis/14_Perfil_Excel_Por_Gasera.md
    python database/perfilador_excel.py --muestra            # muestra valores de columnas NO PII

Privacidad: por defecto NO se imprime ningún valor de dato, solo estructura,
conteos de nulos y número de distintos. Las columnas PII (documento, telefono,
correo, nombre, direccion, cedula) se excluyen siempre del muestreo.
"""

import argparse
import hashlib
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import openpyxl
import pandas as pd

# ----------------------------------------------------------------------------------
# Catálogos de reconocimiento de columnas
# ----------------------------------------------------------------------------------

PATRONES: Dict[str, List[str]] = {
    "fecha_gestion": [
        "fecha_de_ejecucion", "fecha_ejecucion", "fecha_de_atencion", "fecha_atencion",
        "fecha_de_llamada", "fecha_llamada", "fecha_registro_solicitud",
        "fecha_de_registro_solicitud", "fecha_de_legalizacion", "fecha_legalizacion",
        "fecha", "fec",
    ],
    "fecha_venta": ["fecha_de_venta", "fecha_venta", "fecha_venta_raw"],
    "fecha_lote": ["fecha_base", "fecha_de_base", "base"],
    "resultado": [
        "estado", "resultado_final", "resultado_de_retencion", "resultado_llamada",
        "resultado", "tipifiacion_de_pqr",
    ],
    "motivo": ["subtipificacion", "motivo", "categoria_detalle", "subcategoria"],
    "contrato": ["contrato", "suscripcion", "cod_contrato", "numero_solicitud", "solicitud"],
    "mes": ["mes"],
    "operador": ["operador", "gestor", "nombre_asesor_retencion", "empresa"],
    "canal": ["canal", "medio_de_recepcion", "medio_recepcion"],
    "tipo_contacto": ["tipo_de_contacto", "tipo_contacto", "tipo_contacto_homolog"],
    "producto": ["producto", "producto_1", "producto_norm"],
    "aseguradora": ["aseguradora", "entidad_facturacion", "aseguradora_norm"],
    "localidad": ["localidad", "localidad_solicitud", "ciudad"],
    "validacion": ["validacion"],
}

COLUMNAS_PII = [
    "documento", "cedula", "identificacion", "telefono", "correo", "email",
    "nombre_cliente", "nombre_solicitante", "direccion", "barrio", "password",
    "pass", "usuario", "email_cliente",
]

COLUMNAS_MUESTRA_SEGURA = ["estado", "mes", "canal", "cabina", "validacion",
                           "tipo_de_contacto", "resultado_final", "resultado_de_retencion",
                           "resultado_llamada", "subtipificacion", "categoria"]

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


def norm(s: Any) -> str:
    """Normaliza un encabezado a snake_case sin tildes para comparar.
    Guiones, signos y '_' se collapsan: 'FECHA_REGISTRO_SOLICITUD' == 'FECHA REGISTRO SOLICITUD'.
    """
    if s is None:
        return ""
    t = str(s).strip().lower()
    t = t.replace("á", "a").replace("é", "e").replace("í", "i")
    t = t.replace("ó", "o").replace("ú", "u").replace("ü", "u").replace("ñ", "n")
    t = re.sub(r"[^a-z0-9]+", "_", t)
    return t.strip("_")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def clasificar_columna(nombre: str) -> List[str]:
    """Devuelve los roles semánticos que un encabezado puede cumplir."""
    n = norm(nombre)
    roles = []
    for rol, patrones in PATRONES.items():
        for p in patrones:
            if n == p:
                roles.append(rol)
                break
            if n.startswith(p) or n.endswith(p):
                roles.append(rol)
                break
    return sorted(set(roles))


def es_pii(nombre: str) -> bool:
    n = norm(nombre)
    return any(p in n for p in COLUMNAS_PII)


def perfilar_hoja(ruta: Path, hoja: str, mostrar_muestra: bool) -> Optional[Dict[str, Any]]:
    """Perfila una hoja: encabezado, filas, nulos, distintos y candidatos."""
    try:
        df = pd.read_excel(ruta, sheet_name=hoja, dtype=object, engine="openpyxl")
    except Exception as e:
        return {"hoja": hoja, "error": str(e)[:200]}

    df = df.dropna(how="all").dropna(axis=1, how="all")
    if df.empty:
        return {"hoja": hoja, "filas": 0, "columnas": 0, "encabezados": [], "detalle": []}

    # El encabezado real puede estar en una fila previa (hojas con título).
    encabezados = [str(c) for c in df.columns]
    df.columns = [norm(c) for c in df.columns]

    detalle = []
    for col in df.columns:
        serie = df[col]
        no_nulos = serie.notna().sum()
        nulos_pct = round(100 * (1 - no_nulos / len(df)), 1)
        distintos = int(serie.nunique(dropna=True))
        rol = clasificar_columna(col)
        item = {
            "columna": col,
            "encabezado_excel": encabezados[df.columns.get_loc(col)],
            "nulos_pct": nulos_pct,
            "distintos": distintos,
            "roles": rol,
        }
        if mostrar_muestra and col in [norm(c) for c in COLUMNAS_MUESTRA_SEGURA] and not es_pii(col):
            try:
                vals = serie.dropna().astype(str).value_counts().head(6)
                item["muestra"] = {str(k): int(v) for k, v in vals.items()}
            except Exception:
                pass
        detalle.append(item)

    return {
        "hoja": hoja,
        "filas": int(len(df)),
        "columnas": int(len(df.columns)),
        "encabezados": encabezados,
        "detalle": detalle,
    }


def perfilar_libro(ruta: Path, mostrar_muestra: bool) -> Dict[str, Any]:
    """Perfila todas las hojas de un libro."""
    try:
        wb = openpyxl.load_workbook(ruta, read_only=True, data_only=True)
        hojas = wb.sheetnames
        wb.close()
    except Exception as e:
        return {"archivo": ruta.name, "error": f"No se pudo abrir: {str(e)[:200]}"}

    info: Dict[str, Any] = {
        "archivo": ruta.name,
        "ruta": str(ruta),
        "bytes": ruta.stat().st_size,
        "sha256": sha256(ruta),
        "modificado": datetime.fromtimestamp(ruta.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
        "hojas": hojas,
        "detalle_hojas": [],
    }
    for h in hojas:
        r = perfilar_hoja(ruta, h, mostrar_muestra)
        if r:
            info["detalle_hojas"].append(r)
    return info


def ruta_mes(hoja: str) -> Optional[str]:
    """Detecta si la hoja es un mes (para inventarios tipo Caribe/Surtigas)."""
    h = norm(hoja)
    for m in MESES:
        if h.startswith(m) or h == m:
            return m.upper()
    return None


def md_tabla(filas: List[List[str]], cabeceras: List[str]) -> str:
    out = ["| " + " | ".join(cabeceras) + " |",
           "|" + "|".join(["---"] * len(cabeceras)) + "|"]
    for f in filas:
        out.append("| " + " | ".join(str(x) for x in f) + " |")
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description="Perfilador de libros Excel de origen")
    ap.add_argument("--ruta", default="data/raw", help="Carpeta raíz de libros (default: data/raw)")
    ap.add_argument("--archivo", help="Analizar un archivo .xlsx específico")
    ap.add_argument("--salida", default="context/Analisis/14_Perfil_Excel_Por_Gasera.md")
    ap.add_argument("--muestra", action="store_true",
                    help="Incluye valores de columnas NO PII (estado, mes, canal...)")
    args = ap.parse_args()

    if args.archivo:
        archivos = [Path(args.archivo)]
    else:
        raiz = Path(args.ruta)
        if not raiz.exists():
            print(f"❌ No existe la carpeta '{raiz}'. Copia ahí los .xlsx de SharePoint.")
            return 1
        archivos = sorted(p for p in raiz.rglob("*.xlsx") if not p.name.startswith("~$"))
        if not archivos:
            print(f"⚠️  No hay .xlsx en '{raiz}'.")
            return 0

    # Agrupa por gasera = carpeta de primer nivel
    grupos: Dict[str, List[Path]] = {}
    for p in archivos:
        if args.archivo:
            gasera = "ARCHIVO"
        else:
            gasera = p.relative_to(Path(args.ruta)).parts[0] if len(p.relative_to(Path(args.ruta)).parts) > 1 else "raiz"
        grupos.setdefault(gasera, []).append(p)

    lineas: List[str] = []
    lineas.append("# 14. Perfil Real de los Libros Excel de Origen")
    lineas.append("")
    lineas.append("**Proyecto:** Reporte de Gestión Diaria - Retención Promigas")
    lineas.append(f"**Generado:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lineas.append(f"**Origen:** `{args.ruta}`")
    lineas.append("")
    lineas.append("> Generado por `database/perfilador_excel.py` a partir de los archivos reales.")
    lineas.append("> No contiene valores de datos (solo estructura, nulos y distintos).")
    lineas.append("")

    for gasera, archivos_g in sorted(grupos.items()):
        lineas.append(f"## 📁 {gasera.upper()}")
        lineas.append("")
        for ruta in archivos_g:
            info = perfilar_libro(ruta, args.muestra)
            if "error" in info:
                lineas.append(f"### ❌ `{info['archivo']}`")
                lineas.append("")
                lineas.append(f"> {info['error']}")
                lineas.append("")
                continue

            lineas.append(f"### 📄 `{info['archivo']}`")
            lineas.append("")
            lineas.append(f"| sha256 | bytes | modificado |")
            lineas.append("|---|---|---|")
            lineas.append(f"| `{info['sha256'][:16]}…` | {info['bytes']:,} | {info['modificado']} |")
            lineas.append("")
            lineas.append(f"**Hojas:** {len(info['hojas'])} → " + ", ".join(f"`{h}`" for h in info["hojas"]))
            lineas.append("")

            for hd in info["detalle_hojas"]:
                if hd.get("error"):
                    lineas.append(f"#### `{hd['hoja']}` — ⚠️ {hd['error']}")
                    lineas.append("")
                    continue
                mes = ruta_mes(hd["hoja"])
                titulo = f"#### `{hd['hoja']}`"
                if mes:
                    titulo += f" (mes: {mes})"
                lineas.append(titulo)
                lineas.append("")
                lineas.append(f"**{hd['filas']:,} filas × {hd['columnas']} columnas**")
                lineas.append("")
                filas_tb = []
                for d in hd["detalle"]:
                    roles = ", ".join(d["roles"]) if d["roles"] else "—"
                    filas_tb.append([
                        f"`{d['columna']}`",
                        d["encabezado_excel"],
                        f"{d['nulos_pct']}%",
                        f"{d['distintos']:,}",
                        roles,
                    ])
                lineas.append(md_tabla(filas_tb, ["Columna (snake)", "Encabezado en Excel", "Nulos", "Distintos", "Rol"]))
                lineas.append("")
                if args.muestra:
                    muestras = [(d["columna"], d["muestra"]) for d in hd["detalle"] if d.get("muestra")]
                    if muestras:
                        lineas.append("<details><summary>Muestra de valores (no PII)</summary>")
                        lineas.append("")
                        for c, m in muestras:
                            lineas.append(f"- `{c}`: " + ", ".join(f"`{k}` ({v})" for k, v in m.items()))
                        lineas.append("")
                        lineas.append("</details>")
                        lineas.append("")

    salida = Path(args.salida)
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text("\n".join(lineas), encoding="utf-8")
    print(f"✅ Perfil generado: {salida}")
    print(f"   Gaseras: {', '.join(sorted(grupos.keys()))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
