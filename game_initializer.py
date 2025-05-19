import pygame
import logging

import config # Necesario para ANCHO_PANTALLA, ALTO_PANTALLA, ANCHO_MUNDO, ALTO_MUNDO
import settings # Necesario para MODO_DEBUG_LOGS, LOG_CATEGORIAS

from jugador import Jugador
from camara import Camara2D
from hud import DebugHUD

# Logger para la inicialización del juego
logger_init = logging.getLogger("log_general") # Podríamos usar un logger más específico si se desea

def crear_elementos_juego(asset_manager, gestor_nivel, factor_zoom_inicial, juego_ref_para_hud):
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
    if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_general", False):
        logger_init.debug("GameInitializer: Creando grupos de sprites y elementos del juego.")

    todos_los_sprites = pygame.sprite.Group()

    spawn_x = config.ANCHO_PANTALLA // 2
    spawn_y = config.ALTO_PANTALLA // 2
    jugador = Jugador(spawn_x, spawn_y, asset_manager)
    todos_los_sprites.add(jugador)
    if settings.MODO_DEBUG_LOGS:
        logger_init.info(f"GameInitializer: Jugador creado en ({spawn_x},{spawn_y}).")

    gestor_nivel.cargar_elementos_nivel_inicial()
    obstaculos = gestor_nivel.get_obstaculos()
    enemigos = gestor_nivel.get_enemigos()
    todos_los_sprites.add(obstaculos.sprites())
    todos_los_sprites.add(enemigos.sprites())
    
    if settings.MODO_DEBUG_LOGS:
        logger_init.info(f"GameInitializer: Elementos del nivel cargados: {len(obstaculos)} obstáculos, {len(enemigos)} enemigos.")

    camara = Camara2D(config.ANCHO_MUNDO, config.ALTO_MUNDO, config.ANCHO_PANTALLA, config.ALTO_PANTALLA)
    
    fuente_hud_debug = asset_manager.get_font('debug_font')
    if fuente_hud_debug is asset_manager.placeholder_surface: # Comprobación si es el placeholder
        logger_init.warning("GameInitializer: Fuente 'debug_font' no cargada. Usando Pygame default para HUD.")
        fuente_hud_debug = pygame.font.Font(None, 24)

    # Se pasa juego_ref_para_hud (la instancia de Juego) al DebugHUD
    hud = DebugHUD(jugador, fuente_hud_debug, juego_ref_para_hud)
    if settings.MODO_DEBUG_LOGS:
        logger_init.info("GameInitializer: Cámara y HUD creados.")

    camara.update(jugador, factor_zoom_inicial)
    if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_camara", False): # Usar log_camara si existe
        logger_init.debug(f"  GameInitializer: Cámara actualizada inicialmente. Zoom: {factor_zoom_inicial}")

    return jugador, obstaculos, enemigos, todos_los_sprites, camara, hud 