# Lista de Tareas Pendientes

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
- [ ] Mejorar el sistema de colisiones
    - [x] Corregido bug mayor de teletransporte del jugador al colisionar con obstáculos (relacionado con `ajuste_final_y`).
    - [ ] Investigar y solucionar bug donde el jugador es 'expulsado' o experimenta un desplazamiento anómalo cuando es rodeado por múltiples enemigos que se mueven hacia él (posible problema en resolución de múltiples colisiones o lógica de empuje). (Prioridad Alta)
    - [ ] (Idea a futuro) Considerar la implementación de un sistema de 'peso' o 'prioridad' para las entidades para gestionar colisiones complejas de forma más robusta.
- [ ] Refinar el sistema de animaciones
- [ ] Optimizar el sistema de eventos

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
```markdown
### [TAREA-XXX] Título de la Tarea
**Descripción**: Breve descripción de la tarea.

**Requisitos**:
- Requisito 1
- Requisito 2

**Dependencias**:
- [TAREA-YYY] Tarea de la que depende

**Notas**:
- Notas adicionales
- Consideraciones especiales
```