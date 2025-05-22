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