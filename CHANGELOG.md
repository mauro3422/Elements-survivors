# Registro de Cambios (CHANGELOG)

## [0.1.0] - 2024-03-XX

### Añadido
- Estructura base del proyecto
- Sistema de logging centralizado
- Módulo de utilidades (`utils.py`)
- Documentación completa en README.md

### Mejorado
- Modularización del código
- Sistema de documentación

### Solucionado
- Problemas de importación circular
- Errores de atributos en settings.py

## Problemas y Soluciones Documentadas

### [LOG-001] Modularización del Código
**Problema**: Código inicial estaba todo en un solo archivo, dificultando el mantenimiento y la escalabilidad.

**Solución**:
1. Creación de módulos específicos:
   - `entidad_base.py` para la clase base
   - `jugador.py` y `enemigo.py` para entidades específicas
   - `collision_handler.py` para manejo de colisiones
   - `gestor_eventos.py` para sistema de eventos
2. Implementación de un sistema de logging centralizado
3. Creación de un módulo de utilidades común

**Lecciones Aprendidas**:
- Separar responsabilidades en módulos específicos
- Usar herencia para compartir funcionalidad común
- Centralizar la configuración en `settings.py`

### [LOG-002] Sistema de Documentación
**Problema**: Falta de documentación clara sobre la estructura y convenciones del proyecto.

**Solución**:
1. Creación de README.md detallado con:
   - Estructura del proyecto
   - Guía de desarrollo
   - Convenciones de código
   - Sistemas y sus interrelaciones
2. Documentación de variables globales y configuraciones
3. Guía para la IA sobre cómo manejar nuevas funcionalidades

**Lecciones Aprendidas**:
- Documentar la estructura del proyecto
- Establecer convenciones claras
- Proporcionar ejemplos de uso

### [LOG-003] Manejo de Configuraciones
**Problema**: Variables globales dispersas y falta de consistencia en configuraciones.

**Solución**:
1. Centralización de configuraciones en `settings.py`
2. Creación de sistema de perfiles en JSON
3. Implementación de gestores de configuración

**Lecciones Aprendidas**:
- Centralizar configuraciones
- Usar archivos JSON para perfiles
- Implementar gestores específicos

### [LOG-004] Sistema de Assets
**Problema**: Falta de estructura clara para recursos del juego.

**Solución**:
1. Creación de estructura de carpetas para assets
2. Implementación de `asset_manager.py`
3. Establecimiento de convenciones de nombres

**Lecciones Aprendidas**:
- Organizar assets por tipo
- Implementar sistema de carga centralizado
- Establecer convenciones de nombres

## Notas para Futuras IAs

1. **Verificación de Sistemas**:
   - Siempre verificar todos los sistemas existentes antes de añadir nueva funcionalidad
   - Seguir las convenciones establecidas en README.md
   - Usar los sistemas existentes en lugar de crear nuevos

2. **Documentación**:
   - Mantener el CHANGELOG actualizado
   - Documentar problemas y soluciones
   - Seguir el formato establecido

3. **Configuración**:
   - Verificar `settings.py` antes de añadir nuevas variables
   - Usar el sistema de perfiles para configuraciones específicas
   - Seguir las convenciones de nombres

4. **Assets**:
   - Seguir la estructura de carpetas establecida
   - Usar las convenciones de nombres
   - Implementar a través de `asset_manager.py`

## Formato para Nuevas Entradas 

## [0.2.0] - 2024-07-29

### Añadido
- Logs organizados por sesión en subcarpetas con timestamp (ej. `logs/YYYY-MM-DD_HH-MM-SS/`).
- Filtro `DuplicateFilter` para evitar mensajes idénticos repetidos en corto tiempo.
- Opción `skip_duplicate_check` en `extra` para saltar el filtro de duplicados en logs específicos.

### Mejorado
- **Sistema de Logging Refactorizado Extensamente**:
    - Cada módulo principal ahora puede tener su propio archivo de log (controlado por `settings.MODULOS_CON_LOG_PROPIO`).
    - Estandarización: todos los módulos obtienen su logger con `logging.getLogger("nombre_del_modulo")`.
    - Todas las llamadas al logger ahora usan `extra={"categoria_log": "nombre_categoria"}` para control granular.
    - `config_logging.py` centraliza toda la configuración de logging, incluyendo formateadores, handlers y filtros.
    - Uso de `colorlog` para salida en consola con colores.
    - `CategoryFilter` compartido para activar/desactivar logs por categoría desde `settings.LOG_CATEGORIAS`.
    - `DuplicateFilter` compartido para todos los handlers.
    - Se actualizaron todos los módulos principales del juego (`main`, `juego`, `jugador`, `enemigo`, `entidad_base`, `asset_manager`, `collision_handler`, `renderer`, `camara`, `hud`, `utils`, `game_initializer`, `gestor_eventos`, `gestor_estado`, `gestor_nivel`, `entorno`, `attack_profile_manager`) para adherirse al nuevo sistema.
- Mayor robustez en la importación de `settings` en `config_logging.py`.

### Solucionado
- Múltiples instancias de filtros de logging; ahora se usa una instancia compartida para `CategoryFilter` y `DuplicateFilter`.
- Problemas con el `DuplicateFilter` no suprimiendo mensajes correctamente. 

### Documentación y Estructura del Proyecto
- **README.md Actualizado y Reestructurado Extensamente**:
    - Se movió y renombró la sección de directrices para colaboradores a "Guía Esencial para Colaboradores (IA y Humanos)", ubicándola al inicio del documento para mayor visibilidad.
    - Se expandieron significativamente las directrices para colaboradores, incluyendo:
        - Énfasis en la obligatoriedad de leer y actualizar `README.md` y `CHANGELOG.md`.
        - Reglas de desarrollo detalladas sobre la creación de nueva funcionalidad, manejo de `settings.py`, reutilización de código, y creación de nuevas entidades/sistemas.
        - Introducción de la sección "Diccionario de Código / Mapa Conceptual de Módulos" (a construir), con directrices sobre su propósito y mantenimiento (cuándo y qué actualizar).
    - Se revisó y actualizó la sección "Sistema de Logging" para reflejar la refactorización completa.
    - Se reorganizaron secciones para mejorar la claridad y el flujo del documento.
- Se estableció la práctica de mantener `README.md` y `CHANGELOG.md` como "documentos vivos". 

## [0.2.1] - 2024-05-19

### Solucionado
- **Bug Mayor de Teletransporte del Jugador**: Corregido un bug crítico donde el jugador se teletransportaba incorrectamente en el eje Y al colisionar con obstáculos y ser empujado. El problema residía en la lógica de `ajuste_final_y` dentro de `_resolver_solapamientos_estaticos_eje` en `CollisionHandler.py`, que no consideraba adecuadamente la dirección del movimiento original del input, llevando a un ajuste incorrecto.
- **Precisión en el Movimiento**: Se ajustó la lógica de movimiento del jugador para que `dx_para_colision` y `dy_para_colision` se redondeen al entero más cercano antes de pasarlos al `CollisionHandler`, pero la actualización final de la posición flotante ahora considera el `delta_real` devuelto por el `CollisionHandler` para evitar desincronizaciones y movimientos entrecortados.

### Cambiado
- Se añadieron logs detallados temporalmente en `CollisionHandler.py` y `jugador.py` para diagnosticar problemas de colisión y movimiento. Estos logs fueron posteriormente eliminados tras la identificación y corrección de los bugs.
- Se modificó `mapa_conceptual_modulos.py` para actualizar la ruta de `config_logging.py` a `src/config/config_logging.py` y `settings.py` a `src/config/settings.py`, y se agruparon conceptualmente bajo una categoría "Config".
- Se actualizó el `README.md` para reflejar la nueva ubicación de `config_logging.py`.

### Problemas Conocidos y Nuevos
- **Bug de "Expulsión" del Jugador**: Se ha observado un comportamiento donde el jugador puede ser "expulsado" o experimentar un desplazamiento anómalo y rápido cuando es rodeado por múltiples enemigos que se mueven activamente hacia él. Esto podría estar relacionado con la forma en que se resuelven múltiples colisiones simultáneas o la lógica de empuje acumulado. (Ver `TODO.md` - Prioridad Alta).
- **Bug Crítico - Cierre Inesperado del Juego**: Se ha reportado un nuevo bug donde el juego se cierra inesperadamente al presionar una tecla después de las últimas sesiones de depuración. La causa es desconocida y requiere investigación inmediata. (Ver `TODO.md` - Prioridad Máxima - Bloqueante).

### Próximos Pasos (Investigación Inmediata)
- Analizar los logs de la sesión `logs/2024-05-19_21-20-16/` (y anteriores si es necesario) para entender el bug de "expulsión".
- Intentar reproducir y diagnosticar el bug del cierre inesperado del juego.

## [0.2.2] - 2024-05-20

### Solucionado
- **Bug Crítico - Cierre Inesperado del Juego**: Resuelto el problema que causaba que el juego se cerrara inesperadamente al presionar teclas. El bug era causado por prints de depuración no protegidos en `jugador.py` y errores en la forma de acceder al perfil de ataque activo en el `AttackProfileManager`.

### Mejorado
- **Sistema de Depuración**:
  - Se añadieron variables de control en `settings.py` para todos los prints de depuración: `DEBUG_PRINT_JUGADOR_MOV_DEBUG` y `DEBUG_PRINT_JUGADOR_ATAQUE_DEBUG`.
  - Se encapsularon todos los prints de depuración con condicionales que verifican estas variables, evitando errores cuando los prints están presentes pero desactivados.

- **Gestión de Errores**:
  - Se mejoró el manejo de excepciones en `gestor_eventos.py` para capturar y loguear errores durante el procesamiento de eventos sin interrumpir el juego.
  - Se corrigió la forma en que se accede a los parámetros de ataque en `jugador.py`, utilizando el método correcto `get_parametro_ataque_activo()` en lugar de intentar acceder directamente al objeto del perfil.

### Problemas Conocidos
- **Bug de "Expulsión" del Jugador**: Continúa presente el comportamiento donde el jugador es "expulsado" cuando está rodeado por múltiples enemigos en movimiento. Se mantiene como próxima prioridad de investigación.

### Próximos Pasos
- Investigar y solucionar el bug de "expulsión" del jugador.
- Considerar la implementación de un sistema de "peso" o "prioridad" para las entidades en las colisiones. 

## [0.3.0] - 2025-05-19

### Añadido
- **Protocolos de Desarrollo Detallados**:
    - Se creó el archivo `DEVELOPMENT_PROTOCOLS.md` que consolida y expande todas las guías de desarrollo, colaboración con IA, manejo de documentación, sistemas de logging, depuración, y convenciones del proyecto.
    - Se definió un "Protocolo de Sincronización y Actualización de Documentación al Cierre de Sesión/Hito" dentro de `DEVELOPMENT_PROTOCOLS.md`.
- **Cursor Rule para Asistentes IA**:
    - Se generó el archivo `.cursor/rules/ai_development_protocol.mdc` con directrices específicas para la IA, basadas en los protocolos establecidos, para mejorar la comprensión del código y la autonomía informada. Incluye referencias directas (mdc:) a los archivos de documentación clave.
- **Archivo de Notas de Desarrollo**:
    - Se ha establecido la práctica de usar `dev_notes.md` para mantener un registro del estado del trabajo entre sesiones (se creará si no existe).

### Mejorado
- **Estructura de la Documentación Principal**:
    - `README.md` fue significativamente simplificado para servir como una introducción general al proyecto, con enlaces prominentes a `DEVELOPMENT_PROTOCOLS.md` para detalles de desarrollo.
    - Se migraron secciones extensas de `README.md` (Guía Esencial, Reglas de Desarrollo, Guía de Desarrollo, Protocolos de Depuración, etc.) al nuevo `DEVELOPMENT_PROTOCOLS.md`.
- **Claridad en la Colaboración con IA**:
    - Los protocolos ahora especifican claramente cómo la IA debe obtener contexto, interactuar con los archivos del proyecto, y mantener actualizada la documentación.

### Cambiado
- La fecha de las entradas anteriores en `CHANGELOG.md` que usaban "2025" (específicamente las versiones 0.2.1 y 0.2.2) ha sido actualizada a "2024" para reflejar el año correcto en que ocurrieron esos cambios, manteniendo la consistencia con el resto del historial del proyecto. 