import pygame
import logging

from src.entidades.jugador import Jugador
from src.entidades.enemigo import Enemigo
from src.entidades.entorno import Arbol, Obstaculo
from src.config import settings # CAMBIADO de config a settings
from src.renderizado.camara import Camara2D
from src.renderizado.hud import DebugHUD

# Logger para la inicialización del juego
# logger_init = logging.getLogger("log_general") # Podríamos usar un logger más específico si se desea
logger = logging.getLogger("game_initializer")

def crear_elementos_juego(asset_manager, gestor_nivel, factor_zoom_inicial, juego_ref_para_hud):
    # logger.error("GAME_INITIALIZER_LOGGER_TEST: Esta es una prueba de escritura directa en el log de game_initializer.", extra={"categoria_log": "log_game_initializer"})
    """
    Crea y configura los elementos iniciales del juego.

    Args:
        asset_manager: Instancia del AssetManager para cargar recursos.
        gestor_nivel: Instancia del GestorNivel para cargar elementos del nivel.
        factor_zoom_inicial: El factor de zoom inicial para la cámara.
        juego_ref_para_hud: Referencia a la instancia de Juego, para pasarla al HUD.

    Returns:
        tuple: Contiene (jugador, obstaculos, enemigos, todos_los_sprites, camara, hud)
    """
    # if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_general", False):
    #     logger_init.debug("GameInitializer: Creando grupos de sprites y elementos del juego.")
    if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_game_initializer", False):
        logger.debug("GameInitializer: Creando grupos de sprites y elementos del juego.", extra={"categoria_log": "log_game_initializer"})

    todos_los_sprites = pygame.sprite.Group()

    spawn_x = settings.ANCHO_PANTALLA // 2
    spawn_y = settings.ALTO_PANTALLA // 2
    jugador = Jugador(spawn_x, spawn_y, asset_manager)
    todos_los_sprites.add(jugador)
    if settings.MODO_DEBUG_LOGS:
        # logger_init.info(f"GameInitializer: Jugador creado en ({spawn_x},{spawn_y}).")
        logger.info(f"GameInitializer: Jugador creado en ({spawn_x},{spawn_y}).", extra={"categoria_log": "log_game_initializer"})

    gestor_nivel.cargar_elementos_nivel_inicial()
    obstaculos = gestor_nivel.get_obstaculos()
    enemigos = gestor_nivel.get_enemigos()
    todos_los_sprites.add(obstaculos.sprites())
    todos_los_sprites.add(enemigos.sprites())
    
    if settings.MODO_DEBUG_LOGS:
        # logger_init.info(f"GameInitializer: Elementos del nivel cargados: {len(obstaculos)} obstáculos, {len(enemigos)} enemigos.")
        logger.info(f"GameInitializer: Elementos del nivel cargados: {len(obstaculos)} obstáculos, {len(enemigos)} enemigos.", extra={"categoria_log": "log_game_initializer"})

    camara = Camara2D(settings.ANCHO_MUNDO_JUEGO, settings.ALTO_MUNDO_JUEGO, settings.ANCHO_PANTALLA, settings.ALTO_PANTALLA)
    
    fuente_hud_debug = asset_manager.get_font('debug_font')
    if fuente_hud_debug is asset_manager.placeholder_surface: # Comprobación si es el placeholder
        # logger_init.warning("GameInitializer: Fuente 'debug_font' no cargada. Usando Pygame default para HUD.")
        logger.warning("GameInitializer: Fuente 'debug_font' no cargada. Usando Pygame default para HUD.", extra={"categoria_log": "log_game_initializer"})
        fuente_hud_debug = pygame.font.Font(None, 24)

    # Se pasa juego_ref_para_hud (la instancia de Juego) al DebugHUD
    hud = DebugHUD(jugador, fuente_hud_debug, juego_ref_para_hud)
    if settings.MODO_DEBUG_LOGS:
        # logger_init.info("GameInitializer: Cámara y HUD creados.")
        logger.info("GameInitializer: Cámara y HUD creados.", extra={"categoria_log": "log_game_initializer"})

    camara.update(jugador, factor_zoom_inicial)
    # if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_camara", False): # Usar log_camara si existe
    #     logger_init.debug(f"  GameInitializer: Cámara actualizada inicialmente. Zoom: {factor_zoom_inicial}")
    # El siguiente log está condicionado por "log_camara" pero usa el logger de game_initializer.
    # Se mantendrá la condición original de la categoría, pero se usará "log_game_initializer" para el `extra` ya que es el logger de este módulo.
    # Alternativamente, se podría obtener el logger de "camara" aquí si el mensaje es puramente sobre la cámara.
    # Por consistencia, se usará "log_game_initializer" ya que este log está en game_initializer.py
    if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_camara", False):
        logger.debug(f"  GameInitializer: Cámara actualizada inicialmente. Zoom: {factor_zoom_inicial}", extra={"categoria_log": "log_game_initializer"})

    return jugador, obstaculos, enemigos, todos_los_sprites, camara, hud 