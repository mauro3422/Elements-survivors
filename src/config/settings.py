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
JUGADOR_VIDA_MAX_DEFAULT = 100
JUGADOR_ENERGIA_MAX_DEFAULT = 100
JUGADOR_DANO_BASE_ATAQUE_DEFAULT = 10
JUGADOR_COOLDOWN_GENERAL_ATAQUE_MS = 500 # Tiempo en ms
JUGADOR_MAX_FUERZA_EMPUJE_FRAME = 7.0 # Límite a la fuerza de empuje total que el jugador puede recibir en un frame.

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
ENEMIGO_DIST_MIN_JUGADOR = 30 # Distancia mínima que el enemigo intenta mantener con el jugador
ENEMIGO_DANO_CONTACTO_DEFAULT = 10 # Daño por defecto que inflige un enemigo por contacto
ENEMIGO_FUERZA_EMPUJE_BASE = 2.5 # Nueva constante para la magnitud del empuje del enemigo (píxeles/frame tentativo)

# --- Configuración del Zoom de la Cámara ---
# Factor de zoom inicial. Un valor mayor significa más zoom (objetos más grandes, vista más cercana).
# 1.0 = sin zoom. 2.0 = los objetos se ven el doble de grandes.
FACTOR_ZOOM_INICIAL = 2.3
# Zoom más alejado (ej: ve el doble de área que con zoom 2.0)
FACTOR_ZOOM_MIN = 1.9
# Zoom más cercano (ej: ve la mitad de área que con zoom 1.5)
FACTOR_ZOOM_MAX = 3.0
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
RUTA_BASE_PROYECTO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RUTA_ASSETS = os.path.join(RUTA_BASE_PROYECTO, "assets")
RUTA_DATOS_PERFILES_ATAQUE = os.path.join(RUTA_ASSETS, "data", "attack_profiles")
RUTA_NIVEL_1 = os.path.join(RUTA_ASSETS, "data", "niveles", "nivel_1.json")

# --- Configuraciones de Depuración ---
DEBUG_VER_HITBOXES = True
INCREMENTO_AJUSTE_DEBUG = 2
INCREMENTO_DURACION_DEBUG = 10
ARCHIVO_CONFIG_ATAQUE = "config_ataque.json"
NOMBRE_PERFIL_ATAQUE_INICIAL = "espada_predeterminada"

# Nueva constante para el umbral de contacto en píxeles
PIXEL_CONTACT_THRESHOLD = 1 # Umbral para considerar contacto, usado en colisiones

# DEBUG_PRINT_GESTION_DANO = False # Se manejará por log_enemigo_vida o log_gestor_estado

# --- Configuración Global de Logs ---
MODO_DEBUG_LOGS = True # CAMBIADO A True PARA VER ERRORES
LOG_LEVEL_VERBOSE = "DEBUG"
LOG_LEVEL_STANDARD = "INFO"

LOG_CATEGORIAS = {
    # Categorías Generales y de Sistema
    "log_general": False,               # Para mensajes generales no específicos de un módulo. ¡ACTIVAR CON PRECAUCIÓN! Puede ser muy verboso.
    "log_main": True,                  # Logs específicos del script principal main.py # CAMBIADO A True PARA VER ERRORES
    "log_juego": False,                 # Logs del bucle principal del juego, eventos de alto nivel en Juego.py
    "log_game_initializer": False,      # Logs del proceso de inicialización del juego
    "log_config_logging": False,       # Logs relacionados con la configuración del propio sistema de logging (puede ser meta-verboso)
    "log_asset_manager": False,         # Logs de carga y gestión de assets (imágenes, sonidos, fuentes) # CAMBIADO A False TEMPORALMENTE
    
    # Categorías de Entidades
    "log_entidad_base": False,         # Logs de la clase EntidadBase (si se añaden)
    "log_jugador_general": False,      # Logs generales del jugador (estados, inicialización)
    "log_jugador_mov_detalle": True,  # ACTIVADO PARA DEBUG DE EMPUJE
    "log_jugador_ataque_calculo": False,
    "log_jugador_ataque_debug": False,   # MANTENER ACTIVADO PARA PRUEBA # CAMBIADO A False TEMPORALMENTE
    "log_jugador_vida": False,         # ACTIVADO PARA PRUEBA DE DAÑO # CAMBIADO A False TEMPORALMENTE
    "log_jugador_anim": False,         # Logs específicos de la animación del jugador
    "log_enemigo": False,              # ACTIVADO PARA PRUEBA DE DAÑO # CAMBIADO A False TEMPORALMENTE
    "log_enemigo_ia": True,           # ACTIVADO PARA DEBUG DE EMPUJE
    "log_enemigo_mov": False,          # Logs del movimiento del enemigo
    "log_enemigo_col": False,          # Logs de colisiones específicas del enemigo
    "log_entorno": False,              # Logs de los elementos del entorno (DEBUG_PRINT_ENTORNO, DEBUG_PRINT_ENTORNO_ANIM)

    # Categorías de Sistemas y Gestores
    "log_collision_handler": True,
    "log_collision_handler_detalle": True,
    "log_gestor_eventos": False,
    "log_gestor_eventos_verbose": False, # Nueva categoría para logs detallados de eventos
    "log_gestor_estado": False,         # Logs de alto nivel del GestorEstado # CAMBIADO A False TEMPORALMENTE
    "log_gestor_estado_detalle": False, # Logs detallados de GestorEstado.actualizar_entidades_y_logica
    "log_gestor_nivel": False,
    "log_gestor_nivel_detalle": False, # Nueva categoría para logs detallados de GestorNivel
    "log_attack_profile_manager": False,
    "log_renderer": False,             # Logs del sistema de renderizado (si se implementa un logger específico)
    "log_renderer_verbose": False,     # Para logs detallados del renderer
    "log_renderer_hitbox": False,      # Para logs específicos del renderizado de hitboxes
    "log_hud": False,                  # Logs del HUD
    "log_camara": False,               # Logs del sistema de cámara
    "log_camara_verbose": False,       # Para logs detallados de la cámara
    "log_dialogo": False,              # Logs del sistema de diálogos
    "log_inventario": False,           # Logs del sistema de inventario
    "log_misiones": False,             # Logs del sistema de misiones
    "log_motor_fisica": True,          # ACTIVADO PARA DEBUG DE EMPUJE

    # Categorías para Debugging Específico (Usar con moderación)
    "log_debug_temporal": True,       # Para logs temporales durante una sesión de debugging específica # CAMBIADO A True PARA VER ERRORES
    "log_posiciones_debug": False,     # Nueva categoría para debug de posiciones de entidades

    # Categorías de Rendimiento y Debugging Detallado
    "log_juego_perf_detalle": False,    # Logs detallados de rendimiento para fases internas de Juego.py # CAMBIADO A False TEMPORALMENTE

    # Categorías de Utilidades y Otros
    "log_utils": False,                # Logs de funciones en utils.py
}

# Nueva constante para el filtro de duplicados
LOG_DUPLICATE_MESSAGE_TIMEDELTA_MS = 50

# Lista de nombres de loggers que tendrán su propio archivo de log en la carpeta 'logs/'
MODULOS_CON_LOG_PROPIO = [
    "juego",
    "main",
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
    "utils",
    "attack_profile_manager",
    "game_initializer",
    "entorno",
    "motor_fisica",
]

# --- Configuración de Fuentes ---
NOMBRE_FUENTE_HUD = "Arial"
NOMBRE_FUENTE_DEBUG = "Consolas"
TAMANO_FUENTE_HUD = 18
TAMANO_FUENTE_DEBUG = 16

# --- Configuraciones de Renderizado de Depuración ---
HITBOX_COLOR_COLISION = ROJO
HITBOX_COLOR_RECT_SPRITE = AZUL
HITBOX_COLOR_ATAQUE = COLOR_ATAQUE_HITBOX

GROSOR_HITBOX_COLISION_DEBUG = 1
GROSOR_RECT_SPRITE_DEBUG = 1
GROSOR_HITBOX_ATAQUE_DEBUG = 2

# --- Configuraciones de Layout del HUD de Depuración ---
HUD_PADDING_X = 10
HUD_PADDING_Y = 10
HUD_LINE_HEIGHT = 20
HUD_ESPACIO_ENTRE_SECCIONES = 25

# --- Constantes de Gameplay/Física ---
UMBRAL_MOV_FLOTANTE_ENTIDAD = 0.0001
FACTOR_UMBRAL_TELETRANSPORTACION = 1.5
MAX_PASADAS_RESOLUCION_ESTATICA = 4