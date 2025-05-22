# Juego Pygame Modular

**Nota Importante:** Este README es un documento vivo y evoluciona con el proyecto. Se actualizará continuamente para reflejar los cambios más recientes en la arquitectura, funcionalidades clave, y las mejores prácticas aprendidas. Se espera que futuras IAs y desarrolladores consulten y contribuyan a este documento.

## Pautas de Colaboración y Desarrollo: Guía de Inicio Rápido

**Para asegurar una colaboración efectiva, un desarrollo coherente y el mantenimiento de la calidad del proyecto, es fundamental que todos los colaboradores (humanos y asistentes IA) sigan estos pasos iniciales para familiarizarse con el proyecto:**

1.  **Lee este `README.md` completamente:** Entiende la descripción general del proyecto, su estructura básica y cómo empezar a utilizarlo.
2.  **Consulta `DEVELOPMENT_PROTOCOLS.md`:** Este es el documento central que contiene todas las guías detalladas, reglas, protocolos de depuración, convenciones de código y procedimientos de contribución. Su lectura y comprensión son **obligatorias** antes de realizar cualquier trabajo. Puedes encontrarlo aquí: [`DEVELOPMENT_PROTOCOLS.md`](DEVELOPMENT_PROTOCOLS.md).
3.  **Estudia `mapa_conceptual_modulos.py` PROFUNDAMENTE:** Este archivo es tu **mapa mental y visual principal** del proyecto. Describe los módulos clave, sus responsabilidades, cómo interactúan, y los componentes internos más importantes. Su consulta y comprensión son **cruciales y continuas** para navegar la arquitectura del código, entender dónde residen las funcionalidades y cómo se conectan las diferentes partes del juego. Es una herramienta viva que debe reflejar el estado actual del proyecto.
4.  **Explora la Estructura del Proyecto:** Familiarízate con la organización de las carpetas principales:
    *   `src/`: Contiene todo el código fuente del juego.
    *   `assets/`: Alberga todos los recursos gráficos, de sonido y datos.
    *   `docs/`: (Si existe) Para documentación adicional detallada.
5.  **Revisa `TODO.md` y `CHANGELOG.md`:** Estos archivos te darán una idea de las tareas pendientes, bugs conocidos y el historial de cambios y versiones del proyecto.
6.  **Inspecciona `dev_notes.md`:** Contiene notas de desarrollo relevantes, estado actual, y problemas pendientes que pueden no estar en `TODO.md`. Es especialmente útil para la continuidad entre sesiones.
7.  **Consulta `docs/PERFORMANCE_OPTIMIZATION_PROTOCOLS.md`:** Si tu tarea involucra optimización de rendimiento, este documento es tu guía principal.

Una vez familiarizado con estos documentos, puedes proceder a explorar el código fuente en `src/`.

## Diccionario de Código / Mapa Conceptual de Módulos

**El archivo `mapa_conceptual_modulos.py` es una herramienta fundamental y de consulta constante para todos los desarrolladores (humanos y IA). Actúa como un glosario interactivo y un mapa visual de la arquitectura del proyecto, siendo esencial para una comprensión rápida y precisa de cómo está estructurado el juego y dónde encontrar cada pieza de funcionalidad.**

*   **Propósito:** Esta sección describe un archivo complementario, `mapa_conceptual_modulos.py`, que sirve como un glosario o "mapa conceptual" de los principales módulos, clases y sistemas del juego. Su objetivo es proporcionar una visión general rápida que facilite la incorporación de nuevos colaboradores y la comprensión de la arquitectura del código.
*   **Ubicación y Formato:** El mapa conceptual detallado se encuentra en el archivo `mapa_conceptual_modulos.py`, ubicado en la raíz del proyecto. Este archivo Python contiene un diccionario principal llamado `MAPA_MODULOS_POR_CATEGORIA`. Las claves de este diccionario son cadenas que representan las categorías lógicas del proyecto (ej. "Core", "Entidades", "Sistemas"), que idealmente se alinearán con la estructura de carpetas del código fuente (ej. `src/core`, `src/entidades`). El valor asociado a cada clave de categoría es una lista de diccionarios, donde cada diccionario representa un módulo específico y típicamente incluye claves como:
    *   `nombre_modulo`: Nombre del archivo del módulo (ej. "juego.py").
    *   `categoria`: (Duplica la clave del diccionario padre para referencia interna si es útil, aunque la agrupación ya está dada por la estructura).
    *   `ruta_relativa`: Ruta al archivo desde la raíz del proyecto (ej. "juego.py" o, después de la reestructuración, "src/core/juego.py").
    *   `responsabilidad_principal`: Descripción concisa de lo que hace el módulo.
    *   `interacciones_principales`: Un diccionario con listas `entrantes` (módulos que lo usan o de los que depende) y `salientes` (módulos que usa o de los que depende).
    *   `componentes_clave_internos`: Lista de las clases o funciones más importantes dentro del módulo.
    *   `notas_adicionales`: Cualquier otra información relevante.
*   **Mantenimiento:** Este diccionario en `mapa_conceptual_modulos.py` es un esfuerzo manual y colaborativo.
    *   **Cuándo actualizar:** Se debe actualizar siempre que:
        *   Se añada un nuevo módulo principal al proyecto.
        *   Se elimine un módulo principal existente.
        *   Se refactorice un módulo existente de tal manera que su propósito central, sus responsabilidades clave o sus interacciones principales con otros módulos cambien significativamente.
        La actualización de esta sección debe considerarse parte integral del conjunto de cambios (commit/pull request) que introduce la modificación en el código. No se recomienda un umbral numérico fijo (ej. "cada X cambios"), sino un juicio basado en el impacto del cambio en la arquitectura general.
    *   **Qué actualizar (Nivel de Detalle):** El foco debe estar en:
        *   La **responsabilidad principal** del módulo (ej. "¿Qué hace `collision_handler.py`?\").
        *   Sus **interacciones clave** con otros módulos principales (ej. \"`collision_handler.py` es utilizado por `juego.py` y opera sobre instancias de `entidad_base.py`\").
        No es necesario ni recomendable listar todas las funciones internas, clases secundarias o variables de un módulo. El objetivo es mantener una visión general conceptual, no un reflejo detallado del código fuente.

## Estructura del Proyecto

### Módulos Principales

#### Core
- `main.py`: Punto de entrada principal del juego
- `juego.py`: Clase principal que maneja el bucle del juego
- `settings.py`: Configuraciones globales del juego (ruta: `src/config/settings.py`)
- `config_logging.py`: Configuración del sistema de logging (ruta: `src/config/config_logging.py`)

#### Entidades
- `entidad_base.py`: Clase base para todas las entidades del juego
- `jugador.py`: Implementación del jugador
- `enemigo.py`: Implementación de enemigos
- `entorno.py`: Elementos del entorno del juego

#### Sistemas
- `collision_handler.py`: Sistema de detección y resolución de colisiones
- `gestor_eventos.py`: Sistema de manejo de eventos
- `gestor_estado.py`: Sistema de estados del juego
- `gestor_nivel.py`: Sistema de gestión de niveles
- `attack_profile_manager.py`: Sistema de perfiles de ataque

#### Renderizado
- `renderer.py`: Sistema de renderizado
- `hud.py`: Interfaz de usuario
- `camara.py`: Sistema de cámara

#### Utilidades
- `utils.py`: Funciones de utilidad comunes
- `asset_manager.py`: Gestión de recursos (imágenes, sonidos, etc.)

### Estructura de Carpetas
```
├── assets/              # Recursos del juego
│   ├── images/         # Imágenes y sprites
│   ├── sounds/         # Efectos de sonido y música
│   └── fonts/          # Fuentes
├── src/                # Código fuente
└── tests/             # Pruebas unitarias
```

## Instalación y Ejecución

1. **Requisitos**:
   - Python 3.8+
   - Pygame 2.0+
   - Dependencias listadas en requirements.txt

2. **Instalación**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Ejecución**:
   ```bash
   python main.py
   ```

# Sistema de Colisiones - Juego 2D
## Registro de Cambios y Problemas

### Problema Principal
El sistema de empuje de las gallinas (enemigos) al jugador presenta inconsistencias:
- ✅ Funciona correctamente en el eje X
- ❌ No funciona en el eje Y
- ✅ Se detectan colisiones correctamente
- ✅ Los logs muestran actividad en el eje X
- ❌ No hay registros de empuje en el eje Y

### Cambios Realizados

#### 1. Sistema de Empuje
- Modificación del factor de empuje:
  - Eje X: 1.5
  - Eje Y: 2.0 (aumentado para mayor efecto vertical)

#### 2. Correcciones en `collision_handler.py`
- Eliminación de condiciones `if empuje > 0` en el eje Y
- Eliminación de modificación inmediata del hitbox en colisiones Y
- Corrección de errores de tipeo (`rect_colision_obstulo` → `rect_colision_obstaculo`)
- Unificación del manejo de empuje entre ejes X e Y

### Problemas Pendientes

1. **Empuje Vertical**
   - El empuje en el eje Y sigue sin funcionar correctamente
   - Posible interferencia con la gravedad o salto del jugador

2. **Errores de Tipeo**
   - Se encontraron inconsistencias en nombres de variables
   - Necesario revisar todo el código para unificar nomenclatura

### Próximos Pasos

1. **Revisión de Logs**
   - Implementar logs más detallados para el eje Y
   - Verificar que los logs estén habilitados correctamente

2. **Pruebas de Colisión**
   - Crear casos de prueba específicos para colisiones verticales
   - Verificar interacción entre empuje y otros movimientos verticales

3. **Optimizaciones**
   - Revisar y optimizar el cálculo de empuje
   - Considerar ajustes en los factores de empuje según feedback

### Notas Técnicas

- Los logs están configurados a través de `settings.MODO_DEBUG_LOGS`
- El sistema usa `pygame.Rect` para hitboxes
- Las colisiones se manejan en dos fases:
  1. Resolución de solapamientos estáticos
  2. Aplicación de movimiento y colisiones dinámicas

### Configuración de Debug

Para habilitar los logs detallados:
```python
settings.MODO_DEBUG_LOGS = True
settings.LOG_CATEGORIAS["log_collision_handler"] = True
```

### Expectativas de Colaboración con Asistente IA (Tipo Cursor)

Para una colaboración más efectiva y eficiente con un asistente de IA avanzado (como el que estás usando ahora):

*   **Autonomía Basada en Documentación:** Se espera que el asistente IA lea, comprenda y siga proactivamente las directrices de los archivos `README.md`, `DEVELOPMENT_PROTOCOLS.md`, y cualquier otro documento de protocolo referenciado (como `docs/PERFORMANCE_OPTIMIZATION_PROTOCOLS.md`).
*   **Análisis Proactivo:** Ante una tarea general (ej. "analiza el rendimiento", "busca bugs"), el asistente debe tomar la iniciativa de consultar los documentos relevantes para guiar su análisis y flujo de trabajo sin necesidad de preguntas intermedias si la información ya está disponible.
*   **Ejecución de Comandos y Herramientas:** El asistente tiene la capacidad de proponer la ejecución de comandos de terminal (por ejemplo, para instalar dependencias, ejecutar scripts, o realizar verificaciones). Es importante entender que, dependiendo de la configuración del entorno del usuario, la aprobación y ejecución de estos comandos puede ser automática. El asistente debe tener esto en cuenta y asegurarse de que los comandos propuestos son seguros y directamente relevantes para la tarea en curso.
*   **Comunicación Post-Tarea:** Después de completar una tarea (ej. análisis de un archivo, implementación de una función, aplicación de una corrección), el asistente debe resumir brevemente:
    1.  **Qué hizo:** Una descripción concisa de la acción realizada.
    2.  **Cómo lo hizo/Protocolos Seguidos:** Referencia a los protocolos o guías específicas que siguió (ej. "según la sección X de `DEVELOPMENT_PROTOCOLS.md`", "aplicando el método Y de `PERFORMANCE_OPTIMIZATION_PROTOCOLS.md`").
    3.  **Hallazgos Clave/Observaciones:** Puntos más importantes detectados (ej. "se encontró una posible fuga de memoria en Z", "la función X es un cuello de botella").
    4.  **Siguientes Pasos Propuestos (si aplica):** Recomendaciones basadas en los hallazgos.
*   **Claridad en Instrucciones:** Si el asistente IA no sigue un protocolo o parece no entender una instrucción que se considera clara en la documentación, es una señal para revisar y mejorar la claridad de la documentación misma.

### Protocolo de Inicialización de Contexto para Asistentes IA

**CRÍTICO: Al iniciar una nueva conversación o reanudar después de un reinicio del IDE**, el asistente IA DEBE realizar la siguiente secuencia de inicialización de contexto:

1.  **Lectura Inmediata de Estado Actual:**
    *   `dev_notes.md`: Para entender el estado más reciente del desarrollo, problemas en curso, y contexto de la última sesión.
    *   `CHANGELOG.md`: Para conocer los últimos cambios implementados y su impacto.
    *   `TODO.md`: Para identificar las tareas pendientes y sus prioridades.

2.  **Revisión del Historial de Conversación Reciente y Detección de Interrupciones (Si aplica y está disponible):**
    *   Analizar los últimos intercambios de la conversación para capturar el contexto inmediato, tareas específicas en curso antes del reinicio, y cualquier instrucción o decisión reciente.
    *   **Prestar especial atención a si la conversación parece haberse interrumpido abruptamente mientras una tarea estaba en progreso.**
    *   Comparar la información del chat con los hallazgos de `dev_notes.md`, `CHANGELOG.md` y `TODO.md` para cruzar referencias y buscar consistencias o discrepancias.

3.  **Análisis, Síntesis y Formulación de Hipótesis (en caso de interrupción):**
    *   Identificar problemas críticos o bloqueantes basándose en todos los documentos y el chat.
    *   Determinar el contexto general de la última sesión de trabajo.
    *   **Si se detectó una posible interrupción abrupta de una tarea (del paso 2):**
        *   Formular una hipótesis clara sobre cuál era la tarea específica en curso.
        *   Analizar cómo esta hipótesis se alinea con el contenido de `dev_notes.md` y si los logs recientes (si fueron revisados como parte del contexto general) la respaldan o contradicen.
    *   Establecer las prioridades generales basadas en la documentación y la conversación.
    *   Verificar si es necesario actualizar `mapa_conceptual_modulos.py` u otros documentos clave.

4.  **Comunicación del Contexto y Confirmación de Tarea Interrumpida (si aplica):**
    *   Informar brevemente sobre los hallazgos clave de la lectura de los archivos de estado (`dev_notes.md`, `CHANGELOG.md`, `TODO.md`) y la revisión general del chat.
    *   Destacar cualquier problema crítico o discrepancia importante identificada entre las fuentes.
    *   **Si se formuló una hipótesis sobre una tarea interrumpida (del paso 3):**
        *   Presentar claramente la hipótesis: "Parece que antes de la interrupción estábamos trabajando en [describir la tarea hipotética]".
        *   Justificar brevemente la hipótesis: "Esto se basa en [mencionar el final del chat / la última acción clara] y parece [consistente/parcialmente consistente/no mencionado] en `dev_notes.md` porque [explicación breve]. Los logs recientes [mencionar si apoyan, contradicen o no son concluyentes, si fueron analizados]".
        *   **Preguntar explícitamente para confirmación:** "Corrígeme si me equivoco, pero ¿es esta la tarea que debemos retomar? ¿Hay algo más que debería considerar de la última sesión?"
    *   Proponer los siguientes pasos (o la continuación de la tarea confirmada) basados en las prioridades y la información recopilada. Sugerir actualizaciones a la documentación si es necesario.

5.  **Verificación Final de Inicialización:** Presentar el checklist actualizado al usuario (como se hace actualmente, pero reflejando el nuevo paso, similar al definido en `ai_overall_conduct_and_workflow_entry.mdc`).

Este protocolo es OBLIGATORIO y debe ejecutarse automáticamente al inicio de cada nueva conversación o después de un reinicio del IDE, incluso antes de recibir instrucciones específicas del usuario. El objetivo es mantener la continuidad del desarrollo y asegurar que todas las decisiones y acciones se tomen con pleno conocimiento del contexto actual del proyecto.

## Guía de Inicio Rápido y Análisis Inicial (Para Colaboradores y Asistente IA)

1.  **Comienza aquí (`README.md`):** Entiende el propósito general del proyecto, la estructura básica y las herramientas principales.
2.  **Consulta `DEVELOPMENT_PROTOCOLS.md`:** Este es el documento central que contiene todas las guías detalladas, reglas, protocolos de depuración, convenciones de código y procedimientos de contribución. Su lectura y comprensión son **obligatorias** antes de realizar cualquier trabajo. Puedes encontrarlo aquí: [`DEVELOPMENT_PROTOCOLS.md`](DEVELOPMENT_PROTOCOLS.md).
3.  **Estudia `mapa_conceptual_modulos.py`:** Este archivo es un glosario/mapa conceptual que describe los módulos principales, sus responsabilidades e interacciones. Es crucial para entender la arquitectura del código.
4.  **Explora la Estructura del Proyecto:** Familiarízate con la organización de las carpetas principales:
    *   `src/`: Contiene todo el código fuente del juego.
    *   `assets/`: Alberga todos los recursos gráficos, de sonido y datos.
    *   `docs/`: Contiene documentación adicional detallada, incluyendo:
        *   `PERFORMANCE_OPTIMIZATION_PROTOCOLS.md`: Guía para diagnosticar y solucionar problemas de rendimiento.
    *   `logs/`: (Si existe) Donde se guardan los archivos de log.
    *   `tests/`: (Si existe) Para pruebas unitarias y de integración.
5.  **Revisa `TODO.md` y `CHANGELOG.md`:** Para ponerte al día sobre el estado actual, las tareas pendientes, los bugs conocidos y el historial de cambios.
6.  **Inspecciona `dev_notes.md`:** Contiene notas de desarrollo importantes, problemas conocidos, ideas y recordatorios que pueden no estar formalizados en `TODO.md`. Es vital para entender el contexto de desarrollo actual y los desafíos recientes. **Mantenerlo actualizado y vigilado.**
7.  **Analiza `main.py` y el Núcleo del Juego:** Revisa `main.py` y los archivos principales en `src/core/` (especialmente `juego.py` o su equivalente como `game_loop.py`) para entender el flujo principal y la inicialización.
8.  **Revisa los Sistemas Clave:** Inspecciona los archivos en `src/sistemas/` para entender cómo se gestionan los eventos, estados, colisiones, niveles, etc.
9.  **Revisa los Módulos de Utilidades:** Inspecciona los archivos en `src/utils/` (como `asset_manager.py`, `config_loader.py`) para ver cómo se manejan las tareas comunes.

### Depuración y Diagnóstico de Problemas

Para investigar bugs o problemas de rendimiento, el proyecto cuenta con un sistema de logging configurable y herramientas de depuración. Es crucial utilizar estos sistemas de manera efectiva.

*   **Logging Selectivo:** La clave para un diagnóstico eficiente es activar solo los logs relevantes. Consulta la sección **"6.3. Debugging Selectivo con LOG_CATEGORIAS"** y **"6.4. Análisis de Logs de Sesión"** en [`DEVELOPMENT_PROTOCOLS.md`](DEVELOPMENT_PROTOCOLS.md) para aprender a controlar las categorías de log desde `src/config/settings.py`.
*   **Diagnóstico de Rendimiento:** Para problemas de optimización, además del logging selectivo (ver sección **"6.5. Aplicación al Diagnóstico de Rendimiento"** en [`DEVELOPMENT_PROTOCOLS.md`](DEVELOPMENT_PROTOCOLS.md)), consulta la guía detallada en [`docs/PERFORMANCE_OPTIMIZATION_PROTOCOLS.md`](docs/PERFORMANCE_OPTIMIZATION_PROTOCOLS.md).
*   **Otros Protocolos de Depuración:** Revisa la sección **"Protocolos de Depuración y Documentación"** en [`DEVELOPMENT_PROTOCOLS.md`](DEVELOPMENT_PROTOCOLS.md).