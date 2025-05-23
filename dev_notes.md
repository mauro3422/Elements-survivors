# Notas de Desarrollo - Estado Actual

## Última Actualización: 2025-05-22 21:05:00 (Argentina)

**Protocolo de Limpieza y Estructura del Código (Fase 1 Completada):**

*   Se refactorizó `MotorFisica.py` a una clase instanciable para manejar fuerzas persistentes (empuje) con fricción y umbral.
*   `Jugador.py` fue actualizado para utilizar la nueva instancia de `MotorFisica`, simplificando su lógica de empuje.
*   Se añadieron configuraciones relevantes (`FACTOR_FRICCION_GENERICO`, `UMBRAL_FUERZA_MINIMA_GENERICO`, `log_motor_fisica_verbose`) a `src/config/settings.py`.
*   Se actualizaron los docstrings en `Jugador.py` para reflejar estos cambios.
*   Se actualizó `mapa_conceptual_modulos.py`.
*   Se revisaron `gestor_estado.py`, `gestor_eventos.py`, `gestor_nivel.py`, `enemigo.py` en busca de `print`s no controlados y oportunidades de limpieza inicial; se encontraron en buen estado general respecto a los prints y logging.
*   **Pendiente:** Decisión sobre el código comentado de "daño por contacto" en `gestor_estado.py` (línea 134: `# self.jugador.recibir_dano(dano, tipo_dano) # <--- DAÑO POR CONTACTO ACTUALMENTE DESACTIVADO PARA PRUEBAS`).

**Próximos Pasos:**
*   Verificación rápida de ejecución del juego para asegurar que la refactorización del sistema de empuje funciona como se espera.
*   Resolver la decisión sobre el daño por contacto en `gestor_estado.py`.
*   Continuar con otras tareas de `TODO.md` o siguientes fases del protocolo de limpieza si es necesario.

### Estado Actual del Proyecto
- Versión: 0.3.1
- Se ha decidido cambiar el enfoque para la resolución de problemas de empuje en colisiones. Se abandonará el sistema actual de "empuje especial promedio" en `collision_handler.py`.
- **Nueva Dirección:** Se diseñará e implementará un sistema de empuje por contacto basado en la suma de vectores de fuerza.
- La lógica de detección de colisiones y resolución de solapamientos básicos (para evitar interpenetración) en `collision_handler.py` se mantiene.

### Contexto de la Sesión Actual

**Tarea Principal en Curso:**
- **REDEFINIDA:** Diseño e Implementación Inicial del Sistema de Empuje por Vectores.
  - **Objetivo Anterior (Suspendido):** Resolver bug "Empuje Inconsistente en Eje Y".
  - **Razón del Cambio:** El sistema de empuje existente en `collision_handler.py` (basado en promedios de "empujes especiales") ha demostrado ser difícil de estabilizar y propenso a comportamientos anómalos (deslizamientos, falta de empuje en ejes puros).
  - **Nueva Hipótesis:** Un sistema basado en la suma vectorial de fuerzas de empuje individuales proporcionará un comportamiento más predecible, controlable y físicamente intuitivo.
  - **Archivos Relevantes para la Nueva Implementación:**
    - `src/sistemas/collision_handler.py` (para integrar la aplicación del vector de empuje resultante)
    - `src/entidades/jugador.py` (para recibir y reaccionar al vector de empuje)
    - `src/entidades/enemigo.py` (para generar vectores de empuje al contacto)
    - `pygame.math.Vector2` (como herramienta principal)

**Progreso de la Sesión:**
1.  Se intentaron múltiples ajustes a la lógica de "empuje especial" en `collision_handler.py` sin lograr un empuje consistente y correcto en el eje Y.
2.  Se añadió `PIXEL_CONTACT_THRESHOLD = 1` a `src/config/settings.py`, lo que corrigió el empuje por contacto en el eje X.
3.  **Decisión Tomada:** Abandonar el sistema de "empuje especial promedio" actual.
4.  Se comentó la lógica de generación y aplicación de `empujes_enemigos` y `empuje_total_calculado` en `_resolver_solapamientos_estaticos_eje` dentro de `collision_handler.py`. El `CollisionHandler` ahora solo resuelve solapamientos básicos.
5.  **Análisis de Logs (Sesión 2025-05-21_22-32-07):** Tras un reinicio de contexto, se analizaron los logs (`jugador`, `enemigo`, `collision_handler`, `motor_fisica`) para reconstruir el estado de la implementación del empuje vectorial:
    *   **Flujo de Empuje Identificado:** `Enemigo` detecta contacto -> llama a `MotorFisica.calcular_vector_empuje` (usa `ENEMIGO_FUERZA_EMPUJE_BASE`) -> `Enemigo` aplica vector resultante a `Jugador.aplicar_fuerza_empuje` -> `Jugador` acumula fuerzas y las suma a su movimiento -> `CollisionHandler` procesa el movimiento.
    *   **Problema "Teletransporte Lateral con Dos Enemigos":**
        *   Los logs muestran que solo `Enemigo_2` está aplicando empuje activamente. `Enemigo_1` no cumple la condición `ZonaInfluenciaHB.colliderect(JugadorHB)`.
        *   La fuerza de empuje actual proviene de un solo enemigo (`~2.5` de magnitud). El `JUGADOR_MAX_FUERZA_EMPUJE_FRAME` (límite de `7.0`) no parece estar activándose.
    *   **Problema "Temblor del Pollo en Empuje Diagonal":**
        *   El empuje es diagonal como se esperaba.
        *   La causa más probable del temblor es un ajuste en la coordenada Y del jugador que ocurre *después* de la resolución de colisiones por el `CollisionHandler` (ej. `pos_flotante.y` cambia de `1779` a `1778`). Esto se observa en `jugador.log` y parece estar relacionado con la lógica de `mantener_dentro_de_limites` o la sincronización entre `Rect` y posiciones flotantes.
6.  Se está procediendo a actualizar la documentación (`dev_notes.md`, `TODO.md`) y a planificar los siguientes pasos de depuración e implementación del nuevo sistema de empuje vectorial.
7.  **Análisis de Logs (Sesión 2025-05-22_01-47-30):** Tras una interrupción y reinicio del entorno, se analizaron los logs de la sesión `2025-05-22_01-47-30/` para entender el estado actual y posibles bugs no relacionados directamente con el sistema de empuje vectorial explícito, sino con el movimiento base y colisiones.
    *   **Flujo de Empuje Vectorial Confirmado:** Los logs de `jugador`, `enemigo` y `motor_fisica` confirman que el sistema de empuje (enemigo detecta, `MotorFisica` calcula vector, jugador recibe y acumula fuerza) funciona como se espera en términos de aplicación de fuerzas.
    *   **PROBLEMA CRÍTICO IDENTIFICADO - "Teletransportes / Saltos Anómalos":**
        *   Se observaron movimientos drásticos e inesperados (saltos) tanto en el jugador como en los enemigos. El `dx_real` o `dy_real` resultante de `CollisionHandler.gestionar_movimiento_y_colision` (o `EntidadBase._mover_y_colisionar`) es a menudo muy diferente del `dx_int`, `dy_int` de entrada.
        *   **Sospechoso Principal:** La Fase 1 del `CollisionHandler` (`_resolver_solapamientos_estaticos_eje`). Parece estar causando grandes ajustes de posición ANTES de que se aplique el movimiento del frame. El logging actual de esta fase es insuficiente para determinar la causa exacta.
        *   Ejemplo: En un caso, la posición `y` del jugador cambió de `220` a `388` dentro de la Fase 1 del CH, con un `dy_int` de entrada de solo `2`.
    *   **"Temblor" (Límites del Jugador):** No fue observable en esta sesión de logs, ya que la lógica de `mantener_dentro_de_limites` del jugador no realizó correcciones.
    *   **Estado de Logs Adicionales:**
        *   `juego.log`: Vacío.
        *   `main.log`: Solo cubre el inicio y tiene un timestamp (`01:47:30`) anterior al resto de los logs de la misma carpeta de sesión (`01:48:51` - `01:49:01`), lo cual es anómalo.
        *   `collision_handler.log`: Muy corto, cubriendo solo una llamada a `gestionar_movimiento_y_colision` y con logging insuficiente para la Fase 1.

## Plan de Acción Inmediato y Discusiones Pendientes
*(Esta sección se revisa al inicio de la sesión y se actualiza al final o al cambiar de tarea mayor)*

**Última Actualización del Plan:** 2025-05-22 (Después del análisis de logs de la sesión `..._01-47-30`)

**PRIORIDAD 0: Resolución de Problemas con el Empuje Vertical del Jugador**
    *   **Objetivo:** Asegurar que el empuje vertical aplicado por los enemigos al jugador funcione de manera consistente y predecible, especialmente cuando hay múltiples enemigos o están alineados.
    *   **Contexto del Problema:** El jugador reporta que el movimiento vertical de empuje no funciona correctamente. Los logs iniciales muestran que los vectores de empuje con componentes Y se calculan y aplican, pero el efecto final no es el esperado.
    *   **Hipótesis Actuales (a investigar con más logging):
        *   Magnitud del empuje vertical es demasiado pequeña en relación con otros movimientos o se ve disminuida por el `JUGADOR_MAX_FUERZA_EMPUJE_FRAME`.
        *   Interferencia de la lógica de `CollisionHandler` que podría estar anulando o modificando el movimiento vertical intentado tras el empuje.
    *   **Próximos Pasos Inmediatos (Plan Actual):
        1.  Añadir logging más detallado en `jugador.py` para verificar si se activa el clamp de `JUGADOR_MAX_FUERZA_EMPUJE_FRAME` y cómo afecta la componente Y.
        2.  Añadir logging más detallado en `CollisionHandler._aplicar_movimiento_y_colision_eje_y` para observar el `dy_aplicado` al inicio y el `dy_real_aplicado_hb` al final.
        3.  Ejecutar el juego y analizar los nuevos logs.

**PRIORIDAD 1: Refinamiento General del Sistema de Empuje y Adición de "Resistencia"**
    *   **Objetivo:** Una vez que el empuje funcione correctamente en todas las direcciones, pulir las interacciones y considerar añadir un sistema de "resistencia" o "inercia" al jugador para que los empujes se sientan más naturales.
    *   **Estado:** Pendiente hasta resolver la Prioridad 0.

**PRIORIDAD 2: (Anterior PRIORIDAD 0) Resolución de "Teletransportes / Saltos Anómalos" en `CollisionHandler` (Observación)**
    *   **Objetivo:** Eliminar los saltos de posición inesperados causados por `CollisionHandler`.
    *   **Estado Actual:** Aunque el foco se ha movido al empuje, se seguirá observando si este comportamiento general persiste una vez solucionado el tema del empuje. Los logs de la sesión `..._01-47-30` mostraban saltos que podrían o no estar relacionados con el sistema de empuje actual.

## Plan de Trabajo Sesión Actual / Próximos Pasos Generales

1.  **Implementar Protocolo de Actualización de Documentos al Inicio de Tarea:** (Esta tarea)
2.  **Continuar con Prioridad 0:** Añadir logging para el empuje vertical.
3.  Analizar logs y, si es necesario, realizar ajustes en el código de empuje o `CollisionHandler`.

## Notas Adicionales y Observaciones

*   Se ha creado y referenciado `docs/JULES_COLLABORATION_PROTOCOL.md`.
*   Se ha discutido la importancia de verificar los timestamps de los logs y de `dev_notes.md` para mantener la sincronización.

### Estado de la Documentación
-   `dev_notes.md`: Actualizado con el análisis de logs de la sesión `2025-05-21_22-32-07` y próximos pasos.
-   `CHANGELOG.md`: Pendiente de actualizar para reflejar la tarea de rediseño del sistema de empuje y los hallazgos.
-   `TODO.md`: Pendiente de actualizar para priorizar las subtareas de depuración del sistema de empuje vectorial.

---

**(Sección a eliminar o archivar - Contexto Anterior)**

*Esta sección contiene notas de una sesión anterior centrada en problemas de rendimiento del IDE y `memory_profiler`. Se mantiene temporalmente para referencia pero no es el foco actual.*

**Tarea Anterior (Pausada):**
- Investigación y resolución de problemas de rendimiento del IDE.
- Se estaba evaluando el uso de `memory_profiler`.
- Se encontró un problema con la instalación de dependencias (Pygame y Python 3.13.1).

**Últimas acciones realizadas (Tarea Pausada):**
- Se intentó instalar `memory_profiler`.
- Se identificó incompatibilidad con Pygame en Python 3.13.1.
- Se propusieron soluciones: Usar Python 3.11.x, buscar wheel de Pygame para Python 3.13, o instalar `setuptools`.
- Se añadió `memory_profiler` a `requirements.txt`.

---

## Dev Notes - 22 de Mayo de 2025 - 19:00 (Argentina)

**Contexto Actual:**

*   **¡ÉXITO MAYOR!** Se ha implementado y perfeccionado la mecánica de **empuje del enemigo al jugador**.
    *   Inicialmente, el empuje era instantáneo y se sentía como "ticks" o "golpecitos" porque la fuerza de empuje aplicada al jugador se reseteaba en cada frame.
    *   Se modificó `jugador.py` para introducir un sistema de **fricción** a las `fuerzas_de_empuje_acumuladas_frame`. Ahora, la fuerza de empuje persiste a través de los frames y decae gradualmente, resultando en un efecto de **deslizamiento** que el USER ha confirmado como "espectacular" y "funciona como yo quería".
    *   Se añadieron (o se usarán por defecto si no existen en `settings.py`) las constantes `FACTOR_FRICCION_EMPUJE_JUGADOR` (e.g., 0.85) y `UMBRAL_FUERZA_EMPUJE_MINIMA_JUGADOR` (e.g., 0.5) para controlar este comportamiento.
*   Las colisiones generales y el movimiento de entidades parecen estables después de las correcciones previas.

**Próximos Pasos (Planificados para la siguiente sesión después del reinicio del IDE):**

1.  **Actualización del Mapa Conceptual (`mapa_conceptual_modulos.py`):**
    *   Reflejar los cambios recientes y la lógica actual de interacciones, especialmente en lo referente al sistema de empuje y colisiones.
2.  **Protocolo de Limpieza y Estructura del Código:**
    *   Revisar la estructura general del proyecto.
    *   Aplicar buenas prácticas de codificación y organización.
    *   Asegurar que la estructura sea clara y mantenible para facilitar la colaboración (incluyendo con otras IAs).
    *   Esto podría implicar refactorizaciones menores para mejorar la claridad y la cohesión.
3.  **Revisión General de `TODO.md` y `CHANGELOG.md`:**
    *   Asegurar que estén completamente al día después de estos cambios significativos.

**Notas Adicionales:**

*   El USER está muy satisfecho con la sensación actual del empuje.
*   La sesión actual concluirá para reiniciar el IDE, y se retomará con las tareas de limpieza y actualización estructural. 