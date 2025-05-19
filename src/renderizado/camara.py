import pygame
from src.config import settings # MODIFICADO
import logging # Asegurarse de que logging esté importado

# Eliminar loggers antiguos y sus setLevel:
# # Logger para mensajes de depuración detallados de la cámara.
# logger_cam_debug = logging.getLogger("log_camara")
# logger_cam_debug.setLevel(logging.DEBUG)
# 
# # Logger para mensajes generales (INFO) de la cámara.
# logger_cam_general = logging.getLogger("juego.camara.general")
# logger_cam_general.setLevel(logging.INFO)

# Nuevo logger unificado para el módulo
logger = logging.getLogger("camara")

class Camara2D:
    def __init__(self, ancho_mundo, alto_mundo, ancho_pantalla_fisica, alto_pantalla_fisica):
        """Constructor de la clase Camara2D.

        Args:
            ancho_mundo (int): Ancho total del mundo del juego.
            alto_mundo (int): Alto total del mundo del juego.
            ancho_pantalla_fisica (int): Ancho físico de la pantalla de visualización.
            alto_pantalla_fisica (int): Alto físico de la pantalla de visualización.
        """
        self.ancho_mundo = ancho_mundo
        self.alto_mundo = alto_mundo
        self.ancho_pantalla_fisica = ancho_pantalla_fisica
        self.alto_pantalla_fisica = alto_pantalla_fisica
        
        # camera_rect.topleft es el offset_x, offset_y del mundo (esquina superior izquierda de la vista de la cámara en el mundo)
        # camera_rect.size es el tamaño de la vista de la cámara en el mundo (depende del zoom)
        # Inicialmente, sin zoom, el tamaño de la vista es el tamaño físico de la pantalla.
        self.camera_rect = pygame.Rect(0, 0, self.ancho_pantalla_fisica, self.alto_pantalla_fisica)

        if settings.MODO_DEBUG_LOGS:
            logger.info(f"Camara2D inicializada: Mundo({ancho_mundo}x{alto_mundo}), PantallaFisica({ancho_pantalla_fisica}x{alto_pantalla_fisica})", extra={"categoria_log": "log_camara"})
            if settings.LOG_CATEGORIAS.get("log_camara", False):
                 logger.debug(f"  Camara2D init: camera_rect inicial: {self.camera_rect}", extra={"categoria_log": "log_camara"})

    def update(self, objetivo, factor_zoom_actual):
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_camara", False):
            logger.debug(f"Cam2D Update: Objetivo centro: {objetivo.rect.center if objetivo else 'N/A'}, Zoom: {factor_zoom_actual:.2f}", extra={"categoria_log": "log_camara"})

        """Actualiza la posición y el tamaño de la vista de la cámara.
        
        El offset de la cámara (self.camera_rect.x, .y) es la posición en el mundo
        de la esquina superior izquierda de la vista de la cámara.
        El tamaño de la vista (self.camera_rect.width, .height) depende del zoom.
        Args:
            objetivo: La entidad (con .rect) que la cámara debe seguir.
            factor_zoom_actual (float): El factor de zoom actual del juego.
        """
        # Calcular el ancho y alto de la vista de la cámara en el mundo, según el zoom
        # Si zoom es 2.0, la cámara ve la mitad del área en términos de píxeles del mundo.
        ancho_vista_mundo = self.ancho_pantalla_fisica / factor_zoom_actual
        alto_vista_mundo = self.alto_pantalla_fisica / factor_zoom_actual
        
        self.camera_rect.width = ancho_vista_mundo
        self.camera_rect.height = alto_vista_mundo
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_camara", False):
            logger.debug(f"  Cam2D Update: VistaMundo calculada: {ancho_vista_mundo:.2f}x{alto_vista_mundo:.2f}", extra={"categoria_log": "log_camara"})

        # Calcular el offset_x, offset_y (topleft de la camera_rect en el mundo)
        # para que el objetivo (su centro) quede en el centro de esta vista_mundo.
        if objetivo:
            offset_x = objetivo.rect.centerx - (ancho_vista_mundo / 2)
            offset_y = objetivo.rect.centery - (alto_vista_mundo / 2)
        else: # Si no hay objetivo, centrar en el mundo o en 0,0
            offset_x = (self.ancho_mundo - ancho_vista_mundo) / 2
            offset_y = (self.alto_mundo - alto_vista_mundo) / 2
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_camara", False):
                logger.debug(f"  Cam2D Update: Sin objetivo. Offset calculado para centrar: ({offset_x:.2f}, {offset_y:.2f})", extra={"categoria_log": "log_camara"})

        # Aplicar límites al offset_x para que la vista de la cámara no se salga del mundo.
        if self.ancho_mundo >= ancho_vista_mundo:
            # El mundo es igual o más grande que la vista: la cámara puede moverse.
            offset_x = max(0, min(offset_x, self.ancho_mundo - ancho_vista_mundo))
        else:
            # El mundo es más pequeño que la vista: centrar el mundo dentro de la vista.
            offset_x = (self.ancho_mundo - ancho_vista_mundo) / 2
            
        if self.alto_mundo >= alto_vista_mundo:
            offset_y = max(0, min(offset_y, self.alto_mundo - alto_vista_mundo))
        else:
            offset_y = (self.alto_mundo - alto_vista_mundo) / 2

        self.camera_rect.x = int(offset_x)
        self.camera_rect.y = int(offset_y)

        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_camara", False):
            logger.debug(f"  Cam2D Update: Offset final ({offset_x:.2f}, {offset_y:.2f}). Camera_rect final: {self.camera_rect}", extra={"categoria_log": "log_camara"})

    def apply(self, rect_mundo, factor_zoom_actual):
        """Aplica la transformación de la cámara (offset y zoom) a un rect del mundo.

        Args:
            rect_mundo (pygame.Rect): El rectángulo en coordenadas del mundo.
            factor_zoom_actual (float): El factor de zoom actual.

        Returns:
            pygame.Rect: El rectángulo transformado a coordenadas de pantalla.
        """
        # Mover el rect del mundo por el negativo del offset de la cámara
        # Luego, escalar todo (posición y tamaño) por el factor de zoom.
        
        # Coordenadas relativas a la cámara (en el espacio del mundo, antes del zoom)
        x_relativo_mundo = rect_mundo.x - self.camera_rect.x
        y_relativo_mundo = rect_mundo.y - self.camera_rect.y

        # Aplicar zoom a las coordenadas relativas y al tamaño
        x_pantalla = x_relativo_mundo * factor_zoom_actual
        y_pantalla = y_relativo_mundo * factor_zoom_actual
        ancho_pantalla = rect_mundo.width * factor_zoom_actual
        alto_pantalla = rect_mundo.height * factor_zoom_actual
        
        return pygame.Rect(int(x_pantalla), int(y_pantalla), int(ancho_pantalla), int(alto_pantalla))

    def apply_rect(self, rect_mundo, factor_zoom_actual): # Podría ser un alias o la forma preferida.
        return self.apply(rect_mundo, factor_zoom_actual)

    def get_sprites_visibles_ordenados(self, todos_los_sprites):
        """
        Obtiene una lista de sprites que son visibles dentro de la cámara y los ordena.

        El orden es por `sprite.rect.bottom`, para dibujar los sprites más bajos/cercanos al final.
        La visibilidad se determina por la colisión del `sprite.rect` con `self.camera_rect`.
        `self.camera_rect` ya está en coordenadas del mundo y su tamaño está ajustado por el zoom.

        Args:
            todos_los_sprites (pygame.sprite.Group): Un grupo con todos los sprites del juego.

        Returns:
            list: Una lista de sprites visibles, ordenados para el renderizado.
        """
        sprites_visibles = []
        for sprite in todos_los_sprites:
            if hasattr(sprite, 'rect') and self.camera_rect.colliderect(sprite.rect):
                sprites_visibles.append(sprite)
            elif not hasattr(sprite, 'rect') and settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_camara", False):
                logger.warning(f"Cam2D GetVisible: Sprite {sprite} sin atributo 'rect'. No se puede determinar visibilidad.", extra={"categoria_log": "log_camara"})

        # Ordenar por la parte inferior del rect del sprite (más bajo en Y se dibuja después/encima)
        sprites_visibles.sort(key=lambda s: s.rect.bottom)

        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_camara_verbose", False): # Nueva categoría para verbosidad
            logger.debug(f"Cam2D GetVisible: {len(sprites_visibles)} sprites visibles de {len(todos_los_sprites)}. Ordenados por rect.bottom.", extra={"categoria_log": "log_camara_verbose"})
            # for s_idx, s_vis in enumerate(sprites_visibles):
            #     logger.debug(f"    {s_idx}: {s_vis} (bottom: {s_vis.rect.bottom})")
        
        return sprites_visibles

    # La lógica de dibujar la escena (fondo, sprites, HUD) ahora está en la clase Juego.
    # Camara2D se enfoca solo en calcular el offset y aplicar la transformación.
    # Si se necesitara un método para dibujar directamente en una superficie a través de la cámara,
    # se podría añadir aquí, pero el método `apply` es más versátil para que Juego lo use.

    # def dibujar_sprites_en_superficie(self, superficie_destino, grupo_sprites):
    #     """Dibuja un grupo de sprites en la superficie_destino usando la cámara."""
    #     for sprite in grupo_sprites:
    #         if hasattr(sprite, 'image') and sprite.image is not None:
    #             superficie_destino.blit(sprite.image, self.apply(sprite))
    
    # def dibujar_rect_debug_en_superficie(self, superficie_destino, rect_mundo, color, grosor=1):
    #     """Dibuja un rect (en coordenadas del mundo) en la superficie_destino usando la cámara."""
    #     pygame.draw.rect(superficie_destino, color, self.apply_rect(rect_mundo), grosor)

# Nota: La clase Camara anterior tenía una `camara_surface` interna y manejaba el zoom y dibujado de tiles.
# Esta versión Camara2D es más simple: solo maneja el offset de la cámara basado en un objetivo y los límites del mundo.
# El renderizado (incluyendo fondo y zoom si se reimplementa) se manejaría en la clase Juego o similar.
# La implementación de `__init__` y `update` en `Juego` refleja este cambio, ya que `Camara2D` toma
# `ancho_mundo`, `alto_mundo`, `ancho_pantalla`, `alto_pantalla` en su constructor,
# que coinciden con `config.ANCHO_MUNDO`, `config.ALTO_MUNDO`, `config.ANCHO_PANTALLA`, `config.ALTO_PANTALLA`. 