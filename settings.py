import os

# --- Dimensiones de la Pantalla y FPS ---
# Ancho de la ventana principal del juego en píxeles.
ANCHO_PANTALLA = 800
# Alto de la ventana principal del juego en píxeles.
ALTO_PANTALLA = 600
# Fotogramas Por Segundo (Frames Per Second): A cuántas "imágenes" por segundo se actualizará el juego.
# Un valor común es 60 para una animación fluida.
FPS = 60

# --- Configuración del Zoom de la Cámara ---
# Factor de zoom inicial. Un valor mayor significa más zoom (objetos más grandes, vista más cercana).
# 1.0 = sin zoom. 2.0 = los objetos se ven el doble de grandes.
FACTOR_ZOOM_INICIAL = 2.0
# Zoom más alejado (ej: ve el doble de área que con zoom 2.0)
FACTOR_ZOOM_MIN = 1.2
# Zoom más cercano (ej: ve la mitad de área que con zoom 1.5)
FACTOR_ZOOM_MAX = 2.5
# Cuánto cambia el factor de zoom con cada "tick" de la rueda del mouse
FACTOR_ZOOM_PASO = 0.1

# El FACTOR_ZOOM_ACTUAL se manejará en main.py y se usará para calcular
# CAMARA_ANCHO y CAMARA_ALTO dinámicamente.
# Por ahora, podemos calcular un CAMARA_ANCHO/ALTO inicial si es necesario para alguna configuración inicial,
# pero la cámara deberá poder redimensionar su vista.

# --- Dimensiones de la Vista de la Cámara (calculadas) ---
# Ancho de la porción del "mundo" del juego que la cámara ve antes de aplicar el zoom.
# Si el zoom es 2x y la pantalla es 800px, la cámara ve 400px del mundo.
CAMARA_ANCHO_INICIAL = ANCHO_PANTALLA / FACTOR_ZOOM_INICIAL
CAMARA_ALTO_INICIAL = ALTO_PANTALLA / FACTOR_ZOOM_INICIAL

# --- Dimensiones del Mundo del Juego ---
# Estas definen los límites del área jugable total.
# El jugador no podrá moverse más allá de estos límites.
# Por ejemplo, 3 veces el tamaño de la pantalla.
ANCHO_MUNDO_JUEGO = ANCHO_PANTALLA * 3
ALTO_MUNDO_JUEGO = ALTO_PANTALLA * 3

# --- Definiciones de Colores (formato RGB) ---
# Los colores se definen como tuplas de (Rojo, Verde, Azul), donde cada valor va de 0 a 255.
AZUL = (0, 0, 255)
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
ROJO = (255, 0, 0)
VERDE = (0, 255, 0) # Color verde normal
VERDE_DEBUG = (0, 255, 0, 150) # Verde semitransparente para debug (RGBA)
COLOR_HITBOX = (255, 0, 0)  # Rojo para hitboxes de colisión
COLOR_ATAQUE_HITBOX = (255, 255, 0) # Amarillo para hitboxes de ataque

# Colores HUD
COLOR_HUD_TEXTO = BLANCO # Usar el blanco ya definido

# --- Rutas del Proyecto y Assets ---
# `os.path.abspath(__file__)` obtiene la ruta absoluta completa del archivo actual (settings.py).
# `os.path.dirname(...)` obtiene el directorio (carpeta) que contiene ese archivo.
# Esto asegura que RUTA_BASE_PROYECTO siempre apunte a la carpeta raíz de tu juego.
RUTA_BASE_PROYECTO = os.path.dirname(os.path.abspath(__file__))
# `os.path.join(...)` construye una ruta de manera inteligente, compatible con diferentes sistemas operativos.
# Aquí, crea la ruta a la carpeta 'assets' que está dentro de la carpeta base del proyecto.
RUTA_ASSETS = os.path.join(RUTA_BASE_PROYECTO, "assets")

# --- Configuraciones de Depuración ---
DEBUG_VER_HITBOXES = True # Poner a False para ocultar hitboxes/rects de depuración
INCREMENTO_AJUSTE_DEBUG = 2 # Píxeles o unidades a cambiar con cada pulsación para debug
INCREMENTO_DURACION_DEBUG = 10 # Milisegundos a cambiar para la duración del ataque
ARCHIVO_CONFIG_ATAQUE = "config_ataque.json" # Archivo para guardar/cargar config de ataque
NOMBRE_PERFIL_ATAQUE_INICIAL = "espada_predeterminada"

# --- Configuración Global de Logs ---
# Establecer en False para un output de log estándar (INFO) en la consola.
MODO_DEBUG_LOGS = True
LOG_LEVEL_VERBOSE = "DEBUG"  # Nivel de log cuando MODO_DEBUG_LOGS es True
LOG_LEVEL_STANDARD = "INFO"  # Nivel de log cuando MODO_DEBUG_LOGS es False
# La variable LOG_LEVEL que existía antes para el logger de main.py ya no es necesaria
# ya que se determinará con MODO_DEBUG_LOGS.

LOG_CATEGORIAS = {
    "log_general": True,
    "log_assets": False,
    "log_input": False,
    "log_jugador_mov": True,
    "log_jugador_col": True,
    "log_jugador_cmb": True,
    "log_enemigo_mov": True,
    "log_enemigo_ia": False,
    "log_enemigo_col": True,
    "log_enemigo_cmb": False,
    "log_animacion": False,
    "log_camara": False,
    "log_collision_handler": True,
    "log_event_handler": True,
    "log_event_handler_verbose": False,
    "log_gestor_estado": True,
    "log_gestor_estado_detalle": False,
}

# --- Configuración de Fuentes ---
# Define los nombres de las fuentes a usar. 
# Pueden ser nombres de fuentes del sistema (ej: "Arial", "Consolas")
# o nombres de archivos .ttf/.otf (ej: "MyCustomFont.ttf").
# Si es un nombre de archivo, DEBE estar ubicado en la carpeta assets/fonts/.
NOMBRE_FUENTE_HUD = "Arial"  # Fuente para el HUD principal (ej: información del jugador)
NOMBRE_FUENTE_DEBUG = "Consolas" # Fuente para información de depuración
TAMANO_FUENTE_HUD = 18
TAMANO_FUENTE_DEBUG = 16