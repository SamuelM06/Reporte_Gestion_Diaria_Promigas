# 🚀 Plan Fase 04 — Integración y Despliegue

**Proyecto:** Reporte de Gestión Diaria - Retención Promigas
**Stack:** PostgreSQL 16.14 · FastAPI (Uvicorn) · Astro/React · Nginx (o IIS) · HTTPS
**Última actualización:** 21 de octubre de 2026
**Estado:** ⏳ NO INICIADA — bloqueada por las Fases 01, 02 y 03

---

## 1. Objetivo

Poner en producción (o en un entorno de staging validado) el aplicativo completo
(base de datos + backend + frontend) de forma **segura, trazable y reversible**, con:

- Despliegue de la base de datos con migraciones aplicadas y respaldo verificado.
- Despliegue del backend FastAPI con HTTPS, variables de entorno seguras y monitoreo.
- Despliegue del frontend (Astro/React) servido por un reverse proxy.
- CI/CD (GitHub Actions) para builds y tests.
- Backups cifrados y plan de rollback.

---

## 2. Prerrequisitos

- Fases 01, 02 y 03 cerradas (DB armada, API operativa, frontend probado).
- Entorno de staging validado antes de producción.
- Decisiones de infraestructura (hosting, dominio, certificados) acordadas.
- Rol de BD de producción con mínimo privilegio para la API.

---

## 3. Sub-fases y tareas

### 3.1 Sub-fase 4.1 — Preparación de infraestructura (esfuerzo M)

- Definir servidor (Windows/Linux), dominio y certificado TLS.
- Configurar PostgreSQL en producción (o usar la instancia existente `DataCenter_Promigas`
  con un esquema dedicado si aplica).
- Configurar reverse proxy (Nginx/IIS) con HTTPS y headers de seguridad (S-08).
- Variables de entorno en el servidor (no en el repo): `DB_*`, `JWT_SECRET`, `CORS_ORIGINS`.
- Firewall: solo puertos necesarios (443, 5432 restringido).

### 3.2 Sub-fase 4.2 — Despliegue de la base de datos (esfuerzo M)

- Respaldo verificado del esquema (`gestion_diaria_bak_<fecha>` o `pg_dump` si está
  disponible).
- Aplicar migraciones M0–M8 en producción dentro de transacciones (`BEGIN/COMMIT`) con
  verificación de conteos en medio (R-17).
- Cargar datos iniciales (reingesta reproducible) y verificar cuadre al 100%.
- Crear rol de BD para la API con mínimo privilegio (S-11).
- Configurar backups cifrados (S-13) y política de retención.

### 3.3 Sub-fase 4.3 — Despliegue del backend (esfuerzo M)

- Build de la imagen/entorno Python (requirements pinneados).
- Desplegar Uvicorn detrás del reverse proxy (HTTPS).
- Configurar variables de entorno y secretos en el servidor.
- Health checks (`/health`) y monitoreo básico (logs sin PII, S-14).
- Rate limiting y CORS restringido al dominio del frontend.

### 3.4 Sub-fase 4.4 — Despliegue del frontend (esfuerzo S)

- Build de Astro (SSR o estático según decisión).
- Servir por el reverse proxy con HTTPS.
- Configurar la URL base de la API por entorno.

### 3.5 Sub-fase 4.5 — CI/CD (esfuerzo M)

- GitHub Actions: lint, tests (backend + frontend), build.
- Despliegue automatizado a staging; despliegue a producción con aprobación manual.
- Escaneo de secretos en cada push (S-05).

### 3.6 Sub-fase 4.6 — Validación y puesta en marcha (esfuerzo S)

- Smoke tests E2E: login, tipificación, cancelación, dashboard, calidad.
- Verificar cuadre de cifras con la jefatura (R-07).
- Plan de rollback documentado (revertir migraciones, restaurar respaldo).
- Capacitación a asesores y analistas.
- Plan de desconexión de Excel por gasera (doc 07 / `04_Transicion_a_OCM.md`,
  bloqueado por A-18 y cobertura OCM ≥ umbral).

---

## 4. Seguridad en producción (doc `06_Documentacion.md` §6)

- `.env` nunca versionado; verificar con `git check-ignore` antes de cada commit.
- Solo conexiones cifradas (S-12); backups cifrados (S-13).
- Headers de seguridad obligatorios (S-08).
- Sin PII en logs (S-14); minimización en reportes (S-15); seudonimización (S-16).
- Derecho al olvido definido (S-17).
- Escaneo de secretos antes de cada push (S-05).

---

## 5. Entregables de esta fase

1. Aplicativo en producción (o staging validado) con HTTPS.
2. Base de datos con migraciones aplicadas, respaldo y backups cifrados.
3. Backend y frontend desplegados y monitoreados.
4. CI/CD operativo.
5. Documentación de operación y plan de rollback.

---

## 6. Riesgos

- Migraciones sobre producción sin entorno de pruebas (R-14).
- Truncado accidental (R-17).
- Doble conteo Excel/OCM en la transición (R-01, R-19).
- Fuga de credenciales (R-11, S-03).

---

## 7. Referencias

- `context/planes/01_Plan_Estructura.md` — puertas de calidad y riesgos
- `context/planes/02_Plan_Migracion_y_Estrategia_DB.md` — estrategia de migración
- `context/planes/04_Transicion_a_OCM.md` — transición a OCM
- `database/PROCEDENCIA_Y_REINGESTA.md` — procedencia y reingesta
- `context/Analisis/06_Documentacion.md` — seguridad §6