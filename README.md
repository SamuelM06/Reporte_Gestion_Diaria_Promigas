# 📈 Reporte de Gestión Diaria - Retención Promigas

Repositorio centralizado para el análisis, ingesta, estandarización y reportería de la gestión diaria del **Área de Retención** para las gaseras de Promigas (5 a 6 distribuidoras).

---

## 🎯 Objetivo del Proyecto
Diseñar un sistema unificado y robusto de analítica y reportería diaria que permita comprender, monitorear y optimizar los indicadores de retención de clientes en las distintas gaseras asociadas a Promigas.

---

## 🧭 Enfoque de Trabajo: *Data Analyst First*
Este proyecto prioriza la comprensión exhaustiva del dato antes de cualquier desarrollo de software o interfaz gráfica:
1. **Auditoría de Insumos:** Entender cada archivo Excel, cada hoja y cada registro recibido.
2. **Homologación de Criterios:** Estandarizar estados y tipificaciones entre las 5-6 gaseras.
3. **Calidad y Validación:** Control de nulos, duplicados y reglas de negocio.
4. **Automatización:** Conexión a bases de datos y scripts de transformación.
5. **Dashboard:** Presentación ejecutiva y operativa.

---

## 📂 Estructura del Repositorio

```text
├── context/
│   ├── Analisis/
│   │   ├── documentacion.md      # Metodología analítica, alcance y preguntas clave
│   │   └── flujo_de_datos.md     # Arquitectura conceptual del flujo de datos
│   └── planes/
│       └── 01_Plan_Estructura.md # Hoja de ruta por fases del proyecto
├── database/
│   ├── .env.example              # Plantilla de credenciales segura
│   ├── conexion_template.py      # Script plantilla de conexión (SQLAlchemy/pandas)
│   └── README.md                 # Guía para configuración de bases de datos
├── .gitignore                    # Protección de credenciales y datos pesados
└── README.md                     # Descripción general del repositorio
```

---

## 🚀 Estado Actual
* **Fase:** Fase 0 - Preparación, Estructura y Gobernanza de Datos.
* **Próximo Paso:** Recepción de rutas de archivos, inventario de hojas/columnas y credenciales de BD para iniciar la auditoría de datos en profundidad.
