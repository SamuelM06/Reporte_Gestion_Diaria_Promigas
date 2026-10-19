# 09. Normalización y Clasificación de Resultados de Llamada

**Proyecto:** Gestión Diaria Promigas
**Esquema de base de datos:** `gestion_diaria`
**Tabla involucrada:** `clasificacion`
**Estado del documento:** Borrador para revisión del equipo
**Fecha:** 19 de octubre de 2026
**Versión:** 2 — con datos reales de `DataCenter_Promigas` (verificado el 19-oct-2026)

> **Cambio en esta versión:** la §11 "Datos pendientes para cerrar este documento" queda
> **cerrada con evidencia**. Todo lo que se pedía está verificado contra la base de
> datos. Se añadieron además los hallazgos que el perfilado reveló: la asimetría de
> normalización, los fallos por un espacio, y la zona de peligro para la corrección
> automática.

---

## 1. Propósito y contexto

Cada llamada registrada por los asesores trae un campo **resultado**, que describe cómo le fue al asesor en la llamada. Ese resultado se escribe a mano, por lo que contiene errores de digitación (por ejemplo "retenida", "retnido", "etenido", "cancelada+ veta").

A partir del resultado se asigna una **clasificación**:

- **Apta:** a la llamada se le puede hacer una gestión al usuario.
- **No apta:** a la llamada no se le puede hacer gestión.

Solo existen **4 resultados aptos**. Todo lo demás es no apto.

| Resultado apto | Significado |
|---|---|
| Retenido | El usuario fue retenido |
| Cancelado | El usuario canceló el servicio |
| Cancelado + Venta | El usuario canceló y se concretó una venta |
| Cancelado + Reintegro | El usuario canceló y se gestionó un reintegro |

> **Regla de negocio confirmada (D-01):** *Retenido* y *Cancelado* son resultados distintos y no deben tratarse como equivalentes en ningún cálculo. Ambos son aptos para gestión, pero conservan su identidad propia.

**Problema que resuelve este documento:** un error de escritura nunca debe convertir una llamada apta en no apta. Antes de clasificar, el resultado debe normalizarse, y si no hay certeza, el registro debe quedar en revisión, no en "no apto".

### 1.1 Verificación de D-01 contra la base de datos ✅

La decisión D-01 **ya está implementada** en `gestion_diaria.clasificacion`. La columna
`resultado_normalizado` produce **exactamente 4 valores** entre sus 17 variantes APTA
**registradas hasta hoy**:

| Resultado canónico | Variantes registradas hoy | Filas afectadas |
| :--- | :---: | ---: |
| `cancelado` | `cancelado`, `cancelada` | 2 |
| `cancelado + venta` | `cancelada + venta`, `cancelada +venta`, `cancelada+venta`, `cancelado + venta`, `cancelado +venta`, `cancelado+venta` | 6 |
| `cancelado + reintegro` | `cancelacion + reintegro`, `cancelacion+reintegro`, `cancelado + reintegro`, `cancelado +reintegro`, `cancelado /reintegro`, `cancelado+reintegro` | 6 |
| `retenido` | `retenido`, `retenida`, `retnido` | 3 |

**D-01 y D-02 quedan confirmadas con datos.** El diseño propuesto abajo es una
evolución de lo que ya existe, no una corrección de algo roto.

> ⚠️ **La tabla anterior es una foto del 19-oct-2026, no un catálogo cerrado.** Ver §1.2.

### 1.2 El espacio de variantes es ABIERTO — no se puede acotar 🔴

Este es el punto central del documento y el que gobierna todo el diseño.

**Los 4 resultados APTA son conceptos canónicos: son 4, cerrados y fijos.**
D-01 los define y el negocio los conoce. Sobre ellos no hay discusión.

**Las variantes son el espacio de escritura real de los asesores: es abierto,
ilimitado y crece todos los días.** Un asesor puede escribir:

| Concepto canónico | Variantes posibles (muestra ilustrativa) |
| :--- | :--- |
| `retenido` | `retenido`, `retenida`, `retnido`, `retenidoo`, `retenid`, `reteni`, `retennido`, `retenido `, `retenído`, `retenidoo`, `RE TENIDO`, `retenido.` … |
| `cancelado` | `cancelado`, `cancelada`, `cancelad`, `cncelado`, `canceladoo`, `canceladoo`, `cancelao`, `cancelado `, `canceládo`, `canceladdo` … |
| `cancelado + venta` | `cancelado + venta`, `cancelada + venta`, `cancelada+ veta`, `cancelado+venta`, `cancelado  +  venta`, `cancelado + venta `, `cncelado + venta` … |
| `cancelado + reintegro` | `cancelado + reintegro`, `cancelado / reintegro`, `cancelado+reintegro`, `cncelado + reintegro`, `cancelado + rreintegro` … |

> Los ejemplos de la §7 de la versión original de este documento (`etenido`,
> `cancelada+ veta`) **no son una lista de casos: son ilustraciones de un espacio
> infinito.** El mismo asesor puede producir un error distinto cada semana, y 5.000
> asesores pueden producir 5.000 formas del mismo error.

**Consecuencias de diseño (no negociables):**

| # | Consecuencia | Implicación práctica |
| ---: | :--- | :--- |
| 1 | **No se puede resolver el problema enumerando variantes** | Un catálogo escrito a mano queda obsoleto el mismo día |
| 2 | **`resultado_variante` está diseñada para crecer sin límite** | No es un defecto del modelo: es el objetivo. Se indexa y se particiona si hace falta |
| 3 | **La comparación difusa debe hacerse contra los CONCEPTOS, nunca contra las variantes** | Si se compara contra la tabla de variantes, cada variante nueva compite con las anteriores y la calidad del fuzzy se degrada |
| 4 | **La cola de revisión es permanente, no un backlog finito** | Se alimenta todos los días; lo que se resuelve hoy es el snapshot de hoy |
| 5 | **El aprendizaje automático es obligatorio, no opcional** | Sin el ciclo variante→revisión→aprendizaje, la cola crece sin límite |
| 6 | **Un concepto nuevo (no una variante) requiere decisión humana** | "no tiene activos seguros" es un concepto; "no tiene activcos seguros" es una variante |

**Distinción clave:**

| | Concepto canónico | Variante |
| :--- | :--- | :--- |
| Qué es | El significado de negocio | La forma en que se escribió |
| Cuántos hay | ~30 (4 APTA + ~26 NO APTA) | **Ilimitados** |
| Quién lo define | El negocio | Se descubre solo, con el uso |
| Cómo se incorpora | Aprobación explícita | Automático si el fuzzy tiene confianza; revisión si no |
| Dónde vive | `dim_resultado` | `resultado_variante` |

> **El error conceptual a evitar:** tratar "4 resultados aptos" como si fuera "4 cadenas
> de texto aceptadas". Los 4 son conceptos; las cadenas son un universo que el sistema
> **descubre y aprende**, y cuyo número no puede acotarse por adelantado.


---

## 2. Estado actual de la tabla `clasificacion`

**DDL real verificado** (la §2 original decía "por confirmar"; aquí está confirmado):

```sql
CREATE TABLE gestion_diaria.clasificacion (
    gasera                text NOT NULL,
    variante              text NOT NULL,
    resultado_normalizado  text NOT NULL,
    clasificacion         text NOT NULL,
    CONSTRAINT clasificacion_pkey PRIMARY KEY (gasera, variante)
);
```

| Aspecto | Valor verificado |
| :--- | :--- |
| Filas | **40** |
| Columnas | 4, todas `text` |
| Llave primaria | **(gasera, variante)** — compuesta, confirmada |
| Valores de `gasera` | **1 solo: `GasCaribe`** (las 40 filas) |
| Valores de `clasificacion` | 2: `APTA` (17), `NO APTA` (23) |
| Valores de `resultado_normalizado` | **27** (4 APTA + 23 NO APTA literales) |
| Índices | Solo la PK. Sin índice por `resultado_normalizado` ni por `clasificacion`. |

**Interpretación:** la tabla ya funciona como un diccionario de variantes por gasera. Cada fila dice: *"en esta gasera, cuando el asesor escribe X, significa el resultado Y, que se clasifica como Z"*.

### 2.1 Limitaciones del diseño actual (confirmadas con datos)

1. **Solo reconoce lo que ya tiene registrado**, y solo para GasCaribe. Un error nuevo (por ejemplo "retenidoo") no existe como variante y el cruce no lo encuentra. Y como el espacio de variantes es abierto (§1.2), **esta limitación no se cierra enumerando: se cierra con el algoritmo + el aprendizaje**.
2. **`resultado_normalizado` no es único.** Muchas variantes apuntan al mismo valor canónico, por lo que no se puede usar como llave foránea sin una tabla de catálogo.
3. **No hay estado para "sin resolver".** Hoy un resultado desconocido solo puede quedar sin clasificar o caer en "no apta".
4. **No hay trazabilidad.** No se sabe si una variante fue cargada a mano, aprendida automáticamente o revisada por una persona.
5. 🆕 **La normalización es asimétrica: solo se corrigieron los typos APTA.** De las 17 variantes APTA, **13 están corregidas**; de las 23 NO APTA, **0 están corregidas** (los typos se conservan tal cual: `no tiene resursos`, `no tiene resursus`, `no es proteceso de retencion`).

   > Esto es coherente con **D-03**: el esfuerzo de normalización se puso donde el error era caro (convertir un APTA en NO APTA). Pero deja el catálogo NO APTA como una lista de 23 literales sin consolidar, y por eso `resultado_normalizado` tiene 27 valores distintos en vez de un catálogo cerrado.

6. 🆕 **No hay mecanismo de descubrimiento continuo.** Una tabla de 40 filas cargadas a mano, sin cola de revisión y sin aprendizaje, se queda obsoleta de inmediato: el primer "cancelad" que escriba un asesor abre un hueco que nadie va a cerrar.

### 2.2 Cobertura real del catálogo por gasera (snapshot 19-oct-2026)

> ⚠️ **Este es un estado del momento, no un universo.** Mañana habrá más variantes; la
> tabla crece. Lo que importa no es el número de hoy, sino que **el mecanismo para
> absorber las nuevas esté funcionando**.

Medido con `LEFT JOIN clasificacion ON variante = normalizar_texto(estado)`:

| Gasera | Columna de resultado | Distintos | APTA (filas) | NO APTA (filas) | **Sin catalogar (filas)** | Nulos |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: |
| CEO | `ceo_inbound.estado` | 40 | 2.392 | 228 | **65** | 64 |
| Efigas | `efigas_outbound.estado` | 13 | 590 | 398 | **5** | 6 |
| Caribe Inbound | `caribe_inbound.estado` | 20 | 4.753 | 2.044 | **0** ✅ | 0 |
| Caribe Outbound | `caribe_outbound.estado` | 30 | 564 | 741 | **0** ✅ | 0 |
| GDO Inbound | `gdo_inbound.resultado_final` | 11 | 3.941 | 198 | **51** | 0 |
| GDO Outbound | `gdo_outbound.resultado_de_retencion` | 15 | 1.427 | 1.563 | **15** | 279 |
| Surtigas Inbound | `surti_inbound.estado` | 18 | 9.049 | 219 | **100** | 55 |
| Surtigas Outbound | `surti_outbound.estado` | 7 | 221 | 77 | **0** ✅ | 1 |

**43 variantes distintas sin catalogar** (22 en CEO, 11 en Surtigas, 5 en GDO Outbound, 4 en GDO Inbound, 1 en Efigas) que afectan a **236 filas**.

---

## 3. Principio de diseño

1. **Nunca se modifica el texto original.** Se guarda siempre tal como llegó.
2. **Normalizar antes de clasificar.** El orden es: limpiar, buscar, corregir, clasificar.
3. **Ante la duda, revisión.** Un registro sin certeza va a la cola de revisión. Nunca se clasifica por defecto como no apto.
4. **El sistema aprende.** Cada corrección confirmada se agrega como variante, para que el mismo error no vuelva a requerir corrección.

---

## 4. Estados de clasificación propuestos

| Estado | Significado |
|---|---|
| `APTA` | Resultado canónico apto (los 4 definidos) |
| `NO_APTA` | Resultado reconocido que no es apto |
| `POR_REVISAR` | El resultado no pudo normalizarse con certeza; requiere revisión humana |

**Decisión pendiente (ver doc 010):** agregar el tercer estado `POR_REVISAR`. Sin él, los errores no resueltos contaminan el conteo de no aptas.

> **Con dato real:** hoy las 236 filas no catalogadas quedan **sin clasificar** (ni APTA ni
> NO APTA), no mal clasificadas. El riesgo no es que se contamine el conteo de NO APTA,
> sino que esas filas **desaparecen de todo KPI que filtre por clasificación**. El
> estado `POR_REVISAR` hace visible ese hueco en vez de esconderlo.

---

## 5. Modelo de datos propuesto

### Opción A: mantener `clasificacion` como está y ampliarla

Se agregan columnas de trazabilidad a la tabla actual:

| Columna nueva | Tipo sugerido | Descripción |
|---|---|---|
| `origen` | texto | `manual`, `auto`, `revisado` |
| `score_similitud` | numérico | Confianza de la corrección automática |
| `fecha_alta` | fecha-hora | Cuándo se agregó la variante |
| `validado` | booleano | Si una persona confirmó la variante |

### Opción B (recomendada): separar catálogo y variantes

| Tabla | Llave | Contenido |
|---|---|---|
| `dim_resultado` | `resultado_normalizado` | Valores canónicos únicos y su clasificación (APTA / NO_APTA / POR_REVISAR) |
| `resultado_variante` | `(gasera, variante)` | Cada texto escrito por los asesores, apuntando a `dim_resultado` |
| `resultado_pendiente` | `id` | Textos no resueltos, con su conteo y estado de revisión |

**Por qué la opción B:**

- Permite una llave foránea limpia desde las tablas de hechos hacia `dim_resultado`.
- La clasificación se define una sola vez por resultado canónico, no se repite en cada variante.
- Evita que dos variantes del mismo resultado queden con clasificaciones contradictorias.
- **Separa las dos cosas que se estaban confundiendo**: el conjunto **cerrado** de conceptos
  (que el negocio controla) y el conjunto **abierto** de formas escritas (que el sistema
  descubre y aprende). Ver §1.2.

> **Sobre la pregunta abierta de la §5 original** ("si la clasificación de un mismo
> resultado puede cambiar según la gasera"): **A-09 queda resuelta con datos.** La tabla
> `clasificacion` es por gasera, pero los 4 resultados APTA y sus valores normalizados
> son **idénticos** en las 5 gaseras: las 4.753 filas APTA de Caribe, las 2.392 de CEO y
> las 9.049 de Surtigas colapsan a los mismos 4 canónicos. No hay ninguna divergencia
> entre gaseras en el lado APTA.
>
> La Implementación de la §6.5 (M5 del doc 03) conserva la llave `(gasera, variante)`
> para no bloquear el caso future, pero la clasificación se define a nivel de
> `dim_resultado`, que es único.

### Campos en las tablas de hechos de cada llamada

| Campo | Descripción |
|---|---|
| `resultado_original` | Texto exacto que escribió el asesor (nunca se modifica) |
| `resultado_normalizado` | Valor canónico tras la corrección |
| `clasificacion` | APTA, NO_APTA o POR_REVISAR |
| `metodo_normalizacion` | `exacto`, `variante`, `fuzzy`, `manual`, `sin_match` |
| `score_similitud` | Confianza (solo aplica a `fuzzy`) |

### Ejemplo de DDL (opción B) — **ajustado al motor real**

Motor confirmado: **PostgreSQL 16.14**. El SQL siguiente ya usa la sintaxis definitiva.

```sql
CREATE TABLE gestion_diaria.dim_resultado (
    resultado_id   smallserial PRIMARY KEY,
    codigo         text NOT NULL UNIQUE,
    nombre         text NOT NULL,
    clasificacion  text NOT NULL
        CHECK (clasificacion IN ('APTA', 'NO_APTA', 'POR_REVISAR')),
    es_apto        boolean GENERATED ALWAYS AS (clasificacion = 'APTA') STORED,
    activo         boolean NOT NULL DEFAULT true
);

CREATE TABLE gestion_diaria.resultado_variante (
    gasera                 varchar(30)  NOT NULL,
    variante               varchar(200) NOT NULL,
    resultado_id           smallint     NOT NULL
        REFERENCES gestion_diaria.dim_resultado (resultado_id),
    origen                 varchar(20)  NOT NULL DEFAULT 'manual'
        CHECK (origen IN ('manual','auto','revisado')),
    score_similitud        numeric(5,2),
    validado               boolean      NOT NULL DEFAULT false,
    fecha_alta             timestamptz  NOT NULL DEFAULT now(),
    PRIMARY KEY (gasera, variante)
);

CREATE TABLE gestion_diaria.resultado_pendiente (
    id                bigserial PRIMARY KEY,
    gasera            varchar(30)  NOT NULL,
    texto_original    varchar(200) NOT NULL,
    texto_limpio      varchar(200) NOT NULL,
    candidato         varchar(100),
    score_similitud   numeric(5,2),
    ocurrencias       integer      NOT NULL DEFAULT 1,
    estado            varchar(20)  NOT NULL DEFAULT 'PENDIENTE'
        CHECK (estado IN ('PENDIENTE','RESUELTO','DESCARTADO')),
    fecha_registro    timestamptz  NOT NULL DEFAULT now(),
    UNIQUE (gasera, texto_limpio)
);

CREATE INDEX ix_resultado_pendiente_ocurr
    ON gestion_diaria.resultado_pendiente (ocurrencias DESC)
    WHERE estado = 'PENDIENTE';
```

---

## 6. Algoritmo de normalización

Se ejecuta durante la ingesta, para cada registro, en este orden. Se detiene en el primer paso que resuelva.

### Paso 1. Limpieza básica del texto

- Quitar espacios al inicio y al final, y colapsar espacios múltiples.
- Pasar a minúsculas.
- Quitar tildes y caracteres invisibles.
- Estandarizar el símbolo `+` con un espacio a cada lado: `cancelada+ veta` pasa a `cancelada + veta`.
- 🆕 **Quitar tabuladores y saltos de línea** (`\t`, `\n`, `\r`, `_x000D_`): son artefactos del portapapeles de Excel, no del dato. (740 celdas afectadas en el esquema actual.)
- 🆕 **Estandarizar la barra** con espacios a cada lado: `cancelado/reintegro` → `cancelado / reintegro`.

> 🆕 **El último punto corrige un hallazgo real:** hoy `normalizar_texto` normaliza el `+`
> pero **no la `/`**. Por eso `cancelado/reintegro` (26 filas de CEO) no coincide con
> `cancelado /reintegro` (que sí está catalogada como APTA) y queda sin clasificar.
> El mismo `+` ya está cubierto; la `/` es el hueco restante.

### Paso 2. Búsqueda exacta en `resultado_variante`

Se busca `(gasera, texto_limpio)`. Si existe, se toma su `resultado_id` y se termina. Método: `variante`.

### Paso 3. Búsqueda exacta en el catálogo

Se busca `texto_limpio` directamente en `dim_resultado`. Método: `exacto`.

### Paso 4. Bloqueo de negaciones

Si el texto contiene `no `, `sin `, `nunca`, `ninguno` u otra negación, **no se aplica corrección aproximada**. "No retenido" se parece demasiado a "Retenido" y se convertiría en un falso apto. Va directo a revisión salvo que ya exista como variante.

> **Verificado con datos reales.** Todas las negaciones detectadas ya están en el
> catálogo como NO APTA y por tanto se resuelven en el **Paso 2**, antes de llegar al
> Paso 4:
>
> | Gasera | Valores con negación | Filas | ¿En el catálogo? |
> | :--- | :--- | ---: | :--- |
> | CEO | `NO APTO` (104), `NO APLICA` (30), `NO ATENDEMOS EL SEGURO` (1), `NO TIENE SEGUROS ACTIVOS` (1), `NO PTO` (1) | 137 | 4 de 5 |
> | Efigas | `NO CONTACTO` (387), `NO APTO` (9), `NO APLICA` (1) | 397 | ✅ los 3 |
> | Caribe | `SIN REGISTRO` (1.898), `NO CONTACTO` (577), `NO APLICA` (97), `NO APTO` (93), `NO ES PROCESO DE RETENCION` (32), … | ~2.700 | ✅ |
> | GDO | `NO CONTACTO` (1.507), `NO APLICA` (96), `NO APTO` (116), `NUNCA DESEA ADQUIRIR EL SEGURO` (3) | 1.722 | 3 de 4 |
> | Surtigas | `NO APTO` (101), `NO APLICA` (80) | 181 | ✅ los 2 |
>
> **Conclusión:** el orden del algoritmo es correcto y el bloqueo de negaciones es una
> red de seguridad, no un cuello de botella. Las 5 excepciones (`NO ATENDEMOS EL
> SEGURO`, `NO TIENE SEGUROS ACTIVOS`, `NO PTO`, `NUNCA DESEA ADQUIRIR EL SEGURO` y
> `NO ES PROCESO DE RETENCION` con typo) van a `POR_REVISAR` por volumen bajo.

### Paso 5. Coincidencia aproximada por componentes

> 🔴 **Regla estructural: el fuzzy se compara contra los CONCEPTOS (`dim_resultado`),
> nunca contra las variantes (`resultado_variante`).** Como el espacio de variantes es
> abierto (§1.2), comparar contra la tabla de variantes haría que cada variante nueva
> compita con las anteriores y la calidad de la coincidencia se degradaría con el
> tiempo. El universo de comparación es **cerrado y estable**: ~30 conceptos.

1. Separar el texto por `+` en componentes.
2. Comparar **cada componente contra todo el catálogo de conceptos** (aptos y no aptos), no solo contra los 4 aptos. Si solo se compara contra los aptos, un no apto parecido se corregiría de forma errónea.
3. Aceptar la corrección solo si:
   - la similitud supera el **umbral** (valor inicial sugerido: 85, a calibrar con datos reales), y
   - hay un **único candidato claro**: la diferencia con el segundo mejor candidato es de al menos 10 puntos.
4. Reconstruir el resultado uniendo los componentes corregidos con ` + `.
5. Si el resultado reconstruido existe en el catálogo de conceptos, se acepta. Método: `fuzzy`.

> **Por qué el margen es indispensable en un espacio abierto:** con un universo ilimitado
> de escrituras, siempre habrá un texto equidistante entre dos conceptos
> (`cancelacion` está a un punto de `cancelado` y de `cancelacion previa`). El margen de
> 10 puntos es lo que impide que el sistema **invente** una clasificación. Ante la duda,
> `POR_REVISAR`.

> 🆕 **Zona de peligro verificada con datos.** Estos 4 conceptos son los que el Paso 5
> puede convertir erróneamente, y por eso deben ir forzosamente a `POR_REVISAR`:
>
> | Variante | Gasera | Filas | Por qué es ambigua |
> | :--- | :--- | ---: | :--- |
> | `cancelacion` | CEO | 2 | ¿"cancelación previa" (NO APTA) o "cancelado" (APTA)? |
> | `reintegro` | CEO | 1 | ¿"cancelado + reintegro" (APTA) o un reintegro suelto? |
> | `devolucion` | CEO | 1 | ¿"cancelado + devolución de primas" (NO APTA)? |
> | `cancelado/devolucion de primas` | Surtigas | 14 | NO APTA, pero se parece mucho a `cancelado + reintegro` (APTA) |
>
> Regla concreta: **ningún componente que contenga `devolucion`, `reintegro` o
> `previa` se corrige automáticamente.** Van a revisión.
>
> ⚠️ **Esta lista es una muestra de hoy, no una lista cerrada.** La regla general que
> protege al sistema es: **si dos candidatos están demasiado cerca, no se decide.**

### Paso 6. Sin certeza

Si no se resolvió en ninguno de los pasos anteriores:

- `clasificacion` = `POR_REVISAR`
- Se registra o actualiza en `resultado_pendiente` (suma una ocurrencia).
- Método: `sin_match`.

> **Este es el punto donde el sistema reconoce que no sabe.** Un `sin_match` no es un
> error: es la señal de que el asesor escribió algo que el catálogo de conceptos todavía
> no cubre. Por eso la cola de revisión es **permanente** (§8).

### Aprendizaje

Cuando una corrección `fuzzy` supera un umbral alto o una persona la confirma desde la cola de revisión, se inserta en `resultado_variante`. La próxima vez, el Paso 2 la resuelve de forma exacta y sin costo.

> **Este es el mecanismo que hace que el problema sea resoluble.** El espacio de variantes
> es infinito, pero el de conceptos es finito: cada variante nueva que se aprende
> **reduce** el espacio no reconocido. Sin este ciclo, la cola crece sin límite.

> 🆕 **Precaución con el aprendizaje.** La tabla actual muestra que el catálogo fue
> cargado a mano solo para GasCaribe. Si el aprendizaje automático empieza a crear
> variantes a partir de correcciones `fuzzy` sin revisión, el catálogo puede crecer con
> errores. Por eso `validado = FALSE` en las correcciones automáticas y el
> `origen` permite auditar qué se aprendió (`auto` | `revisado` | `manual`).
>
> **Regla de seguridad:** una variante aprendida automáticamente **nunca** crea un
> concepto nuevo. Si el texto no se parece a ningún concepto conocido, se resuelve
> conceptualmente (a un NO APTA) y la **forma** se registra como variante.

### Esquema de referencia en Python

```python
import re, unicodedata
from rapidfuzz import process, fuzz

UMBRAL = 85
MARGEN = 10
NEGACIONES = re.compile(r"\b(no|sin|nunca|ninguno|ninguna)\b")
# Palabras que NUNCA deben corregirse automáticamente (verificado con datos reales).
PELIGROSAS = re.compile(r"\b(devolucion|reintegro|previa)\b")
SUFIJOS_POR_REVISAR = re.compile(r"\b(no|sin|nunca|ningun|ninguna)\b")

def limpiar(texto: str) -> str:
    t = unicodedata.normalize("NFKD", str(texto))
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = t.lower().strip()
    # Artefactos de Excel (H-25, H-26)
    t = t.replace("\t", " ").replace("\n", " ").replace("\r", " ")
    t = t.replace("_x000D_", "")
    # Separadores: tanto el + como la / llevan un espacio a cada lado
    t = re.sub(r"\s*/\s*", " / ", t)
    t = re.sub(r"\s*\+\s*", " + ", t)
    return re.sub(r"\s+", " ", t)

def normalizar(texto, gasera, variantes, catalogo):
    """Normaliza el resultado escrito por un asesor y devuelve su concepto.

    variantes : dict {(gasera, texto_limpio): concepto_id}
                -> tabla resultado_variante. ABIERTA: crece con cada error nuevo.
    catalogo  : dict {concepto_limpio: concepto_id}
                -> tabla dim_resultado. CERRADO: ~30 conceptos, definidos por el
                   negocio. El fuzzy se compara SIEMPRE contra este diccionario,
                   nunca contra `variantes` (ver §1.2 y §6.5).
    """
    limpio = limpiar(texto)

    if (gasera, limpio) in variantes:                      # Paso 2
        return variantes[(gasera, limpio)], "variante", None
    if limpio in catalogo:                                  # Paso 3
        return catalogo[limpio], "exacto", None
    if NEGACIONES.search(limpio):                           # Paso 4
        return None, "sin_match", None
    if PELIGROSAS.search(limpio):                           # Paso 5 (guardia)
        return None, "sin_match", None

    # Paso 5: comparacion contra los CONCEPTOS (universo cerrado)
    partes, scores = [], []
    for parte in limpio.split(" + "):
        top = process.extract(parte, list(catalogo.keys()),
                              scorer=fuzz.ratio, limit=2)
        mejor = top[0]
        segundo = top[1][1] if len(top) > 1 else 0
        if mejor[1] < UMBRAL or (mejor[1] - segundo) < MARGEN:
            return None, "sin_match", None
        partes.append(mejor[0])
        scores.append(mejor[1])

    candidato = " + ".join(partes)
    if candidato in catalogo:
        return catalogo[candidato], "fuzzy", min(scores)
    return None, "sin_match", None                          # Paso 6


def aprender(variante, concepto_id, gasera, conn):
    """Registra una variante nueva para que el Paso 2 la resuelva exacto en el futuro.

    Nunca crea un concepto nuevo: solo asocia una forma escrita a un concepto
    existente. Si el texto no corresponde a ningun concepto conocido, el caso va
    a la cola de revision como PENDIENTE (Paso 6), no se aprende a ciegas.
    """
    conn.execute(
        """INSERT INTO gestion_diaria.resultado_variante
               (gasera, variante, resultado_id, origen, score_similitud, validado)
           VALUES (%s, %s, %s, 'auto', NULL, FALSE)
           ON CONFLICT (gasera, variante) DO NOTHING""",
        (gasera, variante, concepto_id))
```

> Este código es una referencia del algoritmo, no una implementación final. Debe probarse con los valores reales de cada gasera antes de usarse en producción.

---

## 7. Ejemplos — **muestra del 19-oct-2026, no catálogo cerrado**

> ⚠️ **Lo que sigue son ejemplos, no un universo ni una lista de cobertura.**
> Las tres subsecciones ilustran los tres comportamientos posibles del algoritmo
> (resuelve exacto, resuelve por aproximación, no resuelve). El conjunto de textos
> que un asesor puede escribir es **ilimitado** (§1.2): estas tablas son una foto de
> un día, no el alcance del problema.

> Los ejemplos de la §7 de la versión original (`etenido`, `cancelada+ veta`) se
> conservan como **ilustración del espacio abierto**: son representativos, no los únicos
> posibles, y no constituyen una lista de cobertura.

### 7.1 Casos que el algoritmo resuelve correctamente hoy (muestra)

| Texto escrito por el asesor | Gasera | Filas | Resultado normalizado | Clasificación | Método |
|---|---|---:|---|---|---|
| `CANCELADO` | CEO, Caribe, GDO, Surtigas | ~14.400 | `cancelado` | APTA | exacto |
| `RETENIDO` | CEO, Caribe, GDO, Surtigas | ~3.200 | `retenido` | APTA | exacto |
| `CANCELADA` | CEO, Caribe | 104 | `cancelado` | APTA | variante |
| `RETENIDA` | CEO, Efigas, Caribe, GDO | 87 | `retenido` | APTA | variante |
| `CANCELADO+VENTA` | Caribe, GDO | 460 | `cancelado + venta` | APTA | variante |
| `CANCELADA +VENTA` | CEO, Efigas, Surtigas | 551 | `cancelado + venta` | APTA | variante |
| `CANCELADO + REINTEGRO` | CEO, Efigas, Caribe, Surtigas | 713 | `cancelado + reintegro` | APTA | variante |
| `CANCELACION+REINTEGRO` | CEO | 12 | `cancelado + reintegro` | APTA | variante |
| `retnido` | Caribe | 1 | `retenido` | APTA | variante |
| `NO APTO` | las 5 | 503 | `no apto` | NO APTA | exacto |
| `NO CONTACTO` | Efigas, Caribe, GDO | 2.471 | `no contacto` | NO APTA | exacto |
| `SIN REGISTRO` | Caribe | 1.898 | `sin registro` | NO APTA | exacto |
| `cancelad` *(no existe hoy)* | — | 0 | `cancelado` | APTA | fuzzy |
| `cncelado` *(no existe hoy)* | — | 0 | `cancelado` | APTA | fuzzy |
| `retenidoo` *(no existe hoy)* | — | 0 | `retenido` | APTA | fuzzy |
| `cancelada+ veta` *(no existe hoy)* | — | 0 | `cancelado + venta` | APTA | fuzzy |

> Las últimas 4 filas **no aparecen en ninguna base de datos**: son escritos
> hipotéticos que el algoritmo debe resolver por aproximación. **Ese es el escenario
> que hay que probar**, y es la razón por la que el catálogo escrito a mano no basta.

### 7.2 Casos que hoy fallan y el algoritmo debe corregir (muestra del día)

| Texto escrito | Gasera | Filas | Qué debería dar | Por qué falla hoy |
|---|---|---:|---|---|
| `cancelado/reintegro` | CEO | **26** | `cancelado + reintegro` (APTA) | La `/` no se normaliza; el catálogo tiene `cancelado /reintegro` |
| `CANCELADO/REINTEGRO` | GDO Outbound | 1 | `cancelado + reintegro` (APTA) | idem |
| `cancelada + reintegro` | CEO | 3 | `cancelado + reintegro` (APTA) | Variante no registrada; el fuzzy lo resuelve |
| `cancelada previa` | CEO | 4 | `cancelado previa` (NO APTA) | Variante no registrada |
| `retnida` | Efigas | 5 | `retenido` (APTA) | El catálogo tiene `retnido` y `retenida`, no `retnida` |
| `NO ES PROTECESO DE RETENCIÓN` | Caribe Outbound | 2 | `no es proceso de retencion` (NO APTA) | Typo + tilde; `normalizar_texto` quita la tilde pero no el typo |
| `venta nueva` / `nueva venta` | Surtigas | 51 + 6 | Un solo canónico | Dos textos para el mismo concepto; **requiere decisión del negocio** (no fuzzy: son 2 conceptualizaciones) |
| `llamada caida` / `caida de llamada` | CEO, Surtigas | 4 / 7 | Un solo canónico | Tres textos (incluye `caida de llamada` en CEO) |
| `datos incompletos` / `datos incompleto` / `datos incompeto` | CEO | 5 / 1 / 1 | Un solo canónico | Tres truncamientos |

> ⚠️ **Las dos últimas filas no son variantes de un concepto: son dos conceptos que el
> negocio todavía no unificó** (`venta nueva` vs `nueva venta`; `llamada caída` vs
> `caida de llamada`). Ningún algoritmo debe fusionarlas por su cuenta: eso es una
> decisión de negocio. La distinción entre "variante" y "concepto no unificado" es
> exactamente lo que la cola de revisión debe distinguir.

### 7.3 Casos que deben ir a `POR_REVISAR` (nunca resolverse solos)

| Texto | Gasera | Filas | Motivo |
|---|---|---:|---|
| `cancelacion` | CEO | 2 | Ambigüedad real entre NO APTA y APTA |
| `reintegro` | CEO | 1 | ¿Parte de "cancelado + reintegro"? |
| `devolucion` | CEO | 1 | ¿"cancelado + devolución de primas"? |
| `cancelado/devolucion de primas` | Surtigas | 14 | NO APTA, pero se parece a un APTA |
| `no atendemos el seguro` | CEO | 1 | Negación no catalogada |
| `no tiene seguros activos` | CEO | 1 | Negación no catalogada |
| `no pto` | CEO | 1 | Negación no catalogada |
| `nunca desea adquirir el seguro` | GDO Outbound | 3 | Negación no catalogada |
| `numero errado` | GDO Outbound | 6 | Probablemente "número equivocado" (NO APTA) — **confirmar** |
| `contacto a tercero` | GDO Outbound | 3 | NO APTA; el catálogo tiene `tercero` |

> ⚠️ **Los casos que hoy van a `POR_REVISAR` son hoy estos 10.** Mañana habrá otros, y
> la lista no se acota: depende de lo que escriban los asesores.

---

## 8. Cola de revisión — **permanente, no un backlog finito**

| Aspecto | Definición (por acordar) |
|---|---|
| Fuente | Tabla `resultado_pendiente` |
| Responsable | Por definir (propuesta: analista de datos) |
| Frecuencia | Diaria durante la transición a OCM; luego semanal |
| Acción | Asociar el texto a un resultado canónico (se agrega como variante) o marcarlo como un nuevo no apto |
| Prioridad | Por número de ocurrencias, de mayor a menor |

> 🔴 **La cola no tiene tamaño final.** Como el espacio de variantes es abierto (§1.2),
> la cola se alimenta de forma continua. Un día con 43 pendientes y un día con 12 son
> ambos normales. Lo que hay que medir no es "cuántas quedan" sino **"cuánto tarda el
> sistema en vaciarlas"**: ese es el indicador de salud del mecanismo.

> **Carga inicial de la cola:** con el estado actual, la cola arranca con
> **43 variantes** que hoy no resuelven, agrupadas así:
>
> | Gasera | Variantes pendientes | Filas afectadas | Revisión sugerida |
> | :--- | ---: | ---: | :--- |
> | CEO | 22 | 65 | 1 sesión (≈1 h) — son typos y 4 ambigüedades |
> | Surtigas | 11 | 100 | 1 sesión — 3 conceptos nuevos (`venta nueva`, `datos incompletos`, `llamada caida`) + `devolución de primas` |
> | GDO Outbound | 5 | 15 | 1 sesión — 2 conceptos nuevos (`numero errado`, `contacto a tercero`) + 3 de GDO |
> | GDO Inbound | 4 | 51 | 1 sesión — `información de siniestro`, `imposibilidad operativa`, `reiterativa`, `devolución de primas` |
> | Efigas | 1 | 5 | Trivial (`retnida`) |
> | Caribe | 0 | 0 | ✅ Nada que revisar |
>
> **Tiempo total estimado: 4–5 horas de revisión humana** para dejar las 5 gaseras con
> catálogo completo. Es la inversión que desbloquea todos los KPIs de clasificación.

---

## 9. Métricas de calidad de la normalización

Se calculan por gasera y por periodo, y se registran en cada ejecución de la ingesta:

| Métrica | Descripción | Línea base actual (19-oct-2026) |
|---|---|---|
| % exacto o variante | Registros resueltos sin corrección | **99.5%** (47.941 de 48.199 con resultado) |
| % corregido por fuzzy | Registros corregidos automáticamente | **0%** (el algoritmo no existe todavía) |
| % POR_REVISAR | Registros pendientes de decisión humana | **0.5%** (236 filas) — hoy en realidad **0% clasificados y 0.5% invisibles** |
| Top 20 textos sin resolver | Los errores más frecuentes que faltan por mapear | Ver §7.2 y §7.3 |
| Variantes nuevas aprendidas | Cuántas se agregaron en el periodo | 0 |

**Criterio de control:** ningún reporte debe publicarse con registros `POR_REVISAR` sin que su cantidad sea visible.

> **Nota sobre la línea base:** el 99.5% de cobertura se debe a que el catálogo actual
> tiene 40 variantes bien elegidas. Ese número **caerá** a medida que se carguen más
> gaseras: GDO y Surtigas tienen 43 variantes pendientes que son justo las gaseras con
> más tráfico. La cobertura real por gasera está en §2.2.

---

## 10. Riesgos

| Riesgo | Mitigación | Verificación con datos |
|---|---|---|
| "No retenido" se corrige como "Retenido" | Bloqueo explícito de negaciones (Paso 4) | 4.655 filas con negación, todas resueltas en el Paso 2 ✅ |
| "Cancelado" se confunde con "Cancelado + Venta" | Comparación por componentes y margen mínimo entre candidatos | 5 conceptos ambiguos identificados → `POR_REVISAR` (§7.3) |
| Umbral mal calibrado | Calibrar con los valores reales y revisar una muestra manual | 85/10 como punto de partida; recalibrar tras la primera cola |
| Una variante nueva se asocia mal y se aprende | Las correcciones `fuzzy` entran con `validado = FALSE` y se auditan | `origen` + `validado` en `resultado_variante` |
| Misma variante con clasificación distinta entre gaseras | Mantener la llave `(gasera, variante)` y revisar diferencias | **A-09 resuelto**: no hay divergencias en el lado APTA ✅ |
| 🆕 La normalización inventa un APTA que no existe | Zona de peligro (`devolucion`, `reintegro`, `previa`) forzada a revisión | 4 conceptos, 18 filas ✅ |
| 🆕 Una slash o un tabulador rompe la coincidencia | Normalizar `/`, `\t`, `\n`, `_x000D_` en el Paso 1 | 27 filas de CEO por la `/`; 785 celdas con tabulador/salto ✅ |

---

## 11. Datos pendientes para cerrar este documento — ✅ **CERRADO**

| # | Dato pendiente | Respuesta verificada |
| ---: | :--- | :--- |
| 1 | **DDL real de `clasificacion`**: tipos, llaves y número de filas | `text, text, text, text`; PK `(gasera, variante)`; **40 filas**; 1 sola gasera (`GasCaribe`) |
| 2 | **Valores distintos del campo resultado** por gasera, con cantidad | Ver §2.2: 7 columnas de resultado, 20–40 valores distintos cada una, con el desglose APTA / NO APTA / sin catalogar |
| 3 | **Si la clasificación varía por gasera** | **No varía.** Los 4 resultados APTA son idénticos en las 5 gaseras. La tabla es por gasera, pero la clasificación es única. (A-09 → **resuelto**) |
| 4 | **Lista de valores no aptos existentes** | **23 variantes NO APTA** (ver §6.4 del doc 01) — hoy todas literales, sin consolidar |
| 5 | **Motor de base de datos y versión** | **PostgreSQL 16.14** (Ubuntu 22.04). El DDL de la §5 ya está ajustado a PostgreSQL |

**Datos nuevos que el perfilado añadió y que este documento debe incorporar:**

| # | Hallazgo | Impacto en este documento |
| ---: | :--- | :--- |
| 1 | La normalización actual es **asimétrica**: 13/17 APTA corregidas, 0/23 NO APTA | Justifica el `dim_resultado` separado y el paso de consolidation de NO APTA |
| 2 | `normalizar_texto` **no normaliza la `/`** | 26 filas APTA de CEO sin clasificar → corregir en el Paso 1 |
| 3 | 4 conceptos son **intrínsecamente ambiguos** | Necesitan el estado `POR_REVISAR` con guardia explícita, no solo fuzzy |
| 4 | La cola de revisión arranca con **43 variantes / 236 filas** | 4–5 horas de revisión humana; es el camino más corto a un catálogo completo |
| 5 | **GDO no registra el estado en `estado`** sino en `resultado_final` / `resultado_de_retencion` | La ingesta debe mapear 7 columnas distintas al mismo campo de resultado (ver doc 02, §7) |

---

## 12. Impacto en otros documentos

| Documento | Cambio |
|---|---|
| 03 Diccionario de Datos | ✅ **Hecho** — el §6.1.3 documenta los 43 fallos de catálogo y el §6.1.5 las negaciones |
| 04 Mapeo Origen-Destino | ✅ **Hecho** — el §7 define las 7 columnas de resultado y su homogeneización |
| 05 Modelo de Datos (ERD) | ✅ **Hecho** — M2 crea `dim_resultado`; M5 extiende `clasificacion` a las 5 gaseras; M3 agrega `resultado_original` y `metodo_normalizacion` a `fact_gestion` |
| 02 Definición de KPIs | Los KPIs de efectividad se calculan sobre `APTA`; `POR_REVISAR` se reporta aparte. **Falta redactar** |
| 03 Transición a OCM | **Falta redactar.** Relevance: si OCM tipifica con lista cerrada, el catálogo deja de ser necesario — pero eso no invalida la normalización del histórico |
| 08 Registro de Decisiones | ✅ **Hecho** — A-09 cerrada con datos; P-01 a P-05 se mantienen; se añaden P-06 a P-10 |
