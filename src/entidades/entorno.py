import pygame
import os
from src.config import settings # Necesario para RUTA_ASSETS si no se usa AssetManager, pero ahora sí
import logging # <--- AÑADIR IMPORT

# Logger para el módulo de entorno
logger = logging.getLogger("entorno") # <--- AÑADIR LOGGER

class Obstaculo(pygame.sprite.Sprite):
    """
    Clase base para obstáculos estáticos en el juego.
    Maneja carga de imagen/animación simple, escalado y hitbox.
    """
    id_obstaculo_counter = 0

    def __init__(self, x, y, asset_manager_instance,
                 nombre_asset_base,
                 cantidad_frames_anim=1,
                 retraso_anim_ms=200,
                 escala_renderizado=(45, 45),
                 hitbox_offsets=(5, 10),
                 nombre_log_tipo="Obstaculo"):
        super().__init__()
        self.id_obstaculo = Obstaculo.id_obstaculo_counter
        Obstaculo.id_obstaculo_counter += 1
        self.nombre_log_entidad = f"[{nombre_log_tipo}_{self.id_obstaculo}]"

        self.asset_manager = asset_manager_instance
        self.animacion_frames_originales = []
        self.animacion_frames_escalados = []
        self.nombre_asset_base = nombre_asset_base
        self.cantidad_frames_anim = cantidad_frames_anim
        self.escala_renderizado = escala_renderizado

        self._cargar_y_escalar_animacion()

        self.estado_animacion = "idle"
        self.indice_fotograma = 0
        self.tiempo_ultimo_fotograma = pygame.time.get_ticks()
        self.retraso_animacion = retraso_anim_ms

        if self.animacion_frames_escalados:
            self.image = self.animacion_frames_escalados[self.indice_fotograma]
        else:
            self.image = pygame.Surface(self.escala_renderizado)
            self.image.fill(settings.ROJO_ERROR_ASSET if hasattr(settings, 'ROJO_ERROR_ASSET') else (255,0,0))
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_entorno", False):
                logger.error(f"{self.nombre_log_entidad} Animación no encontrada o error de escalado. Usando placeholder.", extra={"categoria_log": "log_entorno"})

        self.rect = self.image.get_rect(topleft=(x,y))

        self.hitbox_offset_x = hitbox_offsets[0]
        self.hitbox_offset_y = hitbox_offsets[1]
        
        hb_ancho = self.rect.width - (2 * self.hitbox_offset_x)
        hb_alto = self.rect.height - (2 * self.hitbox_offset_y)
        hb_ancho = max(1, hb_ancho)
        hb_alto = max(1, hb_alto)

        self.hitbox = pygame.Rect(0, 0, hb_ancho, hb_alto)
        self._actualizar_posicion_hitbox()

        if hasattr(settings, 'DEBUG_PRINT_ENTORNO') and settings.DEBUG_PRINT_ENTORNO:
             print(f"DEBUG_ENTORNO: {self.nombre_log_entidad} creado en ({x},{y}). Hitbox: {self.hitbox.topleft}, Tamaño HB: ({self.hitbox.width},{self.hitbox.height})")

    def _cargar_y_escalar_animacion(self):
        for i in range(1, self.cantidad_frames_anim + 1):
            clave_asset = f"{self.nombre_asset_base}_frame_{i}"
            imagen_original = self.asset_manager.get_image(clave_asset)
            # self.animacion_frames_originales.append(imagen_original) # Opcional si no se necesita el original después

            if imagen_original is not self.asset_manager.placeholder_surface:
                try:
                    imagen_escalada = pygame.transform.scale(imagen_original, self.escala_renderizado)
                    self.animacion_frames_escalados.append(imagen_escalada)
                except pygame.error as e:
                    if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_entorno", False):
                        logger.error(f"{self.nombre_log_entidad} Error al escalar {clave_asset}: {e}", extra={"categoria_log": "log_entorno"})
                    # Añadir placeholder escalado si falla el escalado de una imagen válida
                    placeholder_escalado = pygame.Surface(self.escala_renderizado)
                    placeholder_escalado.fill(settings.ROJO_ERROR_ASSET if hasattr(settings, 'ROJO_ERROR_ASSET') else (255,0,0))
                    pygame.draw.rect(placeholder_escalado, (0,0,0), placeholder_escalado.get_rect(), 1)
                    self.animacion_frames_escalados.append(placeholder_escalado)
            else:
                placeholder_escalado = pygame.Surface(self.escala_renderizado)
                placeholder_escalado.fill(settings.ROJO_ERROR_ASSET if hasattr(settings, 'ROJO_ERROR_ASSET') else (255,0,0))
                pygame.draw.rect(placeholder_escalado, (0,0,0), placeholder_escalado.get_rect(), 1)
                self.animacion_frames_escalados.append(placeholder_escalado)

        if not self.animacion_frames_escalados:
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_entorno", False):
                logger.warning(f"{self.nombre_log_entidad} No se cargaron/escalaron fotogramas para '{self.nombre_asset_base}'.", extra={"categoria_log": "log_entorno"})
            placeholder_escalado = pygame.Surface(self.escala_renderizado)
            placeholder_escalado.fill(settings.ROJO_ERROR_ASSET if hasattr(settings, 'ROJO_ERROR_ASSET') else (255,0,0))
            pygame.draw.rect(placeholder_escalado, (0,0,0), placeholder_escalado.get_rect(), 1)
            self.animacion_frames_escalados = [placeholder_escalado]

    def _actualizar_posicion_hitbox(self):
        self.hitbox.topleft = (self.rect.x + self.hitbox_offset_x,
                               self.rect.y + self.hitbox_offset_y)

    def update(self):
        if len(self.animacion_frames_escalados) > 1:
            ahora = pygame.time.get_ticks()
            if ahora - self.tiempo_ultimo_fotograma > self.retraso_animacion:
                self.tiempo_ultimo_fotograma = ahora
                self.indice_fotograma = (self.indice_fotograma + 1) % len(self.animacion_frames_escalados)
                self.image = self.animacion_frames_escalados[self.indice_fotograma]
                if hasattr(settings, 'DEBUG_PRINT_ENTORNO_ANIM') and settings.DEBUG_PRINT_ENTORNO_ANIM:
                    print(f"DEBUG_ENTORNO_ANIM: {self.nombre_log_entidad} frame actualizado a {self.indice_fotograma}")

    def dibujar_hitbox(self, superficie_destino, camara):
        if settings.DEBUG_VER_HITBOXES and hasattr(self, 'hitbox'):
            hitbox_visible = camara.aplicar_offset_a_rect(self.hitbox)
            pygame.draw.rect(superficie_destino, settings.VERDE_DEBUG, hitbox_visible, 1)

class Arbol(Obstaculo):
    def __init__(self, x, y, asset_manager_instance):
        escala_arbol = (45, 45) 
        hitbox_offsets_arbol = (5, 10) 
        retraso_anim_arbol_ms = 250

        super().__init__(x, y, asset_manager_instance,
                         nombre_asset_base="tree",
                         cantidad_frames_anim=6,
                         retraso_anim_ms=retraso_anim_arbol_ms,
                         escala_renderizado=escala_arbol,
                         hitbox_offsets=hitbox_offsets_arbol,
                         nombre_log_tipo="Arbol")
        
        if hasattr(settings, 'DEBUG_PRINT_ENTORNO') and settings.DEBUG_PRINT_ENTORNO:
            print(f"DEBUG_ENTORNO: Un {self.nombre_log_entidad} específicamente ha sido creado y configurado.")

# Ejemplo de futura expansión:
# class Roca(Obstaculo):
#    def __init__(self, x, y, asset_manager_instance):
#        super().__init__(x, y, asset_manager_instance,
#                         nombre_asset_base="rock", # Asumiendo assets como rock_frame_1.png
#                         cantidad_frames_anim=1, 
#                         escala_renderizado=(30,30), 
#                         hitbox_offsets=(3,3),
#                         nombre_log_tipo="Roca") 