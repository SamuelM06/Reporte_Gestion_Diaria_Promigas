# 📋 Plan 04: Transición a OCM

**Proyecto:** Gestión Diaria Promigas
**Estado:** ⬜ **Pendiente de redactar**
**Alcance previsto:** casamiento entre las planillas de Excel y la plataforma OCM, y plan
de desconexión progresiva de Excel
**Fecha de creación:** 19 de octubre de 2026

---

## 1. Por qué este documento existe

La dirección del proyecto es que desde el **1 de noviembre de 2026** los asesores
tipifiquen, clasifiquen y registren el resultado directamente en **OCM** (Omnichannel
Contact Manager), y que con esa fecha se apague el reporte en Excel.

Ese es el **único hito del proyecto con fecha**, y es el que tiene más riesgo: si OCM no
recibe la información con la misma granularidad que las planillas, el reporte diario se
cae.

Este documento define **cómo se mide y cómo se ejecuta** ese corte.

> ⚠️ **Nota de alcance:** el análisis técnico de este proyecto está acotado al esquema
> `gestion_diaria`. La réplica de OCM que existe en la instancia **no forma parte de este
> proyecto** y no se usa como fuente de datos. Aquí OCM se trata **solo como destino**.

---

## 2. Dependencias

| Dependencia | Estado | Bloquea |
| :--- | :--- | :--- |
| Acceso a la base de OCM y a su documentación de campos | 🔴 Sin verificar | Todo |
| Formato de la lista cerrada de resultados de OCM | 🔴 Sin verificar | El §4 |
| Comportamiento de OCM ante caída (¿se registran llamadas fuera de línea?) | 🔴 Sin verificar | El plan de contingencia |
| Decisión por gasera de la fecha de corte | 🔴 Abierta | El cronograma |
| Doc 03 (modelo) y doc 02 (mapeo) | ✅ Listos | — |

---

## 3. La pregunta que define el proyecto: ¿cuánto se casa?

Antes de apagar Excel hay que responder una pregunta medible:

> **¿Qué porcentaje de las gestiones registradas en Excel tiene su llamada registrada en
> OCM, y viceversa?**

Ese número — y no una fecha — decide si el corte es viable. Se mide con el cruce:

| Dimensión del cruce | Campo disponible en la fuente | Campo disponible en OCM |
| :--- | :--- | :--- |
| Teléfono | `telefono` (CEO, Caribe, Surtigas, GDO Inbound) | `numbercall` |
| Fecha | `fecha_de_llamada` / `fecha_de_ejecucion` | `fecha` (con hora) |
| Resultado | `estado` / `resultado_final` | `resultcall` / `resultcalldesc` |
| Campaña / cola | *(no existe en la fuente)* | `idcampaign` / `idgroup` |
| Agente | `nombre_asesor_retencion` (solo GDO) | `agent` |

> ⚠️ **Obstáculo conocido:** el teléfono no es un identificador de persona (un cliente
> puede tener varios), y **4 de las 5 gaseras no registran el agente de retención**
> (H-23). El cruce tiene que hacerse por teléfono + ventana temporal, no por
> identificador de cliente.

---

## 4. El punto de fricción con el catálogo de normalización

| Pregunta | Por qué importa |
| :--- | :--- |
| ¿OCM usa una **lista cerrada** de resultados? | Si es así, el problema de las variantes mal escritas **desaparece** en el origen, y el catálogo de normalización (doc 09) solo haría falta para el histórico |
| ¿La lista de OCM coincide con los **4 resultados APTA** de D-01? | Si no coincide, hay que decidir cuál manda |
| ¿OCM registra **PQRS** y **abandono**? | Si sí, se acaban los problemas de H-02 y H-09 en el destino |
| ¿OCM entrega **carga masiva** de los registros ya hechos? | Sin migración, se pierde el histórico |
| ¿Qué ocurre si OCM **cae**? | Define si el reporte diario se publica o no |

> **Consecuencia directa para el doc 09:** si OCM tipifica con lista cerrada, el
> espacio abierto de variantes (§1.2 de ese documento) **sigue siendo real para todo el
> histórico acumulado**, pero deja de crecer. El ciclo de aprendizaje (B-03b) pasaría de
> ser crítico a ser de mantenimiento.

---

## 5. Estructura del plan (a definir)

| Fase | Contenido | Estado |
| ---: | :--- | :---: |
| 0 | Verificar acceso a los datos de OCM y documentar sus campos | ⬜ |
| 1 | Construir el cruce OCM × planillas (piloto con una gasera) | ⬜ |
| 2 | Medir el % de casamiento por gasera y por mes | ⬜ |
| 3 | Acordar el umbral de casamiento por debajo del cual no se corta | ⬜ |
| 4 | Definir la fecha de corte por gasera (escalonado o simultáneo) | ⬜ |
| 5 | Plan de contingencia: qué pasa si OCM cae | ⬜ |
| 6 | Regla de exclusión durante el periodo de transición (evitar doble conteo) | ⬜ |
| 7 | Cierre del reporte en Excel y congelación de las planillas | ⬜ |

---

## 6. Riesgos que este documento debe cubrir

| ID | Riesgo | Mitigación a definir |
| ---: | :--- | :--- |
| O-01 | Doble conteo entre Excel y OCM durante la transición | Regla de exclusión por fecha y gasera |
| O-02 | OCM no entrega los datos con la granularidad necesaria | Piloto antes del corte |
| O-03 | El casamiento resulta bajo (< 50%) por el teléfono | Medir antes de comprometer el corte |
| O-04 | LosAssessores no adoptan el registro en OCM | Plan de comunicación y medición de uso |
| O-05 | OCM no cubre PQRS ni abandono | Fuente alternativa definida |
| O-06 | Caída de OCM = pérdida de datos del día | Procedimiento de contingencia |

---

## 7. Lo que hay que pedir para empezar

1. Acceso de lectura a los datos de OCM (mismo nivel que el actual sobre `gestion_diaria`).
2. Documentación de los campos disponibles, en especial: resultado, campaña, cola y
   marcador de llamada abandonada.
3. La definición de la **lista cerrada de resultados** de OCM.
4. El **volumen de llamadas por día** para dimensionar el cruce.
5. Confirmación de si OCM será la **única** fuente o coexistirá con Excel.

---

## 8. Relación con los demás documentos

| Documento | Relación |
| :--- | :--- |
| `03_Modelo_Datos.md` | El modelo debe servir tanto al consumo desde Excel como desde OCM |
| `09_Normalizacion_y_Clasificacion.md` | Su alcance depende de si OCM tipifica con lista cerrada |
| `010_Registro_Decisiones_Riesgos.md` | D-05 (fecha de corte) y las decisiones derivadas se registran ahí |
| `03_Definicion_de_KPIs.md` | Los KPIs deben poder calcularse igual con datos de Excel o de OCM |
