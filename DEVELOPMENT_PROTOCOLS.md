# Protocolos de Desarrollo y Colaboración

Este documento detalla las pautas, protocolos y convenciones para el desarrollo y la colaboración en el proyecto "Juego Pygame Modular". Es esencial para todos los colaboradores (humanos y asistentes IA) leer, comprender y adherirse a estas directrices.

**Nota Importante:** Este documento, al igual que el `README.md` principal y el `CHANGELOG.md`, es un **documento vivo**. Debe ser consultado regularmente y actualizado colaborativamente si los protocolos de desarrollo, las convenciones del proyecto o las mejores prácticas de colaboración evolucionan.

## 1. Introducción y Filosofía

Este documento es la guía central y **obligatoria** para cualquier desarrollo dentro del proyecto "Juego Pygame Modular". Su objetivo es asegurar la coherencia, calidad, mantenibilidad y facilitar la colaboración entre todos los desarrolladores (incluyendo asistentes IA).

**Principios Clave:**
*   **Claridad y Legibilidad:** El código debe ser fácil de entender.
*   **Modularidad:** Componentes bien definidos y débilmente acoplados.
*   **Consistencia:** Seguir las convenciones establecidas en este documento.
*   **Documentación:** Comentarios y documentación donde sea necesario (ver sección específica).
*   **Pruebas:** (Futuro) Fomentar la creación de pruebas para asegurar la estabilidad.

**Documentos Complementarios Importantes:**
*   **`README.md`**: Para la visión general del proyecto y la guía de inicio rápido.
*   **`mapa_conceptual_modulos.py`**: Para entender la arquitectura y responsabilidades de los módulos.
*   **`docs/PERFORMANCE_OPTIMIZATION_PROTOCOLS.md`**: Guía específica para el diagnóstico y optimización de problemas de rendimiento. Consultar este documento ante cualquier tarea relacionada con la mejora del rendimiento.

## Guía Esencial para Colaboradores (IA y Humanos)

Esta sección es fundamental para cualquier colaborador, ya sea una IA o un desarrollador humano. Su propósito es asegurar la coherencia, mantenibilidad y comprensión del proyecto a medida que evoluciona.

**Principios Clave:**

*   **Documentación Activa:** El `README.md` principal y el archivo `CHANGELOG.md` son documentos vivos. **Es obligatorio leerlos y entender su contenido (incluyendo el historial de cambios en `CHANGELOG.md`) antes de realizar cualquier cambio significativo y actualizarlos después de implementar dichos cambios.**
    *   El `README.md` debe reflejar el estado actual de la arquitectura, los sistemas principales y las convenciones de desarrollo.
    *   El `CHANGELOG.md` debe registrar todas las nuevas características, correcciones de errores importantes y cambios que rompan la compatibilidad, versionando adecuadamente el proyecto.
    *   **Nota para la colaboración con IA:** Al interactuar con asistentes IA, es crucial:
        *   **Proporcionar Contexto Inicial:** Guiar al asistente para que consulte activamente las secciones relevantes de esta documentación (este archivo, README principal, CHANGELOG, `mapa_conceptual_modulos.py`, `TODO.md`, plantillas de código, etc.) al inicio de una nueva sesión o al retomar el trabajo. Esto asegura que sus acciones estén alineadas con el estado y las convenciones del proyecto.
        *   **Fomentar la Autonomía Informada:** Una vez otorgado el permiso general para trabajar en el proyecto y con el contexto adecuado, permitir que el asistente utilice la información disponible (como `mapa_conceptual_modulos.py`) para acceder a archivos y realizar acciones relevantes sin requerir confirmación explícita para cada paso individual, siempre que esté dentro del alcance de la tarea actual. El objetivo es una colaboración fluida y eficiente.
        *   **Solicitar Resúmenes de Acciones:** Al finalizar tareas significativas o antes de devolver el control, pedir al asistente un resumen de las acciones realizadas, los archivos modificados y los cambios aplicados. Esto ayuda a mantener un seguimiento claro del progreso.
        *   **Verificar Adherencia a Convenciones:** Confirmar que el asistente sigue las estructuras de datos definidas, utiliza correctamente las variables globales de `settings.py` para configuraciones y control de depuración (ej. `LOG_CATEGORIAS`, `MODO_DEBUG_LOGS`), y comunica si está reutilizando código existente o introduciendo nuevos patrones. El asistente debe justificar sus decisiones si se desvía de las convenciones establecidas.
*   **Comunicación y Comprensión:** Antes de añadir nueva funcionalidad o modificar sistemas existentes, asegúrate de entender cómo encaja en el panorama general del proyecto.

### Ciclo de Depuración Reactivo y Proactivo

Cuando se enfrenta a un error reportado, un comportamiento inesperado del juego, o después de realizar cambios significativos (especialmente en la lógica central o el sistema de logging), el colaborador (IA o humano) debe seguir un ciclo de depuración que incluya:

1.  **Consulta de Logs (Post-Ejecución)**: Inmediatamente después de que el juego se ejecute (y falle, se cierre inesperadamente, o simplemente para verificar cambios), el primer paso es revisar los archivos de log relevantes de la última sesión. Esto incluye `main.log`, `juego.log`, y cualquier log específico de módulo (ej. `jugador.log`, `enemigo.log`, `entidad_base.log`) que pueda ser pertinente.
2.  **Análisis de Errores y Advertencias**: Buscar mensajes de `ERROR` o `CRITICAL` que puedan indicar la causa raíz de un problema. Los mensajes `WARNING` también pueden ofrecer pistas.
3.  **Evaluación de la Información del Log**:
    *   Si los logs proporcionan una traza de error clara (como un `AttributeError` o `ImportError`), proceder a investigar y corregir el código fuente directamente.
    *   Si los logs están "limpios" o no muestran la causa del problema, considerar si las categorías de log activas son suficientes.
4.  **Ajuste Iterativo de Logging (Si es Necesario)**: Si se necesita más detalle, identificar qué `LOG_CATEGORIAS` en `settings.py` podrían ser relevantes para la parte del código que se sospecha está causando el problema y activarlas. Luego, volver a ejecutar el juego para generar logs más detallados. Considerar también el uso temporal de `"log_debug_temporal": True` para aislar trazas muy específicas.
5.  **Formulación de Hipótesis y Acción**: Basándose en el análisis de los logs y el código, formular una hipótesis sobre la causa del problema y proponer una solución o un siguiente paso de depuración (ej. añadir más logging específico, inspeccionar variables, etc.).
6.  **Verificación**: Después de aplicar una corrección, ejecutar el juego nuevamente y revisar los logs para confirmar que el problema se ha resuelto y no se han introducido nuevos errores.
7.  **Limpieza de Configuración de Logging (Post-Depuración)**: Una vez que el problema se ha resuelto y verificado, es importante **revisar y desactivar** cualquier `LOG_CATEGORIAS` específica que se haya activado temporalmente en `settings.py` para la depuración. El objetivo es mantener la configuración de logging por defecto lo menos verbosa posible para el desarrollo normal y evitar una sobrecarga innecesaria de logs. Restaurar los niveles de log a su estado estándar ayuda a mantener la relevancia de los logs y puede contribuir a un mejor rendimiento del entorno de desarrollo al procesar la salida.

Este enfoque proactivo y reactivo hacia el análisis de logs es fundamental para una depuración eficiente y para mantener la estabilidad del proyecto.

### Comunicación y Feedback Post-Tarea (Especialmente para Colaboración con IA)

Al finalizar una tarea o un conjunto de cambios significativos, el colaborador (especialmente si es un asistente IA) debe:

1.  **Resumir las Acciones Realizadas:** Detallar los archivos modificados, las nuevas funcionalidades añadidas o los bugs corregidos, y los principales cambios lógicos implementados.
2.  **Informar sobre el Cumplimiento de Protocolos:** Confirmar explícitamente cómo se siguieron los protocolos de desarrollo relevantes durante la tarea. Esto incluye, pero no se limita a:
    *   **Logging y Depuración:** Explicar cómo se implementaron o ajustaron los logs y prints de depuración, asegurando que siguen las convenciones de categorías, niveles y control de activación (ej. `LOG_CATEGORIAS`, `MODO_DEBUG_LOGS`, `DEBUG_PRINT_VARIABLES`).
    *   **Estructura de Código y Reutilización:** Mencionar si se reutilizó código existente, se extendieron clases base, o si se introdujeron nuevos patrones (justificando estos últimos si es necesario).
    *   **Documentación y Archivos de Proyecto:** Indicar si se actualizaron documentos relevantes como `README.md`, `CHANGELOG.md`, `mapa_conceptual_modulos.py`, o `settings.py` según los cambios realizados.
    *   **Manejo de Errores y Casos Límite:** (Si aplica) Describir brevemente cómo se consideraron y manejaron los posibles errores o casos límite en la nueva lógica.
3.  **Justificar Desviaciones:** Si por alguna razón justificada fue necesario desviarse de un protocolo establecido, explicar el motivo y la alternativa implementada.

Este feedback proactivo ayuda a mantener la transparencia, facilita la revisión y asegura que el proyecto evoluciona de manera coherente y alineada con las directrices establecidas.

### Protocolo Específico para Colaboración con Jules (Agente de Codificación Experimental)

Para directrices detalladas sobre cómo interactuar y colaborar eficazmente con Jules, el agente de codificación experimental de Google, consultar el siguiente documento dedicado:

*   **[`docs/JULES_COLLABORATION_PROTOCOL.md`](docs/JULES_COLLABORATION_PROTOCOL.md)**

Este protocolo cubre la preparación del repositorio, formulación de prompts, revisión de planes y código, y el flujo de trabajo general al utilizar Jules.

**Reglas de Desarrollo:**

1.  **Antes de crear nueva funcionalidad o modificar código existente:**
    *   **Consultar `mapa_conceptual_modulos.py` y el `README.md` principal** para entender la arquitectura, responsabilidades de módulos existentes y cómo la nueva funcionalidad podría interactuar o integrarse.
    *   Verificar si existe un sistema similar o si la funcionalidad puede integrarse en uno existente.
    *   Verificar exhaustivamente si funcionalidades similares, clases base (ej. `EntidadBase`), o módulos existentes ya proveen parte o la totalidad de la lógica necesaria y pueden ser extendidos o reutilizados para evitar la duplicación de código y mantener la consistencia.
    *   Revisar `settings.py` para configuraciones existentes o relevantes.
    *   Seguir las convenciones de nombres y estructuras establecidas en este documento y el `README.md` principal.
    *   Priorizar el uso y extensión de los sistemas existentes sobre la creación de nuevos redundantes.
2.  **Al añadir nuevas características o realizar cambios significativos:**
    *   Documentar la nueva característica o cambio y su uso en este documento, el `README.md` principal (o `docs/PLANTILLAS_CODIGO.md` si aplica), actualizando o creando las secciones pertinentes.
    *   Actualizar `mapa_conceptual_modulos.py` para reflejar nuevos módulos, cambios en responsabilidades o interacciones importantes.
    *   Actualizar `CHANGELOG.md`.
    *   Actualizar `settings.py` si se introducen nuevas configuraciones globales o se modifican existentes.
    *   Mantener la consistencia con los patrones de diseño y la arquitectura de los sistemas existentes.
    *   Utilizar las funciones de utilidad de `utils.py` para tareas comunes siempre que sea posible.
3.  **Para cualquier nueva entidad o sistema que se cree:**
    *   Además de los puntos anteriores, verificar si necesita integrarse con el sistema de animaciones, configuraciones JSON, `gestor_estado.py`, `collision_handler.py`, `gestor_eventos.py`, o `asset_manager.py`.
    *   Seguir las convenciones de nombres y estructuras de directorios correspondientes.
4.  **Logging y Depuración:**
    *   Para el logging estructurado, utilizar el sistema definido en `config_logging.py` y las categorías en `settings.LOG_CATEGORIAS`. Emitir logs con `logger.extra={'categoria_log': 'mi_categoria'}`.
    *   Para prints de depuración temporales o específicos, utilizar el sistema de variables `DEBUG_PRINT_VARIABLES` definido en `settings.py` (ej. `if settings.DEBUG_PRINT_MI_PARTE: print(...)`). Esto permite un control centralizado.
5.  **Limpieza de Código Obsoleto Durante Modificaciones**:
    *   Durante tareas de refactorización, modificación o revisión de código, si se identifica código obsoleto, redundante o que ya no se utiliza (ej. antiguas variables de control de `print`s que han sido reemplazadas por el sistema de logging, funciones comentadas sin justificación clara para su futura reactivación), este debe ser eliminado para mantener la limpieza y claridad del código base.
    *   Si hay dudas sobre si un código es realmente obsoleto (por ejemplo, si una función comentada podría ser útil en el futuro o está pendiente de una revisión más profunda), se debe investigar su propósito original o consultar antes de su eliminación definitiva. El objetivo es evitar la acumulación de código "muerto" que dificulte la comprensión y el mantenimiento del proyecto.

6.  **Protocolo de Limpieza y Estructura del Código (Revisión Periódica y Post-Implementación Mayor)**:
    *   **Objetivo**: Mantener la calidad, legibilidad, y mantenibilidad del código a largo plazo. Este protocolo debe aplicarse periódicamente y especialmente después de la implementación de funcionalidades mayores o cambios significativos.
    *   **Pasos Clave**:
        1.  **Revisión Estructural General**: Analizar la organización de directorios y módulos. Asegurar que la estructura sigue siendo lógica y coherente con `mapa_conceptual_modulos.py`.
        2.  **Identificación de Código Reutilizable**: Buscar funciones o clases que puedan ser generalizadas y movidas a módulos de utilidad (ej., `src/utils/utils.py` o un archivo similar si ya existe una convención). Priorizar la reutilización para evitar duplicación.
        3.  **Uso de Constantes y Configuraciones Centralizadas**: Verificar que todas las constantes, "números mágicos", y configuraciones específicas del juego estén definidas en `src/config/settings.py` y se importen/utilicen desde allí. Evitar valores hardcodeados directamente en la lógica de los módulos.
        4.  **Gestión de `print()` y Depuración**:
            *   Reemplazar sentencias `print()` de depuración por el sistema de logging estructurado: `self.logger.debug("Mensaje", extra={"categoria_log": "categoria_apropiada"})`.
            *   Para prints de depuración que necesiten ser más permanentes pero controlables, utilizar el sistema de flags de depuración en `src/config/settings.py` (ej., `if settings.DEBUG_MODULO_ESPECIFICO: print("...")`).
            *   Eliminar `print()`s que ya no sean necesarios.
        5.  **Aplicación Consistente del Sistema de Logging**: Asegurar que todos los módulos utilicen `logging.getLogger("nombre_del_modulo")` y las categorías definidas en `settings.LOG_CATEGORIAS` de manera consistente.
        6.  **Docstrings y Comentarios**: Revisar y añadir/actualizar docstrings para módulos, clases y funciones importantes. Añadir comentarios donde la lógica no sea inmediatamente obvia. Eliminar comentarios obsoletos.
        7.  **Refactorizaciones Menores**: Considerar pequeñas refactorizaciones para mejorar la claridad, reducir la complejidad ciclomática, mejorar la cohesión de las clases/módulos y reducir el acoplamiento entre ellos.
        8.  **Verificación de Conexiones Inter-Módulos**: Confirmar que las interacciones entre módulos son claras, necesarias y siguen los patrones establecidos en la arquitectura del proyecto.
        9.  **Actualización de Documentación Post-Limpieza**: Una vez finalizada la limpieza, actualizar `mapa_conceptual_modulos.py`, `CHANGELOG.md`, y `dev_notes.md` para reflejar los cambios estructurales o lógicos realizados.
        10. **Revisión y Actualización del Mapa Conceptual (`mapa_conceptual_modulos.py`)**: Después de aplicar cambios de limpieza o refactorización a un módulo (o grupo de módulos), revisar `mapa_conceptual_modulos.py` para asegurar que sigue reflejando con precisión las responsabilidades, componentes clave e interacciones del módulo modificado. Actualizar según sea necesario para mantener el mapa como un documento vivo y fiel a la estructura actual del código.
        11. **Verificación Rápida de Ejecución (Post-Limpieza de Módulo/Substancial)**:
            *   Después de aplicar cambios de limpieza significativos a un módulo o a varios, proponer y (si el USER lo aprueba) ejecutar el juego (`python main.py`) por un corto periodo (ej. 10-15 segundos) para una verificación rápida.
            *   Observar la consola en busca de errores inmediatos o comportamientos anómalos evidentes.
            *   Este paso ayuda a capturar regresiones o problemas introducidos durante la limpieza de forma temprana.
            *   Si se detecta un problema, se debe pausar la limpieza y abordar el nuevo error antes de continuar.

**Mantenimiento de Continuidad de Sesión:**

*   **Propósito:** Para facilitar la transición entre sesiones de trabajo o la colaboración entre diferentes personas (o asistentes IA), se recomienda mantener un breve registro del estado actual del desarrollo.
*   **Archivo Sugerido:** Crear y mantener un archivo simple como `dev_notes.md` o `session_log.txt` en la raíz del proyecto o dentro de un directorio de utilidad (ej. `.cursor/` o `docs/`).
*   **Contenido:** Este archivo debería incluir:
    *   Un resumen de las últimas tareas realizadas.
    *   Bugs o problemas que se estaban investigando y su estado.
    *   Ideas pendientes o próximos pasos planificados.
    *   Cualquier configuración temporal de depuración que se haya activado.
*   **Actualización:** Actualizar este archivo al final de cada sesión de trabajo significativa.

#### Ciclo de Vida y Transición de `dev_notes.md` a `CHANGELOG.md`

Para mantener la claridad en `dev_notes.md` y asegurar que `CHANGELOG.md` capture los hitos relevantes, se sigue el siguiente proceso:

1.  **Registro Continuo en `dev_notes.md`**:
    *   Durante el desarrollo activo, `dev_notes.md` sirve como un borrador de trabajo. Se anotan tareas en curso, bugs identificados, ideas, decisiones de diseño, y el estado de las investigaciones (ej. "Investigando bug X - parece relacionado con Y").
    *   Los elementos pueden marcarse informalmente (ej., con `[PENDIENTE]`, `[EN PROGRESO]`, `[RESUELTO - PENDIENTE DE PRUEBA]`, `[SOLUCIONADO TEMPORALMENTE]`).

2.  **Marcado de Elementos Resueltos en `dev_notes.md`**:
    *   Cuando un bug específico o una subtarea listada en `dev_notes.md` se considera **completamente resuelta y verificada** (idealmente a través de pruebas o ejecución del juego), se marcará explícitamente como `[RESUELTO Y VERIFICADO]` o similar directamente en `dev_notes.md`.
    *   Se puede añadir una breve nota sobre la solución si es concisa.

3.  **Consolidación y Actualización del `CHANGELOG.md`**:
    *   Al alcanzar un hito de desarrollo significativo (ej. finalización de una característica mayor, corrección de varios bugs importantes, preparación para una "versión" interna) o al final de una sesión de trabajo extensa, se revisará `dev_notes.md`.
    *   Los elementos marcados como `[RESUELTO Y VERIFICADO]` (o equivalentes que indiquen finalización y fiabilidad) se agruparán y se redactará una entrada cohesiva para `CHANGELOG.md`.
    *   La entrada en `CHANGELOG.md` debe seguir el formato establecido, ser clara, y enfocarse en el impacto para el usuario o el proyecto (ej. "Corregido bug X que causaba Y", "Implementada nueva característica Z que permite A").

4.  **Limpieza de `dev_notes.md`**:
    *   Una vez que la información de los elementos resueltos y verificados ha sido transferida satisfactoriamente a `CHANGELOG.md`, las entradas correspondientes en `dev_notes.md` pueden ser:
        *   **Eliminadas**: Si la información ya está completamente capturada en `CHANGELOG.md` y no se necesita para contexto inmediato.
        *   **Archivadas**: Si contienen detalles de la investigación o del proceso de solución que podrían ser útiles para referencia futura pero no son adecuados para `CHANGELOG.md`. Esto podría implicar moverlas a una sección de "Archivo" dentro de `dev_notes.md` o a un documento separado de notas técnicas detalladas si el proyecto lo requiriese. La preferencia es mantener `dev_notes.md` enfocado en el trabajo *actual y reciente*.
    *   El objetivo es que `dev_notes.md` se mantenga relevante para el estado actual del desarrollo y no se sobrecargue con historial ya documentado oficialmente.

5.  **Actualización de `TODO.md`**:
    *   Paralelamente, las tareas correspondientes en `TODO.md` también deben marcarse como completadas o actualizarse según corresponda.

## Guía de Desarrollo

### Sistemas y sus Interrelaciones

1. **Sistema de Logging (Refactorizado V. 0.2.0)**:
   - **Filosofía**: El sistema de logging está diseñado para ser centralizado, configurable y ofrecer control granular sobre los mensajes, facilitando tanto el desarrollo como la depuración.
     - **Revisión Activa y Verificación Autónoma**: Es crucial no solo configurar el logging, sino también **revisar activamente** la configuración actual en `settings.py` (incluyendo el estado de `MODO_DEBUG_LOGS`, las `LOG_CATEGORIAS` y la configuración de filtros como `LOG_DUPLICATE_MESSAGE_TIMEDELTA_MS`) antes de asumir un comportamiento específico. Tras una ejecución, especialmente si se están depurando problemas o se han realizado cambios en el logging, se debe **verificar autónomamente los archivos de log generados** para confirmar que los mensajes esperados se están registrando correctamente y que los filtros funcionan según lo previsto. Esta verificación proactiva es esencial para un diagnóstico eficiente.
   - **Configuración Central**: Toda la configuración del sistema de logging reside en `config_logging.py`. Esto incluye la definición de formateadores (para consola y archivos), handlers (stream para consola con `colorlog`, y `RotatingFileHandler` para archivos), y filtros (`CategoryFilter`, `DuplicateFilter`).
   - **Obtención de Loggers**: Cada módulo debe obtener su logger específico usando `logger = logging.getLogger("nombre_del_modulo")`. Por ejemplo, en `jugador.py` se usa `logging.getLogger("jugador")`. Esto permite que los logs se asocien correctamente con su origen.

   - **Momento Crítico: `setup_logging()` Antes de Cualquier Uso del Logger**:
     - Es absolutamente crucial que la función `config_logging.setup_logging()` se ejecute **antes** de que cualquier módulo del proyecto intente obtener y usar un logger (ej. `logger = logging.getLogger("mi_modulo")` seguido de `logger.info(...)`).
     - Si un módulo se importa y define un logger a nivel de módulo (es decir, fuera de cualquier función o clase, en el ámbito global del módulo) y luego intenta usar ese logger inmediatamente a ese mismo nivel global, estos mensajes de log se emitirán **antes** de que `setup_logging()` haya configurado los handlers (como el `StreamHandler` para la consola o los `FileHandler` para archivos), formatos y filtros.
     - **Consecuencia**: Los mensajes emitidos antes de `setup_logging()` pueden no aparecer en la consola o en los archivos de log esperados, o pueden usar una configuración de logging por defecto de Python que no se alinea con la del proyecto (ej. niveles diferentes, sin colores, sin filtros de categoría).
     - **Práctica Recomendada**: 
         1. Asegurar que `config_logging.setup_logging()` se llame lo más temprano posible en el punto de entrada principal de la aplicación (ej. al inicio de `main.py`, antes de la importación de módulos del juego que usen logging).
         2. Evitar realizar llamadas de logging (ej. `logger.info()`, `logger.debug()`) a nivel global de un módulo durante su importación. Si se define `logger = logging.getLogger("mi_modulo")` a nivel global, la primera *llamada* a `logger.info()` (o similar) debería ocurrir dentro de una función o método que se ejecute después de que `setup_logging()` haya completado su trabajo.

   - **Logs por Módulo y Sesión**: 
     - Los logs de los módulos listados en `settings.MODULOS_CON_LOG_PROPIO` se guardan en archivos individuales dentro de una carpeta de sesión (ej. `logs/YYYY-MM-DD_HH-MM-SS/nombre_del_modulo.log`).
     - Los logs de módulos no listados allí (o si el handler específico falla) van a un archivo `general.log` dentro de la misma carpeta de sesión.
   - **Categorías de Log y Control de Activación**:
     - Las categorías de log (ej. `"log_jugador_mov"`, `"log_assets"`) se definen y activan/desactivan en el diccionario `settings.LOG_CATEGORIAS`.
     - Para asignar una categoría a un mensaje, se usa el parámetro `extra` en la llamada al logger: `logger.debug("Mensaje", extra={"categoria_log": "nombre_categoria"})`.
     - El `CategoryFilter` utiliza `settings.LOG_CATEGORIAS` y `settings.MODO_DEBUG_LOGS` para decidir si un mensaje de una categoría particular debe procesarse.
     - `settings.MODO_DEBUG_LOGS = True` habilita un nivel de log más verboso (DEBUG), mientras que `False` usa un nivel estándar (INFO).
   - **Filtro de Duplicados (`DuplicateFilter`)**:
     - Suprime automáticamente mensajes de log idénticos que ocurren repetidamente dentro de un breve intervalo de tiempo (configurable mediante `settings.LOG_DUPLICATE_MESSAGE_TIMEDELTA_MS`).
     - Se puede omitir este filtro para un mensaje específico añadiendo `"skip_duplicate_check": True` al diccionario `extra`: `logger.info("Mensaje importante que no debe filtrarse", extra={"categoria_log": "log_general", "skip_duplicate_check": True})`.
   - **Niveles de Log Estándar**: DEBUG, INFO, WARNING, ERROR, CRITICAL.
   - **Ejemplo de Uso Completo**:
     ```python
     # En un módulo, por ejemplo, mi_modulo.py
     import logging
     import settings

     logger = logging.getLogger("mi_modulo") # Obtener logger específico del módulo

     def alguna_funcion():
         # Este mensaje solo se registrará si MODO_DEBUG_LOGS es True Y LOG_CATEGORIAS["categoria_especifica"] es True
         logger.debug("Este es un mensaje de debug detallado.", extra={"categoria_log": "categoria_especifica"})
         
         logger.info("Información general de la función.", extra={"categoria_log": "log_general"})
         
         if error_condicion:
             logger.error("Ocurrió un error.", extra={"categoria_log": "log_errores"})

     # En settings.py, asegúrate de tener:
     # LOG_CATEGORIAS = {
     #     "categoria_especifica": True, 
     #     "log_general": True,
     #     "log_errores": True,
     #     # ...otras categorías...
     # }
     # MODULOS_CON_LOG_PROPIO = [..., "mi_modulo", ...]
     ```

   - **Consistencia en Nombres de Categorías de Log:**
     - Al definir y utilizar categorías de log (manejadas en `src/config/settings.py` bajo `LOG_CATEGORIAS` y consumidas por `CategoryFilter` en `src/config/config_logging.py`), es crucial asegurar la consistencia absoluta en los nombres de las claves.
     - Un error común puede ser una discrepancia entre el nombre de la clave definido en `settings.LOG_CATEGORIAS` (ej: `"log_mi_modulo_especifico"`) y el nombre utilizado en el código al registrar un mensaje con `extra={"categoria_log": "log_modulo_especifico"}` (nótese la falta del `_mi_` en el segundo caso).
     - Si la clave proporcionada en `extra` no coincide exactamente con una clave existente en `settings.LOG_CATEGORIAS`, el `CategoryFilter` (según su implementación actual) podría bloquear el mensaje silenciosamente, incluso si la intención era que la categoría estuviera activa.
     - **Recomendación:** Al añadir o modificar categorías de log, verifica dos veces que la cadena de texto de la clave sea idéntica en `settings.py` y en todas sus usos dentro del código. Considera usar constantes para los nombres de las categorías si el proyecto crece mucho, aunque por ahora la verificación manual es suficiente.

   - **Prints de Depuración Controlados por Variables Globales (Debug Prints)**:
     - **Propósito**: Además del sistema de logging formal, el proyecto utiliza un mecanismo simple para activar/desactivar `print()`s específicos para depuración rápida y localizada sin necesidad de modificar constantemente el código o la configuración del logger. Esto es útil para trazas temporales mientras se desarrolla o depura una funcionalidad concreta.
     - **Distinción Clave**: Es importante distinguir estos `DEBUG_PRINT_*` del `MODO_DEBUG_LOGS`. 
       - `MODO_DEBUG_LOGS = True` activa el sistema de logging formal a un nivel más verboso (DEBUG) y permite que las `LOG_CATEGORIAS` se respeten para generar archivos de log detallados. Es para un análisis más profundo y persistente.
       - Las variables `DEBUG_PRINT_NOMBRE_AREA = True` activan `print()` directos en la consola para un feedback inmediato y temporal sobre un aspecto muy específico del código. Son más invasivos y deben usarse con moderación y siempre desactivarse (`False`) tras resolver el problema.
     - **Patrón de Uso**:
       1.  **Definición de la Variable de Control**: En `src/config/settings.py`, se define una variable global booleana. El nombre de esta variable debe ser descriptivo del área o funcionalidad que controlan sus prints.
           ```python
           # Ejemplo en src/config/settings.py
           DEBUG_PRINT_GESTION_DANO = True  # Activa prints relacionados con la gestión de daño
           DEBUG_PRINT_CALCULO_FISICAS = False # Desactiva prints de cálculos de físicas
           DEBUG_PRINT_ENTORNO = True # Activa/desactiva prints generales de la creación y estado de Obstaculos
           DEBUG_PRINT_ENTORNO_ANIM = False # Activa/desactiva prints de cada frame de animación de Obstaculos (muy verboso)
           DEBUG_PRINT_JUGADOR_ATAQUE_CALCULO = False # Activa/desactiva prints del cálculo del hitbox de ataque del jugador
           DEBUG_PRINT_JUGADOR_RECIBIR_DANO_INFO = False # Activa/desactiva prints cuando el jugador recibe daño
           ```
       2.  **Uso Condicional en el Código**: En el módulo correspondiente, las sentencias `print()` destinadas a esta depuración se envuelven en una condición que verifica el estado de su variable de control en `settings`.
           ```python
           # Ejemplo en algun archivo .py
           import settings # O from src.config import settings

           def alguna_funcion_con_dano(dano):
               if settings.DEBUG_PRINT_GESTION_DANO:
                   print(f"DEBUG_AREA_DANO: Aplicando daño: {dano}")
               # ... lógica de la función ...

           def simular_fisica(objeto):
               if settings.DEBUG_PRINT_CALCULO_FISICAS:
                   print(f"DEBUG_FISICAS: Calculando para {objeto}")
               # ... lógica de la función ...
           ```
     - **Ventajas**:
       - Permite activar o desactivar grupos de `print`s de forma muy rápida y centralizada (`settings.py`) sin tocar el código fuente donde se usan.
       - Evita la necesidad de comentar/descomentar `print`s manualmente.
       - Mantiene la consola más limpia cuando no se necesitan estos `print`s específicos, separándolos del flujo de logging más formal.
     - **Convención**: Los `print`s controlados de esta manera deberían, idealmente, incluir un prefijo distintivo (ej. `DEBUG_MI_AREA: ...`) para identificarlos fácilmente en la salida de la consola.

2. **Sistema de Animaciones**:
   - Ubicación: `animaciones/` (conceptual, código en entidades y asset_manager)
   - Cualquier entidad con animaciones debe:
     - Definir sus estados en `settings.py` bajo `ANIMACIONES_[TIPO_ENTIDAD]`
     - Usar `asset_manager.py` para cargar sprites
     - Implementar `actualizar_animacion()` y `dibujar_animacion()`
   - Formato de nombres de animaciones: `[tipo_entidad]_[estado]_[frame].png`
   - Ejemplo:
     ```python
     # En settings.py
     ANIMACIONES_ENTIDAD = {
         "idle": {"frames": 4, "duracion": 0.5},
         "run": {"frames": 6, "duracion": 0.4},
         "action": {"frames": 3, "duracion": 0.2}
     }
     ```

3. **Sistema de Perfiles y Configuraciones**:
   - Ubicación: `config/` (archivos JSON), lógica en `AttackProfileManager` y entidades.
   - Cualquier entidad con configuración específica debe:
     - Tener un perfil en `config_[tipo].json` (ej. `config_ataque.json`)
     - Implementar las animaciones correspondientes si aplica
     - Usar el gestor de perfiles correspondiente si existe (ej. `AttackProfileManager`)
   - Formato de nombres: `[tipo_entidad]_[variante].json` o `config_[area].json`
   - Ejemplo:
     ```json
     // En config_ataque.json
     {
         "espada_predeterminada": {
             "tipo": "melee",
             "dano_base": 10,
             // ... otros parámetros ...
         }
     }
     ```

4. **Sistema de Estados**:
   - Ubicación: Lógica en `gestor_estado.py` y en cada entidad que maneje estados.
   - Cualquier entidad con estados debe:
     - Definir sus estados en una enumeración (Enum) si son complejos.
     - Implementar `cambiar_estado()` o lógica similar.
     - Usar `gestor_estado.py` para transiciones si se manejan estados globales del juego.
   - Ejemplo:
     ```python
     from enum import Enum
     class EstadosJugador(Enum):
         IDLE = "idle"
         CORRIENDO = "corriendo"
         ATACANDO = "atacando"
     ```

5. **Sistema de Colisiones**:
   - Ubicación: `sistemas/collision_handler.py`
   - Cualquier entidad colisionable debe:
     - Definir su hitbox (dimensiones y offset respecto al `rect` principal) en `settings.py` o en su inicialización.
     - Implementar `obtener_hitbox()` o tener un atributo `hitbox` (un `pygame.Rect`).
     - Ser pasada al `CollisionHandler` junto con los obstáculos.
   - Tipos de colisión (conceptuales, la implementación puede variar):
     - `COLISION_ESTATICA`: Para objetos estáticos.
     - `COLISION_DINAMICA`: Para entidades móviles.
     - `COLISION_ACCION`: Para áreas de acción/interacción (ej. hitbox de ataque).

6. **Sistema de Eventos**:
   - Ubicación: `sistemas/gestor_eventos.py` (para eventos de Pygame y personalizados).
   - Cualquier sistema que necesite comunicación basada en eventos puede:
     - Definir sus tipos de eventos (si son personalizados) en `settings.py` o localmente.
     - Usar `pygame.event.post(evento_personalizado)` para emitir.
     - El `GestorEventos` procesa los eventos de Pygame.

7. **Sistema de Assets**:
   - Ubicación: `utils/asset_manager.py` (lógica), `assets/` (archivos).
   - Estructura de carpetas en `assets/`:
     ```
     assets/
     ├── images/
     │   ├── entidades/
     │   │   ├── [tipo_entidad]/
     │   │   └── [otro_tipo]/
     │   ├── objetos/
     │   ├── efectos/
     │   └── ui/
     ├── sounds/
     │   ├── efectos/
     │   └── musica/
     └── fonts/
     ```
   - Convenciones de nombres:
     - Imágenes: `[tipo]_[estado]_[frame].png` (o similar, ser consistente).
     - Sonidos: `[tipo]_[efecto].wav` (o `.ogg`).
     - Fuentes: `[nombre]_[estilo].ttf`.

### Manejo de Variables Globales y Configuraciones

1. **Variables Globales**:
   - Todas las variables globales de configuración deben estar en `src/config/settings.py`.
   - Las variables se organizan por categorías con comentarios claros.
   - Formato: `NOMBRE_VARIABLE = valor  # Descripción breve`.
   - Ejemplo:
     ```python
     # --- Configuración del Jugador ---
     VIDA_MAXIMA_JUGADOR = 100  # Vida inicial del jugador
     VELOCIDAD_JUGADOR = 180    # Píxeles por segundo
     ```

2. **Nuevas Configuraciones**:
   - Añadir nuevas variables en la categoría correspondiente en `settings.py`.
   - Si no existe una categoría apropiada, crear una nueva con un comentario descriptivo.
   - Mantener el formato de nombres en MAYÚSCULAS_CON_GUIONES_BAJOS.
   - Documentar el propósito y unidades de la variable.

3. **Perfiles de Configuración (Archivos JSON)**:
   - Configuraciones más complejas o específicas de entidades pueden ir en archivos JSON en la carpeta `src/config/data/` (o similar, ej. `src/config/data/perfiles_ataque/`).
   - Ejemplo: `config_ataque.json` para perfiles de ataque.
   - Usar funciones de utilidad (posiblemente en `utils.py` o `AssetManager`) para cargar estos archivos JSON.

4. **Constantes por Módulo**:
   - Si un módulo necesita constantes que no son de configuración global (es decir, no se espera que el usuario/desarrollador las modifique desde `settings.py`), definirlas al inicio del archivo del módulo.
   - Documentar con comentarios el propósito de cada constante.
   - Mantener consistencia con el estilo de nombres (`MAYUSCULAS_CON_GUIONES_BAJOS`).

### Añadir Nuevas Funcionalidades

1. **Nuevas Entidades**:
   - Considerar heredar de `src/entidades/entidad_base.py`.
   - Implementar métodos requeridos (ej. `actualizar`, `dibujar`).
   - Registrar en el sistema de colisiones si es necesario.
   - Añadir a la lógica de carga de niveles o instanciación en `Juego` o `GestorNivel`.

2. **Nuevas Utilidades**:
   - Añadir funciones en `src/utils/utils.py` o crear un nuevo módulo en `src/utils/` si la utilidad es extensa.
   - Documentar con docstrings claros.
   - Incluir tipos con type hints.

3. **Nuevos Sistemas**:
   - Crear un nuevo módulo en la carpeta `src/sistemas/`.
   - Implementar una interfaz clara (clases, funciones públicas).
   - Integrar con el bucle principal en `src/core/juego.py` si es necesario (ej. llamando a su método `actualizar` o `dibujar`).
   - Actualizar `mapa_conceptual_modulos.py`.

### Convenciones de Código

1. **Nombres**:
   - Clases: `PascalCase` (ej. `Jugador`, `CollisionHandler`).
   - Funciones y variables: `snake_case` (ej. `actualizar_movimiento`, `velocidad_actual`).
   - Constantes (globales en `settings.py` o locales en módulos): `MAYUSCULAS_CON_GUIONES_BAJOS` (ej. `VELOCIDAD_MAXIMA`, `COLOR_ROJO`).
   - Nombres de archivo: `snake_case.py` (ej. `gestor_eventos.py`).

2. **Documentación**:
   - **Docstrings**: Usar docstrings para todas las clases, métodos públicos y funciones. Describir el propósito, argumentos, y lo que retorna (si aplica).
     ```python
     def mi_funcion(param1: int, param2: str) -> bool:
         """
         Descripción breve de lo que hace la función.

         Args:
             param1: Descripción del primer parámetro.
             param2: Descripción del segundo parámetro.

         Returns:
             Descripción de lo que retorna.
         """
         # ... código ...
     ```
   - **Type Hints**: Usar type hints para todos los parámetros de funciones/métodos y para los valores de retorno.
   - **Comentarios**: Usar comentarios (`#`) para explicar lógica compleja, decisiones de diseño importantes, o advertencias (`# TODO:`, `# FIXME:`).

3. **Logging**:
   - Usar el sistema de logging configurado en `config_logging.py` y `settings.py`.
   - Emitir logs con niveles apropiados (DEBUG, INFO, WARNING, ERROR, CRITICAL).
   - Proporcionar mensajes descriptivos y, cuando sea relevante, incluir la categoría de log en `extra`.

4. **Estructura de Archivos**:
   - **Imports**: Agrupar imports: 1) Librerías estándar de Python, 2) Librerías de terceros (Pygame), 3) Módulos propios del proyecto. Separar grupos con una línea en blanco.
     ```python
     import os
     import math
     from enum import Enum

     import pygame

     from src.config import settings
     from src.utils.asset_manager import AssetManager
     from .entidad_base import EntidadBase # Ejemplo de import relativo dentro del mismo paquete
     ```
   - **Definición de Constantes y Loggers**: Al inicio del archivo, después de los imports.
   - **Definición de Clases y Funciones**: Organizadas lógicamente.

### Debugging

1. **Herramientas de Debug**:
   - **Sistema de Logging Configurable**: Controlado principalmente por `MODO_DEBUG_LOGS` y `LOG_CATEGORIAS` en `settings.py`. Permite un registro detallado de eventos en archivos.
   - **Prints de Depuración Específicos**: Controlados por variables `DEBUG_PRINT_*` en `settings.py`. Para salida directa a consola de información puntual. Usar el patrón `if hasattr(settings, 'DEBUG_PRINT_AREA_ESPECIFICA') and settings.DEBUG_PRINT_AREA_ESPECIFICA: print(...)`.
   - **Visualización de Hitboxes**: Activada mediante `DEBUG_VER_HITBOXES = True` en `settings.py`. Dibuja los hitboxes de colisión, ataque, etc., directamente en pantalla. Es una herramienta visual independiente de los logs o prints de consola.

2. **Modo Debug (Activación General)**:
   - Para una sesión de depuración completa, generalmente se activan varias de estas herramientas según sea necesario desde `settings.py`.
   - **Logging Detallado**: `MODO_DEBUG_LOGS = True` y habilitar las `LOG_CATEGORIAS` relevantes.
   - **Visualización en Pantalla**: `DEBUG_VER_HITBOXES = True` (y otras variables visuales si existen).
   - **Prints Específicos**: Activar las variables `DEBUG_PRINT_AREA_ESPECIFICA = True` que correspondan al problema bajo investigación.
   - El objetivo es obtener información adicional y visualizaciones que ayuden a diagnosticar problemas.

## Protocolos de Depuración y Documentación

Esta sección establece pautas claras sobre cómo proceder cuando se encuentran bugs o problemas, cómo implementar soluciones, y cómo documentar adecuadamente todo el proceso.

### Flujo de Trabajo para la Depuración

1.  **Identificación del Problema**:
    *   Documentar el bug en `TODO.md` con una descripción clara del problema, pasos para reproducirlo y comportamiento esperado vs. actual. (Ver plantilla más abajo).
    *   Asignar una prioridad al problema (Crítica, Alta, Media, Baja).
    *   Recopilar logs relevantes si están disponibles (de la carpeta `logs/` correspondiente a la sesión donde ocurrió el error).

2.  **Activación del Modo Depuración**:
    *   Antes de iniciar la depuración, activar las variables de depuración necesarias en `src/config/settings.py`:
        *   Establecer `MODO_DEBUG_LOGS = True` para habilitar el sistema de logging a nivel DEBUG.
        *   Activar las categorías de log relevantes en `LOG_CATEGORIAS` (ej. `"log_collision_handler": True`).
        *   Activar las variables `DEBUG_PRINT_*` específicas para el área problemática (ej. `DEBUG_PRINT_JUGADOR_MOV_DEBUG = True`).
        *   Activar `DEBUG_VER_HITBOXES = True` si el problema puede estar relacionado con colisiones o áreas.

3.  **Proceso de Depuración**:
    *   Ejecutar el juego (`python main.py`) y reproducir el problema con el logging y las ayudas visuales activadas.
    *   **Análisis de Logs y Salida de Consola**:
        *   Revisar los logs generados en la carpeta `logs/` (y subcarpetas de sesión) para entender el flujo de ejecución, el estado de las variables y la secuencia de eventos que llevaron al error.
        *   Observar la salida de la consola en busca de mensajes de error directos de Python, y los mensajes de los `DEBUG_PRINT_*` activados.
    *   **Identificación del Foco del Problema**: Basándose en los errores o comportamientos anómalos, determinar qué módulos, clases o funciones son los más probables causantes del problema. Consultar `mapa_conceptual_modulos.py` puede ayudar a entender las interacciones.
    *   **Activación Selectiva de Ayudas**: Si el problema es complejo, considerar desactivar logs o prints menos relevantes y activar otros más específicos para el área sospechosa.
    *   Usar puntos de interrupción (breakpoints) con un depurador de Python (como el integrado en VSCode o PDB) si es necesario para un análisis paso a paso.
    *   Identificar la causa raíz del problema.

4.  **Implementación de la Solución**:
    *   Implementar la solución siguiendo las convenciones de código establecidas en este documento.
    *   **IMPORTANTE**: Proteger cualquier nuevo print de depuración temporal que se añada con una variable de control `DEBUG_PRINT_*` en `settings.py`.
    *   Mantener los cambios enfocados en resolver el problema específico.

5.  **Verificación**:
    *   Probar que la solución funciona correctamente, reproduciendo los pasos que antes causaban el bug.
    *   Verificar que no se han introducido nuevos problemas (pruebas de regresión informales en áreas relacionadas).
    *   Ejecutar una sesión de prueba completa de las funcionalidades afectadas.

6.  **Desactivación del Modo Depuración**:
    *   **CRUCIAL**: Después de verificar la solución y ANTES de confirmar los cambios (commit):
        *   Establecer `MODO_DEBUG_LOGS = False` en `settings.py`.
        *   Desactivar (`False`) todas las variables `DEBUG_PRINT_*` que se activaron para la depuración.
        *   Desactivar `DEBUG_VER_HITBOXES = False` si se activó.
        *   Asegurarse de que los prints de depuración no se ejecutarán en modo normal.

7.  **Documentación de los Cambios (POST-VERIFICACIÓN)**:
    *   **Esperar la confirmación del funcionamiento correcto antes de actualizar la documentación.**
    *   Solo después de verificar que la solución funciona y que los modos de depuración están desactivados:
        *   **`CHANGELOG.md`**: Añadir una entrada detallando el bug corregido (con referencia al ID del `TODO.md` si aplica), la solución implementada, y si es relevante, un breve resumen del proceso de diagnóstico o los razonamientos clave.
        *   **`TODO.md`**: Marcar el bug como resuelto (`[x]`) y añadir cualquier tarea de seguimiento.
        *   **`dev_notes.md` (o similar, opcional)**: Anotar la solución y cualquier lección aprendida durante el proceso de depuración si fue particularmente complejo o revelador.
        *   Si es necesario, actualizar secciones de este `DEVELOPMENT_PROTOCOLS.md` o el `README.md` principal para reflejar cambios en el comportamiento, uso, o nuevas convenciones establecidas.

### Pruebas y Verificación de Funcionalidad

Después de implementar una corrección de bug o una nueva característica, es crucial verificar que funciona como se espera y que no ha introducido regresiones.

1.  **Pruebas Iniciales (Desarrollo)**:
    *   Ejecutar `python main.py` para realizar pruebas manuales y visuales del área afectada.
    *   Utilizar las herramientas de depuración (visualización de hitboxes, logs específicos, prints condicionales) según sea necesario *durante* el desarrollo para confirmar el comportamiento interno.

2.  **Ciclo Iterativo de Corrección y Prueba**:
    *   Si las pruebas revelan problemas, volver al "Flujo de Trabajo para la Depuración" (activando logs/prints, analizando el código) para identificar y corregir la nueva causa.
    *   Repetir la ejecución de `main.py` y las pruebas específicas hasta que la funcionalidad se verifique como correcta.
    *   **Rol de la IA en las Pruebas:** El desarrollador humano ejecuta el juego (ej. `python main.py`). El asistente IA **no puede ejecutar el juego directamente**. Sin embargo, la IA **puede proponer el comando de ejecución** (que el usuario luego aprueba y corre). La **salida de la consola** de dicha ejecución se muestra automáticamente a la IA, permitiéndole analizarla junto con los archivos de log y el feedback descriptivo del usuario sobre el comportamiento visual. La IA puede así asistir en los ciclos de depuración y corrección. (Ver también la sección "Interacción con Asistentes IA para Ejecución y Pruebas" en `README.md` para un flujo de trabajo detallado).

3.  **Pruebas de Regresión (Recomendado)**:
    *   Antes de finalizar un conjunto de cambios importantes, realizar pruebas más amplias para asegurar que otras áreas del juego no se han visto afectadas negativamente.
    *   (Futuro) Considerar la implementación de un conjunto de pruebas unitarias o de integración automatizadas para componentes críticos del juego.

4.  **Confirmación Final**:
    *   Solo después de que las pruebas confirmen que la solución es efectiva y estable, y que los modos de depuración han sido desactivados, proceder con la documentación final de los cambios (CHANGELOG, TODO, etc.).

### Plantilla para Documentar un Bug en TODO.md

```markdown
- [ ] (Prioridad: Crítica/Alta/Media/Baja) Descripción corta del bug (ID: YYYYMMDD-BreveNombre)
  - **Descripción detallada**: Explicación completa del problema. Qué ocurre, dónde se observa.
  - **Pasos para reproducir**: 
    1. Hacer X.
    2. Hacer Y.
    3. Observar Z.
  - **Comportamiento esperado**: Lo que debería suceder.
  - **Comportamiento actual**: Lo que actualmente sucede (incluyendo mensajes de error si los hay).
  - **Entorno (si es relevante)**: Versión del juego, sistema operativo, configuraciones especiales.
  - **Archivos/Módulos probablemente involucrados**: (ej. `jugador.py`, `collision_handler.py`).
  - **Logs/Screenshots**: (Referencia a archivos de log en `logs/` o descripción de screenshots).
  - **Notas Adicionales**: Cualquier otra información útil.
```

### Consejos para una Depuración Efectiva

1.  **Usar el sistema de logging estratégicamente**:
    *   Preferir el sistema de logging sobre prints directos para mensajes que puedan ser útiles a largo plazo o para entender flujos complejos.
    *   Usar niveles de log apropiados (DEBUG para detalles minuciosos, INFO para eventos normales importantes, WARNING para situaciones anómalas que no detienen el juego, ERROR para fallos recuperables, CRITICAL para fallos que sí detienen el juego).

2.  **Proteger siempre los prints de depuración temporales**:
    *   Todos los prints de depuración temporales deben estar protegidos por una variable de control `DEBUG_PRINT_*` en `settings.py`.
    *   Formato recomendado:
        ```python
        if hasattr(settings, 'DEBUG_PRINT_AREA_ESPECIFICA') and settings.DEBUG_PRINT_AREA_ESPECIFICA:
            print(f"DEBUG_AREA: Mensaje de depuración {variable}")
        ```

3.  **Mantener la depuración limpia**:
    *   Desactivar (`False`) las variables `DEBUG_PRINT_*` en `settings.py` después de solucionar el problema.
    *   Evitar dejar código comentado sin explicación; eliminarlo o refactorizarlo.

4.  **Documentar hallazgos importantes**:
    *   Si durante la depuración se descubren aspectos importantes del sistema, comportamientos inesperados o interacciones complejas no documentadas, tomar notas y considerar añadirlas a este documento, al código como comentarios, o al `dev_notes.md`.
    *   Estos conocimientos pueden ser valiosos para futuras depuraciones o para mejorar la comprensión general del proyecto.

5.  **Correlación de Tiempos en Logs (Consola vs. Archivo)**:
    *   Si se utilizan tanto logs de archivo (generados por el sistema de logging) como prints directos a consola, tener en cuenta que puede haber pequeñas diferencias en los tiempos exactos en que aparecen los mensajes. Los logs de archivo suelen tener timestamps más precisos.
    *   Al analizar un problema, cruzar la información de ambos puede ser útil, pero si se necesita una secuencia temporal exacta, los logs de archivo con timestamps son generalmente más fiables.

## Guía de Patrones y Plantillas de Código Comunes

Esta sección describe patrones de diseño recurrentes y plantillas recomendadas para tareas comunes dentro del proyecto. El objetivo es mantener la consistencia, facilitar la incorporación de nuevas funcionalidades y promover la reutilización de código. Se espera que esta sección sea consultada y actualizada colaborativamente.

Para acceder a las plantillas detalladas, consulta el archivo: [`docs/PLANTILLAS_CODIGO.md`](docs/PLANTILLAS_CODIGO.md).

*(Este archivo `docs/PLANTILLAS_CODIGO.md` se irá poblando con plantillas específicas a medida que se identifiquen y documenten patrones comunes. Ejemplos podrían incluir: "Plantilla para crear una nueva Entidad", "Plantilla para añadir un nuevo Sistema", etc.)*

## Contribución

1.  **Flujo General (Git)**:
    *   Asegurarse de que la rama local `main` (o `master`) esté actualizada con el repositorio remoto.
    *   Crear una nueva rama para la característica o corrección desde `main`:
        *   Para nuevas características: `git checkout -b feature/nombre-descriptivo-caracteristica`
        *   Para correcciones de bugs: `git checkout -b fix/nombre-o-id-bug`
    *   Realizar los cambios en esta nueva rama. Hacer commits pequeños y descriptivos.
    *   Una vez finalizado y probado el trabajo:
        *   Actualizar la documentación relevante (`CHANGELOG.md`, `TODO.md`, este archivo, `README.md` principal si es necesario).
        *   Asegurarse de que los modos de depuración estén desactivados.
        *   Empujar la rama al repositorio remoto: `git push origin nombre-rama`.
        *   Crear un Pull Request (PR) en la plataforma Git (GitHub, GitLab, etc.) desde la rama de trabajo hacia `main`.
        *   Describir los cambios en el PR y enlazar al issue o tarea del `TODO.md` si aplica.

2.  **Nuevas Características**:
    *   Seguir el flujo general de Git.
    *   Implementar los cambios siguiendo las convenciones y guías de este documento.
    *   Añadir la documentación necesaria para la nueva característica.

3.  **Correcciones de Bugs**:
    *   Seguir el flujo general de Git.
    *   Implementar la corrección asegurándose de entender la causa raíz.
    *   Añadir pruebas (unitarias o de integración, si el proyecto las tiene) para evitar regresiones del bug corregido.
    *   Documentar la corrección en `CHANGELOG.md` y actualizar `TODO.md`.

## Protocolo de Sincronización y Actualización de Documentación al Cierre de Sesión/Hito

Este protocolo se activa cuando el usuario indica el final de una sesión de trabajo (ej. "terminamos por hoy", "hagamos una pausa larga") o después de alcanzar un hito importante (ej. "hemos solucionado este bug crítico", "terminamos de implementar esta característica"). Su objetivo es asegurar que toda la documentación esté al día, el contexto se preserve y se capture cualquier aprendizaje relevante.

**Pasos a seguir por el Asistente IA (y a ser recordados/verificados por el colaborador humano):**

1.  **Confirmación de Funcionamiento (si aplica):**
    *   Si se han realizado cambios de código para solucionar bugs o implementar funcionalidades, el asistente debe recordar al usuario la importancia de verificar que todo funciona como se espera ANTES de proceder a la documentación final de esos cambios específicos en `CHANGELOG.md` y `TODO.md` (siguiendo el "Flujo de Trabajo para la Depuración").
    *   El asistente preguntará: "¿Hemos verificado que los últimos cambios de código funcionan correctamente y que los modos de depuración están desactivados?"

2.  **Actualización de Documentación Principal (Post-Confirmación):**
    *   Una vez confirmada la funcionalidad (o si no hubo cambios de código recientes que requieran esta confirmación), el asistente procederá a proponer actualizaciones para:
        *   **`TODO.md`**: Marcar tareas completadas, añadir nuevas tareas o bugs identificados durante la sesión.
        *   **`CHANGELOG.md`**: Añadir entradas para nuevas versiones, funcionalidades implementadas, bugs corregidos, detallando los cambios realizados y, si es relevante, el razonamiento o proceso seguido.
        *   **`mapa_conceptual_modulos.py`**: Si se han añadido nuevos módulos, eliminado existentes, o si las responsabilidades o interacciones principales de los módulos han cambiado significativamente.
        *   **`README.md` (principal)**: Si la estructura general del proyecto, la forma de ejecutarlo, o la descripción de alto nivel ha cambiado.
        *   **`DEVELOPMENT_PROTOCOLS.md` (este mismo archivo)**: Si se han acordado nuevos protocolos, modificado existentes, o si se han identificado nuevas convenciones o mejores prácticas de colaboración/desarrollo durante la sesión.
        *   **`docs/PLANTILLAS_CODIGO.md` (si existe y aplica)**: Si se han desarrollado nuevos patrones de código reutilizables. (Este directorio y archivo se crearán y poblarán a medida que se identifiquen y documenten patrones comunes).

3.  **Actualización del Registro de Continuidad de Sesión:**
    *   El asistente propondrá actualizar el archivo `dev_notes.md` (o `session_log.txt`). (Se recomienda crear y mantener un archivo simple como `dev_notes.md` - puedes crearlo en la raíz del proyecto si aún no existe). Este archivo debería incluir:
        *   Un resumen conciso de las tareas realizadas durante la sesión.
        *   El estado actual de los bugs o problemas que se estaban investigando (resueltos, pendientes, próximos pasos).
        *   Ideas pendientes o próximos pasos planificados discutidos durante la sesión.
        *   Cualquier configuración temporal de depuración que se haya utilizado y su estado final (asegurándose de que esté desactivada si corresponde).

4.  **Reflexión y Captura de Aprendizajes (Meta-Protocolo):**
    *   El asistente revisará mentalmente la sesión y considerará:
        *   **Nuevos Protocolos o Mejoras a Existentes**: ¿Surgió alguna situación no cubierta por los protocolos actuales? ¿Se puede mejorar alguna directriz existente para mayor claridad o eficiencia? Si es así, se propondrá la modificación/adición a `DEVELOPMENT_PROTOCOLS.md`.
        *   **Preferencias del Usuario**: ¿El usuario expresó preferencias claras sobre cómo presentar la información (ej. tablas, resúmenes más detallados, etc.) o sobre el flujo de interacción? El asistente tomará nota interna de estas preferencias para futuras interacciones y, si parece una preferencia generalizable, podría sugerir añadirla como una nota en la sección de "Colaboración con IA".
        *   **Patrones de Problemas/Soluciones Recurrentes**: ¿Se identificaron patrones en los problemas encontrados o en las soluciones aplicadas que podrían ser útiles para el futuro? (Esto contribuye al "aprendizaje" del asistente sobre el proyecto). Podría ser material para `dev_notes.md` o incluso para una futura sección de "Lecciones Aprendidas" o "FAQ de Desarrollo" si se acumulan varios.

5.  **Resumen Final de la Sesión para el Usuario:**
    *   Una vez completadas las actualizaciones (o propuestas y a la espera de aplicación), el asistente proporcionará un resumen final al usuario, indicando qué archivos de documentación se han actualizado (o se propone actualizar) y los puntos clave del `dev_notes.md`.

**Frecuencia y Disparadores para la Sincronización:**

*   **Iniciada por el Usuario:**
    *   **Obligatorio:** Cuando el usuario indica explícitamente el final de una sesión de trabajo (ej. "terminamos por hoy", "hagamos una pausa larga").
*   **Iniciada o Sugerida por el Asistente IA:**
    *   **Recomendado y Proactivo:** El asistente IA, utilizando el contexto de la conversación y la magnitud de los cambios/logros, sugerirá aplicar este protocolo después de:
        *   Resolver bugs críticos, bloqueantes o de alta prioridad.
        *   Completar la implementación de características significativas o múltiples tareas del `TODO.md`.
        *   Realizar refactorizaciones importantes o cambios estructurales en el código o diseño.
        *   Discutir y acordar nuevos protocolos o modificaciones significativas a los existentes.
        *   Períodos extensos de trabajo productivo donde se han acumulado varios cambios o decisiones no documentadas.
    *   El asistente evaluará la "importancia" y el "volumen" del trabajo realizado para proponer una sincronización, con el objetivo de mantener la documentación fresca y el contexto compartido.

## 5. Gestión de Errores y Excepciones

*   **Captura Específica:** Evitar bloques `except Exception:` genéricos siempre que sea posible. Capturar las excepciones específicas que se esperan.
*   **Logging Detallado:** Al capturar una excepción, loguear suficiente información para diagnosticar el problema, incluyendo `exc_info=True` para obtener la traza de la pila.
*   **Manejo Propio vs. Propagación:** Decidir si un error puede ser manejado localmente o si debe ser propagado para que un módulo superior lo maneje.

## 6. Sistema de Logging

El proyecto utiliza el módulo `logging` de Python para un registro estructurado y configurable de eventos.

### 6.1. Configuración Centralizada

La configuración principal del logging se encuentra en `src/config/config_logging.py` y los settings que la controlan en `src/config/settings.py`.

*   **`MODO_DEBUG_LOGS`**: Un interruptor global en `settings.py` para activar (`True`) o desactivar (`False`) los logs de nivel DEBUG. Los logs INFO y superiores siempre se registran si la categoría específica está habilitada.
*   **`LOG_CATEGORIAS`**: Un diccionario en `settings.py` que permite habilitar (`True`) o deshabilitar (`False`) el logging para módulos o funcionalidades específicas. El nombre de la clave en este diccionario (ej: `"log_jugador"`, `"log_collision_handler"`) debe coincidir con el `extra={"categoria_log": "nombre_categoria"}` usado al emitir el log.
*   **Archivos de Log por Sesión y Módulo**:
    *   Cada vez que se ejecuta el juego, se crea una nueva carpeta de sesión con timestamp en `logs/` (ej: `logs/YYYY-MM-DD_HH-MM-SS/`).
    *   Dentro de cada carpeta de sesión, se crean subcarpetas para cada módulo listado en `MODULOS_CON_LOG_PROPIO` en `settings.py` (ej: `main/main.log`, `juego/juego.log`).

### 6.2. Emisión de Logs

*   Obtener un logger específico para el módulo: `logger = logging.getLogger(__name__)` o `logger = logging.getLogger("nombre_modulo_custom")`.
*   Usar los niveles de log apropiados: `logger.debug()`, `logger.info()`, `logger.warning()`, `logger.error()`, `logger.critical()`.
*   **Incluir `extra={"categoria_log": "nombre_de_categoria_en_settings"}`** en cada llamada al logger para permitir el filtrado por categoría.

### 6.3. Debugging Selectivo con `LOG_CATEGORIAS` (¡MUY IMPORTANTE!)

Una de las herramientas más poderosas para la depuración es la capacidad de activar solo los logs que son relevantes para el problema que se está investigando.

**Procedimiento:**

1.  **Identificar Módulos Sospechosos:** Determinar qué partes del código podrían estar involucradas en el bug o comportamiento inesperado.
2.  **Modificar `src/config/settings.py`**:
    *   Asegurarse de que `MODO_DEBUG_LOGS = True` si se necesitan mensajes DEBUG.
    *   En el diccionario `LOG_CATEGORIAS`, establecer en `True` las categorías correspondientes a los módulos/funcionalidades que se quieren investigar (ej: `"log_renderer": True`, `"log_enemigo_ia": True`).
    *   **Establecer en `False` la mayoría de las otras categorías**, especialmente aquellas que generan mucho "ruido" (logs muy frecuentes que no son relevantes para el problema actual). Esto hará que los archivos de log sean más pequeños y fáciles de analizar.
3.  **Ejecutar el Juego:** Replicar el problema.
4.  **Analizar los Logs Enfocados:** Revisar los archivos de log generados. Ahora deberían contener principalmente información de las áreas de interés.

Esta técnica reduce drásticamente la cantidad de información a revisar y acelera significativamente el proceso de diagnóstico.

### 6.4. Análisis de Logs de Sesión

Al investigar un problema utilizando los logs:

1.  **Directorio de Sesión Más Reciente:** Navegar a la carpeta `logs/` y localizar la subcarpeta con el timestamp más reciente. Esta corresponde a la última ejecución del juego.
2.  **Archivos de Log Relevantes:** Dentro de la carpeta de sesión, identificar los archivos `.log` de los módulos que se activaron mediante `LOG_CATEGORIAS` (o aquellos que se sospecha que son relevantes). Por ejemplo, si se está depurando un problema de colisiones, se revisaría `collision_handler/collision_handler.log`.
3.  **Revisión Progresiva (para el Asistente IA):**
    *   Si un archivo de log es extenso (más de ~200-250 líneas), el asistente IA solo podrá ver una porción a la vez.
    *   El asistente debe indicar si el archivo es más largo que lo mostrado.
    *   El usuario puede solicitar al asistente que lea partes anteriores o siguientes del archivo si es necesario.
    *   No asumir que la porción inicial de un log contiene toda la información relevante si el archivo es grande.
4.  **Comparación con Sesiones Anteriores (si es necesario):** Si un log parece anómalamente pequeño, vacío, o si se sospecha que un comportamiento ha cambiado, puede ser útil comparar los logs de la sesión actual con los de sesiones anteriores para identificar diferencias.

### 6.5. Aplicación al Diagnóstico de Rendimiento

El sistema de logging, combinado con el debugging selectivo, es una herramienta valiosa no solo para bugs funcionales sino también para investigar problemas de rendimiento (FPS bajos, tirones, tiempos de carga excesivos).

**Estrategia General:**

1.  **Identificar Síntomas:** ¿El juego va lento en general? ¿Hay caídas de FPS en momentos específicos (ej. al cargar un nivel, durante combates intensos, con muchos objetos en pantalla)? ¿Los tiempos de carga iniciales o entre niveles son muy largos?
2.  **Consultar Protocolos de Optimización:** Antes de una inmersión profunda en los logs, revisa el documento `docs/PERFORMANCE_OPTIMIZATION_PROTOCOLS.md`. Este archivo contiene una guía más estructurada sobre cómo abordar la optimización del rendimiento, incluyendo el uso de profilers y otras técnicas específicas. El análisis de logs es una de las herramientas dentro de ese proceso.
3.  **Activar Categorías Relevantes:** En `src/config/settings.py`, activa las `LOG_CATEGORIAS` que puedan ofrecer pistas sobre el cuello de botella:
    *   `"log_juego"`: Para ver la duración de los ciclos del bucle principal, tiempos de `update` y `draw`.
    *   `"log_renderer"` (si existe o se crea una categoría específica para el renderizado): Para tiempos de dibujado de diferentes capas o tipos de entidades.
    *   `"log_asset_manager"`: Para tiempos de carga de imágenes, sonidos, fuentes.
    *   `"log_gestor_nivel"`: Para tiempos de carga y creación de niveles.
    *   `"log_collision_handler"`: Si se sospecha que las colisiones intensivas están ralentizando el juego.
    *   `"log_entidad_ia"` (o similar): Si la IA de muchos enemigos parece ser la causa.
    *   **Desactiva** las categorías que no sean relevantes para minimizar el ruido.
4.  **Analizar Timestamps y Frecuencia:**
    *   Busca en los logs operaciones que tarden consistentemente mucho tiempo. Los timestamps entre mensajes pueden revelar cuánto tarda una sección de código.
    *   Observa la frecuencia de ciertos logs. ¿Hay algún sistema que esté logueando excesivamente por segundo, indicando una actividad muy intensa?
5.  **Correlacionar con el Juego:** Ejecuta el juego e intenta reproducir las condiciones donde ocurre la ralentización. Luego, revisa los logs correspondientes a esos momentos.
6.  **Iterar:** Basándote en los hallazgos, puedes refinar las categorías de log activadas, añadir más logs específicos (protegidos por `LOG_CATEGORIAS`) en áreas sospechosas, o pasar a herramientas más especializadas como un profiler si los logs no son suficientes.

Recuerda que los logs son una pieza del rompecabezas. Para un análisis de rendimiento exhaustivo, considera los pasos detallados en `docs/PERFORMANCE_OPTIMIZATION_PROTOCOLS.md`.

## 7. Control de Versiones (Git)

## X. GESTIÓN DE INTERRUPCIONES Y CONTINUIDAD DEL DESARROLLO

### X.1. Protocolo ante Ralentización o Fallo del IDE/Entorno de Desarrollo

**Objetivo:** Minimizar la pérdida de trabajo y contexto, y asegurar una reanudación eficiente de las tareas después de una interrupción causada por problemas con el entorno de desarrollo (IDE lento, cuelgues, necesidad de reinicio del sistema, etc.).

**Pasos a Seguir:**

1.  **Prioridad: No Perder Trabajo No Guardado:**
    *   Si es posible, intentar guardar todos los archivos modificados y no guardados.
    *   Si el entorno está completamente colgado, este paso podría no ser viable. Proceder al siguiente.

2.  **Documentar el Estado Actual en `[dev_notes.md](mdc:dev_notes.md)`:**
    *   Crear una nueva entrada con la fecha y hora.
    *   **Motivo de la interrupción:** Ej. "IDE extremadamente lento, se requiere reinicio.", "Cursor/IDE se colgó."
    *   **Tarea en curso:** Descripción breve de la tarea o el problema que se estaba abordando.
        *   Ej: "Refactorizando `player.py` para el nuevo sistema de logging."
        *   Ej: "Investigando bug de colisión reportado en `TODO #123`."
    *   **Últimas acciones realizadas:** ¿Qué se estaba haciendo justo antes de la interrupción?
        *   Ej: "A punto de probar cambios en la función `update_estado()`."
        *   Ej: "Analizando logs de la última ejecución."
    *   **Próximos pasos inmediatos planeados (antes de la interrupción):**
        *   Ej: "Siguiente paso era ejecutar `python main.py` para verificar."
    *   **Estado de archivos clave o configuraciones temporales:**
        *   Archivos modificados pendientes de guardar/commitear (si se recuerdan).
        *   Cualquier configuración temporal en `[src/config/settings.py](mdc:src/config/settings.py)` (ej. `LOG_CATEGORIAS` específicas activadas para depuración).
        *   Ramas de Git activas, si es relevante.
    *   **Asistente IA (si aplica):** Mencionar si se estaba trabajando con un asistente IA y cuál era el contexto de la conversación, para facilitar la reanudación con el asistente.

3.  **Proceder con el Reinicio:**
    *   Cerrar el IDE.
    *   Reiniciar el IDE o el sistema operativo, según sea necesario.

4.  **Reanudación del Trabajo:**
    *   Una vez que el entorno esté estable, **consultar inmediatamente la última entrada en `[dev_notes.md](mdc:dev_notes.md)`** para retomar el contexto.
    *   Restaurar cualquier configuración temporal que se haya anotado (ej. `LOG_CATEGORIAS`).
    *   Continuar con los "próximos pasos" identificados.
    *   Si se estaba trabajando con un asistente IA, proporcionarle un resumen breve basado en `dev_notes.md` para reanudar la colaboración.

**Este protocolo es crucial para la eficiencia y para evitar la frustración de perder el hilo del trabajo debido a problemas técnicos del entorno.**

### X.2. Protocolo de Sincronización y Actualización de Documentación al Cierre de Sesión/Hito

Al finalizar una sesión de trabajo significativa o alcanzar un hito importante (ej. cierre de una tarea mayor en `TODO.md`, corrección de un bug importante, implementación de una nueva característica):

1.  **Actualizar `dev_notes.md`**:
    *   Resumir el trabajo realizado durante la sesión.
    *   Documentar el estado actual de la tarea en curso (si aplica).
    *   Identificar cualquier problema nuevo, bug encontrado, o decisión de diseño tomada.
    *   Esbozar los próximos pasos planeados para la siguiente sesión.
    *   **Asegurarse de que la fecha y hora de "Última Actualización" al inicio de `dev_notes.md` se actualice.**

2.  **Actualizar `TODO.md`**:
    *   Marcar tareas completadas.
    *   Añadir nuevas tareas si surgieron.
    *   Revisar y ajustar prioridades si es necesario.

3.  **Actualizar `CHANGELOG.md`**:
    *   Añadir una entrada concisa para los cambios significativos implementados, siguiendo el formato establecido. Referenciar versiones si aplica.

4.  **Comunicación (si aplica)**:
    *   Informar al usuario (humano) sobre las actualizaciones realizadas en la documentación y los resultados clave de la sesión.

5.  **Verificación Asistida (Propuesta para IA)**:
    *   Al cierre, la IA puede proponer un checklist de estos puntos para confirmar con el usuario.
    *   Al inicio de una nueva sesión, si la IA detecta una discrepancia significativa entre la fecha/hora de "Última Actualización" de `dev_notes.md` y la fecha/hora actual, o entre el último `CHANGELOG.md` y las notas, deberá señalarlo proactivamente como un posible indicador de que el contexto puede estar desactualizado y solicitar una aclaración antes de proceder.

El objetivo es mantener estos documentos como fuentes de verdad vivas y actualizadas, facilitando la continuidad y la comprensión del estado del proyecto.

### 2.4. Protocolo de Actualización de Documentos al Inicio de Nueva Tarea / Cambio de Foco

**Propósito:** Asegurar que todos los documentos de seguimiento estén actualizados y reflejen el estado y los planes actuales ANTES de sumergirse en una nueva tarea significativa o cuando el foco de trabajo cambia considerablemente (ej. de un bug a una nueva feature, o de un módulo a otro con implicaciones diferentes).

**Pasos Obligatorios:**

1.  **Obtener Fecha y Hora Actual:**
    *   Utilizar un medio fiable (ej. búsqueda web "hora actual en [zona horaria relevante]") para obtener la fecha y hora precisas.

2.  **Actualizar `dev_notes.md`:**
    *   Encabezar el archivo o la sección de notas más reciente con: `Última Actualización: [AAAA-MM-DD HH:MM:SS]` usando la hora obtenida.
    *   Resumir brevemente la conclusión de la tarea anterior o el motivo del cambio de foco.
    *   Describir claramente la **nueva tarea** o el **nuevo foco de trabajo**.
    *   Listar los **objetivos específicos** de esta nueva tarea.
    *   Detallar los **próximos pasos inmediatos** planeados para abordar la nueva tarea.
    *   Actualizar o añadir cualquier **hipótesis, observación relevante o dependencia** relacionada con la nueva tarea.

3.  **Revisar y Actualizar `TODO.md`:**
    *   Asegurarse de que la nueva tarea esté claramente definida en `TODO.md`.
    *   Si la tarea es nueva, añadirla con la prioridad adecuada.
    *   Si es una tarea existente que se retoma, actualizar su estado (ej. a "En Progreso") y sus subtareas si es necesario.
    *   Marcar tareas anteriores como completadas, pausadas u obsoletas según corresponda.
    *   Revisar prioridades generales si el cambio de foco lo amerita.

4.  **Actualizar `CHANGELOG.md` (si aplica):**
    *   Si la finalización de la tarea anterior o el inicio de la nueva constituyen un hito registrable (ej. corrección de bug importante, inicio de desarrollo de una feature mayor), añadir una entrada concisa en la sección `[UNRELEASED]` o en la versión actual en progreso.
    *   La actualización del `CHANGELOG.md` puede ser más frecuente al finalizar bloques de trabajo que al iniciar cada pequeña tarea, pero debe considerarse.

5.  **Comunicación (si aplica):**
    *   Informar al equipo (o al usuario, en el caso de un asistente IA) sobre la actualización de los documentos y el nuevo plan de trabajo.

**Cuándo Ejecutar:**
*   Al iniciar una sesión de trabajo después de una pausa considerable.
*   Al concluir una tarea principal listada en `TODO.md` y antes de comenzar la siguiente.
*   Cuando se decide cambiar significativamente el enfoque del trabajo actual.

Este protocolo complementa el "Protocolo de Sincronización y Actualización de Documentación al Cierre de Sesión/Hito" (sección 2.5) y está diseñado para mantener la agilidad y la claridad a medida que el proyecto evoluciona.

### 2.5. Protocolo de Sincronización y Actualización de Documentación al Cierre de Sesión/Hito

## XI. Registro de Hitos de Desarrollo y Sincronización de Contexto

Para mejorar la continuidad del trabajo y evitar la repetición de tareas, especialmente tras interrupciones o reinicios (reales o percibidos del entorno de la IA), se seguirán estas pautas:

1.  **Marcado en `dev_notes.md`**: Al finalizar una tarea significativa o una refactorización que afecte múltiples archivos o la lógica central (ej: actualización completa del mapa conceptual, finalización de una fase de limpieza), se registrará explícitamente en `dev_notes.md` con:
    *   La descripción de la tarea completada.
    *   La fecha y hora de finalización.
    *   Una lista de los principales artefactos o módulos que se consideran "consolidados" o "actualizados hasta este punto".
        *   Ejemplo: "Mapa conceptual (`mapa_conceptual_modulos.py`) completamente revisado y actualizado a fecha YYYY-MM-DD HH:MM."

2.  **Referencia Cruzada en `CHANGELOG.md`**: Los cambios estructurales o funcionales significativos seguirán siendo registrados en `CHANGELOG.md` con su fecha correspondiente.

3.  **Comunicación Explícita de la IA**: Si la IA ha completado una tarea de revisión o actualización extensa (como la del mapa conceptual), lo comunicará explícitamente, indicando la fecha/hora de su última verificación de dicho artefacto. Esto ayudará al usuario a entender qué tan "fresco" es el conocimiento de la IA sobre ese punto.

4.  **Consulta Proactiva por Parte del Usuario**: Si el usuario tiene dudas sobre si una tarea ya fue realizada recientemente (especialmente si hubo interrupciones), puede consultar `dev_notes.md` o preguntar directamente a la IA, haciendo referencia a este protocolo.

Este sistema busca crear "puntos de control" claros en el estado del proyecto, facilitando la reanudación del trabajo y asegurando que tanto el usuario como la IA operen con la información más reciente posible sobre el estado de las tareas y la documentación.

## 8. Protocolo de Creación y Desarrollo Incremental de Módulos Complejos (ej. Paneles UI)

Este protocolo debe seguirse para la creación de nuevos módulos complejos (como sistemas de UI, paneles interactivos, etc.) y también puede guiar la refactorización extensiva de módulos existentes si se están reestructurando significativamente o añadiendo funcionalidades complejas de forma incremental. El objetivo es asegurar la estabilidad del proyecto, facilitar la depuración temprana y mantener la calidad del código mediante un desarrollo paso a paso con verificación continua.

**Principios Clave:**

*   **Planificación Detallada Previa:** Entender completamente el propósito, responsabilidades, interacciones y subcomponentes del módulo antes de escribir código.
*   **Integración Temprana y Continua:** Conectar el módulo al sistema principal lo antes posible, incluso en su forma más esquelética.
*   **Pasos Mínimos Viables:** Implementar la funcionalidad en incrementos extremadamente pequeños, donde cada incremento sea fácilmente verificable.
*   **Pruebas Inmediatas y Frecuentes:** Ejecutar el juego y probar la funcionalidad específica después de CADA pequeño incremento.
*   **Commits Atómicos:** Guardar el progreso con `git commit` después de cada incremento funcional verificado.
*   **Documentación Progresiva:** Actualizar `dev_notes.md`, `mapa_conceptual_modulos.py` y `CHANGELOG.md` a medida que el módulo toma forma y se completan hitos.

**Pasos del Protocolo:**

1.  **Fase de Diseño y Planificación Detallada:**
    *   **Definir Propósito y Alcance:** ¿Qué hará el módulo? ¿Cuáles son sus límites?
    *   **Identificar Responsabilidades Clave:** Desglosar las funciones principales del módulo.
    *   **Diseñar la API Externa:** ¿Cómo interactuará este módulo con otros sistemas (ej. `GestorEstado`, `Juego`, otros gestores)? ¿Qué métodos públicos ofrecerá? ¿Qué datos necesitará o proporcionará?
    *   **Esbozar Componentes Internos (si aplica):** Para módulos complejos como paneles UI, identificar subcomponentes visuales (botones, sliders, áreas de texto) y lógicos.
    *   **Planificar Estructura de Archivos:** Definir el nombre del nuevo archivo `.py` y su ubicación (ej. `src/sistemas/nombre_panel_manager.py`). Si el módulo tendrá subcomponentes en archivos separados, planificar esa estructura también (ej. dentro de `src/sistemas/ui_components/`).
    *   **Documentar el Diseño:** Registrar este plan en `dev_notes.md` o en una sección dedicada si es un módulo mayor. Actualizar `mapa_conceptual_modulos.py` con la intención del nuevo módulo.

2.  **Preparación del Entorno:**
    *   Asegurar que el código base actual esté en un estado estable y funcional, verificado por ejecución del juego y pruebas.
    *   Realizar un `git commit` del estado estable actual antes de iniciar la creación del nuevo módulo.

3.  **Creación del Esqueleto del Módulo:**
    *   Crear el nuevo archivo `.py` (y las carpetas necesarias) según el plan.
    *   Implementar la clase principal del módulo con métodos esenciales vacíos o con `pass` (ej. `__init__`, `actualizar()`, `dibujar()`, `manejar_evento()`).
        *   El `__init__` debe aceptar las dependencias necesarias (ej. `asset_manager`, referencias a otros gestores) pero puede que no las use todas inmediatamente.
    *   Asegurar que el archivo tenga las importaciones mínimas necesarias para no dar error (ej. `pygame`, `logging`, `settings`).

4.  **Integración Temprana del Esqueleto:**
    *   En el módulo que usará/coordinará este nuevo módulo (ej. `Juego.py` o un futuro `GestorUI`), importar la nueva clase esqueleto.
    *   Crear una instancia del nuevo módulo esqueleto (ej. `self.nuevo_panel = NuevoPanelManager(self.asset_manager)`).
    *   Si el nuevo módulo tiene métodos `actualizar`, `dibujar`, `manejar_evento`, llamarlos desde los bucles correspondientes del módulo coordinador, incluso si aún no hacen nada.
    *   **PRUEBA DE INTEGRACIÓN MÍNIMA:** Ejecutar el juego (`python main.py`).
        *   **Verificar:** El juego debe arrancar y funcionar sin errores. No se espera nueva funcionalidad visible aún.
        *   **Si hay errores:** Corregirlos antes de continuar. El error probablemente estará en la instanciación o en las llamadas a los métodos vacíos.
    *   **COMMIT:** Hacer un commit con un mensaje como: "Creado esqueleto e integración inicial de [NombreModulo]".

5.  **Desarrollo Incremental (Ciclo Iterativo Pequeñísimo):**
    *   Para CADA pequeña pieza de funcionalidad a añadir:
        *   a. **Implementar la Funcionalidad Mínima:**
            *   Escribir la menor cantidad de código posible para lograr un cambio visible o comprobable.
            *   Ejemplos para un panel UI:
                *   Dibujar un rectángulo de fondo simple cuando el panel está "activo".
                *   Añadir un solo botón (solo visual, sin lógica de clic aún).
                *   Implementar el cambio de color de un botón al pasar el mouse (hover).
                *   Hacer que un botón ejecute una acción de `print()` simple al hacer clic.
        *   b. **PRUEBA INMEDIATA Y ESPECÍFICA:** Ejecutar el juego (`python main.py`).
            *   **Verificar:** Probar específicamente la pequeña funcionalidad añadida. ¿Se ve el rectángulo? ¿Aparece el botón? ¿Funciona el hover/clic simple? ¿No hay errores nuevos en la consola?
            *   **Si hay errores o no funciona:** Depurar y corregir esta pequeña pieza ANTES de añadir más código.
        *   c. **COMMIT ATÓMICO:** Una vez que la pequeña pieza funcione y se haya probado:
            *   `git add <archivo(s)_modificado(s)>`
            *   `git commit -m "MóduloX: [Descripción muy breve y específica de la funcionalidad añadida]"`
            *   Ejemplos: "PanelPrincipal: Dibujado fondo del panel", "PanelPrincipal: Añadido botón \'Aceptar\' (visual)", "PanelPrincipal: Implementado hover para botón \'Aceptar\'".
        *   d. **Refactorización Interna Oportunista (Opcional):** Si el código añadido, aunque pequeño, puede mejorarse (nombres, claridad), hacerlo antes del commit.
    *   Repetir este ciclo (a, b, c, d) para cada subsiguiente pieza de funcionalidad.

6.  **Documentación Progresiva:**
    *   Periódicamente (ej. al final del día, o al completar un subcomponente mayor del módulo), actualizar `dev_notes.md` con el progreso.
    *   Si la estructura interna del módulo o sus interacciones con otros cambian significativamente, actualizar `mapa_conceptual_modulos.py`.
    *   Al completar hitos importantes del módulo, considerar una entrada en `CHANGELOG.md`.

7.  **Revisión y Limpieza Final del Módulo:**
    *   Una vez que toda la funcionalidad planificada para el módulo esté implementada incrementalmente:
        *   Realizar una revisión general del código del módulo.
        *   Asegurar la consistencia en estilo, comentarios y docstrings.
        *   Eliminar código de prueba temporal o `print()`s de depuración que ya no sean necesarios (reemplazándolos con logging si es apropiado).

8.  **Verificación Completa Post-Desarrollo del Módulo:**
    *   Realizar pruebas más exhaustivas del módulo completo y su integración en el juego para asegurar que no se hayan introducido regresiones o comportamientos inesperados.

**Consideraciones Adicionales (similares al protocolo de refactorización):**

*   **Importaciones Circulares:** Prestar atención para evitar dependencias circulares, especialmente si el nuevo módulo interactúa con muchos otros.
*   **Módulos Muy Grandes:** Si un módulo planificado sigue siendo demasiado grande incluso con este enfoque, considerar si puede dividirse en varios módulos más pequeños desde la fase de diseño, cada uno siguiendo este protocolo.

Al seguir estas directrices, se espera que el desarrollo del proyecto sea más eficiente, colaborativo y que el producto final sea de mayor calidad.