# Notas de Desarrollo - Estado Actual

## Última Actualización: 2025-05-20 (Fecha Actual de la Conversación)

### Estado Actual del Proyecto
- Versión: 0.3.1
- Se ha retomado el trabajo después de un reinicio del IDE, aplicando el "Protocolo de Inicialización de Contexto" (detallado en `ai_overall_conduct_and_workflow_entry.mdc` y `README.md`).
- Se reitera la importancia de mantener actualizados `dev_notes.md`, `CHANGELOG.md`, y `TODO.md` como pilares para la continuidad y el contexto del proyecto entre sesiones.
- La tarea principal actual es la resolución del bug de "Expulsión del Jugador" en el sistema de colisiones.
- Previamente se estaba trabajando en la implementación de `memory_profiler` para problemas de rendimiento del IDE, pero esta tarea está temporalmente en pausa.

### Contexto de la Sesión Actual

**Tarea Principal en Curso:**
- Bug Crítico: "Expulsión del Jugador"
  - **Descripción**: El jugador es "expulsado" o experimenta un desplazamiento anómalo cuando está rodeado por múltiples enemigos que se mueven hacia él.
  - **Hipótesis Principal**: Problema en la resolución de múltiples colisiones simultáneas y/o la lógica de empuje acumulado en `collision_handler.py`.
  - **Archivos Relevantes**:
    - `src/sistemas/collision_handler.py`
    - `src/entidades/jugador.py`
    - `src/entidades/enemigo.py`

**Progreso de la Sesión:**
1.  Se reinició la sesión de trabajo.
2.  Se está actualizando la documentación (`dev_notes.md`, `CHANGELOG.md`, `TODO.md`) para reflejar el cambio de enfoque hacia el bug de colisión.
3.  Se discutió la necesidad de limpiar la información obsoleta en `dev_notes.md` referente a problemas de rendimiento del IDE y la instalación de `memory_profiler`, ya que la prioridad ahora es el bug de colisión.

**Próximos Pasos Inmediatos:**
1.  Confirmar la correcta actualización de `dev_notes.md`, `CHANGELOG.md` y `TODO.md`.
2.  Revisar el estado actual del código relacionado con `collision_handler.py`.
3.  Analizar los logs existentes (si los hay) o planificar la generación de nuevos logs para diagnosticar el bug de expulsión.
4.  Discutir y aplicar estrategias de depuración específicas para el sistema de colisiones.

### Estado de la Documentación
-   `dev_notes.md`: En proceso de actualización crítica.
-   `CHANGELOG.md`: Necesita actualizarse para reflejar el cambio de enfoque y el estado actual.
-   `TODO.md`: Necesita actualizarse para priorizar el bug de colisión y reevaluar la tarea de profiling.
-   `README.md`, `DEVELOPMENT_PROTOCOLS.md`, `mapa_conceptual_modulos.py`: Revisar si requieren pequeñas actualizaciones contextuales.

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