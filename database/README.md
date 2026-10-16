# 🗄️ Módulo de Base de Datos / Conexión

Este directorio contiene las plantillas y utilidades para la conexión a las bases de datos de Promigas / Gaseras.

---

## 📌 Instrucciones de Uso

1. **Crear archivo `.env`:**
   * Copiar el archivo `.env.example` en la raíz del proyecto y renombrarlo como `.env`.
   * Diligenciar las credenciales reales (`DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`).
   * *Nota de Seguridad:* El archivo `.env` ya está agregado al `.gitignore` para no exponer contraseñas en GitHub.

2. **Validar conexión:**
   * Ejecutar `python database/conexion_template.py` para probar la conectividad contra la base de datos.

3. **Librerías sugeridas según motor:**
   * **SQL Server:** `pyodbc`, `sqlalchemy`
   * **PostgreSQL:** `psycopg2-binary`, `sqlalchemy`
   * **MySQL:** `pymysql`, `sqlalchemy`
   * **Oracle:** `cx_Oracle` / `oracledb`, `sqlalchemy`
