# Juego Pygame Modular

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

1. **Sistema de Logging**:
   - Configuración central en `config_logging.py`
   - Cada módulo debe usar: `logger = logging.getLogger(__name__)`
   - Categorías de log definidas en `settings.py` bajo `LOG_CATEGORIAS`
   - Niveles de log: DEBUG, INFO, WARNING, ERROR, CRITICAL
   - Ejemplo de uso:
     ```python
     logger.debug("Mensaje de debug", extra={"categoria": "log_entidad_mov"})
     logger.info("Mensaje informativo")
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
   - Al añadir nuevas características:
     1. Documentar en el README
     2. Actualizar `settings.py` si es necesario
     3. Mantener consistencia con sistemas existentes
     4. Usar las utilidades de `utils.py`
   - Para cualquier nueva entidad o sistema:
     1. Verificar si necesita animaciones
     2. Verificar si necesita configuración específica
     3. Verificar si necesita estados
     4. Verificar si necesita colisiones
     5. Verificar si necesita eventos
     6. Verificar si necesita assets
     7. Seguir las convenciones de nombres correspondientes

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