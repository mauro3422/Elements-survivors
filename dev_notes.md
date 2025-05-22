# Notas de Desarrollo - Estado Actual

## Última Actualización: 2025-05-22 (Fecha Actual de la Conversación Simulada tras reinicio)

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

**PRIORIDAD 0: Resolución de "Teletransportes / Saltos Anómalos" en `CollisionHandler`**
    *   **Objetivo:** Eliminar los saltos de posición inesperados causados por `CollisionHandler`.
    *   **Análisis de Logs Reciente (Sesión `..._01-47-30`):**
        *   Los logs combinados de `jugador.log` y `collision_handler.log` confirman el salto anómalo. Ejemplo: Jugador entra a `gestionar_movimiento_y_colision` en `y=220` y sale en `y=388` (salto de +168px).
        *   El `collision_handler.log` actual para `_resolver_solapamientos_estaticos_eje (y)` (Fase 1 - Eje Y) muestra que la entidad ya tiene la coordenada `y` "saltada" (`y=388`) al inicio de la porción logueada de esta función.
        *   Esto sugiere que el gran desplazamiento ocurre ANTES de la lógica de resolución de solapamientos del eje Y que se está logueando actualmente, posiblemente en la resolución de solapamientos del eje X (Fase 1 - Eje X) o en una etapa inicial no logueada de `gestionar_movimiento_y_colision`.
    *   **Acción 1: Mejorar Logging en `CollisionHandler.py` (CRÍTICO):**
        *   **Función `gestionar_movimiento_y_colision`:**
            *   Añadir un log al INICIO MISMO de esta función para registrar el `HB_Ent` (hitbox de la entidad) y los `dx, dy` de entrada originales, ANTES de cualquier otra operación.
        *   **Función `_resolver_solapamientos_estaticos_eje` (Fase 1):**
            *   Añadir un log AL INICIO de esta función que registre claramente para QUÉ EJE (`'x'` o `'y'`) se está ejecutando y el estado del `HB_Ent` en ese preciso instante.
            *   Dentro del bucle de corrección:
                *   Loguear `HB_Ent` ANTES de cualquier ajuste.
                *   Loguear con QUÉ tile/obstáculo específico se está colisionando/solapando.
                *   Loguear CÓMO se calcula el ajuste de posición (el vector de corrección).
                *   Loguear `HB_Ent` DESPUÉS de cada ajuste.
        *   **Salida de `gestionar_movimiento_y_colision`:**
            *    Revisar y asegurar que el log del `Delta Real (dx,dy)` final refleje con precisión el movimiento neto efectivo aplicado a la entidad en relación con su posición de entrada a la función.
    *   **Acción 2: Revisar Lógica de `_resolver_solapamientos_estaticos_eje` (para AMBOS ejes):**
        *   Utilizando el logging mejorado, analizar por qué se producen los grandes desplazamientos. La función solo debería "des-solapar" la entidad del tile, no moverla a coordenadas lejanas. Prestar especial atención a la ejecución para el eje X.
    *   **Acción 3 (Opcional, si es necesario): Investigar Discrepancia Timestamps `main.log` y Configuración `juego.log`**. (Se mantiene como tarea secundaria).

**A. Diseño e Implementación Sistema de Empuje Vectorial (En Pausa hasta resolver Prioridad 0):**
    1.  **Limpieza de Código (Completado):**
        *   **Acción:** Se comentó la lógica de "empuje especial promedio" en `src/sistemas/collision_handler.py`.
        *   **Estado:** Completado.
    2.  **Actualización de Documentos de Seguimiento (En Curso):**
        *   **Acción:** Modificar `dev_notes.md` y `TODO.md` para reflejar el cambio de enfoque y los hallazgos.
        *   **Estado:** `dev_notes.md` actualizado tras análisis de logs. `TODO.md` pendiente de revisión detallada. `CHANGELOG.md` pendiente.
    3.  **Investigación y Depuración (Basado en Análisis de Logs - Próximos Pasos):**
        *   **Subtarea 1: Empuje de Múltiples Enemigos:**
            *   **Objetivo:** Asegurar que múltiples enemigos cercanos empujen al jugador como se espera.
            *   **Acción:** Revisar `enemigo.py` para `Enemigo_1`. ¿Por qué `ZonaInfluenciaHB.colliderect(JugadorHB)` es `False` en los logs cuando se esperaba `True`? Analizar posiciones relativas, tamaño de `ZonaInfluenciaHB` y cualquier otra lógica condicional en `Enemigo.update_ia` o `Enemigo._intentar_empujar_jugador`.
        *   **Subtarea 2: "Temblor" del Jugador:**
            *   **Objetivo:** Eliminar el temblor del jugador al ser empujado diagonalmente.
            *   **Acción:** Investigar en `jugador.py` (método `actualizar_movimiento` o similar, después de la llamada a `_mover_y_colisionar` y la aplicación de `mantener_dentro_de_limites`) por qué la `posicion_flotante.y` del jugador es ajustada (ej., de `1779.0` a `1778.0`) de una forma que podría causar el temblor. Considerar la interacción entre las posiciones enteras de `pygame.Rect` y las posiciones flotantes internas del jugador, especialmente al aplicar límites del mundo.
            *   **Subtarea 3: Verificación del Clamp de Fuerza (Si aplica con múltiples enemigos):**
            *   **Objetivo:** Una vez que múltiples enemigos empujen, verificar que `JUGADOR_MAX_FUERZA_EMPUJE_FRAME` funcione correctamente.
            *   **Acción:** Añadir logs en `jugador.py` donde se aplica este clamp para observar su comportamiento cuando se sumen fuerzas de múltiples enemigos.
    4.  **Diseño Conceptual del Empuje Vectorial (Continuación - Preguntas Clave Persisten):**
        *   Una vez resueltos los bugs anteriores, continuar con el diseño si es necesario. Las preguntas originales siguen siendo relevantes:
            *   ¿Dónde se generarán los vectores de empuje individuales (ej. en `Enemigo.update` al detectar colisión con el jugador, o en `CollisionHandler`)?
            *   ¿Cómo se determinará la magnitud y dirección de cada vector de empuje individual (ej. basado en `ENEMIGO_VELOCIDAD`, una nueva constante `ENEMIGO_FUERZA_EMPUJE`)?
            *   ¿Cómo se comunicarán estos vectores al jugador o a la entidad que los recibe?
            *   ¿Dónde se sumarán los vectores si hay múltiples empujes simultáneos? (¿El jugador acumula fuerzas?)
            *   ¿Cómo modificará el vector de empuje resultante el movimiento del jugador? (¿Se aplica como un `dx`, `dy` adicional antes de la detección de colisiones del propio jugador, o se integra de otra forma?)
            *   ¿Se considerará la masa/resistencia del jugador en esta primera implementación? (Probablemente no, para simplificar).
        *   **Entregable:** Un esquema o descripción en `dev_notes.md` de cómo funcionará (puede evolucionar con la depuración).
    5.  **Implementación Iterativa (Continuación):**
        *   Expandir para múltiples enemigos (vinculado a Subtarea 1).
        *   Probar y refinar.

**B. Discusiones Pendientes / Mejoras de Proceso:**
    1.  **Sistema de Empuje Avanzado (Vinculado a A):**
        *   **Tema:** Una vez que el empuje vectorial básico funcione, cómo integrar "peso", "nivel" y "prioridad" de habilidades (del `DESIGN_VISION.md`).
    2.  **Documentación del Protocolo de "Plan de Acción":**
        *   **Tema:** Añadir formalmente a `DEVELOPMENT_PROTOCOLS.md` las reglas para el uso y actualización de esta sección.

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