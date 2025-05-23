# Protocolo de Colaboración con Jules

Este documento establece las directrices para interactuar con Jules, el agente de codificación experimental de Google, en el contexto de este proyecto. El objetivo es maximizar su utilidad y asegurar que su contribución se alinee con nuestros estándares y arquitectura.

## 1. Principios Generales

*   **Jules como Asistente:** Considerar a Jules como un asistente que puede ayudar con tareas de codificación bien definidas. No reemplaza la supervisión y revisión humana.
*   **Iteración y "Pulido":** El trabajo de Jules a menudo requerirá revisión, refinamiento y "pulido" por parte de un desarrollador humano.
*   **Documentación como Contexto:** La calidad de la documentación del proyecto (`README.md`, `DEVELOPMENT_PROTOCOLS.md`, `mapa_conceptual_modulos.py`, etc.) es crucial para que Jules entienda la base de código y los requisitos.

## 2. Preparación del Repositorio para Jules

Antes de asignar una tarea a Jules:

1.  **Sincronización:** Asegurarse de que la rama de trabajo esté actualizada con los últimos cambios (`git pull`).
2.  **Documentación Clave Actualizada:**
    *   Verificar que `README.md`, `DEVELOPMENT_PROTOCOLS.md`, `mapa_conceptual_modulos.py`, `TODO.md` y especialmente `dev_notes.md` (para el contexto más reciente) estén lo más actualizados posible.
3.  **Dependencias Claras:** Confirmar que `requirements.txt` está al día.
4.  **Entorno Limpio:** Asegurar que no haya cambios locales sin commitear que puedan interferir o confundir a Jules, a menos que la tarea sea específicamente sobre esos cambios.
5.  **`.gitignore` Correcto:** Verificar que archivos y carpetas generados (logs, venv, etc.) estén correctamente ignorados.
6.  **Logs Específicos para Depuración (Opcional):** Si la tarea para Jules es depurar un bug específico, y si se tienen logs relevantes que muestren el bug, considerar copiar estos logs a una carpeta temporal específica (ej. `temp_logs_for_jules/`) y mencionarla en el prompt para que Jules pueda analizarlos. Asegurarse de que esta carpeta temporal también esté en `.gitignore` o se elimine después.

## 3. Formulación de Prompts para Jules

La efectividad de Jules depende en gran medida de la calidad del prompt.

1.  **Claridad y Especificidad:**
    *   Ser lo más claro y específico posible. Evitar la ambigüedad.
    *   Ejemplo bueno: "En `src/entidades/jugador.py`, refactoriza la función `aplicar_daño(self, cantidad)` para que también registre un mensaje de nivel INFO usando el logger del módulo con la categoría 'log_jugador_vida' indicando la cantidad de daño recibido y la vida restante."
    *   Ejemplo malo: "Mejora el manejo de daño del jugador."
2.  **Descomposición de Tareas:**
    *   Para tareas complejas (ej. "Implementar un nuevo sistema de inventario"), descomponerlas en subtareas más pequeñas y manejables, cada una con su propio prompt.
3.  **Referencias Explícitas:**
    *   Mencionar archivos específicos (con su ruta desde la raíz del proyecto), nombres de funciones, clases y variables.
    *   Si se espera que Jules modifique o use código existente, señalarlo claramente.
4.  **Adherencia a Protocolos:**
    *   Incluir en el prompt una instrucción como: "Asegúrate de seguir las convenciones y protocolos definidos en `DEVELOPMENT_PROTOCOLS.md`."
5.  **Contexto Adicional (Opcional):**
    *   Si es relevante, proporcionar un breve contexto del problema o la razón del cambio.
    *   Se puede copiar y pegar fragmentos de código relevantes directamente en el prompt si ayuda a la especificidad.

### 3.1 Plantilla Recomendada para Prompts a Jules (Especialmente para Depuración o Tareas Complejas)

Al formular un prompt para Jules, especialmente para tareas que implican depuración, análisis de comportamiento o implementación de lógica compleja, considera la siguiente estructura para proporcionar un contexto completo:

```text
**Tarea Principal:** [Descripción clara y concisa de lo que se espera que Jules haga. Ej: Depurar bug de teletransporte del jugador, Implementar nueva habilidad de 'dash', Refactorizar función X.]

**Contexto del Problema/Objetivo:**
[Explicar brevemente el bug (comportamiento actual vs. esperado) o el objetivo de la nueva funcionalidad. Referenciar IDs de `TODO.md` si aplica. Ej: "El jugador se teletransporta inesperadamente en el eje Y al colisionar con ciertos obstáculos estáticos. Esto se observó en la sesión de logs X. El objetivo es que el jugador solo se desplace la cantidad solicitada por el input y las fuerzas de empuje, resolviendo colisiones sin saltos."]

**Comportamiento Esperado Detallado / Criterios de Éxito:**
[Describir con más detalle cómo debería funcionar o qué se considera una solución exitosa. Ej: "Tras la corrección, al mover el jugador contra un muro, solo debe detenerse o deslizarse suavemente, sin cambios bruscos de posición no solicitados. El `delta_real` devuelto por `CollisionHandler` debe ser consistente con el movimiento solicitado y las colisiones encontradas."]

**Información y Archivos Clave a Considerar:**
*   **Documentación Principal:** "Revisa `README.md` para una visión general del proyecto y `DEVELOPMENT_PROTOCOLS.md` para las convenciones de código, logging y flujo de trabajo que DEBES seguir."
*   **Mapa Conceptual:** "Consulta `mapa_conceptual_modulos.py` para entender la arquitectura general y las interacciones entre módulos."
*   **Configuraciones Globales:** "Ten en cuenta las configuraciones definidas en `src/config/settings.py`, especialmente [mencionar configuraciones relevantes si las hay, ej. `VELOCIDAD_JUGADOR`, constantes de colisión, etc.]."
*   **Notas de Desarrollo Actuales:** "El archivo `dev_notes.md` contiene el estado más reciente de la investigación y las prioridades. Presta especial atención a la sección 'PRIORIDAD 0' o la tarea relevante."
*   **Archivos de Código Fuente Principales Implicados:**
    *   `[ruta/al/archivo1.py]`: [Breve descripción de por qué es relevante o qué buscar aquí. Ej: Contiene la lógica de `gestionar_movimiento_y_colision`.]
    *   `[ruta/al/archivo2.py]`: [Ej: Define la clase Jugador y cómo se actualiza su movimiento.]
    *   ...
*   **Archivos de Diseño / Visión (si aplica):**
    *   "Consulta `[ruta/al/DESIGN_VISION.md o similar]` para entender los objetivos de diseño del efecto/mecánica [nombre del efecto/mecánica]." (Este archivo no existe actualmente, adaptar si se crea).
*   **Logs para Análisis (si se proporcionan para depuración):**
    *   "He preparado logs relevantes en la carpeta `temp_logs_for_jules/`. Analiza `[nombre_del_log_especifico.log]` para observar el comportamiento X."

**Pasos Sugeridos para el Análisis/Implementación (Opcional):**
[Si tienes una idea de cómo abordar el problema, puedes sugerir pasos. Ej:
1.  "Analiza la función `_resolver_solapamientos_estaticos_eje` en `collision_handler.py`."
2.  "Presta atención a cómo se modifica la posición de la entidad antes y después de cada ajuste por colisión."
3.  "Considera añadir logs temporales (siguiendo el protocolo de `DEBUG_PRINT_VARIABLES` o categorías de log) para rastrear el valor de `HB_Ent.y` en puntos clave."]

**Entregables Esperados:**
[Definir qué se espera como resultado. Ej: "Un parche para `collision_handler.py` que corrija el bug. Actualiza los comentarios en el código modificado para explicar los cambios. No modifiques otros archivos a menos que sea estrictamente necesario y lo justifiques."]

**Recordatorio de Protocolos:**
"Recuerda seguir estrictamente todos los protocolos de `DEVELOPMENT_PROTOCOLS.md`, incluyendo el sistema de logging, manejo de prints de depuración, y la actualización de documentación (aunque para esta tarea específica, yo me encargaré de actualizar `CHANGELOG.md` y `TODO.md` basándome en tu solución)."
```

Esta plantilla es una guía. Adapta y elimina secciones según la naturaleza y complejidad de la tarea para Jules.

## 4. Revisión del Plan de Jules

Antes de que Jules aplique cualquier cambio, generará un plan.

1.  **Comprensión de la Tarea:** ¿El plan refleja una correcta comprensión del prompt?
2.  **Alcance:** ¿Los archivos y funciones que planea modificar son los correctos? ¿El alcance es apropiado para la tarea?
3.  **Lógica Propuesta:** ¿La lógica o el enfoque que describe parece sensato y alineado con la arquitectura del proyecto?
4.  **Impacto Potencial:** ¿Hay riesgos obvios o efectos secundarios no deseados?

**No aprobar el plan si hay dudas significativas. Es mejor cancelar y refinar el prompt.**

## 5. Revisión del Código Generado por Jules ("Pulido")

Una vez que Jules aplica los cambios (tras la aprobación del plan), es **obligatorio** revisar el código.

1.  **Funcionalidad:** ¿El código hace lo que se pidió? Probarlo.
2.  **Adherencia a Protocolos y Convenciones:**
    *   ¿Sigue las convenciones de nombrado, formato, docstrings, type hints de `DEVELOPMENT_PROTOCOLS.md`?
    *   ¿Utiliza correctamente el sistema de logging, configuraciones de `settings.py`, etc.?
3.  **Lógica y Eficiencia:**
    *   ¿La lógica es correcta y robusta?
    *   ¿Hay casos límite no considerados?
    *   ¿Es razonablemente eficiente? ¿Hay redundancias o código innecesario?
4.  **Integración:** ¿Se integra bien con el resto del código?
5.  **Documentación del Código:** ¿Ha añadido o actualizado docstrings y comentarios relevantes? (Si no, el desarrollador humano debe hacerlo).
6.  **Errores o Efectos Secundarios:** ¿Ha introducido nuevos bugs?

## 6. Actualización de Documentación del Proyecto Post-Jules

Después de que los cambios de Jules hayan sido revisados, "pulidos" y verificados:

1.  **`CHANGELOG.md`**: Añadir una entrada detallando los cambios (puede mencionarse que fue "asistido por Jules").
2.  **`TODO.md`**: Marcar la tarea como completada.
3.  **`dev_notes.md`**: Registrar brevemente la tarea realizada con Jules y cualquier observación relevante sobre el proceso.
4.  **Otros Documentos:** Actualizar `mapa_conceptual_modulos.py` o `DEVELOPMENT_PROTOCOLS.md` si los cambios de Jules implican modificaciones estructurales o de convenciones.

## 7. Cuándo NO Usar Jules (o Usarlo con Extrema Cautela)

*   **Tareas de Depuración Profunda y Compleja:** Para bugs muy intrincados que requieren un entendimiento contextual profundo del flujo de ejecución y múltiples interacciones (como el actual problema de "teletransporte" en `CollisionHandler`), Jules podría no ser la herramienta más eficiente.
*   **Decisiones Arquitectónicas de Alto Nivel:** A menos que se le proporcionen directrices de diseño extremadamente detalladas, no es recomendable para tomar decisiones fundamentales sobre la arquitectura del software.
*   **Refactorizaciones Masivas sin Especificaciones Claras:** Tareas como "refactoriza todo el sistema de renderizado para que sea más rápido" son demasiado amplias y ambiguas.
*   **Código Crítico de Seguridad o Rendimiento (sin revisión exhaustiva):** Cualquier código generado por IA para áreas críticas debe ser sometido a un escrutinio humano especialmente riguroso.

## 8. Flujo de Trabajo con Git

1.  Asegurarse de estar en una rama dedicada para la tarea de Jules (ej. `feature/jules-task-xyz` o `fix/jules-bug-abc`).
2.  Permitir a Jules realizar los cambios en esta rama.
3.  Revisar y "pulir" los cambios localmente.
4.  Realizar commits de los cambios pulidos.
5.  Actualizar la documentación del proyecto.
6.  Hacer un `git push` de la rama.
7.  Crear un Pull Request para revisión (si el flujo de trabajo del proyecto lo requiere) o para fusionar a la rama principal.

Este protocolo es un punto de partida y puede evolucionar a medida que ganemos más experiencia trabajando con Jules. 