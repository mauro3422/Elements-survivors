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
        
        # Inicializar posiciones flotantes basadas en la posición inicial del hitbox
        # Esto es DESPUÉS de que super().__init__() haya configurado el hitbox inicial.
        self.pos_x_flotante = float(self.hitbox.x)
        self.pos_y_flotante = float(self.hitbox.y)

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

    def _mover_y_colisionar_con_obstaculos(self, dx_int, dy_int, obstaculos): # Ahora recibe deltas enteros
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_enemigo_col", False):
            logger_enemigo_col.debug(f"{self.nombre_log_entidad} Inicia _mover_y_colisionar_con_obstaculos. dx_int={dx_int}, dy_int={dy_int}. HB Actual: {self.hitbox.topleft}")
        
        hitbox_x_antes_colision = self.hitbox.x
        hitbox_y_antes_colision = self.hitbox.y

        CollisionHandler.gestionar_movimiento_y_colision(
            self.hitbox,
            self.rect,
            self.hitbox_offset_x,
            self.hitbox_offset_y,
            dx_int, # Usar los deltas enteros
            dy_int, # Usar los deltas enteros
            obstaculos
        )

        # Resincronizar las posiciones flotantes con la posición del hitbox post-colisión.
        self.pos_x_flotante = float(self.hitbox.x)
        self.pos_y_flotante = float(self.hitbox.y)

        self._actualizar_posicion_rect_desde_hitbox() 
        self._actualizar_posicion_hitbox() 

        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_enemigo_mov", False):
            logger_enemigo_mov.debug(f"{self.nombre_log_entidad} _mover_y_colisionar: HB Antes CH: ({hitbox_x_antes_colision},{hitbox_y_antes_colision}), HB Despues CH y Sinc: ({self.hitbox.x},{self.hitbox.y}), Rect: {self.rect.topleft}, PosFlotante: ({self.pos_x_flotante:.2f},{self.pos_y_flotante:.2f})")

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
            logger_enemigo_ia.debug(f"{self.nombre_log_entidad} --- Inicio Update IA --- Delta: {delta_time:.4f}s. Pos ANTES: HB {self.hitbox.topleft}, Rect {self.rect.topleft}, Flot ({self.pos_x_flotante:.2f}, {self.pos_y_flotante:.2f})")

        # Guardar la posición actual del hitbox para referencia ANTES de actualizar las posiciones flotantes
        hitbox_x_antes_update = self.hitbox.x
        hitbox_y_antes_update = self.hitbox.y

        dx_al_objetivo = objetivo_rect.centerx - self.hitbox.centerx
        dy_al_objetivo = objetivo_rect.centery - self.hitbox.centery
        distancia_al_objetivo = math.sqrt(dx_al_objetivo**2 + dy_al_objetivo**2)
        
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_enemigo_ia", False):
            logger_enemigo_ia.debug(f"{self.nombre_log_entidad} Target (centro {objetivo_rect.center}), Dist: {distancia_al_objetivo:.2f}. Mi Centro HB: {self.hitbox.center}")

        mov_x_input_ia = 0 
        mov_y_input_ia = 0 

        if distancia_al_objetivo < self.rango_agro and distancia_al_objetivo > self.distancia_minima_al_jugador:
            if distancia_al_objetivo > 0: 
                dir_x = dx_al_objetivo / distancia_al_objetivo
                dir_y = dy_al_objetivo / distancia_al_objetivo
                mov_x_input_ia = dir_x * self.velocidad
                mov_y_input_ia = dir_y * self.velocidad
                if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_enemigo_ia", False):
                    logger_enemigo_ia.debug(f"{self.nombre_log_entidad} EN RANGO AGRO. Input IA (vel): ({mov_x_input_ia:.2f}, {mov_y_input_ia:.2f})")
            else: 
                 if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_enemigo_ia", False):
                    logger_enemigo_ia.debug(f"{self.nombre_log_entidad} EN RANGO AGRO PERO DISTANCIA CERO. No se calcula mov.") 
        else:
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_enemigo_ia", False):
                logger_enemigo_ia.debug(f"{self.nombre_log_entidad} FUERA DE RANGO AGRO/DEMASIADO CERCA. No se calcula mov.")
        
        delta_x_flotante_frame = mov_x_input_ia * delta_time
        delta_y_flotante_frame = mov_y_input_ia * delta_time

        self.pos_x_flotante += delta_x_flotante_frame
        self.pos_y_flotante += delta_y_flotante_frame
        
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_enemigo_mov", False):
            logger_enemigo_mov.debug(f"{self.nombre_log_entidad} Pos flotante (post-IA y delta): ({self.pos_x_flotante:.4f}, {self.pos_y_flotante:.4f})")

        # Calcular el delta flotante total desde la posición ANTERIOR del hitbox
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
                 logger_enemigo_mov.debug(f"{self.nombre_log_entidad} Solicita movimiento a CH (deltas enteros): dx_int={dx_para_colision}, dy_int={dy_para_colision}. HB Actual: {self.hitbox.topleft} (Flotantes totales: dx={delta_x_flotante_total:.4f}, dy={delta_y_flotante_total:.4f})")
            self._mover_y_colisionar_con_obstaculos(dx_para_colision, dy_para_colision, grupo_obstaculos)
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_enemigo_mov", False):
                 logger_enemigo_mov.debug(f"{self.nombre_log_entidad} Posición DESPUÉS de mov/col: HB {self.hitbox.topleft}, Rect {self.rect.topleft}, Flot ({self.pos_x_flotante:.2f}, {self.pos_y_flotante:.2f})")
        else:
            self.pos_x_flotante = float(self.hitbox.x)
            self.pos_y_flotante = float(self.hitbox.y)
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_enemigo_mov", False):
                 logger_enemigo_mov.debug(f"{self.nombre_log_entidad} Sin mov. para CH (delta_int fue 0). HB: {self.hitbox.topleft}, PosFlotante resinc: ({self.pos_x_flotante:.2f},{self.pos_y_flotante:.2f})")
        
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
