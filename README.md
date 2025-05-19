# Juego Pygame Modular

**Nota Importante:** Este README es un documento vivo y evoluciona con el proyecto. Se actualizará continuamente para reflejar los cambios más recientes en la arquitectura, funcionalidades clave, y las mejores prácticas aprendidas. Se espera que futuras IAs y desarrolladores consulten y contribuyan a este documento.

## Guía Esencial para Colaboradores (IA y Humanos)

Esta sección es fundamental para cualquier colaborador, ya sea una IA o un desarrollador humano. Su propósito es asegurar la coherencia, mantenibilidad y comprensión del proyecto a medida que evoluciona.

**Principios Clave:**

*   **Documentación Activa:** Este `README.md` y el archivo `CHANGELOG.md` son documentos vivos. **Es obligatorio leerlos antes de realizar cualquier cambio significativo y actualizarlos después de implementar dichos cambios.**
    *   El `README.md` debe reflejar el estado actual de la arquitectura, los sistemas principales y las convenciones de desarrollo.
    *   El `CHANGELOG.md` debe registrar todas las nuevas características, correcciones de errores importantes y cambios que rompan la compatibilidad, versionando adecuadamente el proyecto.
*   **Comunicación y Comprensión:** Antes de añadir nueva funcionalidad o modificar sistemas existentes, asegúrate de entender cómo encaja en el panorama general del proyecto.

**Reglas de Desarrollo:**

1.  **Antes de crear nueva funcionalidad:**
    *   Verificar si existe un sistema similar o si la funcionalidad puede integrarse en uno existente.
    *   Revisar `settings.py` para configuraciones existentes o relevantes.
    *   Seguir las convenciones de nombres y estructuras establecidas en este `README.md`.
    *   Priorizar el uso y extensión de los sistemas existentes sobre la creación de nuevos redundantes.
2.  **Al añadir nuevas características:**
    *   Documentar la nueva característica y su uso en este `README.md`, actualizando o creando las secciones pertinentes.
    *   Actualizar `settings.py` si la nueva característica introduce nuevas configuraciones globales o modifica existentes.
    *   Mantener la consistencia con los patrones de diseño y la arquitectura de los sistemas existentes.
    *   Utilizar las funciones de utilidad de `utils.py` para tareas comunes siempre que sea posible.
3.  **Para cualquier nueva entidad o sistema que se cree:**
    *   Verificar si necesita integrarse con el sistema de animaciones.
    *   Verificar si necesita archivos de configuración específicos (ej. JSON en `config/`).
    *   Verificar si necesita un manejo de estados a través de `gestor_estado.py`.
    *   Verificar si necesita interactuar con el sistema de colisiones (`collision_handler.py`).
    *   Verificar si necesita emitir o escuchar eventos a través de `gestor_eventos.py`.
    *   Verificar si necesita cargar assets a través de `asset_manager.py`.
    *   Seguir las convenciones de nombres y estructuras de directorios correspondientes.

**Diccionario de Código / Mapa Conceptual de Módulos:**

*   **Propósito:** Esta sección (a construir y mantener) servirá como un glosario de los principales módulos, clases y sistemas del juego. Describirá brevemente la responsabilidad de cada uno y cómo interactúan entre sí. El objetivo es proporcionar una visión general rápida que facilite la incorporación de nuevos colaboradores y la comprensión de la arquitectura del código.
*   **Mantenimiento:** Este diccionario es un esfuerzo manual y colaborativo.
    *   **Cuándo actualizar:** Se debe actualizar siempre que:
        *   Se añada un nuevo módulo principal al proyecto.
        *   Se elimine un módulo principal existente.
        *   Se refactorice un módulo existente de tal manera que su propósito central, sus responsabilidades clave o sus interacciones principales con otros módulos cambien significativamente.
        La actualización de esta sección debe considerarse parte integral del conjunto de cambios (commit/pull request) que introduce la modificación en el código. No se recomienda un umbral numérico fijo (ej. "cada X cambios"), sino un juicio basado en el impacto del cambio en la arquitectura general.
    *   **Qué actualizar (Nivel de Detalle):** El foco debe estar en:
        *   La **responsabilidad principal** del módulo (ej. "¿Qué hace `collision_handler.py`?").
        *   Sus **interacciones clave** con otros módulos principales (ej. "`collision_handler.py` es utilizado por `juego.py` y opera sobre instancias de `entidad_base.py`").
        No es necesario ni recomendable listar todas las funciones internas, clases secundarias o variables de un módulo. El objetivo es mantener una visión general conceptual, no un reflejo detallado del código.

## Estructura del Proyecto

### Módulos Principales

#### Core
- `main.py`: Punto de entrada principal del juego
- `juego.py`: Clase principal que maneja el bucle del juego
- `settings.py`: Configuraciones globales del juego
- `config.py`: Configuraciones adicionales
- `config_logging.py`: Configuración del sistema de logging

#### Entidades
- `entidad_base.py`: Clase base para todas las entidades del juego
- `jugador.py`: Implementación del jugador
- `enemigo.py`: Implementación de enemigos
- `entorno.py`: Elementos del entorno del juego

#### Sistemas
- `collision_handler.py`: Sistema de detección y resolución de colisiones
- `gestor_eventos.py`: Sistema de manejo de eventos
- `gestor_estado.py`: Sistema de estados del juego
- `gestor_nivel.py`: Sistema de gestión de niveles
- `attack_profile_manager.py`: Sistema de perfiles de ataque

#### Renderizado
- `renderer.py`: Sistema de renderizado
- `hud.py`: Interfaz de usuario
- `camara.py`: Sistema de cámara

#### Utilidades
- `utils.py`: Funciones de utilidad comunes
- `asset_manager.py`: Gestión de recursos (imágenes, sonidos, etc.)

### Estructura de Carpetas
```
├── assets/              # Recursos del juego
│   ├── images/         # Imágenes y sprites
│   ├── sounds/         # Efectos de sonido y música
│   └── fonts/          # Fuentes
├── src/                # Código fuente
└── tests/             # Pruebas unitarias
```

## Guía de Desarrollo

### Sistemas y sus Interrelaciones

1. **Sistema de Logging (Refactorizado V. 0.2.0)**:
   - **Filosofía**: El sistema de logging está diseñado para ser centralizado, configurable y ofrecer control granular sobre los mensajes, facilitando tanto el desarrollo como la depuración.
   - **Configuración Central**: Toda la configuración del sistema de logging reside en `config_logging.py`. Esto incluye la definición de formateadores (para consola y archivos), handlers (stream para consola con `colorlog`, y `RotatingFileHandler` para archivos), y filtros (`CategoryFilter`, `DuplicateFilter`).
   - **Obtención de Loggers**: Cada módulo debe obtener su logger específico usando `logger = logging.getLogger("nombre_del_modulo")`. Por ejemplo, en `jugador.py` se usa `logging.getLogger("jugador")`. Esto permite que los logs se asocien correctamente con su origen.
   - **Logs por Módulo y Sesión**: 
     - Los logs de los módulos listados en `settings.MODULOS_CON_LOG_PROPIO` se guardan en archivos individuales dentro de una carpeta de sesión (ej. `logs/YYYY-MM-DD_HH-MM-SS/nombre_del_modulo.log`).
     - Los logs de módulos no listados allí (o si el handler específico falla) van a un archivo `general.log` dentro de la misma carpeta de sesión.
   - **Categorías de Log y Control de Activación**:
     - Las categorías de log (ej. `"log_jugador_mov"`, `"log_assets"`) se definen y activan/desactivan en el diccionario `settings.LOG_CATEGORIAS`.
     - Para asignar una categoría a un mensaje, se usa el parámetro `extra` en la llamada al logger: `logger.debug("Mensaje", extra={"categoria_log": "nombre_categoria"})`.
     - El `CategoryFilter` utiliza `settings.LOG_CATEGORIAS` y `settings.MODO_DEBUG_LOGS` para decidir si un mensaje de una categoría particular debe procesarse.
     - `settings.MODO_DEBUG_LOGS = True` habilita un nivel de log más verboso (DEBUG), mientras que `False` usa un nivel estándar (INFO).
   - **Filtro de Duplicados (`DuplicateFilter`)**:
     - Suprime automáticamente mensajes de log idénticos que ocurren repetidamente dentro de un breve intervalo de tiempo (configurable mediante `settings.LOG_DUPLICATE_MESSAGE_TIMEDELTA_MS`).
     - Se puede omitir este filtro para un mensaje específico añadiendo `"skip_duplicate_check": True` al diccionario `extra`: `logger.info("Mensaje importante que no debe filtrarse", extra={"categoria_log": "log_general", "skip_duplicate_check": True})`.
   - **Niveles de Log Estándar**: DEBUG, INFO, WARNING, ERROR, CRITICAL.
   - **Ejemplo de Uso Completo**:
     ```python
     # En un módulo, por ejemplo, mi_modulo.py
     import logging
     import settings

     logger = logging.getLogger("mi_modulo") # Obtener logger específico del módulo

     def alguna_funcion():
         # Este mensaje solo se registrará si MODO_DEBUG_LOGS es True Y LOG_CATEGORIAS["categoria_especifica"] es True
         logger.debug("Este es un mensaje de debug detallado.", extra={"categoria_log": "categoria_especifica"})
         
         logger.info("Información general de la función.", extra={"categoria_log": "log_general"})
         
         if error_condicion:
             logger.error("Ocurrió un error.", extra={"categoria_log": "log_errores"})

     # En settings.py, asegúrate de tener:
     # LOG_CATEGORIAS = {
     #     "categoria_especifica": True, 
     #     "log_general": True,
     #     "log_errores": True,
     #     # ...otras categorías...
     # }
     # MODULOS_CON_LOG_PROPIO = [..., "mi_modulo", ...]
     ```

2. **Sistema de Animaciones**:
   - Ubicación: `animaciones/`
   - Cualquier entidad con animaciones debe:
     - Definir sus estados en `settings.py` bajo `ANIMACIONES_[TIPO_ENTIDAD]`
     - Usar `asset_manager.py` para cargar sprites
     - Implementar `actualizar_animacion()` y `dibujar_animacion()`
   - Formato de nombres de animaciones: `[tipo_entidad]_[estado]_[frame].png`
   - Ejemplo:
     ```python
     # En settings.py
     ANIMACIONES_ENTIDAD = {
         "idle": {"frames": 4, "duracion": 0.5},
         "run": {"frames": 6, "duracion": 0.4},
         "action": {"frames": 3, "duracion": 0.2}
     }
     ```

3. **Sistema de Perfiles y Configuraciones**:
   - Ubicación: `config/`
   - Cualquier entidad con configuración específica debe:
     - Tener un perfil en `config_[tipo].json`
     - Implementar las animaciones correspondientes
     - Usar el gestor de perfiles correspondiente
   - Formato de nombres: `[tipo_entidad]_[variante].json`
   - Ejemplo:
     ```json
     {
         "nombre": "entidad_variante",
         "estadisticas": {
             "vida": 100,
             "velocidad": 1.0
         },
         "animaciones": {
             "idle": "entidad_idle",
             "action": "entidad_action"
         }
     }
     ```

4. **Sistema de Estados**:
   - Ubicación: `gestor_estado.py`
   - Cualquier entidad con estados debe:
     - Definir sus estados en una enumeración
     - Implementar `cambiar_estado()`
     - Usar `gestor_estado.py` para transiciones
   - Ejemplo:
     ```python
     class EstadosEntidad(Enum):
         IDLE = "idle"
         MOVIENDOSE = "moving"
         ACCION = "action"
     ```

5. **Sistema de Colisiones**:
   - Ubicación: `collision_handler.py`
   - Cualquier entidad colisionable debe:
     - Definir su hitbox en `settings.py` bajo `[TIPO_ENTIDAD]_HITBOX_*`
     - Implementar `obtener_hitbox()`
     - Registrar en `collision_handler.py`
   - Tipos de colisión:
     - `COLISION_ESTATICA`: Para objetos estáticos
     - `COLISION_DINAMICA`: Para entidades móviles
     - `COLISION_ACCION`: Para áreas de acción/interacción

6. **Sistema de Eventos**:
   - Ubicación: `gestor_eventos.py`
   - Cualquier sistema que necesite comunicación debe:
     - Definir sus eventos en `settings.py` bajo `EVENTOS_[TIPO]`
     - Usar `registrar_evento()` y `despachar_evento()`
   - Ejemplo:
     ```python
     # En settings.py
     EVENTOS_ENTIDAD = {
         "ENTIDAD_ACCION": "entidad_accion",
         "ENTIDAD_ESTADO": "entidad_estado"
     }
     ```

7. **Sistema de Assets**:
   - Ubicación: `asset_manager.py`
   - Estructura de carpetas:
     ```
     assets/
     ├── images/
     │   ├── entidades/
     │   │   ├── [tipo_entidad]/
     │   │   └── [otro_tipo]/
     │   ├── objetos/
     │   ├── efectos/
     │   └── ui/
     ├── sounds/
     │   ├── efectos/
     │   └── musica/
     └── fonts/
     ```
   - Convenciones de nombres:
     - Imágenes: `[tipo]_[estado]_[frame].png`
     - Sonidos: `[tipo]_[efecto].wav`
     - Fuentes: `[nombre]_[estilo].ttf`

8. **Reglas para la IA**:
   - Antes de crear nueva funcionalidad:
     1. Verificar si existe un sistema similar
     2. Revisar `settings.py` para configuraciones existentes
     3. Seguir las convenciones de nombres establecidas
     4. Usar los sistemas existentes en lugar de crear nuevos

### Manejo de Variables Globales y Configuraciones

1. **Variables Globales**:
   - Todas las variables globales deben estar en `settings.py`
   - Las variables se organizan por categorías con comentarios claros
   - Formato: `NOMBRE_VARIABLE = valor  # Descripción breve`
   - Ejemplo:
     ```python
     # --- Configuración del Jugador ---
     VIDA_MAXIMA_JUGADOR = 100  # Vida inicial del jugador
     VELOCIDAD_JUGADOR = 180    # Píxeles por segundo
     ```

2. **Nuevas Configuraciones**:
   - Añadir nuevas variables en la categoría correspondiente en `settings.py`
   - Si no existe una categoría apropiada, crear una nueva con un comentario descriptivo
   - Mantener el formato de nombres en MAYÚSCULAS
   - Documentar el propósito y unidades de la variable

3. **Perfiles de Configuración**:
   - Configuraciones específicas de entidades van en archivos JSON en la carpeta `config/`
   - Ejemplo: `config_ataque.json` para perfiles de ataque
   - Usar `utils.cargar_json()` y `utils.guardar_json()` para manejar estos archivos

4. **Constantes por Módulo**:
   - Si un módulo necesita constantes específicas, definirlas al inicio del archivo
   - Documentar con comentarios el propósito de cada constante
   - Mantener consistencia con el estilo de `settings.py`

5. **Reglas para la IA**:
   - Siempre verificar `settings.py` antes de crear nuevas variables globales
   - Usar las funciones de `utils.py` para manejar configuraciones
   - Mantener la consistencia en el nombramiento y documentación
   - Seguir el patrón de organización existente

### Añadir Nuevas Funcionalidades

1. **Nuevas Entidades**:
   - Heredar de `entidad_base.py`
   - Implementar métodos requeridos
   - Registrar en el sistema de colisiones si es necesario

2. **Nuevas Utilidades**:
   - Añadir funciones en `utils.py`
   - Documentar con docstrings
   - Incluir tipos con type hints

3. **Nuevos Sistemas**:
   - Crear nuevo módulo en la carpeta correspondiente
   - Implementar interfaz clara
   - Registrar en `juego.py` si es necesario

### Convenciones de Código

1. **Nombres**:
   - Clases: PascalCase
   - Funciones y variables: snake_case
   - Constantes: MAYÚSCULAS_CON_GUIONES_BAJOS

2. **Documentación**:
   - Docstrings en todas las funciones y clases
   - Type hints para todos los parámetros y retornos
   - Comentarios explicativos para lógica compleja

3. **Logging**:
   - Usar el sistema de logging configurado
   - Niveles apropiados (DEBUG, INFO, WARNING, ERROR, CRITICAL)
   - Mensajes descriptivos

### Debugging

1. **Herramientas de Debug**:
   - Funciones en `utils.py` para visualización
   - Sistema de logging configurable
   - Hitboxes visibles en modo debug

2. **Modo Debug**:
   - Activar en `settings.py`
   - Mostrar información adicional
   - Visualizar hitboxes y otros elementos de debug

## Contribución

1. **Nuevas Características**:
   - Crear rama feature/nombre-caracteristica
   - Implementar cambios
   - Añadir documentación
   - Crear pull request

2. **Correcciones**:
   - Crear rama fix/nombre-fix
   - Implementar corrección
   - Añadir tests si es necesario
   - Crear pull request

## Instalación y Ejecución

1. **Requisitos**:
   - Python 3.8+
   - Pygame 2.0+
   - Dependencias listadas en requirements.txt

2. **Instalación**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Ejecución**:
   ```bash
   python main.py
   ``` 