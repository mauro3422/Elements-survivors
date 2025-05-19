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