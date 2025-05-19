import pygame
import os
from src.config import settings # MODIFICADO
import math # Para cálculos de distancia y vectores
import logging # <--- AÑADIR IMPORT
from src.entidades.entidad_base import EntidadBase # MODIFICADO
from src.sistemas.collision_handler import CollisionHandler # MODIFICADO
# AssetManager no necesita ser importado aquí si se recibe como instancia

# Unificar loggers
logger = logging.getLogger("enemigo")

class Enemigo(EntidadBase): # <--- HEREDAR DE EntidadBase
    # El id_counter de EntidadBase se usará.

    def __init__(self, x, y, asset_manager_instance, nombre_asset_imagen="enemy_chicken"):
        """Constructor de la clase Enemigo.

        Args:
            x (int): Posición inicial en el eje X del enemigo.
            y (int): Posición inicial en el eje Y del enemigo.
            asset_manager_instance (AssetManager): Instancia del AssetManager para cargar la imagen del enemigo.
            nombre_asset_imagen (str): Nombre del asset de imagen para este enemigo dentro del AssetManager.
        """
        vida_maxima_enemigo = getattr(settings, 'ENEMIGO_VIDA_MAXIMA', 5)
        velocidad_enemigo = getattr(settings, 'ENEMIGO_VELOCIDAD', 1.5)
        hitbox_offset_x_enemigo = getattr(settings, 'ENEMIGO_HITBOX_OFFSET_X', 3)
        hitbox_offset_y_enemigo = getattr(settings, 'ENEMIGO_HITBOX_OFFSET_Y', 3) 

        super().__init__(
            x=x, y=y, asset_manager_instance=asset_manager_instance,
            vida_maxima=vida_maxima_enemigo,
            velocidad=velocidad_enemigo,
            hitbox_offset_x=hitbox_offset_x_enemigo,
            hitbox_offset_y=hitbox_offset_y_enemigo,
            nombre_asset_imagen_inicial=nombre_asset_imagen,
            nombre_entidad_tipo="Enemigo"
        )
        
        self.pos_x_flotante = float(self.hitbox.x)
        self.pos_y_flotante = float(self.hitbox.y)

        self.dano_ataque = getattr(settings, 'ENEMIGO_DANO_ATAQUE', 1)
        self.rango_agro = getattr(settings, 'ENEMIGO_RANGO_AGRO', 200)
        self.distancia_minima_al_jugador = getattr(settings, 'ENEMIGO_DIST_MIN_JUGADOR', 22)

        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_enemigo_ia", False):
            logger.debug(f"{self.nombre_log_entidad} Atributos IA: Agro:{self.rango_agro}, DMinAlJugador:{self.distancia_minima_al_jugador}, DanoAtaque:{self.dano_ataque}", extra={"categoria_log": "log_enemigo_ia"})

    def _actualizar_posicion_hitbox(self):
        """Sobreescribe EntidadBase para centrar el hitbox en el rect del enemigo."""
        self.hitbox.center = self.rect.center
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_enemigo_mov", False):
            logger.debug(f"{self.nombre_log_entidad} Hitbox recentrado (enemigo): {self.hitbox.center} (Rect center: {self.rect.center})", extra={"categoria_log": "log_enemigo_mov"})

    def _mover_y_colisionar_con_obstaculos(self, dx_int, dy_int, obstaculos):
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_enemigo_col", False):
            logger.debug(f"{self.nombre_log_entidad} Inicia _mover_y_colisionar_con_obstaculos. dx_int={dx_int}, dy_int={dy_int}. HB Actual: {self.hitbox.topleft}", extra={"categoria_log": "log_enemigo_col"})
        
        hitbox_x_antes_colision = self.hitbox.x
        hitbox_y_antes_colision = self.hitbox.y

        CollisionHandler.gestionar_movimiento_y_colision(
            self.hitbox,
            self.rect,
            self.hitbox_offset_x,
            self.hitbox_offset_y,
            dx_int,
            dy_int,
            obstaculos
        )

        self.pos_x_flotante = float(self.hitbox.x)
        self.pos_y_flotante = float(self.hitbox.y)

        self._actualizar_posicion_rect_desde_hitbox() 
        self._actualizar_posicion_hitbox() 

        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_enemigo_mov", False):
            logger.debug(f"{self.nombre_log_entidad} _mover_y_colisionar: HB Antes CH: ({hitbox_x_antes_colision},{hitbox_y_antes_colision}), HB Despues CH y Sinc: ({self.hitbox.x},{self.hitbox.y}), Rect: {self.rect.topleft}, PosFlotante: ({self.pos_x_flotante:.2f},{self.pos_y_flotante:.2f})", extra={"categoria_log": "log_enemigo_mov"})

    def update(self, objetivo_rect, grupo_obstaculos, delta_time):
        """Actualiza la lógica del enemigo, incluyendo movimiento y IA básica.

        Args:
            objetivo_rect (pygame.Rect): El rect del objetivo (ej. hitbox del jugador) para seguir.
            grupo_obstaculos (pygame.sprite.Group): Grupo de sprites de obstáculos para evitar (árboles y otros enemigos).
            delta_time (float): Tiempo transcurrido desde el último frame, en segundos.
        """
        self.actualizar_animacion()

        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_enemigo_ia", False):
            logger.debug(f"{self.nombre_log_entidad} --- Inicio Update IA --- Delta: {delta_time:.4f}s. Pos ANTES: HB {self.hitbox.topleft}, Rect {self.rect.topleft}, Flot ({self.pos_x_flotante:.2f}, {self.pos_y_flotante:.2f})", extra={"categoria_log": "log_enemigo_ia"})

        hitbox_x_antes_update = self.hitbox.x
        hitbox_y_antes_update = self.hitbox.y

        dx_al_objetivo = objetivo_rect.centerx - self.hitbox.centerx
        dy_al_objetivo = objetivo_rect.centery - self.hitbox.centery
        distancia_al_objetivo = math.sqrt(dx_al_objetivo**2 + dy_al_objetivo**2)
        
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_enemigo_ia", False):
            logger.debug(f"{self.nombre_log_entidad} Target (centro {objetivo_rect.center}), Dist: {distancia_al_objetivo:.2f}. Mi Centro HB: {self.hitbox.center}", extra={"categoria_log": "log_enemigo_ia"})

        mov_x_input_ia = 0 
        mov_y_input_ia = 0 

        if distancia_al_objetivo < self.rango_agro and distancia_al_objetivo > self.distancia_minima_al_jugador:
            if distancia_al_objetivo > 0: 
                dir_x = dx_al_objetivo / distancia_al_objetivo
                dir_y = dy_al_objetivo / distancia_al_objetivo
                mov_x_input_ia = dir_x * self.velocidad
                mov_y_input_ia = dir_y * self.velocidad
                if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_enemigo_ia", False):
                    logger.debug(f"{self.nombre_log_entidad} EN RANGO AGRO. Input IA (vel): ({mov_x_input_ia:.2f}, {mov_y_input_ia:.2f})", extra={"categoria_log": "log_enemigo_ia"})
            else: 
                 if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_enemigo_ia", False):
                    logger.debug(f"{self.nombre_log_entidad} EN RANGO AGRO PERO DISTANCIA CERO. No se calcula mov.", extra={"categoria_log": "log_enemigo_ia"})
        else:
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_enemigo_ia", False):
                logger.debug(f"{self.nombre_log_entidad} FUERA DE RANGO AGRO/DEMASIADO CERCA. No se calcula mov.", extra={"categoria_log": "log_enemigo_ia"})
        
        delta_x_flotante_frame = mov_x_input_ia * delta_time
        delta_y_flotante_frame = mov_y_input_ia * delta_time

        self.pos_x_flotante += delta_x_flotante_frame
        self.pos_y_flotante += delta_y_flotante_frame
        
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_enemigo_mov", False):
            logger.debug(f"{self.nombre_log_entidad} Pos flotante (post-IA y delta): ({self.pos_x_flotante:.4f}, {self.pos_y_flotante:.4f})", extra={"categoria_log": "log_enemigo_mov"})

        delta_x_flotante_total = self.pos_x_flotante - hitbox_x_antes_update
        delta_y_flotante_total = self.pos_y_flotante - hitbox_y_antes_update
        
        dx_para_colision = 0
        if delta_x_flotante_total > settings.UMBRAL_MOV_FLOTANTE_ENTIDAD: 
            dx_para_colision = math.ceil(delta_x_flotante_total)
        elif delta_x_flotante_total < -settings.UMBRAL_MOV_FLOTANTE_ENTIDAD:
            dx_para_colision = math.floor(delta_x_flotante_total)

        dy_para_colision = 0
        if delta_y_flotante_total > settings.UMBRAL_MOV_FLOTANTE_ENTIDAD:
            dy_para_colision = math.ceil(delta_y_flotante_total)
        elif delta_y_flotante_total < -settings.UMBRAL_MOV_FLOTANTE_ENTIDAD:
            dy_para_colision = math.floor(delta_y_flotante_total)

        if dx_para_colision != 0 or dy_para_colision != 0:
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_enemigo_mov", False):
                 logger.debug(f"{self.nombre_log_entidad} Solicita movimiento a CH (deltas enteros): dx_int={dx_para_colision}, dy_int={dy_para_colision}. HB Actual: {self.hitbox.topleft} (Flotantes totales: dx={delta_x_flotante_total:.4f}, dy={delta_y_flotante_total:.4f})", extra={"categoria_log": "log_enemigo_mov"})
            self._mover_y_colisionar_con_obstaculos(dx_para_colision, dy_para_colision, grupo_obstaculos)
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_enemigo_mov", False):
                 logger.debug(f"{self.nombre_log_entidad} Posición DESPUÉS de mov/col: HB {self.hitbox.topleft}, Rect {self.rect.topleft}, Flot ({self.pos_x_flotante:.2f}, {self.pos_y_flotante:.2f})", extra={"categoria_log": "log_enemigo_mov"})
        else:
            self.pos_x_flotante = float(self.hitbox.x)
            self.pos_y_flotante = float(self.hitbox.y)
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_enemigo_mov", False):
                 logger.debug(f"{self.nombre_log_entidad} Sin mov. entero para CH. HB: {self.hitbox.topleft}, PosFlotante re-sincronizada a ({self.pos_x_flotante:.2f},{self.pos_y_flotante:.2f})", extra={"categoria_log": "log_enemigo_mov"})