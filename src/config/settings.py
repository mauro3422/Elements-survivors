import os
import pygame

# --- Dimensiones de la Pantalla y FPS ---
# Ancho de la ventana principal del juego en píxeles.
ANCHO_PANTALLA = 800
# Alto de la ventana principal del juego en píxeles.
ALTO_PANTALLA = 600
# Fotogramas Por Segundo (Frames Per Second): A cuántas "imágenes" por segundo se actualizará el juego.
# Un valor común es 60 para una animación fluida.
FPS = 60

# --- Título del Juego ---
TITULO_VENTANA = "Prueba Juego 2D"

# --- Configuración del Jugador ---
VIDA_MAXIMA_JUGADOR = 100 # Ejemplo, ajustar según necesidad
VELOCIDAD_JUGADOR = 180 # Unidades por segundo
JUGADOR_HITBOX_OFFSET_X = 4 # Offset horizontal para el hitbox del jugador
JUGADOR_HITBOX_OFFSET_Y = 6 # Offset vertical superior para el hitbox del jugador
JUGADOR_HITBOX_AJUSTE_INFERIOR = 4 # Ajuste adicional para la parte inferior del hitbox del jugador
JUGADOR_RETRASO_ANIM_DESCANSO = 150 # ms entre frames de animación de descanso
JUGADOR_DANO_BASE_ATAQUE = 5
JUGADOR_COOLDOWN_ATAQUE = 700 # ms

# --- Configuración Base de Parámetros de Ataque (usados como fallback si no están en perfil) ---
ATAQUE_BASE_OFFSET_DISTANCIA = 25.0
ATAQUE_BASE_EXTENSION = 30.0
ATAQUE_BASE_GROSOR = 15.0
ATAQUE_BASE_DURACION_TOTAL_MS = 300.0
ATAQUE_BASE_PLANTILLA_ANGULOS_GRADOS = [-45, -22, 0, 22, 45] # Actualizado para el perfil por defecto del APM
ATAQUE_BASE_DANO_MODIFICADOR = 1.0
ATAQUE_BASE_COOLDOWN_MODIFICADOR = 1.0

# --- Configuración del Enemigo ---
ENEMIGO_VIDA_MAXIMA = 5
ENEMIGO_VELOCIDAD = 70  # Unidades (píxeles) por segundo
ENEMIGO_HITBOX_OFFSET_X = 3
ENEMIGO_HITBOX_OFFSET_Y = 3
ENEMIGO_DANO_ATAQUE = 1 # Daño que hace el enemigo (si tuviera un ataque explícito)
ENEMIGO_RANGO_AGRO = 200 # Distancia a la que el enemigo detecta y persigue al jugador
ENEMIGO_DIST_MIN_JUGADOR = 22 # Distancia mínima que el enemigo intenta mantener con el jugador
ENEMIGO_DANO_CONTACTO_DEFAULT = 10 # Daño por defecto que inflige un enemigo por contacto

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
COLOR_FONDO_DEFAULT = (100, 100, 100) # Gris oscuro, tomado de config.py

# Colores HUD
COLOR_HUD_TEXTO = BLANCO # Usar el blanco ya definido

# --- Rutas del Proyecto y Assets ---
# `os.path.abspath(__file__)` obtiene la ruta absoluta completa del archivo actual (settings.py).
# `os.path.dirname(...)` obtiene el directorio (carpeta) que contiene ese archivo.
# Esto asegura que RUTA_BASE_PROYECTO siempre apunte a la carpeta raíz de tu juego.
RUTA_BASE_PROYECTO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# `os.path.join(...)` construye una ruta de manera inteligente, compatible con diferentes sistemas operativos.
# Aquí, crea la ruta a la carpeta 'assets' que está dentro de la carpeta base del proyecto.
RUTA_ASSETS = os.path.join(RUTA_BASE_PROYECTO, "assets")
RUTA_DATOS_PERFILES_ATAQUE = os.path.join(RUTA_ASSETS, "data", "attack_profiles") # NUEVA CONSTANTE
RUTA_NIVEL_1 = os.path.join(RUTA_ASSETS, "data", "niveles", "nivel_1.json") # RUTA PARA EL NIVEL 1

# --- Configuraciones de Depuración ---
DEBUG_VER_HITBOXES = True # Poner a False para ocultar hitboxes/rects de depuración
INCREMENTO_AJUSTE_DEBUG = 2 # Píxeles o unidades a cambiar con cada pulsación para debug
INCREMENTO_DURACION_DEBUG = 10 # Milisegundos a cambiar para la duración del ataque
ARCHIVO_CONFIG_ATAQUE = "config_ataque.json" # Archivo para guardar/cargar config de ataque
NOMBRE_PERFIL_ATAQUE_INICIAL = "espada_predeterminada"
DEBUG_PRINT_GESTION_DANO = True # Activa/desactiva prints relacionados con la recepción y gestión de daño
DEBUG_PRINT_ENTORNO = True # Activa/desactiva prints generales de la creación y estado de Obstaculos
DEBUG_PRINT_ENTORNO_ANIM = False # Activa/desactiva prints de cada frame de animación de Obstaculos (muy verboso)
DEBUG_PRINT_JUGADOR_ATAQUE_CALCULO = False # Activa/desactiva prints del cálculo del hitbox de ataque del jugador
DEBUG_PRINT_JUGADOR_RECIBIR_DANO_INFO = False # Activa/desactiva prints cuando el jugador recibe daño

# --- Configuración Global de Logs ---
# Establecer en False para un output de log estándar (INFO) en la consola.
MODO_DEBUG_LOGS = False
LOG_LEVEL_VERBOSE = "DEBUG"  # Nivel de log cuando MODO_DEBUG_LOGS es True
LOG_LEVEL_STANDARD = "INFO"  # Nivel de log cuando MODO_DEBUG_LOGS es False
# La variable LOG_LEVEL que existía antes para el logger de main.py ya no es necesaria
# ya que se determinará con MODO_DEBUG_LOGS.

LOG_CATEGORIAS = {
    "log_general": True,
    "log_assets": False,
    "log_input": True,
    "log_jugador_mov": True,
    "log_jugador_col": True,
    "log_jugador_cmb": True,
    "log_jugador_general": True,
    "log_enemigo_mov": True,
    "log_enemigo_ia": True,
    "log_enemigo_col": True,
    "log_enemigo_cmb": False,
    "log_enemigo_general": True,
    "log_animacion": False,
    "log_camara": False,
    "log_collision_handler": True,
    "log_event_handler": True,
    "log_event_handler_verbose": False,
    "log_gestor_estado": True,
    "log_gestor_estado_detalle": False,
    "log_render": True,
    "log_render_verbose": False,
    "log_render_hitbox": False,
    "log_camara_verbose": False,
    "log_apm": True,
    "log_initializer": True,
    "log_entidad_base": True,
    "log_gestor_nivel": True,
    "log_gestor_nivel_detalle": False,
    "log_entorno": True,
}

# Nueva constante para el filtro de duplicados
LOG_DUPLICATE_MESSAGE_TIMEDELTA_MS = 50 # Milisegundos. Mensajes idénticos dentro de este tiempo se suprimen.

# Lista de nombres de loggers que tendrán su propio archivo de log en la carpeta 'logs/'
# Estos nombres idealmente coincidirán con los nombres de los módulos (ej., "juego" para juego.py)
MODULOS_CON_LOG_PROPIO = [
    "juego",
    "main", # Para logs del script principal
    "renderer",
    "jugador",
    "enemigo",
    "asset_manager",
    "collision_handler",
    "gestor_eventos",
    "gestor_estado",
    "gestor_nivel",
    "camara",
    "hud",
    "entidad_base",
    "utils", # Si decidimos que utils también necesita logs específicos
    "attack_profile_manager",
    "game_initializer",
    "entorno",
]

# --- Configuración de Fuentes ---
# Define los nombres de las fuentes a usar. 
# Pueden ser nombres de fuentes del sistema (ej: "Arial", "Consolas")
# o nombres de archivos .ttf/.otf (ej: "MyCustomFont.ttf").
# Si es un nombre de archivo, DEBE estar ubicado en la carpeta assets/fonts/.
NOMBRE_FUENTE_HUD = "Arial"  # Fuente para el HUD principal (ej: información del jugador)
NOMBRE_FUENTE_DEBUG = "Consolas" # Fuente para información de depuración
TAMANO_FUENTE_HUD = 18
TAMANO_FUENTE_DEBUG = 16

# --- Configuraciones de Renderizado de Depuración ---
HITBOX_COLOR_COLISION = ROJO # Ya definido
HITBOX_COLOR_RECT_SPRITE = AZUL # Ya definido
HITBOX_COLOR_ATAQUE = COLOR_ATAQUE_HITBOX # Ya definido (amarillo)

GROSOR_HITBOX_COLISION_DEBUG = 1
GROSOR_RECT_SPRITE_DEBUG = 1 # Para el rect del sprite si se dibuja separado del hitbox
GROSOR_HITBOX_ATAQUE_DEBUG = 2

# --- Configuraciones de Layout del HUD de Depuración ---
HUD_PADDING_X = 10
HUD_PADDING_Y = 10
HUD_LINE_HEIGHT = 20
HUD_ESPACIO_ENTRE_SECCIONES = 25 # Espacio entre la info general y la lista de categorías

# --- Constantes de Gameplay/Física ---
UMBRAL_MOV_FLOTANTE_ENTIDAD = 0.0001 # Para evitar micro-movimientos por errores de precisión flotante
FACTOR_UMBRAL_TELETRANSPORTACION = 1.5 # Factor para calcular el umbral de detección de teletransportación
MAX_PASADAS_RESOLUCION_ESTATICA = 2 # Número máximo de pasadas para resolver solapamientos estáticos

# Corrección: Obtener la ruta del directorio que contiene 'src' (es decir, la raíz del proyecto)
# Asumiendo que settings.py está en src/config/settings.py
RUTA_BASE_PROYECTO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print(f"Ruta base del proyecto configurada en settings: {RUTA_BASE_PROYECTO}")

# Dimensiones de la pantalla y FPS
ANCHO_PANTALLA = 800
ALTO_PANTALLA = 600
FPS = 60
TILE_SIZE = 32 # Tamaño de los tiles, si se usa un sistema de grillas

# Colores básicos
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
ROJO = (255, 0, 0)
VERDE = (0, 255, 0)
AZUL = (0, 0, 255)
ROJO_ERROR_ASSET = (255, 0, 128) # Un color distintivo para assets faltantes

# Rutas a assets (Imágenes, Sonidos, Fuentes, Datos JSON, etc.)
RUTA_ASSETS = os.path.join(RUTA_BASE_PROYECTO, "assets")
RUTA_IMAGENES = os.path.join(RUTA_ASSETS, "images")
RUTA_SONIDOS = os.path.join(RUTA_ASSETS, "sounds")
RUTA_FUENTES = os.path.join(RUTA_ASSETS, "fonts")
RUTA_DATOS = os.path.join(RUTA_ASSETS, "data")
RUTA_PERFILES_ATAQUE = os.path.join(RUTA_DATOS, "attack_profiles")
print(f"Assets path: {RUTA_ASSETS}")
print(f"Attack profiles path: {RUTA_PERFILES_ATAQUE}")

# Configuraciones de Logging Detallado (Control por Categorías)
MODO_DEBUG_LOGS = False # True para activar logs de DEBUG según categorías, False para INFO global

# Mapeo de categorías de log a su estado (True para activado, False para desactivado)
# Solo se aplica si MODO_DEBUG_LOGS es True.
# Si MODO_DEBUG_LOGS es False, el nivel global será INFO y estas categorías no tendrán efecto individualmente
# para logs de nivel DEBUG, aunque sí podrían usarse para filtrar logs de nivel INFO o superior si la
# configuración de logging lo permite (actualmente no está configurado así).
LOG_CATEGORIAS = {
    "log_general": True,
    "log_asset_manager": True,
    "log_entidad_base": True, 
    "log_jugador": True,
    "log_enemigo": True,
    "log_entorno": True,
    "log_collision_handler": True,
    "log_attack_profile_manager": True,
    "log_game_initializer": True,
    "log_gestor_estado": True, 
    "log_hud": True,
    "log_renderer": True,
    "log_camara": True,
    "log_game_loop": True, # Para el bucle principal en juego.py
    "log_event_handler": True,
    "log_event_handler_verbose": False,
    # ... añadir más categorías según sea necesario
}

# Módulos que deben tener su propio logger con un nivel específico si MODO_DEBUG_LOGS es True.
# El formato es "nombre_modulo_o_logger": "NIVEL_LOGGING" (ej. "DEBUG", "INFO")
# Esto es más para un control ultra-fino si fuera necesario, no se usa activamente ahora.
MODULOS_CON_LOG_PROPIO = {
    # "mi_modulo_especial": "DEBUG",
}

# --- Configuraciones del Juego ---
TITULO_VENTANA = "Mi Juego Pygame"

# --- Configuraciones del Jugador ---
JUGADOR_VELOCIDAD = 200  # Pixeles por segundo
JUGADOR_VIDA_MAXIMA = 100
JUGADOR_DANO_BASE_ATAQUE = 10 # Daño base que se usa si el perfil no especifica uno.
JUGADOR_HITBOX_OFFSET_X = 5
JUGADOR_HITBOX_OFFSET_Y = 20 # Para que el hitbox esté más abajo, en los pies
JUGADOR_HITBOX_WIDTH_RATIO = 0.6 # 60% del ancho del rect original
JUGADOR_HITBOX_HEIGHT_RATIO = 0.5 # 50% del alto del rect original, desde el offset
# Cooldowns para acciones del jugador (en milisegundos)
JUGADOR_COOLDOWN_ATAQUE_MS = 500 # Cooldown base del ataque del jugador

# --- Configuraciones de Enemigos ---
ENEMIGO_VELOCIDAD = 100
ENEMIGO_VIDA_MAXIMA = 50
ENEMIGO_HITBOX_OFFSET_X = 0 # Centrado por defecto en enemigo.py
ENEMIGO_HITBOX_OFFSET_Y = 0 # Centrado por defecto en enemigo.py
ENEMIGO_DANO_ATAQUE = 5
ENEMIGO_RANGO_AGRO = 200  # Rango en el que el enemigo detecta al jugador
ENEMIGO_DIST_MIN_JUGADOR = TILE_SIZE // 2 # Distancia mínima que el enemigo intenta mantener del jugador

# --- Configuraciones de Colisiones ---
DEBUG_VER_HITBOXES = True  # True para dibujar hitboxes, False para ocultarlos
MAX_PASADAS_RESOLUCION_ESTATICA = 5 # Número de pasadas para resolver colisiones estáticas
FACTOR_UMBRAL_TELETRANSPORTACION = 2.0 # Factor para detectar teletransportaciones (ej: 2.0 = dos veces el tamaño de la entidad)

# --- Configuraciones de Entorno (Obstáculos, etc.) ---
ARBOL_ESCALA = 0.75
ARBOL_HITBOX_OFFSET_X = 5
ARBOL_HITBOX_OFFSET_Y = 10 
ARBOL_HITBOX_WIDTH_RATIO = 0.7 # 70% del ancho escalado
ARBOL_HITBOX_HEIGHT_RATIO = 0.4 # 40% del alto escalado, en la parte inferior

# --- Configuraciones de Cámara y Renderizado ---
CAMARA_SUAVIZADO = 0.07 # Factor de suavizado para el movimiento de la cámara (más bajo = más suave)
FACTOR_ZOOM_INICIAL = 1.0
FACTOR_ZOOM_PASO = 0.1
FACTOR_ZOOM_MIN = 0.5
FACTOR_ZOOM_MAX = 2.0

# --- Configuraciones de Debug Print Variables (Control de prints específicos) ---
# Estas variables controlan la salida de sentencias print() específicas para depuración.
# Son independientes del sistema de logging y permiten una depuración rápida y puntual.
DEBUG_PRINT_GENERAL = False
DEBUG_PRINT_GESTION_DANO = False
DEBUG_PRINT_ENTORNO = False # Para logs de creación y configuración de entidades de entorno
DEBUG_PRINT_ENTORNO_ANIM = False # Para logs de animación de entidades de entorno
# Añadir más según sea necesario

# --- Configuraciones de HUD ---
HUD_MARGEN_BORDE = 10
HUD_ESPACIADO_ELEMENTO = 5
HUD_ALTURA_BARRA_VIDA = 15
HUD_ANCHO_BARRA_VIDA = 150
HUD_COLOR_VIDA = VERDE
HUD_COLOR_VIDA_FONDO = ROJO
HUD_COLOR_TEXTO = BLANCO
# Configuración de fuente para el HUD (None para usar la fuente por defecto de Pygame)
# HUD_NOMBRE_FUENTE = "arial" # Ejemplo: "arial", "comicsansms"
HUD_NOMBRE_FUENTE = None # Para usar la fuente por defecto de Pygame
HUD_TAMANO_FUENTE = 20