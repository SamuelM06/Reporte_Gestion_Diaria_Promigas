# 🖥️ Plan Fase 03 — Frontend (React + Astro)

**Proyecto:** Reporte de Gestión Diaria - Retención Promigas
**Stack:** Astro (shell/SSR) · React (islas) · Tailwind CSS · Recharts/Chart.js · Axios/fetch
**Backend:** FastAPI (Fase 02) · Base de datos: PostgreSQL (Fase 01)
**Última actualización:** 21 de octubre de 2026
**Estado:** ⏳ NO INICIADA — bloqueada por la Fase 02 (backend)

> ⚠️ **Prerrequisito duro:** esta fase no inicia hasta que la Fase 02 (backend FastAPI)
> esté operativa con endpoints documentados y probados. El frontend es un consumidor de
> la API; sin API no hay datos.

> 📝 **Nota del usuario:** los detalles funcionales del frontend se darán más adelante.
> Este plan deja placeholders explícitos para incorporarlos cuando se definan. El alcance
> funcional mínimo aquí descrito se basa en la documentación existente
> (`08_Flujo_De_Datos.md` §6, `06_Documentacion.md`, `12_Asesores_Gestion_Diaria.md`).

---

## 1. Objetivo

Construir el **aplicativo web** que:

1. Permite a los **asesores tipificar** gestiones en el sistema (gasera, cabina, contrato,
   fecha, resultado, motivo, operador, tipo de contacto, canal, producto, aseguradora).
2. Permite a los asesores que realizan **cancelaciones** registrarlas (contrato, fecha,
   motivo, asesor, gasera, tipo de cancelación) conectadas al esquema.
3. Expone **dashboards y reportes** (volumen, resultados APTA/NO APTA, % retención,
   abandono, motivos, operadores, calidad del dato) alimentados por la base de datos vía
   la API.
4. Muestra el **panel de calidad del dato** (cargas, rechazos, `POR_REVISAR`, cobertura).

Todo queda **conectado con la base de datos y el aplicativo**: lo que los asesores
tipifiquen y cancelen alimenta el esquema y, por tanto, los reportes.

---

## 2. Stack y estructura propuesta

```
frontend/
├── astro.config.mjs
├── src/
│   ├── layouts/
│   │   └── BaseLayout.astro
│   ├── pages/
│   │   ├── index.astro              # Dashboard ejecutivo
│   │   ├── login.astro
│   │   ├── tipificacion.astro       # Formulario de tipificación (React island)
│   │   ├── cancelaciones.astro      # Registro de cancelaciones (React island)
│   │   ├── reportes.astro           # Reportes por gasera/cabina/mes
│   │   ├── calidad.astro           # Panel de calidad del dato
│   │   └── pqrs.astro
│   ├── components/
│   │   ├── react/                   # Islas React (interactividad)
│   │   │   ├── TipificacionForm.tsx
│   │   │   ├── CancelacionForm.tsx
│   │   │   ├── FiltrosGlobales.tsx
│   │   │   ├── KpiCard.tsx
│   │   │   └── TablaGestion.tsx
│   │   └── charts/                  # Gráficos (Recharts)
│   │       ├── ResultadosChart.tsx
│   │       ├── AbandonoChart.tsx
│   │       └── MotivosChart.tsx
│   ├── lib/
│   │   ├── api.ts                   # Cliente HTTP (axios/fetch) a FastAPI
│   │   ├── auth.ts                  # Manejo de JWT
│   │   └── types.ts                 # Tipos compartidos
│   └── styles/
│       └── global.css
├── package.json
└── .env.example
```

---

## 3. Prerrequisitos

- Fase 02 (backend) operativa con OpenAPI documentado y endpoints probados.
- Decisiones de negocio que afectan la UI: A-11 (granularidad del reporte: empresa vs
  asesor), A-12 (abandono de GDO), A-14 (campos obligatorios por gasera).
- Definición de los KPIs a mostrar (doc `03_Definicion_de_KPIs.md`).

---

## 4. Módulos funcionales

### 4.1 Módulo de Tipificación (asesores)

- Formulario conectado a `POST /api/v1/gestion` con validación en cliente y en servidor.
- Campos: gasera, cabina (inbound/outbound), contrato, fecha de gestión, resultado,
  motivo (de `dim_motivo`), operador (empresa/persona), tipo de contacto, canal, producto,
  aseguradora, observaciones.
- La normalización del resultado se hace en el backend (doc 09); el frontend solo envía
  `resultado_original` y muestra el resultado normalizado devuelto.
- Feedback inmediato: clasificación (APTA/NO_APTA/POR_REVISAR) y método de normalización.
- Listado de gestiones del día con filtros (gasera, cabina, resultado).

### 4.2 Módulo de Cancelaciones

- Formulario para registrar cancelaciones realizadas por los asesores, conectado a
  `POST /api/v1/gestion/cancelacion`.
- Campos: contrato, fecha, motivo, asesor, gasera, tipo de cancelación (cancelado /
  cancelado + venta / cancelado + reintegro).
- Las cancelaciones registradas alimentan `fact_gestion` y por tanto los reportes
  (motivos de pérdida, % retención).
- Validación de campos obligatorios por gasera (A-14).

### 4.3 Dashboard ejecutivo

- KPIs: volumen total, APTA/NO APTA, **Total Retenciones** = `retenido` +
  `cancelado + venta`, **% Retención** = Total Retenciones / Total Aptos.
- Desglose por gasera, cabina, mes.
- Semántica literal de `APTA` visible (R-10): "Apta = a la llamada se le puede hacer
  gestión", no "el cliente se quedó" (H-22, D-01, D-02).

### 4.4 Panel de resultados y motivos

- Distribución de los 4 resultados APTA y los NO APTA.
- Motivos de pérdida (top motivos por gasera) — depende de B-28 (maestro de 52 motivos).
- Operadores: volumen por empresa operadora (A-11); productividad individual solo GDO.

### 4.5 Panel de abandono y nivel de servicio

- Tasa de abandono por hora/día (solo gaseras con abandono confiable; GDO bloqueado por
  A-12).
- Cobertura de abandono con fecha válida.

### 4.6 Panel de calidad del dato

- Cargas (`dim_carga`): filas leídas/cargadas/rechazadas, estado.
- `POR_REVISAR` visibles con su conteo y ocurrencias.
- Duplicados, sangrado, fechas fuera de rango.
- Cobertura por gasera.

### 4.7 Panel de PQRS

- Radicados, ANS de notificación/respuesta, estado, cumplimiento.

---

## 5. Conexión con la base de datos (vía API)

- Todo dato mostrado proviene de la API (Fase 02), que consulta `fact_gestion`,
  `fact_pqrs`, las dimensiones y las vistas de consumo.
- La tipificación y las cancelaciones se escriben vía API → `fact_gestion` (con
  `origen`, `carga_id`, normalización y bitácora), de modo que **los reportes se
  alimentan automáticamente**.
- El frontend **no** accede directamente a la BD ni cachea datos sensibles (S-07).
- `Cache-Control: no-store` para endpoints con datos de gestión.

---

## 6. Seguridad en el frontend

- Autenticación por JWT (login contra la API); token en memoria (no en `localStorage`
  si es posible) y refresh rotativo.
- Roles visibles en la UI: asesor, analista, admin.
- Minimización de PII: no mostrar nombre/documento/teléfono/dirección en reportes
  agregados (S-15, S-16).
- Headers de seguridad heredados del backend/proxy (S-08).
- Sin datos sensibles en URLs (S-09).

---

## 7. Placeholders para detalles del usuario (a completar)

> El usuario indicó que dará más detalles del frontend cuando comencemos. Los siguientes
> puntos quedan como **placeholders** para incorporarlos:

- [ ] **Diseño visual / marca** (colores, logo Promigas, tipografía, layout).
- [ ] **Flujo de tipificación detallado** (pasos, validaciones de negocio, campos
      obligatorios por gasera).
- [ ] **Flujo de cancelaciones detallado** (tipos de cancelación, documentos soporte,
      aprobaciones).
- [ ] **Permisos por gasera** (un asesor solo ve su gasera).
- [ ] **Exportaciones requeridas** (PDF/Excel, formato, periodicidad).
- [ ] **Notificaciones/alertas** (email, toast, umbrales).
- [ ] **Internacionalización** (español; ¿inglés?).
- [ ] **Accesibilidad y dispositivos** (desktop/móvil, responsive).
- [ ] **Integración con OCM** en el frontend (si aplica).

---

## 8. Sub-fases y tareas (borrador)

### 8.1 Sub-fase 3.1 — Fundación del frontend (esfuerzo S)

- Inicializar proyecto Astro + React + Tailwind.
- Configurar cliente HTTP a la API (base URL por entorno).
- Layout base, navegación, autenticación (login/logout).
- Variables de entorno (`.env.example`).

### 8.2 Sub-fase 3.2 — Módulo de tipificación (esfuerzo M)

- Formulario de tipificación con validación.
- Integración con `POST /api/v1/gestion`.
- Listado de gestiones del día con filtros.

### 8.3 Sub-fase 3.3 — Módulo de cancelaciones (esfuerzo M)

- Formulario de cancelaciones.
- Integración con `POST /api/v1/gestion/cancelacion`.
- Listado y seguimiento de cancelaciones.

### 8.4 Sub-fase 3.4 — Dashboards y reportes (esfuerzo M)

- Dashboard ejecutivo con KPIs.
- Gráficos de resultados, motivos, operadores, abandono.
- Filtros globales (fecha, gasera, cabina).

### 8.5 Sub-fase 3.5 — Panel de calidad (esfuerzo S)

- Cargas, rechazos, `POR_REVISAR`, cobertura, duplicados.

### 8.6 Sub-fase 3.6 — PQRS (esfuerzo S)

- Listado y seguimiento de PQRS con ANS.

### 8.7 Sub-fase 3.7 — Pruebas y pulido (esfuerzo S)

- Tests de componentes (Vitest/RTL).
- Pruebas E2E (Playwright) de flujos críticos (tipificación, cancelación, login).
- Accesibilidad y responsive.

---

## 9. Entregables de esta fase

1. Aplicativo web (Astro + React) funcional.
2. Módulos de tipificación y cancelaciones conectados a la API y a la BD.
3. Dashboards y reportes alimentados por la base de datos.
4. Panel de calidad del dato.
5. Documentación de uso y despliegue.

---

## 10. Riesgos

- Iniciar el frontend antes de tener la API estable → retrabajo.
- Prometer KPIs no calculables (productividad por asesor fuera de GDO) (R-11).
- Abandono de GDO no confiable contaminando nivel de servicio (R-12).
- Exposición de PII en el cliente (S-04, S-07, S-15).

---

## 11. Referencias

- `context/planes/05_Plan_Fase_01_Base_Datos.md` — prerrequisito
- `context/planes/06_Plan_Fase_02_Backend_FastAPI.md` — prerrequisito
- `context/Analisis/08_Flujo_De_Datos.md` — arquitectura y dashboard propuesto §6
- `context/Analisis/06_Documentacion.md` — seguridad §6
- `context/Analisis/012_Asesores_Gestion_Diaria.md` — asesores

> **Siguiente fase:** una vez cerrada esta fase, iniciar
> `08_Plan_Fase_04_Integracion_Despliegue.md`.