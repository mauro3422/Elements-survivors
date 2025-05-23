import pygame
from src.config import settings
import math
import logging

logger = logging.getLogger("renderer")

class Renderer:
    def __init__(self, pantalla, camara, asset_manager):
        self.pantalla = pantalla
        self.camara = camara
        self.asset_manager = asset_manager
        self.fondo_tile = self.asset_manager.get_image('background_tierra')
        if self.fondo_tile is self.asset_manager.placeholder_surface:
            logger.warning("Renderer: Patrón de fondo 'background_tierra' no cargado. Se usará color sólido por defecto.", extra={"categoria_log": "log_renderer"})
            self.fondo_color_default = settings.NEGRO
        else:
            self.fondo_color_default = None

        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_renderer", False):
            logger.debug("Renderer inicializado.", extra={"categoria_log": "log_renderer"})

    def _renderizar_fondo_tileado(self, superficie_destino, factor_zoom):
        if self.fondo_tile is self.asset_manager.placeholder_surface or self.fondo_color_default:
            superficie_destino.fill(self.fondo_color_default if self.fondo_color_default else settings.COLOR_FONDO_DEFAULT)
            return

        ancho_tile, alto_tile = self.fondo_tile.get_size()
        
        ancho_tile_escalado = int(ancho_tile * factor_zoom)
        alto_tile_escalado = int(alto_tile * factor_zoom)

        if ancho_tile_escalado <= 0 or alto_tile_escalado <= 0:
            superficie_destino.fill(settings.COLOR_FONDO_DEFAULT)
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_renderer", False):
                logger.warning(f"Renderer: Tile de fondo escalado a tamaño cero o negativo ({ancho_tile_escalado}x{alto_tile_escalado}). Usando color de fondo por defecto.", extra={"categoria_log": "log_renderer"})
            return
        
        fondo_escalado = pygame.transform.scale(self.fondo_tile, (ancho_tile_escalado, alto_tile_escalado))

        offset_x_camara = self.camara.camera_rect.left
        offset_y_camara = self.camara.camera_rect.top

        start_x = - (offset_x_camara * factor_zoom % ancho_tile_escalado) 
        start_y = - (offset_y_camara * factor_zoom % alto_tile_escalado)

        num_tiles_x = math.ceil(superficie_destino.get_width() / ancho_tile_escalado) + 1
        num_tiles_y = math.ceil(superficie_destino.get_height() / alto_tile_escalado) + 1

        for i in range(num_tiles_x):
            for j in range(num_tiles_y):
                superficie_destino.blit(fondo_escalado, (start_x + i * ancho_tile_escalado, 
                                                         start_y + j * alto_tile_escalado))
        
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_renderer_verbose", False):
            logger.debug(f"Renderer: Fondo tileado renderizado. Zoom: {factor_zoom:.2f}, OffsetCamMundo: ({offset_x_camara},{offset_y_camara}), TileEscalado: {ancho_tile_escalado}x{alto_tile_escalado}, StartXYBlit: ({start_x:.2f},{start_y:.2f})", extra={"categoria_log": "log_renderer_verbose"})

    def _renderizar_sprites_juego(self, superficie_destino, todos_los_sprites, factor_zoom):
        sprites_visibles_ordenados = self.camara.get_sprites_visibles_ordenados(todos_los_sprites)
        
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_renderer_verbose", False):
            logger.debug(f"Renderer: Renderizando {len(sprites_visibles_ordenados)} sprites visibles y ordenados.", extra={"categoria_log": "log_renderer_verbose"})

        for sprite in sprites_visibles_ordenados:
            if not hasattr(sprite, 'image') or not hasattr(sprite, 'rect'):
                if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_renderer", False):
                    logger.warning(f"Renderer: Sprite {getattr(sprite, 'nombre_log_entidad', sprite)} no tiene 'image' o 'rect'. Saltando renderizado.", extra={"categoria_log": "log_renderer"})
                continue
            
            rect_en_pantalla = self.camara.apply(sprite.rect, factor_zoom)
            imagen_original = sprite.image

            if imagen_original is self.asset_manager.placeholder_surface:
                if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_renderer", False):
                    logger.debug(f"Renderer: Sprite {getattr(sprite, 'nombre_log_entidad', sprite)} usa imagen placeholder. Se dibujará un rect con {settings.ROJO_ERROR_ASSET}.", extra={"categoria_log": "log_renderer"})
                pygame.draw.rect(superficie_destino, settings.ROJO_ERROR_ASSET, rect_en_pantalla, 1)
                continue
            
            ancho_escalado, alto_escalado = rect_en_pantalla.size
            if ancho_escalado <= 0 or alto_escalado <= 0: 
                if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_renderer_verbose", False):
                    logger.debug(f"Renderer: Sprite {getattr(sprite, 'nombre_log_entidad', sprite)} escalado a tamaño cero o negativo ({ancho_escalado}x{alto_escalado}). No se renderizará.", extra={"categoria_log": "log_renderer_verbose"})
                continue

            try:
                imagen_escalada = pygame.transform.scale(imagen_original, (ancho_escalado, alto_escalado))
                superficie_destino.blit(imagen_escalada, rect_en_pantalla.topleft)
            except pygame.error as e:
                if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_renderer", False):
                     logger.error(f"Renderer: Error al escalar/blitear imagen para {getattr(sprite, 'nombre_log_entidad', sprite)} (tamaño escalado: {ancho_escalado}x{alto_escalado}): {e}", extra={"categoria_log": "log_renderer"})
                pygame.draw.rect(superficie_destino, settings.FUCSIA, rect_en_pantalla, 2)

            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_renderer_verbose", False):
                logger.debug(f"  Renderer: Sprite {getattr(sprite, 'nombre_log_entidad', sprite)} renderizado en {rect_en_pantalla.topleft}, escalado a {ancho_escalado}x{alto_escalado}. Pos mundo original: {sprite.rect.topleft}", extra={"categoria_log": "log_renderer_verbose"})

    def _renderizar_hitboxes_debug(self, superficie_destino, todos_los_sprites, factor_zoom):
        if not hasattr(settings, 'DEBUG_VER_HITBOXES') or not settings.DEBUG_VER_HITBOXES:
            return

        sprites_visibles = self.camara.get_sprites_visibles_ordenados(todos_los_sprites)
        for sprite in sprites_visibles:
            if hasattr(sprite, 'hitbox'):
                hitbox_mundo = sprite.hitbox
                rect_hitbox_pantalla = self.camara.apply(hitbox_mundo, factor_zoom)
                pygame.draw.rect(superficie_destino, settings.HITBOX_COLOR_COLISION, rect_hitbox_pantalla, settings.GROSOR_HITBOX_COLISION_DEBUG) 
                
                if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_renderer_hitbox", False):
                    logger.debug(f"Renderer: Hitbox COLISION para {getattr(sprite, 'nombre_log_entidad', sprite)} en {rect_hitbox_pantalla}", extra={"categoria_log": "log_renderer_hitbox"})
            
            if settings.DEBUG_VER_HITBOXES and hasattr(sprite, 'rect'): 
                rect_mundo = sprite.rect
                rect_sprite_pantalla = self.camara.apply(rect_mundo, factor_zoom)
                pygame.draw.rect(superficie_destino, settings.HITBOX_COLOR_RECT_SPRITE, rect_sprite_pantalla, settings.GROSOR_RECT_SPRITE_DEBUG) 

            if settings.DEBUG_VER_HITBOXES and hasattr(sprite, 'hitbox_ataque_actual_rect'):
                attack_hb_mundo = sprite.hitbox_ataque_actual_rect
                if attack_hb_mundo.width > 0 and attack_hb_mundo.height > 0:
                    rect_attack_hb_pantalla = self.camara.apply(attack_hb_mundo, factor_zoom)
                    pygame.draw.rect(superficie_destino, settings.COLOR_ATAQUE_HITBOX, rect_attack_hb_pantalla, settings.GROSOR_HITBOX_ATAQUE_DEBUG) 
                    if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_renderer_hitbox", False):
                        logger.debug(f"Renderer: Hitbox ATAQUE para {getattr(sprite, 'nombre_log_entidad', sprite)} en {rect_attack_hb_pantalla}", extra={"categoria_log": "log_renderer_hitbox"})

    def render_escena_completa(self, todos_los_sprites, factor_zoom):
        self._renderizar_fondo_tileado(self.pantalla, factor_zoom)
        self._renderizar_sprites_juego(self.pantalla, todos_los_sprites, factor_zoom)

        if settings.DEBUG_VER_HITBOXES:
            self._renderizar_hitboxes_debug(self.pantalla, todos_los_sprites, factor_zoom)
        elif not hasattr(settings, 'DEBUG_VER_HITBOXES'):
            logger.warning("Renderer: settings.DEBUG_VER_HITBOXES no definido. No se renderizarán hitboxes.", extra={"categoria_log": "log_renderer"})

        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_renderer", False):
            logger.debug("Renderer: Escena completa renderizada (sin flip).", extra={"categoria_log": "log_renderer"})

    def render_hud(self, hud_instance):
        if hud_instance and hasattr(hud_instance, 'draw') and callable(hud_instance.draw):
            hud_instance.draw(self.pantalla)
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_renderer_verbose", False):
                logger.debug("Renderer: HUD renderizado.", extra={"categoria_log": "log_renderer_verbose"})
        elif hud_instance:
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_renderer", False):
                logger.warning(f"Renderer: Instancia de HUD ({hud_instance}) no tiene método draw() o no es llamable.", extra={"categoria_log": "log_renderer"}) 