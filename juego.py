import pygame
import sys
import logging
import math

import config
import settings

from asset_manager import AssetManager
from jugador import Jugador
from enemigo import Enemigo
from entorno import Arbol
from camara import Camara2D
from hud import DebugHUD
from gestor_nivel import GestorNivel
from gestor_eventos import GestorEventos
from gestor_estado import GestorEstado
# Asumimos que collide_rect_extended está en utils.py
# from utils import collide_rect_extended 

# --- Loggers Categóricos para Juego ---
logger_juego_gen = logging.getLogger("log_general") # Usado también por otras partes para logs generales
logger_juego_gen.setLevel(logging.DEBUG) # Permitir DEBUG, la visibilidad la da la config raíz + categoría

logger_juego_input = logging.getLogger("log_input")
logger_juego_input.setLevel(logging.DEBUG)

logger_juego_estado = logging.getLogger("log_juego_estado")
logger_juego_estado.setLevel(logging.DEBUG)

logger_juego_render = logging.getLogger("log_juego_render")
logger_juego_render.setLevel(logging.DEBUG)

# Definición temporal de collide_rect_extended si no está en utils.py
# Esto es para evitar un error de importación inmediato.
# El usuario debe asegurarse de que esta función esté correctamente importada o definida.
def collide_rect_extended(sprite1, sprite2):
    if hasattr(sprite1, 'hitbox') and hasattr(sprite2, 'hitbox'):
        return sprite1.hitbox.colliderect(sprite2.hitbox)
    elif hasattr(sprite1, 'rect') and hasattr(sprite2, 'rect'):
        return sprite1.rect.colliderect(sprite2.rect) # Fallback a rect si no hay hitbox
    return False

class Juego:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        if settings.MODO_DEBUG_LOGS: # Log general de inicialización
            logger_juego_gen.info("Juego: Pygame y módulos inicializados.")

        self.pantalla = pygame.display.set_mode((config.ANCHO_PANTALLA, config.ALTO_PANTALLA))
        pygame.display.set_caption(config.TITULO_JUEGO)
        self.reloj = pygame.time.Clock()

        if not hasattr(settings, 'RUTA_BASE_PROYECTO') or not settings.RUTA_BASE_PROYECTO:
            logger_juego_gen.error("Juego ERROR: RUTA_BASE_PROYECTO no configurada en settings.py.")
            # Podríamos lanzar una excepción aquí si es crítico.
        
        self.asset_manager = AssetManager(settings.RUTA_BASE_PROYECTO)
        self.asset_manager.preload_all() # AssetManager tiene sus propios logs
        if settings.MODO_DEBUG_LOGS:
            logger_juego_gen.info("Juego: AssetManager inicializado y assets precargados.")

        # Crear GestorNivel ANTES de inicializar elementos del juego
        self.gestor_nivel = GestorNivel(self.asset_manager)
        if settings.MODO_DEBUG_LOGS:
            logger_juego_gen.info("Juego: GestorNivel instanciado.")

        self.factor_zoom_actual = settings.FACTOR_ZOOM_MIN
        
        # _inicializar_elementos_juego() debe llamarse ANTES de crear GestorEventos
        # si GestorEventos depende de elementos creados en _inicializar_elementos_juego (como self.jugador, self.hud)
        self._inicializar_elementos_juego() 

        # Crear GestorEventos DESPUÉS de self.jugador y self.hud
        self.gestor_eventos = GestorEventos(self.jugador, self.hud)
        if settings.MODO_DEBUG_LOGS:
            logger_juego_gen.info("Juego: GestorEventos instanciado.")

        # Crear GestorEstado DESPUÉS de inicializar todos los elementos del juego
        # Necesita jugador, grupos de enemigos, obstáculos, etc.
        self.gestor_estado = GestorEstado(
            self.jugador, 
            self.enemigos, 
            self.obstaculos, 
            self.todos_los_sprites
        )
        if settings.MODO_DEBUG_LOGS:
            logger_juego_gen.info("Juego: GestorEstado instanciado.")

        self.running = True
        if settings.MODO_DEBUG_LOGS:
            logger_juego_gen.info("Juego: Elementos del juego inicializados. Juego listo.")
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_general", False):
            logger_juego_gen.debug(f"  Juego init: Pantalla: {config.ANCHO_PANTALLA}x{config.ALTO_PANTALLA}, Zoom inicial: {self.factor_zoom_actual}")

    def _inicializar_elementos_juego(self):
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_general", False):
            logger_juego_gen.debug("Juego: _inicializar_elementos_juego() -> Creando grupos de sprites.")
        self.todos_los_sprites = pygame.sprite.Group()
        # self.enemigos = pygame.sprite.Group() # Estos se obtendrán del GestorNivel
        # self.obstaculos = pygame.sprite.Group() # Estos se obtendrán del GestorNivel

        # Crear jugador (esto permanece en Juego)
        spawn_x = config.ANCHO_PANTALLA // 2
        spawn_y = config.ALTO_PANTALLA // 2
        self.jugador = Jugador(spawn_x, spawn_y, self.asset_manager)
        self.todos_los_sprites.add(self.jugador)
        if settings.MODO_DEBUG_LOGS:
             logger_juego_gen.info(f"Juego: Jugador creado en ({spawn_x},{spawn_y}).")

        # Cargar obstáculos y enemigos usando GestorNivel
        self.gestor_nivel.cargar_elementos_nivel_inicial() # Esto poblará gestor_nivel.obstaculos y .enemigos
        
        self.obstaculos = self.gestor_nivel.get_obstaculos()
        self.enemigos = self.gestor_nivel.get_enemigos()

        # Añadir obstáculos y enemigos a todos_los_sprites
        self.todos_los_sprites.add(self.obstaculos.sprites())
        self.todos_los_sprites.add(self.enemigos.sprites())
        
        if settings.MODO_DEBUG_LOGS:
            logger_juego_gen.info(f"Juego: Elementos del nivel cargados desde GestorNivel: {len(self.obstaculos)} obstáculos, {len(self.enemigos)} enemigos.")
            logger_juego_gen.info(f"Juego: Total sprites en 'todos_los_sprites': {len(self.todos_los_sprites)}.")

        self.camara = Camara2D(config.ANCHO_MUNDO, config.ALTO_MUNDO, config.ANCHO_PANTALLA, config.ALTO_PANTALLA)
        # Camara2D tiene sus propios logs de init.
        
        fuente_hud_debug = self.asset_manager.get_font('debug_font')
        if fuente_hud_debug is self.asset_manager.placeholder_surface: # Chequeo más robusto
             logger_juego_gen.warning("Juego: Fuente 'debug_font' no cargada por AM. Usando Pygame default para HUD.")
             fuente_hud_debug = pygame.font.Font(None, 24)

        self.hud = DebugHUD(self.jugador, fuente_hud_debug)
        if settings.MODO_DEBUG_LOGS:
            logger_juego_gen.info("Juego: Cámara y HUD creados.")

        self.camara.update(self.jugador, self.factor_zoom_actual)
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_general", False) or settings.LOG_CATEGORIAS.get("log_camara", False):
            logger_juego_gen.debug(f"  Juego: Cámara actualizada inicialmente. Pos: {self.camara.camera_rect.topleft if self.camara else 'N/A'}, Zoom: {self.factor_zoom_actual}")

    def _manejar_eventos(self):
        eventos_pygame = pygame.event.get() # Obtener eventos una vez
        
        # Procesar eventos a través del GestorEventos
        nuevo_zoom = self.gestor_eventos.procesar_eventos(eventos_pygame, self.factor_zoom_actual)
        self.factor_zoom_actual = nuevo_zoom

        if self.gestor_eventos.debe_salir():
            self.running = False
            # Los logs de solicitud de salida ya los hace GestorEventos o se pueden añadir aquí si se quiere redundancia.
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_input", False): # Usamos log_input como antes para el cierre
                 logger_juego_input.debug("Juego: Solicitud de salir procesada.")

    def _actualizar_estado(self, delta_time):
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_juego_estado", False):
            # Este logger ahora es más general para la clase Juego
            logger_juego_estado.debug(f"Juego _actualizar_estado: Inicio. Delta: {delta_time:.4f}s. Delegando a GestorEstado...")
        
        teclas_presionadas = pygame.key.get_pressed()

        # Delegar la lógica principal de actualización de entidades al GestorEstado
        self.gestor_estado.actualizar_entidades_y_logica(teclas_presionadas, delta_time)

        # La clase Juego sigue siendo responsable de actualizar la cámara y el HUD,
        # ya que son más parte de la "presentación" y dependen del estado ya actualizado.
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_juego_estado", False):
            logger_juego_estado.debug("  Juego _actualizar_estado: Actualizando cámara y HUD post-GestorEstado...")
        
        self.camara.update(self.jugador, self.factor_zoom_actual) # Camara2D.update() tiene sus propios logs
        self.hud.update() # DebugHUD.update() puede tener logs si se añaden
        
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_juego_estado", False):
            logger_juego_estado.debug("Juego _actualizar_estado: Fin.")
    
    def _renderizar(self):
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_juego_render", False):
            logger_juego_render.debug("Juego Render: Inicio _renderizar.")
        
        self.pantalla.fill(config.COLOR_FONDO_DEFAULT)
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_juego_render", False):
            logger_juego_render.debug("  Juego Render: Pantalla limpiada.")

        factor_zoom_renderizado = self.factor_zoom_actual
        imagen_fondo_tile = self.asset_manager.get_image("fondo_nivel_1")

        if imagen_fondo_tile and imagen_fondo_tile != self.asset_manager.placeholder_surface:
            tile_ancho_orig, tile_alto_orig = imagen_fondo_tile.get_size()
            if tile_ancho_orig > 0 and tile_alto_orig > 0:
                tile_ancho_zoom = int(tile_ancho_orig * factor_zoom_renderizado)
                tile_alto_zoom = int(tile_alto_orig * factor_zoom_renderizado)
                if tile_ancho_zoom > 0 and tile_alto_zoom > 0:
                    imagen_fondo_tile_zoom = pygame.transform.scale(imagen_fondo_tile, (tile_ancho_zoom, tile_alto_zoom))
                    cam_wx, cam_wy = self.camara.camera_rect.left, self.camara.camera_rect.top
                    start_tile_x = math.floor(cam_wx / tile_ancho_orig)
                    start_tile_y = math.floor(cam_wy / tile_alto_orig)
                    screen_start_x = (start_tile_x * tile_ancho_orig - cam_wx) * factor_zoom_renderizado
                    screen_start_y = (start_tile_y * tile_alto_orig - cam_wy) * factor_zoom_renderizado
                    tiles_x_count = math.ceil(self.pantalla.get_width() / tile_ancho_zoom) + 1
                    tiles_y_count = math.ceil(self.pantalla.get_height() / tile_alto_zoom) + 1
                    
                    if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_juego_render", False):
                        logger_juego_render.debug(f"  Juego Render: Fondo tileado. TW_orig:{tile_ancho_orig}, TH_orig:{tile_alto_orig}. TW_zoom:{tile_ancho_zoom}, TH_zoom:{tile_alto_zoom}. Tiles X:{tiles_x_count}, Y:{tiles_y_count}")

                    for y_offset in range(tiles_y_count):
                        for x_offset in range(tiles_x_count):
                            self.pantalla.blit(imagen_fondo_tile_zoom, (screen_start_x + x_offset * tile_ancho_zoom, screen_start_y + y_offset * tile_alto_zoom))
                else:
                    if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_juego_render", False):
                        logger_juego_render.debug("  Juego Render: Tamaño de tile con zoom es 0. No se dibuja fondo tileado.")
            else:
                if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_juego_render", False):
                     logger_juego_render.debug("  Juego Render: Tamaño de tile original es 0. No se dibuja fondo tileado.")
        elif settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_juego_render", False):
            logger_juego_render.debug("  Juego Render: No hay imagen de fondo válida. No se dibuja fondo tileado.")

        # Renderizar todos los sprites
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_juego_render", False):
            logger_juego_render.debug(f"  Juego Render: Renderizando {len(self.todos_los_sprites)} sprites...")

        for sprite in sorted(self.todos_los_sprites, key=lambda s: s.rect.bottom if hasattr(s, 'rect') else 0):
            if hasattr(sprite, 'image') and sprite.image is not None:
                # Calcular posición en pantalla con zoom y offset de cámara
                sprite_mundo_x, sprite_mundo_y = sprite.rect.topleft
                sprite_pantalla_x = (sprite_mundo_x - self.camara.camera_rect.left) * factor_zoom_renderizado
                sprite_pantalla_y = (sprite_mundo_y - self.camara.camera_rect.top) * factor_zoom_renderizado
                
                # Escalar la imagen del sprite por el zoom
                nuevo_ancho = int(sprite.image.get_width() * factor_zoom_renderizado)
                nuevo_alto = int(sprite.image.get_height() * factor_zoom_renderizado)

                if nuevo_ancho > 0 and nuevo_alto > 0:
                    try:
                        imagen_escalada = pygame.transform.scale(sprite.image, (nuevo_ancho, nuevo_alto))
                        self.pantalla.blit(imagen_escalada, (sprite_pantalla_x, sprite_pantalla_y))
                        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_juego_render", False):
                             # Este log puede ser MUY verboso, considerar un sub-nivel o quitarlo.
                             sprite_id_log = getattr(sprite, 'nombre_log_entidad', type(sprite).__name__)
                             logger_juego_render.debug(f"    Render Sprite: {sprite_id_log} en ({sprite_pantalla_x:.0f},{sprite_pantalla_y:.0f}) con tamaño ({nuevo_ancho}x{nuevo_alto}). Mundo: {sprite.rect.topleft}")
                    except pygame.error as e:
                        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_juego_render", False):
                            logger_juego_render.error(f"Error al escalar sprite {getattr(sprite, 'nombre_log_entidad', type(sprite).__name__)}: {e}. Imagen original: {sprite.image.get_size()}, Target: ({nuevo_ancho},{nuevo_alto})")
                elif settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_juego_render", False):
                    logger_juego_render.warning(f"Sprite {getattr(sprite, 'nombre_log_entidad', type(sprite).__name__)} con tamaño escalado 0. No dibujado.")
        
        # Dibujar hitboxes si DEBUG_VER_HITBOXES está activo
        if settings.DEBUG_VER_HITBOXES:
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_juego_render", False):
                logger_juego_render.debug("  Juego Render: Dibujando hitboxes (DEBUG_VER_HITBOXES=True).")
            for sprite in self.todos_los_sprites:
                if hasattr(sprite, 'hitbox'):
                    hb_mundo_rect = sprite.hitbox
                    hb_pantalla_x = (hb_mundo_rect.left - self.camara.camera_rect.left) * factor_zoom_renderizado
                    hb_pantalla_y = (hb_mundo_rect.top - self.camara.camera_rect.top) * factor_zoom_renderizado
                    hb_pantalla_ancho = hb_mundo_rect.width * factor_zoom_renderizado
                    hb_pantalla_alto = hb_mundo_rect.height * factor_zoom_renderizado
                    hb_pantalla_rect = pygame.Rect(hb_pantalla_x, hb_pantalla_y, hb_pantalla_ancho, hb_pantalla_alto)
                    pygame.draw.rect(self.pantalla, settings.COLOR_HITBOX, hb_pantalla_rect, 1)

                # Dibujar hitbox de ataque del jugador si está activa
                if sprite is self.jugador and self.jugador.hitbox_ataque_actual_rect and self.jugador.hitbox_ataque_actual_rect.size != (0,0):
                    ataque_rect_mundo = self.jugador.hitbox_ataque_actual_rect
                    ataque_pantalla_x = (ataque_rect_mundo.left - self.camara.camera_rect.left) * factor_zoom_renderizado
                    ataque_pantalla_y = (ataque_rect_mundo.top - self.camara.camera_rect.top) * factor_zoom_renderizado
                    ataque_pantalla_ancho = ataque_rect_mundo.width * factor_zoom_renderizado
                    ataque_pantalla_alto = ataque_rect_mundo.height * factor_zoom_renderizado
                    ataque_pantalla_rect_dibujo = pygame.Rect(ataque_pantalla_x, ataque_pantalla_y, ataque_pantalla_ancho, ataque_pantalla_alto)
                    pygame.draw.rect(self.pantalla, settings.COLOR_ATAQUE_HITBOX, ataque_pantalla_rect_dibujo, 2)
        
        self.hud.draw(
            self.pantalla, 
            self.factor_zoom_actual, 
            self.jugador.attack_profile_manager.get_nombres_perfiles_disponibles(), 
            self.jugador.attack_profile_manager.nombre_perfil_ataque_activo
        )
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_juego_render", False):
            logger_juego_render.debug("  Juego Render: HUD dibujado.")
        
        pygame.display.flip()
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_juego_render", False):
            logger_juego_render.debug("Juego Render: Fin _renderizar (pygame.display.flip() llamado).")

    def run(self):
        if settings.MODO_DEBUG_LOGS:
            logger_juego_gen.info("Juego: Iniciando bucle principal...")
        while self.running:
            tiempo_delta = self.reloj.tick(config.FPS) / 1000.0 # Tiempo delta en segundos
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_general", False): # Podría ser "log_performance" o similar
                logger_juego_gen.debug(f"Juego Loop: FPS: {self.reloj.get_fps():.2f}, DeltaTime: {tiempo_delta:.4f}s")
            
            self._manejar_eventos()
            self._actualizar_estado(tiempo_delta)
            self._renderizar()

            # Condición de salida si el jugador muere (ejemplo)
            if self.jugador and self.jugador.ha_muerto:
                if settings.MODO_DEBUG_LOGS:
                     logger_juego_gen.info("Juego: Jugador ha muerto. Terminando bucle.")
                # self.running = False # Descomentar para que el juego termine al morir el jugador
                pass # Por ahora, el juego continúa si el jugador muere

        self.quit()

    def quit(self):
        if settings.MODO_DEBUG_LOGS:
            logger_juego_gen.info("Juego: Saliendo del juego...")
        pygame.quit()
        sys.exit()