# Lista de Tareas Pendientes

## Prioridad CRÍTICA
1. ✨ **[RESUELTO - COLISIONES/FÍSICAS]** Sistema de Empuje Vectorial con Fricción Implementado Satisfactoriamente.
   - **Descripción**: Se ha implementado y perfeccionado la mecánica de empuje del enemigo al jugador. El sistema de empuje por contacto basado en vectores, con la adición de un mecanismo de fricción en `jugador.py`, ha resultado en un comportamiento de deslizamiento que cumple con las expectativas del USER. Esto incluye el correcto funcionamiento del empuje en todas las direcciones, incluyendo el vertical.
   - **Estado**: ¡COMPLETADO Y VALIDADO POR EL USER! 🎉

2. 🐛 **[BUG - COLISIONES - OBSERVACIÓN]** Observar si persisten "Teletransportes / Saltos Anómalos" en `CollisionHandler`.
   - **Estado**: En observación. Se prioriza el bug de empuje vertical.
   - **Descripción Original**: Saltos de posición inesperados causados por `CollisionHandler`.

## Prioridad Alta (En Pausa Temporal)
1. 🔥 **[RENDIMIENTO]** Investigar y resolver degradación de rendimiento del IDE
   - [x] Añadir memory_profiler a requirements.txt
   - [ ] Resolver incompatibilidad con Pygame en Python 3.13.1 (TAREA PAUSADA)
     - [ ] Buscar wheel compatible para Python 3.13
     - [ ] Si no se encuentra, realizar downgrade a Python 3.11.x
   - [ ] Implementar profiling de memoria (TAREA PAUSADA)
   - [ ] Revisar gestión de recursos de Pygame (TAREA PAUSADA)
   - [ ] Optimizar ciclo de cierre del juego (TAREA PAUSADA)
   - [ ] Crear PERFORMANCE_METRICS.md para seguimiento (TAREA PAUSADA)

2. 🐛 **[BUG]** Resolver problema de empuje en colisiones
   - Corregir comportamiento en eje Y
   - Optimizar manejo de colisiones múltiples

## Prioridad Alta

### Sistema de Juego
- [ ] Implementar sistema de guardado/carga de partida
- [ ] Añadir sistema de sonido y música
- [ ] Implementar sistema de partículas para efectos visuales
- [ ] Crear sistema de diálogos para NPCs

### Optimización
- [ ] Implementar sistema de pooling para objetos frecuentes
- [ ] Optimizar el sistema de colisiones para grandes cantidades de entidades
- [ ] Mejorar el rendimiento del sistema de renderizado

### Documentación
- [ ] Completar la documentación de cada módulo con docstrings
- [ ] Crear diagramas de flujo para los sistemas principales
- [ ] Añadir ejemplos de uso para cada sistema

## Prioridad Media

### Jugabilidad
- [ ] Implementar sistema de combos para ataques
- [ ] Añadir sistema de habilidades especiales
- [ ] Crear sistema de progresión de personaje
- [ ] Implementar sistema de misiones/objetivos

### UI/UX
- [ ] Crear menú principal
- [ ] Implementar sistema de inventario
- [ ] Añadir HUD personalizable
- [ ] Crear sistema de notificaciones

### Contenido
- [ ] Diseñar más tipos de enemigos
- [ ] Crear más armas y objetos
- [ ] Implementar diferentes biomas/zonas
- [ ] Añadir más animaciones y efectos

## Prioridad Baja

### Mejoras Técnicas
- [ ] Implementar sistema de pruebas unitarias
- [ ] Añadir sistema de análisis de rendimiento
- [ ] Crear herramientas de desarrollo
- [ ] Implementar sistema de modding

### Características Adicionales
- [ ] Añadir sistema de logros
- [ ] Implementar sistema de comercio
- [ ] Crear sistema de crafting
- [ ] Añadir sistema de clima y día/noche

## En Progreso
- [ ] **[BUG - COLISIONES]** Bug "Expulsión del Jugador" (Actualmente en investigación - Prioridad CRÍTICA)
- [ ] Mejorar el sistema de colisiones
    - [x] Corregido bug mayor de teletransporte del jugador al colisionar con obstáculos (relacionado con `ajuste_final_y`).
    - [ ] Investigar y solucionar bug donde el jugador es 'expulsado' o experimenta un desplazamiento anómalo cuando es rodeado por múltiples enemigos que se mueven hacia él (posible problema en resolución de múltiples colisiones o lógica de empuje). (AHORA EN PRIORIDAD CRÍTICA)
    - [ ] (Idea a futuro) Considerar la implementación de un sistema de 'peso' o 'prioridad' para las entidades para gestionar colisiones complejas de forma más robusta.
- [ ] Refinar el sistema de animaciones
- [ ] Optimizar el sistema de eventos
- [ ] Implementación inicial de herramientas de profiling (EN PAUSA)
    - [x] Investigación y selección de memory_profiler
    - [x] Documentación de problemas de compatibilidad
    - [ ] Resolución de dependencias (Bloqueado por Pygame/Python 3.13.1 - EN PAUSA)

### Bugs Críticos Recientes
- [x] Investigar y solucionar bug que causa que el juego se cierre inesperadamente al presionar una tecla. (Prioridad Máxima - Bloqueante) - Solucionado en versión 0.2.2 protegiendo los prints de depuración y corrigiendo errores en el manejo del perfil de ataque.

## Documentación y Protocolos
- [x] Reestructurar documentación principal (README.md, DEVELOPMENT_PROTOCOLS.md).
- [x] Definir Protocolo de Sincronización y Actualización de Documentación.
- [x] Crear Cursor Rule para Asistentes IA (.cursor/rules/ai_development_protocol.mdc).
- [ ] Completar la documentación de cada módulo con docstrings.
- [ ] Crear diagramas de flujo para los sistemas principales.
- [ ] Añadir ejemplos de uso para cada sistema.

## Completado
- [x] Estructura base del proyecto
- [x] Sistema de logging
- [x] Módulo de utilidades
- [x] Documentación inicial
- [x] Sistema de modularización
- [x] Gestión de assets

## Notas
- Las tareas se pueden mover entre categorías según la prioridad
- Cada tarea completada debe ser documentada en CHANGELOG.md
- Antes de comenzar una nueva tarea, verificar dependencias
- Mantener actualizada esta lista

## Formato para Nuevas Tareas

## Tareas Pendientes (Priorizadas)

### Próxima Sesión (Después de Reinicio de IDE) -> ¡AHORA!
- **[CRÍTICA - EN CURSO] Protocolo de Limpieza y Estructura del Código:**
  - Revisar la estructura general del proyecto (directorios, módulos).
  - Aplicar buenas prácticas de codificación y organización de manera consistente.
  - Asegurar que la estructura sea clara, mantenible y fácilmente accesible para colaboración (humanos e IAs).
  - Considerar posibles refactorizaciones menores para mejorar la claridad, cohesión y acoplamiento.
  - Verificar y asegurar la correcta conexión y comunicación entre módulos.
  - **Detalles Adicionales (según feedback del USER):**
    - Identificar y mover funciones reutilizables a `src/utils/` (ej. `utils.py`).
    - Asegurar el uso consistente de variables globales/constantes desde `src/config/settings.py`.
    - Limpiar sentencias `print()`: convertirlas a logging estructurado (usando `self.logger` y categorías de `settings.LOG_CATEGORIAS`) o a prints de depuración condicionales (controlados por flags en `settings.py`).
    - Aplicar consistentemente el sistema de logging y depuración definido.
- **[ALTA] Actualización del Mapa Conceptual (`mapa_conceptual_modulos.py`):**
  - Reflejar todos los cambios recientes en la lógica y las interacciones de los módulos.
  - Especial atención a los sistemas de colisión, empuje, y movimiento de entidades.
  - Asegurar que el mapa sea un fiel reflejo del estado actual del código para guiar el desarrollo futuro.
- **[MEDIA] Revisión y Actualización Completa de Documentos de Seguimiento:**
  - Asegurar que `CHANGELOG.md`, `TODO.md` y `dev_notes.md` estén completamente actualizados y sincronizados con el estado del proyecto post-limpieza.

### En Curso / Desarrollo Activo
- **Mecánica de Empuje del Enemigo al Jugador:**
  - ~~Implementar reseteo de fuerzas de empuje en el jugador para evitar deslizamiento infinito.~~ (HECHO - Implementada fricción en su lugar)
  - **[HECHO Y RESUELTO]** ~~Empuje se siente como "ticks". Investigar y corregir para que sea un empuje más fluido o con inercia.~~ (Corregido con sistema de fricción, el USER está satisfecho).

### General (Backlog / Ideas a Futuro)
- **[MEDIA] Implementar sistema de habilidades para el jugador (y potencialmente enemigos).**
  - Definir diferentes tipos de habilidades (ataque, defensa, utilidad).
  - Crear sistema para activar y gestionar cooldowns de habilidades.
- **[MEDIA] Mejorar IA de los Enemigos:**
  - Comportamientos más variados (patrullaje, evasión, ataque coordinado si hay varios).
  - Diferentes tipos de enemigos con distintas estadísticas y patrones de ataque.
- **[BAJA] Sistema de Niveles/Escenarios:**
  - Carga de diferentes mapas o configuraciones de nivel.
  - Transiciones entre niveles o zonas.
- **[BAJA] UI y HUD Mejorado:**
  - Indicadores visuales más claros para vida, energía (si aplica), cooldowns.
  - Menús del juego (inicio, pausa, opciones).
- **[BAJA] Efectos de Sonido y Música.**

### Consideraciones de Diseño / Refactorización (A revisar durante el protocolo de limpieza)
- Evaluar la cohesión y acoplamiento de los módulos actuales (especialmente `CollisionHandler`, `EntidadBase`, `Jugador`, `Enemigo`).
- Revisar el flujo de datos y la comunicación entre `GestorEstado` y las entidades.
- Considerar la creación de un sistema de eventos más robusto si es necesario.