import pygame
import os
from src.config import settings # MODIFICADO
import math # Para cálculos de distancia y vectores
import logging # <--- AÑADIR IMPORT
from src.entidades.entidad_base import EntidadBase # MODIFICADO
from src.sistemas.collision_handler import CollisionHandler # MODIFICADO
from src.sistemas.motor_fisica import MotorFisica # <--- AÑADIR IMPORT
from src.entidades.jugador import Jugador # <--- AÑADIR IMPORT PARA TYPE HINTING/INSTANCIA
from src.utils import utils # Añadir import de utils
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

        # Cooldown para el empuje
        self.tiempo_ultimo_empuje = 0.0
        self.cooldown_empuje = getattr(settings, 'ENEMIGO_COOLDOWN_EMPUJE', 0.5) # 0.5 segundos de cooldown

        # Instancia de CollisionHandler para el enemigo
        self.collision_handler = CollisionHandler()

        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_enemigo_ia", False):
            logger.debug(f"{self.nombre_log_entidad} Atributos IA: Agro:{self.rango_agro}, DMinAlJugador:{self.distancia_minima_al_jugador}, DanoAtaque:{self.dano_ataque}", extra={"categoria_log": "log_enemigo_ia"})

    def _actualizar_posicion_hitbox(self):
        """Sobreescribe EntidadBase para centrar el hitbox en el rect del enemigo."""
        self.hitbox.center = self.rect.center
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_enemigo_mov", False):
            logger.debug(f"{self.nombre_log_entidad} Hitbox recentrado (enemigo): {self.hitbox.center} (Rect center: {self.rect.center})", extra={"categoria_log": "log_enemigo_mov"})

    def _mover_y_colisionar_con_obstaculos(self, dx_int, dy_int, obstaculos, mundo_ancho, mundo_alto):
        if settings.DEBUG_ENEMIGO_MOVIMIENTO:
            print(f"DEBUG_ENEMIGO: {self.nombre_log_entidad} - INICIO _mover_y_colisionar_con_obstaculos(). dx_int={dx_int}, dy_int={dy_int}")
        
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_enemigo_col", False):
            logger.debug(f"{self.nombre_log_entidad} Inicia _mover_y_colisionar_con_obstaculos. dx_int={dx_int}, dy_int={dy_int}. HB Actual: {self.hitbox.topleft}", extra={"categoria_log": "log_enemigo_col"})
        
        hitbox_x_antes_colision = self.hitbox.x
        hitbox_y_antes_colision = self.hitbox.y

        if settings.DEBUG_ENEMIGO_MOVIMIENTO:
            print(f"DEBUG_ENEMIGO: {self.nombre_log_entidad} - ANTES de llamar a self.collision_handler.gestionar_movimiento_y_colision()")
        
        # Usar la instancia de collision_handler
        self.collision_handler.gestionar_movimiento_y_colision(
            self,                       # entidad_actual
            self.hitbox,                # entidad_hitbox
            self.rect,                  # entidad_rect
            self.hitbox_offset_x,
            self.hitbox_offset_y,
            dx_int,
            dy_int,
            obstaculos,
            mundo_ancho,
            mundo_alto
        )
        if settings.DEBUG_ENEMIGO_MOVIMIENTO:
            print(f"DEBUG_ENEMIGO: {self.nombre_log_entidad} - DESPUÉS de llamar a self.collision_handler.gestionar_movimiento_y_colision()")

        self.pos_x_flotante = float(self.hitbox.x)
        self.pos_y_flotante = float(self.hitbox.y)

        self._actualizar_posicion_rect_desde_hitbox() 
        self._actualizar_posicion_hitbox() 

        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_enemigo_mov", False):
            logger.debug(f"{self.nombre_log_entidad} _mover_y_colisionar: HB Antes CH: ({hitbox_x_antes_colision},{hitbox_y_antes_colision}), HB Despues CH y Sinc: ({self.hitbox.x},{self.hitbox.y}), Rect: {self.rect.topleft}, PosFlotante: ({self.pos_x_flotante:.2f},{self.pos_y_flotante:.2f})", extra={"categoria_log": "log_enemigo_mov"})

    def update(self, objetivo_rect, grupo_obstaculos, delta_time, mundo_ancho, mundo_alto):
        """Actualiza la lógica del enemigo, incluyendo movimiento y IA básica.

        Args:
            objetivo_rect (pygame.Rect): El rect del objetivo (ej. hitbox del jugador) para seguir.
            grupo_obstaculos (pygame.sprite.Group): Grupo de sprites de obstáculos para evitar (árboles y otros enemigos).
            delta_time (float): Tiempo transcurrido desde el último frame, en segundos.
            mundo_ancho (int): Ancho total del mundo del juego.
            mundo_alto (int): Alto total del mundo del juego.
        """
        if settings.DEBUG_ENEMIGO_MOVIMIENTO:
            print(f"DEBUG_ENEMIGO: {self.nombre_log_entidad} - INICIO Enemigo.update()")
        
        self.actualizar_animacion()

        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_enemigo_ia", False):
            logger.debug(f"{self.nombre_log_entidad} --- Inicio Update IA --- Delta: {delta_time:.4f}s. Pos ANTES: HB {self.hitbox.topleft}, Rect {self.rect.topleft}, Flot ({self.pos_x_flotante:.2f}, {self.pos_y_flotante:.2f})", extra={"categoria_log": "log_enemigo_ia"})

        hitbox_x_antes_update = self.hitbox.x
        hitbox_y_antes_update = self.hitbox.y

        if settings.DEBUG_ENEMIGO_MOVIMIENTO:
            print(f"DEBUG_ENEMIGO: {self.nombre_log_entidad} - Antes de lógica IA (cálculo mov_input)")
        
        # Asegurarse de que usamos el hitbox del jugador para la IA de movimiento si objetivo_rect es Jugador
        if isinstance(objetivo_rect, Jugador):
            centro_objetivo_x = objetivo_rect.hitbox.centerx
            centro_objetivo_y = objetivo_rect.hitbox.centery
        else: # Fallback por si acaso no es un Jugador (aunque debería serlo)
            centro_objetivo_x = objetivo_rect.centerx
            centro_objetivo_y = objetivo_rect.centery

        dx_al_objetivo = centro_objetivo_x - self.hitbox.centerx
        dy_al_objetivo = centro_objetivo_y - self.hitbox.centery
        distancia_al_objetivo = math.sqrt(dx_al_objetivo**2 + dy_al_objetivo**2)
        
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_enemigo_ia", False):
            logger.debug(f"{self.nombre_log_entidad} Target (centro: ({centro_objetivo_x}, {centro_objetivo_y})), Dist: {distancia_al_objetivo:.2f}. Mi Centro HB: {self.hitbox.center}", extra={"categoria_log": "log_enemigo_ia"})

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
        
        if settings.DEBUG_ENEMIGO_MOVIMIENTO:
            print(f"DEBUG_ENEMIGO: {self.nombre_log_entidad} - Después de lógica IA, mov_input_ia=({mov_x_input_ia:.2f}, {mov_y_input_ia:.2f})")
        
        if settings.DEBUG_ENEMIGO_MOVIMIENTO:
            print(f"DEBUG_ENEMIGO: {self.nombre_log_entidad} - Antes de aplicar delta_time")
        
        delta_x_flotante_frame = mov_x_input_ia * delta_time
        delta_y_flotante_frame = mov_y_input_ia * delta_time

        self.pos_x_flotante += delta_x_flotante_frame
        self.pos_y_flotante += delta_y_flotante_frame
        
        if settings.DEBUG_ENEMIGO_MOVIMIENTO:
            print(f"DEBUG_ENEMIGO: {self.nombre_log_entidad} - Después de aplicar delta_time, pos_flotante=({self.pos_x_flotante:.4f}, {self.pos_y_flotante:.4f})")

        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_enemigo_mov", False):
            logger.debug(f"{self.nombre_log_entidad} Pos flotante (post-IA y delta): ({self.pos_x_flotante:.4f}, {self.pos_y_flotante:.4f})", extra={"categoria_log": "log_enemigo_mov"})

        delta_x_flotante_total = self.pos_x_flotante - hitbox_x_antes_update
        delta_y_flotante_total = self.pos_y_flotante - hitbox_y_antes_update
        
        # Usar la función de utilidad para convertir deltas
        dx_para_colision, dy_para_colision = utils.convertir_deltas_a_enteros_para_colision(
            delta_x_flotante_total, delta_y_flotante_total, settings.UMBRAL_MOV_FLOTANTE_ENTIDAD_PARA_COLISION
        )

        if dx_para_colision != 0 or dy_para_colision != 0:
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_enemigo_mov", False):
                 logger.debug(f"{self.nombre_log_entidad} Solicita movimiento a CH (deltas enteros): dx_int={dx_para_colision}, dy_int={dy_para_colision}. HB Actual: {self.hitbox.topleft} (Flotantes totales: dx={delta_x_flotante_total:.4f}, dy={delta_y_flotante_total:.4f})", extra={"categoria_log": "log_enemigo_mov"})
            if settings.DEBUG_ENEMIGO_MOVIMIENTO:
                print(f"DEBUG_ENEMIGO: {self.nombre_log_entidad} - Antes de _mover_y_colisionar_con_obstaculos()")
            
            self._mover_y_colisionar_con_obstaculos(dx_para_colision, dy_para_colision, grupo_obstaculos, mundo_ancho, mundo_alto)
            
            if settings.DEBUG_ENEMIGO_MOVIMIENTO:
                print(f"DEBUG_ENEMIGO: {self.nombre_log_entidad} - Después de _mover_y_colisionar_con_obstaculos()")
            
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_enemigo_mov", False):
                 logger.debug(f"{self.nombre_log_entidad} Posición DESPUÉS de mov/col: HB {self.hitbox.topleft}, Rect {self.rect.topleft}, Flot ({self.pos_x_flotante:.2f}, {self.pos_y_flotante:.2f})", extra={"categoria_log": "log_enemigo_mov"})
        else:
            self.pos_x_flotante = float(self.hitbox.x)
            self.pos_y_flotante = float(self.hitbox.y)
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_enemigo_mov", False):
                 logger.debug(f"{self.nombre_log_entidad} Sin mov. entero para CH. HB: {self.hitbox.topleft}, PosFlotante re-sincronizada a ({self.pos_x_flotante:.2f},{self.pos_y_flotante:.2f})", extra={"categoria_log": "log_enemigo_mov"})

        if settings.DEBUG_ENEMIGO_MOVIMIENTO:
            print(f"DEBUG_ENEMIGO: {self.nombre_log_entidad} - Antes de lógica de empuje al jugador")
        
        # --- LÓGICA DE EMPUJE AL JUGADOR ---
        # Asumimos que 'objetivo_rect' es el hitbox del jugador y que tenemos acceso a la instancia del jugador.
        # Esta parte necesita que 'objetivo_rect' en realidad sea el objeto Jugador o que se pase el objeto Jugador.
        # Por ahora, vamos a asumir que 'objetivo_rect' es un mal nombre y es en realidad la instancia del jugador.
        # Esto deberá corregirse en GestorEstado al llamar a este update.
        if isinstance(objetivo_rect, Jugador): # Verificar si el objetivo es realmente el Jugador
            jugador_objetivo = objetivo_rect 
            
            # ---- COMPROBACIÓN DE EMPUJE CON ZONA DE INFLUENCIA ----
            # zona_influencia_empuje_enemigo = self.hitbox.inflate(2, 2) # Inflar 1 pixel en cada lado/dir
            # zona_influencia_empuje_enemigo = self.hitbox.inflate(4, 4) # Inflar 2 píxeles en cada lado/dir
            # zona_influencia_empuje_enemigo = self.hitbox.inflate(6, 6) # Inflar 3 píxeles en cada lado/dir
            zona_influencia_empuje_enemigo = self.hitbox.inflate(16, 16) # EXPERIMENTAL: Inflar 8 píxeles en cada lado/dir
            
            colision_detectada_para_empuje = zona_influencia_empuje_enemigo.colliderect(jugador_objetivo.hitbox)
            
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_enemigo_ia", True):
                logger.info(f"{self.nombre_log_entidad} DESPUES IF EMPUJE (con inflate(16,16)): ZonaInfluenciaHB ({zona_influencia_empuje_enemigo}) vs JugadorHB ({jugador_objetivo.hitbox})? {colision_detectada_para_empuje}. Mi HB real: {self.hitbox}", extra={"categoria_log": "log_enemigo_ia"})
            # ---- FIN LOGS DETALLADOS ----

            if colision_detectada_para_empuje:
                if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_enemigo_ia", False):
                    logger.debug(f"{self.nombre_log_entidad} Detectó colisión con Jugador para empuje. Enemigo HB: {self.hitbox}, Jugador HB: {jugador_objetivo.hitbox}", extra={"categoria_log": "log_enemigo_ia"})

                # --- INICIO LÓGICA COOLDOWN EMPUJE ---
                tiempo_actual = pygame.time.get_ticks() / 1000.0 # En segundos
                if (tiempo_actual - self.tiempo_ultimo_empuje > self.cooldown_empuje):
                    vector_empuje = MotorFisica.calcular_vector_empuje_simple(
                        origen_pos_center=pygame.math.Vector2(self.hitbox.center),
                        destino_pos_center=pygame.math.Vector2(jugador_objetivo.hitbox.center),
                        fuerza_magnitud=settings.ENEMIGO_FUERZA_EMPUJE_BASE
                    )
                    
                    # Loguear el vector calculado si hubo colisión y se va a intentar aplicar (después del cooldown)
                    if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_enemigo_ia", False):
                        logger.info(f"{self.nombre_log_entidad} Vector de empuje CALCULADO (post-cooldown): {vector_empuje}", extra={"categoria_log": "log_enemigo_ia"})

                    # El vector calculado es DESDE el enemigo HACIA el jugador. Queremos empujar al jugador en esa dirección.
                    if vector_empuje.length_squared() > 0: # Solo aplicar si hay un vector (evita NaN si están en el mismo centro)
                        jugador_objetivo.aplicar_fuerza_de_empuje(vector_empuje)
                        self.tiempo_ultimo_empuje = tiempo_actual # Actualizar el tiempo del último empuje
                        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_enemigo_ia", False):
                            logger.info(f"{self.nombre_log_entidad} Aplicando empuje a Jugador. Vector: {vector_empuje}", extra={"categoria_log": "log_enemigo_ia"})

                        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_enemigo_ia", True): # Este log es más general y siempre se muestra si la categoría está activa
                            logger.info(f">>> EMPUJE APLICADO! {self.nombre_log_entidad} aplicó {vector_empuje} a Jugador.", extra={"categoria_log": "log_enemigo_ia"})
                else: # Empuje en cooldown
                    if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_enemigo_ia", False): 
                         logger.debug(f"{self.nombre_log_entidad} Empuje en cooldown para Jugador. Tiempo restante aprox: {self.cooldown_empuje - (tiempo_actual - self.tiempo_ultimo_empuje):.2f}s", extra={"categoria_log": "log_enemigo_ia"})
                # --- FIN LÓGICA COOLDOWN EMPUJE ---
        elif settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_enemigo_ia", False):
            if objetivo_rect is not None: # Solo loguear si no es None, para evitar spam si no hay objetivo
                logger.warning(f"{self.nombre_log_entidad} El objetivo_rect proporcionado no es una instancia de Jugador. Tipo: {type(objetivo_rect)}. No se aplicará empuje.", extra={"categoria_log": "log_enemigo_ia"})
        
        if settings.DEBUG_ENEMIGO_MOVIMIENTO:
            print(f"DEBUG_ENEMIGO: {self.nombre_log_entidad} - Después de lógica de empuje al jugador")
        
        print(f"DEBUG: {self.nombre_log_entidad} - FIN Enemigo.update()") # <--- PRINT AÑADIDO

    def dibujar(self, superficie_renderizado, offset_camara):
        # Implementa la lógica para dibujar el enemigo en la superficie de renderizado
        pass