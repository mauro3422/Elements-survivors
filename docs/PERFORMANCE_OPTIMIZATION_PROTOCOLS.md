# Protocolos de Diagnóstico y Optimización de Rendimiento

Este documento detalla el proceso recomendado para identificar, diagnosticar y solucionar problemas de rendimiento en el proyecto "Juego Pygame Modular". Debe ser consultado cuando se detecten problemas de FPS, uso excesivo de memoria/CPU, tiempos de carga prolongados, o cualquier otra degradación del rendimiento.

## 1. Identificación del Problema de Rendimiento

### 1.1. Descripción Clara del Problema
- **Síntomas Detallados:** Documentar exhaustivamente qué está sucediendo.
    - ¿El juego va lento (bajos FPS)? ¿En qué momentos?
    - ¿Hay picos de lag o congelamientos? ¿Cuándo ocurren?
    - ¿El uso de memoria o CPU es excesivo? ¿Cuánto y en qué procesos?
    - ¿Los tiempos de carga son largos? ¿Para qué assets o etapas?
    - ¿El IDE o el sistema se vuelven inestables durante/después de ejecutar el juego?
- **Contexto:** ¿Ocurre siempre, después de cierto tiempo de juego, al realizar acciones específicas, en niveles particulares, con ciertas configuraciones?

### 1.2. Reproducibilidad
- **Pasos para Reproducir:** Detallar los pasos exactos para provocar el problema de forma consistente. Si no es 100% reproducible, describir las condiciones bajo las cuales es más probable que ocurra.
- **Frecuencia y Severidad:** ¿Con qué frecuencia ocurre? ¿Qué tan severo es el impacto (ej. injugable, molesto, leve)?

### 1.3. Métricas Iniciales (Base de Referencia)
- Si es posible, tomar mediciones antes de cualquier intento de optimización:
    - **FPS:** Promedio, mínimos, fluctuaciones. Usar el HUD de debug si muestra FPS.
    - **Uso de Memoria:** Memoria RAM consumida por el proceso del juego al inicio, durante el juego, y después de cerrarlo (si el problema es de no liberación). Herramientas del sistema operativo o `memory_profiler`.
    - **Uso de CPU:** Porcentaje de CPU consumido por el proceso del juego. Herramientas del sistema operativo o `cProfile`.
    - **Tiempos de Carga:** Tiempo para iniciar el juego, cargar niveles, etc.
- Registrar estas métricas en `PERFORMANCE_METRICS.md` (o crearlo si no existe) con fecha y versión del juego.

### 1.4. Consulta de Documentación Existente
- Revisar `dev_notes.md`: Puede contener información sobre investigaciones en curso o problemas de rendimiento ya identificados.
- Revisar `TODO.md`: Puede listar tareas de optimización o bugs de rendimiento.
- Revisar `CHANGELOG.md`: Para entender si cambios recientes podrían haber introducido el problema.

## 2. Formulación de Hipótesis

- Basándose en los síntomas y la información recopilada, generar hipótesis sobre las posibles causas raíz.
- **Ejemplos de Hipótesis:**
    - **Fuga de Memoria:** Objetos no liberados (Surfaces, sprites, datos de nivel, etc.).
    - **CPU Bound (Cuello de Botella de CPU):**
        - Algoritmos ineficientes (ej. búsquedas, colisiones O(n^2)).
        - Búcles muy costosos o que se ejecutan con demasiada frecuencia.
        - Recálculos redundantes en cada frame.
        - Operaciones de dibujo (renderizado) excesivas o no optimizadas.
    - **GPU Bound (Limitaciones de Renderizado):** (Menos común en juegos 2D simples, pero posible)
        - Demasiados objetos en pantalla.
        - Uso ineficiente de blending o efectos.
        - No usar dirty rect rendering si es apropiado (aunque este proyecto parece redibujar todo).
    - **Carga/Descarga de Assets Ineficiente:** Cargar assets en el bucle principal, no liberar assets no usados.
    - **Problemas de Estructura de Datos:** Usar listas para búsquedas frecuentes en lugar de sets o diccionarios.
- Identificar los módulos o sistemas del juego que podrían estar involucrados según las hipótesis (consultar `mapa_conceptual_modulos.py`).

## 3. Herramientas y Técnicas de Diagnóstico

### 3.1. Logging Estratégico
- Activar logs relevantes en `settings.py` (`MODO_DEBUG_LOGS = True` y las `LOG_CATEGORIAS` apropiadas).
- **Añadir Logs Específicos para Rendimiento:**
    - Medir tiempo de ejecución de funciones críticas:
      ```python
      import time
      start_time = time.perf_counter()
      mi_funcion_costosa()
      end_time = time.perf_counter()
      logger.debug(f"Tiempo ejecución mi_funcion_costosa: {(end_time - start_time) * 1000:.2f} ms", extra={"categoria_log": "log_performance"})
      ```
    - Rastrear la creación y (si aplica) destrucción/liberación de objetos que consumen muchos recursos.
    - Usar el sistema `DEBUG_PRINT_VARIABLES` en `settings.py` para inspecciones rápidas de variables relevantes durante la ejecución.

### 3.2. Profiling

- **CPU Profiling (para identificar cuellos de botella de tiempo):**
    - Usar el módulo `cProfile` (integrado en Python).
    - Ejecutar el juego con profiling: `python -m cProfile -o profile_output.prof main.py`
    - Analizar la salida con `pstats` o herramientas visuales como `snakeviz` (`pip install snakeviz`, luego `snakeviz profile_output.prof`).
    - Identificar las funciones que consumen más tiempo acumulado y tiempo por llamada.
- **Memory Profiling (para identificar fugas de memoria y uso excesivo):**
    - Usar la librería `memory_profiler` (`pip install memory_profiler`).
    - Decorar funciones clave con `@profile` (después de `from memory_profiler import profile`).
    - Ejecutar el script con: `python -m memory_profiler main.py`
    - Analizar la salida para ver el incremento de memoria por línea y el uso total.
    - Para trazar la memoria a lo largo del tiempo, se puede usar `mprof run main.py` y luego `mprof plot`.

### 3.3. Inspección de Código
- **Revisión Algorítmica:**
    - Analizar la complejidad de los algoritmos utilizados (ej. O(n), O(n log n), O(n^2)).
    - Buscar bucles anidados que puedan ser optimizados o evitados.
- **Gestión de Recursos:**
    - Verificar que los recursos (especialmente `pygame.Surface`) se carguen una vez y se reutilicen.
    - Asegurar que los recursos se liberen/eliminen cuando ya no son necesarios (ver métodos de limpieza en `AssetManager`, `GestorEstado`).
    - Revisar si hay archivos abiertos que no se cierran.
- **Recálculos Redundantes:** Identificar si se están realizando los mismos cálculos costosos en cada frame cuando podrían hacerse solo cuando cambian los datos de entrada.
- **Operaciones de Dibujo:**
    - ¿Se están dibujando objetos fuera de la pantalla innecesariamente? (La cámara debería ayudar con esto).
    - ¿Hay un uso excesivo de `convert()` o `convert_alpha()`? (Debería hacerse una vez al cargar).

### 3.4. Pruebas Aisladas
- Si se sospecha de un componente específico, intentar crear un script de prueba mínimo que solo use ese componente para reproducir el problema de rendimiento de forma aislada. Esto simplifica el diagnóstico.

### 3.5. Logs de Tiempo por Fase
- **Logs de Tiempo por Fase:** Implementar logs que midan la duración de las principales fases del bucle de juego (ej. manejo de eventos, actualización de estado, renderizado). Esto ayuda a aislar qué parte general del frame es más costosa.
- **Profiling Integrado (si aplica):** Algunos frameworks o motores pueden ofrecer herramientas de profiling integradas.

### 2.3. Instrumentación Detallada y Desglose Iterativo

Una vez que el profiling general (ya sea con cProfile o logs de tiempo por fase) ha identificado una función o método como un cuello de botella principal (ej. `Juego._actualizar_estado()` consume la mayor parte del tiempo del frame), el siguiente paso es aplicar un desglose más detallado dentro de esa función.

**Técnica de Desglose por Fases Internas:**

1.  **Identificar Sub-Operaciones Clave:** Dentro de la función costosa, identificar las principales sub-operaciones o llamadas a otros métodos que realiza.
    *   Por ejemplo, si `_actualizar_estado()` llama a `gestor_entidades.update()`, `collision_handler.check_collisions()`, y `camara.update()`, estas son las sub-operaciones a medir.

2.  **Medición Individual:** Similar a la instrumentación del bucle principal, añadir mediciones de tiempo (ej. usando `time.perf_counter()`) al inicio y al final de cada una de estas sub-operaciones clave.
    ```python
    # Ejemplo conceptual dentro de una función costosa
    def funcion_costosa(self, dt):
        log_detallado = settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_mi_modulo_detalle", False)

        sub_operacion1_start_time = time.perf_counter()
        self.sub_componente1.hacer_algo_importante(dt)
        if log_detallado:
            duration_ms = (time.perf_counter() - sub_operacion1_start_time) * 1000
            logger.debug(f"    Sub-Op 1 (hacer_algo_importante): {duration_ms:.4f}ms", extra={"categoria_log": "log_mi_modulo_detalle"})

        sub_operacion2_start_time = time.perf_counter()
        self.sub_componente2.procesar_datos(dt)
        if log_detallado:
            duration_ms = (time.perf_counter() - sub_operacion2_start_time) * 1000
            logger.debug(f"    Sub-Op 2 (procesar_datos): {duration_ms:.4f}ms", extra={"categoria_log": "log_mi_modulo_detalle"})
        
        # ... más sub-operaciones ...
    ```

3.  **Análisis de Logs Detallados:** Ejecutar el juego y analizar los logs generados. Esto permitirá identificar con precisión cuál de las sub-operaciones es la responsable de la mayor parte del tiempo de ejecución de la función padre.

4.  **Iteración (Si es Necesario):** Si una sub-operación sigue siendo un "caja negra" y consume mucho tiempo, se puede aplicar este mismo proceso de desglose de forma recursiva a esa sub-operación.

Esta técnica permite "profundizar" progresivamente en el código para encontrar la causa raíz del problema de rendimiento a un nivel granular. Es crucial activar/desactivar estos logs detallados selectivamente (usando `LOG_CATEGORIAS`) para evitar un exceso de información irrelevante durante el debugging normal.

## 4. Implementación de Optimizaciones

- **Cambios Enfocados:** Realizar un cambio de optimización a la vez para poder medir su impacto individualmente.
- **Priorización:** Abordar primero los cuellos de botella más significativos identificados por el profiling o la inspección.
- **No Optimizar Prematuramente:** Enfocarse en código que *realmente* es un cuello de botella.
- **Buenas Prácticas:**
    - **Caching/Memoization:** Almacenar resultados de funciones costosas para evitar recalcularlos.
    - **Lazy Loading:** Cargar recursos solo cuando son necesarios, si la precarga completa es un problema.
    - **Optimización de Estructuras de Datos:** Usar `set` o `dict` para búsquedas rápidas en lugar de `list` si el orden no importa.
    - **Vectorización/Operaciones por Lotes:** Si se usan librerías como NumPy (no actualmente en el proyecto), aprovechar sus capacidades. Para Pygame, a veces agrupar operaciones puede ser beneficioso.
- Seguir las convenciones de código y protocolos de documentación (`DEVELOPMENT_PROTOCOLS.md`).
- Utilizar control de versiones (Git) para cada cambio significativo, en ramas separadas.

## 5. Verificación y Medición Post-Optimización

- **Repetir Pruebas:** Ejecutar los mismos pasos que se usaron para identificar el problema.
- **Medir Impacto:**
    - Comparar las métricas de rendimiento (FPS, memoria, CPU, tiempos de carga) con la base de referencia.
    - Registrar las nuevas métricas en `PERFORMANCE_METRICS.md`.
- **Pruebas de Regresión:** Asegurarse de que la optimización no haya introducido nuevos bugs o roto funcionalidades existentes.
- **Limpieza:** Desactivar o eliminar logs de diagnóstico muy verbosos o decoradores de profiling una vez que la optimización esté verificada y confirmada.

## 6. Documentación de Cambios

- **`CHANGELOG.md`:** Añadir una entrada detallando la optimización realizada, el problema que resuelve y, si es posible, el impacto medido (ej. "Mejorado el uso de memoria al cerrar el juego en un X%").
- **`TODO.md`:** Marcar la tarea de optimización como completada o actualizar su estado.
- **`dev_notes.md`:** Registrar los hallazgos clave, las técnicas de diagnóstico utilizadas y las lecciones aprendidas durante el proceso de optimización, especialmente si fue complejo.
- **Este Protocolo (`PERFORMANCE_OPTIMIZATION_PROTOCOLS.md`):** Si se descubre una nueva técnica de diagnóstico útil, una herramienta no listada, o una "mejor práctica" de optimización específica para este proyecto, considerar añadirla a este documento.
- **`PERFORMANCE_METRICS.md`:** Asegurarse de que esté actualizado con los resultados de las mediciones post-optimización. 