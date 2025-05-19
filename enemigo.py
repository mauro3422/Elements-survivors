import pygame
import os
import settings # Para RUTA_ASSETS
import math # Para cálculos de distancia y vectores
import logging # <--- AÑADIR IMPORT
from entidad_base import EntidadBase # <--- IMPORTAR EntidadBase
from collision_handler import CollisionHandler # <--- IMPORTAR COLLISION_HANDLER
# AssetManager no necesita ser importado aquí si se recibe como instancia

# --- Loggers Categóricos para Enemigo ---
logger_enemigo_mov = logging.getLogger("log_enemigo_mov")
logger_enemigo_mov.setLevel(logging.DEBUG)

logger_enemigo_ia = logging.getLogger("log_enemigo_ia")
logger_enemigo_ia.setLevel(logging.DEBUG)

logger_enemigo_col = logging.getLogger("log_enemigo_col") # Para colisiones específicas del enemigo (no del CollisionHandler)
logger_enemigo_col.setLevel(logging.DEBUG)

logger_enemigo_gen = logging.getLogger("juego.enemigo.general") # Para INFOs, WARNINGs generales
logger_enemigo_gen.setLevel(logging.INFO)

class Enemigo(EntidadBase): # <--- HEREDAR DE EntidadBase
    # id_counter de EntidadBase se usará, así que este contador de clase aquí podría ser redundante
    # a menos que queramos un conteo separado solo para enemigos. 
    # Por simplicidad, usaremos el de EntidadBase (self.id_entidad).
    # id_counter = 0 

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
        # Para el hitbox del enemigo, parece que los offsets se usan para centrar un hitbox más pequeño
        # que el rect. EntidadBase calcula: 
        # hb_ancho = self.rect.width - (2 * self.hitbox_offset_x)
        # hb_alto = self.rect.height - (2 * self.hitbox_offset_y)
        # Esto es diferente a cómo el enemigo original calcula su hitbox_offset_y en _actualizar_posicion_hitbox:
        # self.hitbox.centery = self.rect.centery (lo que implica que el offset_y es para el tamaño, no posición directa)
        # Vamos a pasar los offsets, y EntidadBase lo construirá. Si el centrado es clave,
        # Enemigo._actualizar_posicion_hitbox() deberá sobreescribirse.

        super().__init__(
            x=x, y=y, asset_manager_instance=asset_manager_instance,
            vida_maxima=vida_maxima_enemigo,
            velocidad=velocidad_enemigo,
            hitbox_offset_x=hitbox_offset_x_enemigo,
            hitbox_offset_y=hitbox_offset_y_enemigo, # OJO: Ver nota arriba sobre el cálculo del hitbox
            nombre_asset_imagen_inicial=nombre_asset_imagen,
            nombre_entidad_tipo="Enemigo"
            # No dict_animaciones_config por ahora, ya que el enemigo es estático
        )
        
        # logger.debug(f"[Enemigo_{self.id_entidad}] Creado en ({x}, {y}) con imagen {nombre_asset_imagen}")
        # El log de creación ya lo hace EntidadBase con self.nombre_entidad_tipo y self.id_entidad

        # Atributos específicos del Enemigo
        self.dano_ataque = getattr(settings, 'ENEMIGO_DANO_ATAQUE', 1)
        self.rango_agro = getattr(settings, 'ENEMIGO_RANGO_AGRO', 200)
        self.distancia_minima_al_jugador = getattr(settings, 'ENEMIGO_DIST_MIN_JUGADOR', 22)

        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_enemigo_ia", False): # O log_general si es más apropiado
            logger_enemigo_ia.debug(f"{self.nombre_log_entidad} Atributos IA: Agro:{self.rango_agro}, DMinAlJugador:{self.distancia_minima_al_jugador}, DanoAtaque:{self.dano_ataque}")

        # El hitbox original del enemigo se centraba en el rect. 
        # EntidadBase lo crea basado en topleft y offsets para reducir tamaño.
        # Si el comportamiento de centrado es crucial, debemos sobreescribir _actualizar_posicion_hitbox.
        # Por ahora, probaremos con el hitbox de EntidadBase.
        # Si el hitbox original era: hb_ancho = self.rect.width - (2*offX), hb_alto = self.rect.height - (2*offY)
        # y luego se centraba, el resultado final del tamaño es el mismo que el de EntidadBase.
        # La diferencia era el método de posicionamiento. EntidadBase usa topleft + offset para el topleft del hitbox.
        # El enemigo original hacía self.hitbox.center = self.rect.center después de calcular el tamaño.
        # Vamos a sobreescribir _actualizar_posicion_hitbox para mantener el centrado.

    def _actualizar_posicion_hitbox(self):
        """Sobreescribe EntidadBase para centrar el hitbox en el rect del enemigo."""
        self.hitbox.center = self.rect.center
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_enemigo_mov", False):
            logger_enemigo_mov.debug(f"{self.nombre_log_entidad} Hitbox recentrado (enemigo): {self.hitbox.center} (Rect center: {self.rect.center})")

    def _mover_y_colisionar_con_obstaculos(self, dx, dy, obstaculos):
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_enemigo_col", False):
            logger_enemigo_col.debug(f"{self.nombre_log_entidad} Inicia _mover_y_colisionar_con_obstaculos. dx={dx:.2f}, dy={dy:.2f}. HB Actual: {self.hitbox.topleft}")
        
        CollisionHandler.gestionar_movimiento_y_colision(
            self.hitbox,
            self.rect,
            self.hitbox_offset_x,
            self.hitbox_offset_y,
            dx,
            dy,
            obstaculos
        )
        # CollisionHandler actualiza rect y hitbox. Aquí nos aseguramos de que el hitbox esté centrado en el rect.
        self._actualizar_posicion_hitbox() 

    def update(self, objetivo_rect, grupo_obstaculos, delta_time):
        """Actualiza la lógica del enemigo, incluyendo movimiento y IA básica.

        Args:
            objetivo_rect (pygame.Rect): El rect del objetivo (ej. hitbox del jugador) para seguir.
            grupo_obstaculos (pygame.sprite.Group): Grupo de sprites de obstáculos para evitar (árboles y otros enemigos).
            delta_time (float): Tiempo transcurrido desde el último frame, en segundos.
        """
        # super().update(delta_time) # Si EntidadBase.update() maneja animaciones y usa delta_time
        self.actualizar_animacion() # <--- Llamada corregida. Enemigo podría no tener animaciones, pero EntidadBase lo maneja.

        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_enemigo_ia", False):
            logger_enemigo_ia.debug(f"{self.nombre_log_entidad} --- Inicio Update IA --- Delta: {delta_time:.4f}s. Pos ANTES: HB {self.hitbox.topleft}, Rect {self.rect.topleft}")

        dx_al_objetivo = objetivo_rect.centerx - self.hitbox.centerx
        dy_al_objetivo = objetivo_rect.centery - self.hitbox.centery
        distancia_al_objetivo = math.sqrt(dx_al_objetivo**2 + dy_al_objetivo**2)
        
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_enemigo_ia", False):
            logger_enemigo_ia.debug(f"{self.nombre_log_entidad} Target (centro {objetivo_rect.center}), Dist: {distancia_al_objetivo:.2f}. Mi Centro HB: {self.hitbox.center}")

        mov_x_input = 0
        mov_y_input = 0

        if distancia_al_objetivo < self.rango_agro and distancia_al_objetivo > self.distancia_minima_al_jugador:
            if distancia_al_objetivo > 0: 
                dir_x = dx_al_objetivo / distancia_al_objetivo
                dir_y = dy_al_objetivo / distancia_al_objetivo
                mov_x_input = dir_x * self.velocidad
                mov_y_input = dir_y * self.velocidad
                if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_enemigo_ia", False):
                    logger_enemigo_ia.debug(f"{self.nombre_log_entidad} EN RANGO AGRO. Movimiento input (dx,dy): ({mov_x_input:.2f}, {mov_y_input:.2f})")
            else: # distancia_al_objetivo == 0
                 if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_enemigo_ia", False):
                    logger_enemigo_ia.debug(f"{self.nombre_log_entidad} EN OBJETIVO (dist 0). No se calcula movimiento desde IA.")
        else:
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_enemigo_ia", False):
                logger_enemigo_ia.debug(f"{self.nombre_log_entidad} FUERA DE RANGO AGRO/DEMASIADO CERCA. Dist: {distancia_al_objetivo:.2f} (RangoAgro: {self.rango_agro}, DistMin: {self.distancia_minima_al_jugador}). No se calcula mov.")
        
        # Aplicar delta_time al movimiento
        mov_x_final = mov_x_input * delta_time
        mov_y_final = mov_y_input * delta_time

        if mov_x_final != 0 or mov_y_final != 0:
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_enemigo_mov", False):
                 logger_enemigo_mov.debug(f"{self.nombre_log_entidad} Solicita movimiento (pre-colisión, con delta_time): dx={mov_x_final:.4f}, dy={mov_y_final:.4f}. HB Actual: {self.hitbox.topleft}")
            self._mover_y_colisionar_con_obstaculos(mov_x_final, mov_y_final, grupo_obstaculos)
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_enemigo_mov", False):
                 logger_enemigo_mov.debug(f"{self.nombre_log_entidad} Posición DESPUÉS de mov/col: HB {self.hitbox.topleft}, Rect {self.rect.topleft}")
        else:
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_enemigo_mov", False):
                 logger_enemigo_mov.debug(f"{self.nombre_log_entidad} Sin movimiento solicitado por IA este frame.")
        
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_enemigo_ia", False):
            logger_enemigo_ia.debug(f"{self.nombre_log_entidad} --- Fin Update IA ---")

    # def puede_atacar_al_jugador(self):
    #     ahora = pygame.time.get_ticks()
    #     # Ejemplo de cooldown para el ataque del enemigo al jugador
    #     if ahora - self.ultimo_ataque_al_jugador > 2000: # Puede atacar cada 2 segundos
    #         return True
    #     return False

    # def atacar_jugador(self, jugador_obj):
    #     if self.puede_atacar_al_jugador():
    #         print(f"Enemigo ataca al jugador por {self.dano_ataque}!")
    #         jugador_obj.recibir_dano(self.dano_ataque)
    #         self.ultimo_ataque_al_jugador = pygame.time.get_ticks()

    # Podríamos añadir un método dibujar_hitbox aquí si queremos que los enemigos
    # tengan un hitbox personalizado distinto de su rect en el futuro.
    # def dibujar_hitbox(self, superficie_camara, cam_mundo_x, cam_mundo_y):
    #     if settings.DEBUG_VER_HITBOXES:
    #         if hasattr(self, 'hitbox'):
    #             # ... lógica similar a la del jugador para dibujar self.hitbox
    #         else:
    #             # ... lógica para dibujar self.rect
