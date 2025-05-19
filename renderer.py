import pygame
import settings
import math # Para ceil
import logging

logger_render = logging.getLogger("log_render") # Logger específico para renderizado

class Renderer:
    def __init__(self, pantalla, camara, asset_manager):
        self.pantalla = pantalla
        self.camara = camara
        self.asset_manager = asset_manager
        self.fondo_tile = self.asset_manager.get_image('background_tierra')
        if self.fondo_tile is self.asset_manager.placeholder_surface:
            logger_render.warning("Renderer: Patrón de fondo 'background_tierra' no cargado. Se usará color sólido.")
            # Podríamos tener un color de fondo por defecto si el tile no carga
            self.fondo_color_default = settings.NEGRO # O cualquier otro color de settings

        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_render", False):
            logger_render.debug("Renderer inicializado.")

    def _renderizar_fondo_tileado(self, superficie_destino, factor_zoom):
        if self.fondo_tile is self.asset_manager.placeholder_surface:
            superficie_destino.fill(self.fondo_color_default)
            return

        ancho_tile, alto_tile = self.fondo_tile.get_size()
        
        # Escalar el tile según el zoom INVERSO para que parezca que el mundo se acerca/aleja
        # Es decir, si el zoom es 2x, el tile debe dibujarse a la mitad de su tamaño para cubrir más "terreno"
        # Esto es incorrecto. Si el zoom es 2x, el tile debe ser 2x más grande en pantalla.
        ancho_tile_escalado = int(ancho_tile * factor_zoom)
        alto_tile_escalado = int(alto_tile * factor_zoom)

        if ancho_tile_escalado == 0 or alto_tile_escalado == 0: # Evitar división por cero o tiles invisibles
            superficie_destino.fill(settings.NEGRO) # Color de fondo si el tile es demasiado pequeño
            return
        
        fondo_escalado = pygame.transform.scale(self.fondo_tile, (ancho_tile_escalado, alto_tile_escalado))

        # Calcular el offset del fondo basado en la cámara y el zoom
        # El offset de la cámara ya está en coordenadas del mundo. 
        # Queremos que el patrón se mueva con la cámara.
        offset_x_camara = self.camara.camera_rect.left
        offset_y_camara = self.camara.camera_rect.top

        # El tileado debe considerar el offset de la cámara. El efecto de paralaje simple es que se mueve con la cámara.
        # Para que el patrón se repita correctamente, el offset para el tileado debe ser en relación al tamaño del tile escalado.
        start_x = - (offset_x_camara * factor_zoom % ancho_tile_escalado) 
        start_y = - (offset_y_camara * factor_zoom % alto_tile_escalado)

        # Cuántos tiles se necesitan para cubrir la pantalla
        num_tiles_x = math.ceil(superficie_destino.get_width() / ancho_tile_escalado) + 1
        num_tiles_y = math.ceil(superficie_destino.get_height() / alto_tile_escalado) + 1

        for i in range(num_tiles_x):
            for j in range(num_tiles_y):
                superficie_destino.blit(fondo_escalado, (start_x + i * ancho_tile_escalado, 
                                                         start_y + j * alto_tile_escalado))
        
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_render_verbose", False):
            logger_render.debug(f"Renderer: Fondo tileado renderizado. Zoom: {factor_zoom:.2f}, OffsetCam: ({offset_x_camara},{offset_y_camara}), StartXY: ({start_x},{start_y})")

    def _renderizar_sprites_juego(self, superficie_destino, todos_los_sprites, factor_zoom):
        sprites_visibles_ordenados = self.camara.get_sprites_visibles_ordenados(todos_los_sprites)
        
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_render_verbose", False):
            logger_render.debug(f"Renderer: Renderizando {len(sprites_visibles_ordenados)} sprites visibles y ordenados.")

        for sprite in sprites_visibles_ordenados:
            if not hasattr(sprite, 'image') or not hasattr(sprite, 'rect'):
                if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_render", False):
                    logger_render.warning(f"Renderer: Sprite {sprite} no tiene 'image' o 'rect'. Saltando renderizado.")
                continue
            
            pos_mundo_original = sprite.rect.topleft
            # Aplicar transformación de cámara (esto incluye el zoom y el desplazamiento)
            rect_en_pantalla = self.camara.apply(sprite.rect, factor_zoom)

            imagen_original = sprite.image
            if imagen_original is self.asset_manager.placeholder_surface:
                if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_render", False):
                    logger_render.debug(f"Renderer: Sprite {sprite} usa imagen placeholder. Se dibujará un rect rojo.")
                pygame.draw.rect(superficie_destino, settings.ROJO, rect_en_pantalla, 1)
                continue
            
            # Escalar la imagen según el factor de zoom
            # El rect_en_pantalla ya tiene las dimensiones escaladas por la cámara.
            ancho_escalado, alto_escalado = rect_en_pantalla.size
            if ancho_escalado <= 0 or alto_escalado <= 0: continue # No dibujar si es invisible

            try:
                imagen_escalada = pygame.transform.scale(imagen_original, (ancho_escalado, alto_escalado))
                superficie_destino.blit(imagen_escalada, rect_en_pantalla.topleft)
            except pygame.error as e:
                if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_render", False):
                     logger_render.error(f"Renderer: Error al escalar/blitear imagen para {sprite} (tamaño: {ancho_escalado}x{alto_escalado}): {e}")
                # Dibujar un rectángulo de error si falla el escalado/blit
                pygame.draw.rect(superficie_destino, settings.FUCSIA, rect_en_pantalla, 2)

            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_render_verbose", False):
                logger_render.debug(f"  Renderer: Sprite {sprite} renderizado en {rect_en_pantalla.topleft}, escalado a {ancho_escalado}x{alto_escalado}. Pos mundo: {pos_mundo_original}")

    def _renderizar_hitboxes_debug(self, superficie_destino, todos_los_sprites, factor_zoom):
        # Usar la variable DEBUG_VER_HITBOXES de settings.py
        if not hasattr(settings, 'DEBUG_VER_HITBOXES') or not settings.DEBUG_VER_HITBOXES:
            return

        # Ya no es necesario MODO_DEBUG_GRL aquí si DEBUG_VER_HITBOXES es el control principal
        # if not (settings.MODO_DEBUG_GRL and settings.RENDER_HITBOXES):
        #     return

        sprites_visibles = self.camara.get_sprites_visibles_ordenados(todos_los_sprites) # Reutilizar visibilidad
        for sprite in sprites_visibles:
            if hasattr(sprite, 'hitbox'):
                hitbox_mundo = sprite.hitbox
                # Aplicar transformación de cámara al hitbox para dibujarlo en pantalla
                rect_hitbox_pantalla = self.camara.apply(hitbox_mundo, factor_zoom)
                pygame.draw.rect(superficie_destino, settings.HITBOX_COLOR_COLISION, rect_hitbox_pantalla, settings.GROSOR_HITBOX_COLISION_DEBUG) 
                
                if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_render_hitbox", False):
                    logger_render.debug(f"Renderer: Hitbox debug para {sprite} en {rect_hitbox_pantalla}")
            
            # Opcionalmente, dibujar también el sprite.rect si es diferente del hitbox y se quiere visualizar
            if settings.DEBUG_VER_HITBOXES and hasattr(sprite, 'rect'): 
                rect_mundo = sprite.rect
                rect_sprite_pantalla = self.camara.apply(rect_mundo, factor_zoom)
                pygame.draw.rect(superficie_destino, settings.HITBOX_COLOR_RECT_SPRITE, rect_sprite_pantalla, settings.GROSOR_RECT_SPRITE_DEBUG) 

            # Dibujar el hitbox de ataque si existe y es visible
            if settings.DEBUG_VER_HITBOXES and hasattr(sprite, 'hitbox_ataque_actual_rect'):
                attack_hb_mundo = sprite.hitbox_ataque_actual_rect
                if attack_hb_mundo.width > 0 and attack_hb_mundo.height > 0: # Solo dibujar si tiene tamaño
                    rect_attack_hb_pantalla = self.camara.apply(attack_hb_mundo, factor_zoom)
                    color_ataque = getattr(settings, 'HITBOX_COLOR_ATAQUE', settings.VERDE) # Usar constante de color
                    pygame.draw.rect(superficie_destino, color_ataque, rect_attack_hb_pantalla, settings.GROSOR_HITBOX_ATAQUE_DEBUG) 
                    if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_render_hitbox", False):
                        logger_render.debug(f"Renderer: Hitbox de ATAQUE para {sprite} en {rect_attack_hb_pantalla}")

    def render_escena_completa(self, todos_los_sprites, factor_zoom):
        # 1. Limpiar/Renderizar Fondo
        # self.pantalla.fill(settings.NEGRO) # O color de fondo del nivel
        self._renderizar_fondo_tileado(self.pantalla, factor_zoom)

        # 2. Renderizar Sprites del Juego (ordenados y escalados)
        self._renderizar_sprites_juego(self.pantalla, todos_los_sprites, factor_zoom)

        # 3. Renderizar Hitboxes (si está activado el modo debug)
        # MODO_DEBUG_GRL y RENDER_HITBOXES deben estar en settings.py
        # Cambiamos para usar DEBUG_VER_HITBOXES directamente
        if hasattr(settings, 'DEBUG_VER_HITBOXES') and settings.DEBUG_VER_HITBOXES:
            self._renderizar_hitboxes_debug(self.pantalla, todos_los_sprites, factor_zoom)
        elif not hasattr(settings, 'DEBUG_VER_HITBOXES'):
            # logger_render.warning("Renderer: settings.DEBUG_VER_HITBOXES no definido. No se renderizarán hitboxes.")
            pass

        # El flip se hace en la clase Juego después de renderizar el HUD
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_render", False):
            logger_render.debug("Renderer: Escena completa renderizada (sin flip).")

    def render_hud(self, hud_instance):
        # Asumimos que la instancia de HUD tiene un método draw(superficie)
        if hud_instance and hasattr(hud_instance, 'draw') and callable(hud_instance.draw):
            hud_instance.draw(self.pantalla) # El HUD se dibuja directamente sobre la pantalla principal
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_render", False):
                logger_render.debug("Renderer: HUD renderizado.")
        elif hud_instance:
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_render", False):
                logger_render.warning(f"Renderer: Instancia de HUD ({hud_instance}) no tiene método draw() o no es llamable.") 