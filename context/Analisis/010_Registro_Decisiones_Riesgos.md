# 08. Registro de Decisiones, Supuestos, Riesgos y Preguntas Abiertas

**Proyecto:** Gestión Diaria Promigas
**Última actualización:** 19 de octubre de 2026
**Versión:** 2 — con verificación contra `DataCenter_Promigas` (19-oct-2026)

Este documento es la memoria del proyecto. Cada vez que el equipo decida algo, descarte una opción o detecte un riesgo, se registra aquí para no discutirlo dos veces.

**Estados:** `ABIERTA` (sin decidir), `PROPUESTA` (hay recomendación pendiente de aprobar), `DECIDIDA` (acordada), `DESCARTADA`.

---

## 1. Decisiones

### 1.1 Decididas

| ID | Decisión | Fuente | Fecha |
|---|---|---|---|
| D-01 | Hay solo **4 resultados aptos**: Retenido, Cancelado, Cancelado + Venta, Cancelado + Reintegro. Todo lo demás es no apto. | Equipo de datos | 19-oct-2026 |
| D-02 | **Retenido y Cancelado son resultados distintos** y no se tratan como equivalentes en ningún cálculo. | Equipo de datos | 19-oct-2026 |
| D-03 | Un error de digitación **no puede convertir una llamada apta en no apta**: se normaliza antes de clasificar. | Equipo de datos | 19-oct-2026 |
| D-04 | El proyecto reemplaza el flujo de reportes en Power BI por una plantilla única por gasera, con datos desde la base de datos. | Descripción del proyecto | 19-oct-2026 |
| D-05 | Fecha objetivo de corte a OCM: **1 de noviembre de 2026**. Desde esa fecha los asesores tipifican, clasifican y registran el resultado en OCM. | Descripción del proyecto | 19-oct-2026 |
| **D-06** | **D-01 está implementada en la base de datos**: `gestion_diaria.clasificacion.resultado_normalizado` produce exactamente los 4 resultados APTA definidos. Los 17 valores APTA colapsan a `cancelado`, `cancelado + venta`, `cancelado + reintegro` y `retenido`. | Verificación en BD | 19-oct-2026 |
| **D-07** | **La clasificación NO varía por gasera.** Los 4 resultados APTA son idénticos en las 5 gaseras: no existe ninguna divergencia. El catálogo se mantiene por gasera, pero la clasificación se define a nivel de resultado canónico. | Verificación en BD | 19-oct-2026 |
| **D-08** | **`operador` es la empresa operadora del contact center**, no una persona. Solo GDO registra el asesor individual de retención (`nombre_asesor_retencion`, `gestor`). | Verificación en BD | 19-oct-2026 |
| **D-09** | **El abandono se modela en la misma tabla de hechos que la atención**, con un discriminante `subtipo_gestion`. PQRS va en tabla aparte. | Propuesta doc 03 §4.2 | 19-oct-2026 |
| **D-10** | **La llave de las llamadas es `id_gestion` sintética + `clave_natural` (md5)**, con índice único parcial que deja los duplicados visibles en vez de borrarlos. | Propuesta doc 03 §4.1 | 19-oct-2026 |

> **Nota sobre D-05:** la fecha D-05 es la indicada por el equipo de datos. El PDF oficial solo habla de una "fecha límite". Conviene confirmarla por escrito con quien corresponda.

> **Nota sobre D-08 — impacto en el alcance del proyecto:** si el reporte debe medir
> productividad por asesor, **solo es calculable para GDO** (4.190 inbound + 3.284
> outbound). En las otras 4 gaseras la granularidad disponible es la empresa de
> tercerización. Esto debe confirmarse con la jefatura antes de prometer ese KPI.

### 1.2 Propuestas pendientes de aprobar

| ID | Tema | Propuesta | Documento | Prioridad |
|---|---|---|---|---|
| ~~P-01~~ | ~~Estado adicional de clasificación~~ | **RECHAZADA (19-oct-2026):** un resultado es APTA o NO_APTA, no puede haber tercera clasificación. Si no entra en los 4 APTA, es NO_APTA | 09 | ✅ Descartada |
| P-02 | Estructura de `clasificacion` | Opción B: separar `dim_resultado` y `resultado_variante` | 09 | 🟠 Media |
| P-03 | Conservar texto original | Guardar `resultado_original` sin modificar en cada registro | 09 | 🔴 Alta |
| P-04 | Aprendizaje de variantes | Las correcciones automáticas se agregan como variante con `validado = FALSE` | 09 | 🟡 Baja |
| P-05 | Umbral de similitud | Valor inicial 85 y margen de 10 puntos, a calibrar con datos reales | 09 | 🟡 Media |
| **P-06** | **Normalizar la barra `/`** | `normalizar_texto` debe normalizar `/` igual que `+`. Sin esto, 26 filas APTA de CEO quedan sin clasificar | 09 §6, doc 02 §4 | 🔴 **Alta** |
| **P-07** | **Guardia de conceptos ambiguos** | `devolucion`, `reintegro` y `previa` nunca se corrigen automáticamente; van a `POR_REVISAR` | 09 §6 | 🔴 Alta |
| **P-08** | **Limpieza de artefactos de Excel** | Quitar tabuladores, `\n`, `\r` y `_x000D_` en el Paso 1 de limpieza | doc 02 §4 | 🟠 Media |
| **P-09** | **Catálogo maestro de motivos** | Adoptar el catálogo de 52 valores de `gdo_inbound.subtipificacion` como vocabulario unificado | doc 01 §6.2 | 🟠 Media |
| **P-10** | **Detección de sangrado de columnas en la ingesta** | Validar el dominio de cada columna y mandar a cuarentena lo que no aplique | doc 02 §6 | 🔴 Alta |
| **P-11** | **Extender `fn_parse_fecha`** | **Confirmado (19-oct-2026):** en Excel los formatos vienen como día/mes/año; en la BD se guardan como año/mes/día. `fn_parse_fecha` debe cubrir `DD/MM/YYYY`, `DD/MM/YYYY HH:MM:SS AM/PM`, `MMM-YY` y seriales de Excel, y normalizar todo a `YYYY-MM-DD HH:MM:SS` | doc 01 §3 | 🟠 Media |
| **P-12** | **Bitácora de carga con hash del archivo** | Tabla `dim_carga` + `dim_origen` con `sha256` de cada Excel | doc 03 §6.2 | 🟠 Media |
| **P-13** | **Cuarentena de registros** | Ningún registro se descarta en silencio; todo rechazo queda registrado con su regla | doc 03 §6.2 | 🟠 Media |
| **P-14** | **Separar `anio_gestion` de `anio_venta`** | `anio` en las fuentes es el año de venta; usar `EXTRACT(YEAR FROM fecha_gestion)` | doc 03 §5 | 🟠 Media |

> **Impacto de la P-01 descartada:** si no existe `POR_REVISAR`, la §4 del doc 09
> (Estados de clasificación) queda invalidada. Los resultados no reconocidos deben
> clasificarse como **NO_APTA** (no como POR_REVISAR), y el mecanismo de la cola de
> revisión pasa a ser un **auditoría de calidad**, no un estado intermedio del registro.

### 1.3 Decisiones abiertas

| ID | Tema | Opciones | Impacto | Estado | Responsable |
|---|---|---|---|---|---|
| A-01 | **Alcance: retención vs. gestión general de llamadas** | Los documentos 01, 02 y `06_Documentacion.md` hablan de retención; el PDF y la descripción del proyecto hablan de llamadas, abandono y PQRS. Debe definirse si el reporte cubre ambos. | KPIs, modelo, fases 2 y 4 | ABIERTA | Negocio |
| A-02 | **Base acumulada local** | Truncar, modificar o reemplazar con histórico homologado (opciones A, B, C del doc 02) | Carga histórica | **RESUELTA** — ver §1.4 | — |
| A-03 | **Llave primaria de las llamadas** | Combinación de campos, hash de contenido o ID generado. Un hash de contenido duplica registros si el asesor edita una fila ya cargada. | Ingesta, upsert | **PROPUESTA** — D-10 | Equipo de datos |
| A-04 | **Una tabla de hechos o varias** | Atención, abandono y PQRS en una sola tabla (con nulos) o en tablas separadas. El abandono no tiene asesor. | ERD | **PROPUESTA** — D-09 | Equipo de datos |
| A-05 | **Fecha de Gas Caribe Outbound** | Solo trae `MES`. Definir de dónde sale la fecha real de la llamada o aceptar granularidad mensual. | Normalización de fechas | ABIERTA | Caribe + equipo de datos |
| A-06 | **Fecha de GDO** | La columna de fecha no está nombrada en la documentación ("fecha en vivo"). | Normalización de fechas | **RESUELTA** — ver §1.4 | — |
| A-07 | **Formato de fecha y zona horaria** | El flujo propone `YYYY-MM-DD HH:MM:SS`. Definir zona horaria (America/Bogota) y qué hacer si solo hay fecha sin hora. | Ingesta | **RESUELTA parcialmente** — ver §1.4 | — |
| A-08 | **GDO: `informativo` vs. `prqs escritas`** | Confirmar si son dos fuentes distintas o la misma, y cómo se fusionan. | Homologación | **RESUELTA con datos** — ver §1.4 | — |
| A-09 | **Clasificación por gasera** | Confirmar si un mismo resultado puede clasificarse distinto según la gasera. | Doc 09 | **RESUELTA** — D-07 | — |
| A-10 | **Motor de base de datos** | El doc 02 lo pregunta, pero la base ya existe. Registrar motor, versión y esquemas. | DDL | **RESUELTA** — ver §1.4 | — |
| **A-11** | **Granularidad del reporte: ¿empresa o asesor?** | `operador` es la empresa de tercerización; solo GDO tiene asesor individual (D-08). ¿El reporte mide productividad por empresa, por asesor o ambos? | KPIs, modelo de datos | **ABIERTA** | Negocio + jefatura |
| **A-12** | **Abandono de GDO** | `gdo_abandono` es un volcado sin delimitación: 92% de contratos nulos, 80% de fechas nulas, nombres de personas en el campo fecha. ¿Se reprocesa con GDO o se declara no confiable? | Cobertura de abandono | **ABIERTA** | GDO + equipo de datos |
| **A-13** | **`gdo_informativo`: ¿maestro o bitácora?** | 4.191 filas con `tipo_registro` = REGISTRO ÚNICO/DUPLICADO y `estado_inf` = PRIMER REGISTRO / 2º REGISTRO - N DÍAS. Es una bitácora de seguimiento. ¿Se carga aparte, se descarta, o se resuelve cada solicitud a su último estado? | Carga de PQRS | **ABIERTA** | Equipo de datos |
| **A-14** | **Campos obligatorios por gasera** | `localidad` 97–100% nula, `operador` 87.6% nula, `subtipificacion` 100% nula en CEO. ¿Qué se exige a cada gasera y con qué fecha? | Cobertura de KPIs | **ABIERTA** | Negocio + gaseras |
| **A-15** | **Estado de `APTA` y OCM** | Si desde el 1-nov los advisers tipifican en OCM con lista cerrada, ¿el catálogo de normalización se mantiene solo para el histórico? | Plan de normalización | **ABIERTA** | Equipo de datos + OCM |

### 1.4 Decisiones resueltas por la verificación en base de datos

| ID | Pregunta original | Respuesta verificada |
|---|---|---|
| **A-02** | ¿Truncar, modificar o reemplazar la base local? | La base local **ya no existe como tabla**: `gestion_diaria` (16 tablas, 48.036 filas) ES la base migrada. La decisión se tomó de facto y fue **modificar** (conservar y ampliar), pero **sin reconciliar**: 7 de 8 pares fuente→consolidado no cuadran, y el consolidado no incluye abandono ni PQRS. La deuda real es **trazabilidad**, no truncamiento. Ver doc 03 §3.3. |
| **A-06** | ¿Qué columna de fecha usa GDO? | `gdo_inbound.fecha_de_llamada` (39 columnas) — **100% parseable** ✅. `gdo_outbound.fecha_ejecucion` (68 columnas) — 93% parseable, con `fecha_de_base` como respaldo. `gdo_pqrs.fecha_registro_solicitud` — 100% parseable ✅. `gdo_pqrs.fecha_atencion` — **1.2% parseable** ❌. `gdo_informativo.fecha_regi` — **0.3% parseable** ❌ (3 formatos). `gdo_abandono.fecha_llamada` — **36.5% parseable** ❌ y contiene nombres de personas. |
| **A-07** | ¿Formato de fecha y zona horaria? | **Formato:** hay 4 formatos distintos conviven. `YYYY-MM-DD` (tipadas), `DD/MM/YYYY`, `MMM-YY` (`jun-26`), `DD/MM/YYYY HH:MM:SS AM/PM` (`10/06/2026 10:05:04 a. m.`). `fn_parse_fecha` cubre solo los 2 primeros. **Zona horaria:** ninguna fuente trae zona; el negocio opera en America/Bogota, y los horarios de abandono (`10:01:10 a. m.`) lo confirman. **Decisión pendiente:** qué hacer con `fecha` sin `hora` (hoy el 73.9% de las atenciones). |
| **A-08** | ¿`informativo` y `prqs escritas` son la misma fuente? | **No, y además hay 3 fuentes PQRS en GDO**, con granularidades distintas: `gdo_pqrs` (747, maestro de solicitud, 63 col., comparte estructura con `gdo_outbound`), `gdo_pqrs_escritas` (86, maestro de PQRS **con trazabilidad de ANS completa**: GDO→Xuma→Aseguradora→Respuesta), `gdo_informativo` (4.191, **bitácora de seguimiento**). Solapamiento: 142 contratos de `informativo` están en `gdo_pqrs`; 61 en `gdo_pqrs_escritas`. 1.180 filas de `informativo` (28.1%) vienen sin `tipo_registro` ni `resultado`, y 160 de ellas (3.8%) tienen las 28 columnas nulas. |
| **A-10** | ¿Qué motor y qué esquemas? | **PostgreSQL 16.14** (Ubuntu 22.04). Esquemas: `gestion_diaria` (18 tablas + 5 vistas + 4 funciones), `ocm_retencion`, `reportes`, `siniestros`, `auditoria`, `public`. **El proyecto usa `gestion_diaria`**; los demás no tienen relación con Retención y quedan fuera de alcance. El usuario de conexión no tiene permiso de escritura ni acceso a `auditoria`. |

---

## 2. Inconsistencias detectadas en la documentación

| ID | Inconsistencia | Dónde | Acción sugerida | Estado |
|---|---|---|---|---|
| I-01 | "5 o 6 gaseras" | `01_Plan_Estructura.md`, Fase 2 | Corregir a 5 gaseras | ✅ Corregido |
| I-02 | La pregunta del motor de BD se plantea como pendiente, pero la base ya está lista | `02_Plan_Migracion_y_Estrategia_DB.md` | Actualizar con el motor real | ✅ Corregido (A-10) |
| I-03 | "Hash PK" tratado como decidido en un documento y como duda en otro | `08_Flujo_De_Datos.md` y `07_Estructura_de_datos.md` | Resolver A-03 y alinear ambos | ✅ Propuesta D-10 |
| I-04 | Normalización de todas las fechas a `YYYY-MM-DD HH:MM:SS`, pero hay fuentes sin hora o sin fecha | `08_Flujo_De_Datos.md` | Resolver A-05, A-06 y A-07 | ✅ A-06, A-07 resueltos; **A-05 sigue abierta** |
| I-05 | El plan semanal programa el DDL antes de tener el diccionario de datos | `02_Plan_Migracion_y_Estrategia_DB.md` | Reordenar: perfilado, diccionario, DDL | ✅ Hecho: doc 01 (diccionario) → doc 02 (mapeo) → doc 03 (ERD + DDL) |
| I-06 | El corte a OCM no aparece en ningún cronograma | Documentos 01 y 02 | Agregar el hito del 1 de noviembre | ✅ Agregado en el plan 01 |
| I-07 | Inbound dice "todas las gaseras" en el PDF, pero Efigas es solo Outbound | PDF oficial | Ya corregido en `07_Estructura_de_datos.md` | ✅ Corregido |
| I-08 | Surtigas: el texto dice "Jul - Oct", pero la carpeta se llama "JULIO - AGOSTO 2026" | PDF y `07_Estructura_de_datos.md` | Confirmar dónde están septiembre y octubre | 🔴 **Responde el dato**: `surti_inbound` llega hasta **2026-08-31** y `surti_outbound` hasta **2026-12-06**. La fecha de venta (`ano_venta`) sí llega a 2026. **No hay registros de septiembre ni octubre en Surtigas Inbound.** Pendiente: confirmar si existen en el Excel y no se cargaron, o si la continuidad aún no llegó. |
| I-09 | Nombres con errores: `abrl`, `prqs`, `surtugas` | Nombres de hojas y archivos | Registrar en el mapeo como nombres reales | ✅ Hecho (doc 02 §2) |
| I-10 | El archivo de GDO se llama "24 de Junio 2026" | PDF | Confirmar que es el archivo vigente | 🔴 **Dato relevante**: `gdo_inbound` cubre marzo–octubre 2026 y `gdo_outbound` enero–noviembre 2026, es decir **el archivo sigueactualizándose** (es el "registro en vivo"). El nombre del archivo es engañoso. |
| I-11 | El doc 02 menciona "0% de errores" tras OCM | Doc 02, Pilar 3 | Reemplazar por una métrica medible | ✅ Sustituido por: % de casamiento OCM×planilla, % de registros con fecha válida, % de clasificaciones en `POR_REVISAR` |
| I-12 | Los documentos de plan describen "motivos de retiro" y estados "Retenido / No Retenido / En Proceso", pero el resultado real tiene otros valores | Docs 01, 02 y `06_Documentacion.md` | Alinear con la clasificación del doc 09 | ✅ Hecho. **El vocabulario real es**: 4 resultados APTA (`cancelado`, `cancelado + venta`, `cancelado + reintegro`, `retenido`) + 23 NO APTA. **No existe "No Retenido" ni "En Proceso" en el dato.** |
| **I-13** | La documentación trata la base de datos, OCM y el catálogo de homologación como **trabajo futuro**, cuando **ya existen y están en producción** | Docs 01, 02, `06_Documentacion.md` | Reescribir el plan desde el estado real | ✅ Hecho (plan 01 y 02 reformulados) |
| **I-14** | El doc 01 dice "una fila = una gestión" sin advertir que un mismo contrato puede repetirse | `06_Documentacion.md` | Documentar la multigestión | ✅ Hecho: 3.114 grupos duplicados (20.2% del consolidado) |
| **I-15** | El doc 01 no distingue el eje temporal de venta del de gestión | `06_Documentacion.md` | Separar `anio_gestion` y `anio_venta` | ✅ Hecho: `anio` en las fuentes es el año de venta en el 100% de los casos |
| **I-16** | Los documentos asumen que `operador` es el asesor | `01_Diccionario_de_Datos.md`, `05_Calidad_de_Datos.md` | Corregir: es la empresa operadora | ✅ Hecho: D-08. El hallazgo inicial fue **incorrecto** y se corrigió con el dominio completo de valores |
| **I-17** | Los documentos asumen que el abandono y PQRS están en la base consolidada | `08_Flujo_De_Datos.md` | Aclarar el alcance | ✅ Hecho: el abandono son 12.710 filas en 4 tablas de `gestion_diaria`; PQRS son 6.280 en 4 tablas |

---

## 3. Supuestos sin verificar

| ID | Supuesto | Qué pasa si es falso | Cómo verificarlo | Estado |
|---|---|---|---|---|
| S-01 | OCM ofrece una API, exportación o acceso a datos utilizable | La integración se retrasa o requiere otro mecanismo | Consultar al proveedor o administrador de OCM | ABIERTA |
| S-02 | Los asesores dejarán de usar Excel el 1 de noviembre | Doble registro y riesgo de doble conteo | Comunicación y seguimiento (ver doc 07) | ABIERTA |
| S-03 | Las hojas mensuales de Gas Caribe y Surtigas tienen las mismas columnas | El lector falla o mezcla datos | Perfilado de columnas por hoja | 🔴 **Parcialmente resuelto**: el consolidado actual es homogéneo por tabla (una sola estructura de columnas para las 9.423 filas de Surtigas Inbound), pero **no se puede verificar por hoja** porque no se conserva la hoja de origen. **Hay evidencia de que NO es cierto en Caribe**: 1.774 filas (26.1%) sin fecha **y** 1.828 (26.9%) sin contrato **y** 1.825 (26.9%) sin teléfono **y** 1.953 (28.7%) sin canal, un patrón de filas estructuralmente distintas. **Pendiente:** pedir el layout real de cada pestaña. |
| S-04 | El archivo "recuperado" de Surtigas es completo y confiable | Faltan registros históricos | Cuadrar totales contra reportes anteriores | 🔴 **Con riesgo alto**: `surti_abandono` no tiene columna de contrato, su fecha es 100% no parseable, y `surti_inbound.operador` está llena con valores de otra columna (11.7%). Además, no hay registros de septiembre ni octubre (ver I-08). |
| S-05 | Existe un esquema de pruebas (Dev/Staging) separado de producción | Riesgo al hacer cargas masivas | Confirmar con quien administra la BD | 🔴 **Confirmado que NO existe**. En `DataCenter_Promigas` hay un solo esquema de trabajo (`gestion_diaria`) sobre 48.036 filas reales, y el usuario de conexión no tiene permiso de escritura. **Alternativa de bajo costo:** el propio `gestion_diaria` sirve de lectura, pero **toda escritura debe probarse primero contra una copia**. |
| S-06 | El script puede leer SharePoint (Graph API o sincronización local) | No hay ingesta automática | Probar acceso con credenciales reales | ABIERTA |
| S-07 | Los errores de escritura son de tipo ortográfico y no de significado | Correcciones erróneas | Revisar muestra manual por gasera | 🔴 **Parcialmente resuelto**: los 43 pendientes se clasificaron en (a) 34 typos, (b) 5 ambigüedades reales, (c) 4 conceptos nuevos. Los typos son 79% del total → **S-07 se sostiene**, pero el 12% restante necesita decisión de negocio. |
| **S-08** | El consolidado actual refleja el estado real de las fuentes | Se reportan cifras que no corresponden a la fuente | Conciliación fuente→consolidado fila a fila | 🔴 **FALSO.** 7 de 8 pares no cuadran. El consolidado tiene meses (septiembre, octubre) que las fuentes no tienen, y Caribe tiene 1.788 filas más que el consolidado. **Hay dos verdades en paralelo.** |
| **S-09** | Las 5 gaseras escriben el mismo nombre de columna para el mismo concepto | El mapeo se rompe en la ingesta | Comparar los encabezados de los 5 Excel | 🔴 **FALSO.** GDO usa `resultado_final` (Inbound) y `resultado_de_retencion` (Outbound) donde las otras usan `estado`; Surtigas usa `suscripcion` donde las otras usan `contrato`; Caribe usa `fecha_de_ejecucion` donde el Excel de origen se llama `FECHA DE ATENCION`; el `mes` de Caribe trae el año embebido (`"ABRIL 2026"`). |
| **S-10** | Los valores de cada columna pertenecen a esa columna | Se reportan métricas sin sentido | Validar el dominio de cada columna | 🔴 **FALSO.** 1.589 filas tienen en `operador` un valor de `tipo_de_contacto`; 186 tienen en `canal` un valor de otra columna; 45 celdas literalmente contienen dos columnas pegadas por tabulador. |

---

## 4. Riesgos

| ID | Riesgo | Prob. | Impacto | Mitigación | Responsable |
|---|---|---|---|---|---|
| R-01 | Doble conteo entre Excel y OCM en los días de transición | Alta | Alto | Definir fecha de corte por gasera y regla de exclusión (doc 07) | Por asignar |
| R-02 | OCM no entrega los datos como se espera | Media | Alto | Verificar S-01 cuanto antes; mantener Excel como respaldo | Por asignar |
| R-03 | Registros pierden clasificación por errores de digitación | Alta | Alto | Normalización y estado `POR_REVISAR` (doc 09) | Equipo de datos |
| R-04 | Falsos aptos por negaciones ("no retenido") | Media | Alto | Bloqueo de negaciones y revisión de muestra | Equipo de datos |
| R-05 | Registros duplicados en re-ejecuciones del script | Media | Medio | Definir llave (A-03) y hacer la carga idempotente | Equipo de datos |
| R-06 | Archivo de SharePoint dañado o renombrado | Media | Medio | Validación de existencia y estructura antes de cada lectura | Equipo de datos |
| R-07 | El nuevo reporte no cuadra con el de Power BI que valida la jefatura | Media | Alto | Plan de validación mes a mes por gasera | Por asignar |
| R-08 | Poco tiempo antes del corte (aprox. 13 días desde el 19 de octubre) | Alta | Alto | Priorizar el doc 07 y los datos pendientes | Equipo |
| R-09 | Datos personales de usuarios en una base centralizada | Media | Alto | Roles de acceso, backups y revisión frente a la Ley 1581 de 2012 | Por asignar |
| **R-10** | **La semántica de "APTA" se interpreta como "retención"** y se reporta una tasa de retención inflada | **Alta** | **Alto** | 🟡 **Aclarado por D-01/D-02 y documentado** (`APTA` = "a la llamada se le puede hacer gestión", **no** = "el cliente se quedó"). 3 de los 4 resultados APTA implican cancelación. **La comunicación debe ser explícita en el dashboard.** | Equipo de datos + Negocio |
| **R-11** | **Fuga de credenciales por versionado accidental de `.env`** | Baja | **Crítico** | `.env` está en `.gitignore`. Verificar con `git check-ignore -v database/.env` antes de cualquier commit. Los valores reales **no** aparecen en la documentación pública. | Equipo de datos |
| **R-12** | **Extracción de credenciales de agentes desde OCM** (`ocm_retencion.agent.pass`) | Baja | **Crítico** | El campo contiene credenciales en texto plano (hash base64 reversible). **No extraer ni copiar** ese campo a ningún artefacto del proyecto. | Equipo de datos |
| **R-13** | **Exposición de datos personales en reportes** (nombre, documento, teléfono, dirección) | Media | Alto | Los datos personales están presentes en varias tablas. Aplicar el **principio de minimización** al exponerlos en reportes. Roles de acceso y revisión frente a la Ley 1581 de 2012. | Equipo de datos + Negocio |
| **R-14** | **El usuario de conexión no tiene permiso de escritura** sobre producción | — | Informativo | El usuario **no es superusuario** y no puede modificar los esquemas de producción verificados. Cualquier cambio de esquema requiere un rol con permisos específicos. | Equipo de datos |
| **R-11** | **El KPI de productividad por asesor no es calculable en 4 de 5 gaseras** | Alta | Medio | 🟡 **Aclarado por D-08**: solo GDO registra el asesor individual. Definir el alcance real (A-11) antes de prometerlo | Negocio + jefatura |
| **R-12** | **El abandono de GDO no es confiable** y contamina cualquier métrica de nivel de servicio | Alta | Medio | Declarar la fuente no confiable (A-12) y no cargarla | GDO + equipo de datos |
| **R-13** | **El consolidado y la fuente son dos verdades** y el reporte no es auditable | Alta | Alto | Reingerir con lineage (P-12) y cuadrar al 100% antes de publicar | Equipo de datos |
| **R-14** | **Migraciones SQL se ejecutan sobre producción sin entorno de pruebas** (S-05) | Media | **Alto** | Todas las migraciones del doc 03 son aditivas, pero **deben probarse contra una copia** antes | DBA + equipo de datos |
| **R-15** | **El sangrado de columnas (1.589 filas) se propaga al modelo nuevo** | Media | Medio | P-10: validar dominio por columna en la ingesta y mandar a cuarentena | Equipo de datos |
| **R-16** | **Pérdida de clasificación por la normalización de la `/`** (27 filas APTA de CEO que hoy no clasifican) | Media | Bajo | P-06 | Equipo de datos |

---

## 5. Preguntas abiertas

1. ¿Cómo entrega OCM los datos (API, exportación, base directa) y qué campos incluye?
2. ¿OCM tendrá los mismos catálogos de resultado, o será una lista cerrada que elimine los errores de digitación?
3. ¿El corte a OCM es el mismo día para las 5 gaseras o escalonado?
4. ¿Qué hacen los asesores con las llamadas que ocurran durante una caída de OCM?
5. ¿Quién es el responsable de revisar la cola de `POR_REVISAR`?
6. ¿Quién aprueba el modelo de datos final y en qué fecha?
7. ¿Qué medidas de Power BI valida hoy la jefatura y cómo se calculan?
8. ~~¿La base local desactualizada tiene datos anteriores a 2026?~~ → **Resuelta**: el consolidado actual cubre enero 2025 – diciembre 2026, pero con 2 fechas corruptas (año 206 y año 2020) y **sin los meses de septiembre y octubre** que sí tienen las fuentes de CEO, Surtigas y GDO. (A-02)
9. ~~¿Dónde están los registros de septiembre y octubre de Surtigas Inbound?~~ → **No están en la base.** `surti_inbound` termina el 2026-08-31. O no se cargaron, o la continuidad del Excel todavía no llegó. **Confirmar con Surtigas.** (I-08)

### 5.1 Preguntas nuevas que levanta el perfilado de la base de datos

10. 🔴 **¿El reporte mide productividad por empresa operadora o por asesor?** Solo GDO tiene asesor individual. (A-11)
11. 🔴 **¿Se incluye el abandono de GDO, cuya fuente no es confiable?** (A-12)
12. 🔴 **¿`gdo_informativo` se carga como bitácora o se descarta?** (A-13)
13. 🟠 **¿Qué campos se exigen a cada gasera?** `localidad` está 100% vacía en Caribe Outbound y 97% en CEO; `operador` 87.6% en Surtigas; `subtipificacion` 100% en CEO. (A-14)
14. 🟠 **¿Quién resuelve la cola de 43 variantes pendientes** (≈4-5 horas de revisión) y con qué fecha? (doc 09 §8)
15. 🟠 **¿Se crea un entorno de pruebas?** Sin él, las migraciones del doc 03 se prueban sobre 48.036 filas reales. (S-05, R-14)
16. 🟡 **¿Qué se hace con el histórico de `resultado_normalizado` cuando OCM tipifique con lista cerrada?** (A-15)
17. 🟡 **¿Se pide a cada gasera el layout real de cada pestaña de Excel?** Es la única forma de resolver S-03 y el bloque de 27% sin datos de Caribe.
18. 🟡 **¿Se valida el dominio de `operador` como dimensión de empresa?** Si un día llega el nombre de un asesor, ¿es la misma dimensión o una nueva?
