import pygame
import os
from src.config import settings
import math
import logging
from src.entidades.entidad_base import EntidadBase
from src.sistemas.attack_profile_manager import AttackProfileManager
from src.sistemas.collision_handler import CollisionHandler
from src.sistemas.collision_handler import logger as logger_ch_externo

# Unificar loggers
logger = logging.getLogger("jugador")

class Jugador(EntidadBase):
    def __init__(self, x, y, asset_manager_instance):
        vida_maxima_jugador = getattr(settings, 'VIDA_MAXIMA_JUGADOR', 100)
        velocidad_jugador = getattr(settings, 'VELOCIDAD_JUGADOR', 180)
        hitbox_offset_x_jugador = getattr(settings, 'JUGADOR_HITBOX_OFFSET_X', 4)
        hitbox_offset_y_jugador = getattr(settings, 'JUGADOR_HITBOX_OFFSET_Y', 6)
        hitbox_ajuste_inferior_jugador = getattr(settings, 'JUGADOR_HITBOX_AJUSTE_INFERIOR', 4)
        retraso_anim_descanso = getattr(settings, 'JUGADOR_RETRASO_ANIM_DESCANSO', 150)

        anim_descanso_claves = [f"player_reposo_{i}" for i in range(1, 5)]
        dict_animaciones_jugador = {
            "descanso": {"claves_assets": anim_descanso_claves, "retraso": retraso_anim_descanso}
            # Aquí se podrían añadir otras animaciones como "corriendo", "atacando", etc.
            # "corriendo": {"claves_assets": ["player_corriendo_1", ...], "retraso": 100}
        }
        
        super().__init__(
            x=x, y=y, asset_manager_instance=asset_manager_instance,
            vida_maxima=vida_maxima_jugador,
            velocidad=velocidad_jugador,
            hitbox_offset_x=hitbox_offset_x_jugador,
            hitbox_offset_y=hitbox_offset_y_jugador,
            dict_animaciones_config=dict_animaciones_jugador,
            estado_anim_inicial="descanso",
            nombre_entidad_tipo="Jugador"
        )
        self.nombre_log_entidad = f"[JUGADOR_{self.id_entidad}]" 

        # --- Gestor de Perfiles de Ataque ---
        self.attack_profile_manager = AttackProfileManager(
            settings.RUTA_DATOS_PERFILES_ATAQUE,
            settings.ARCHIVO_CONFIG_ATAQUE, 
            settings.NOMBRE_PERFIL_ATAQUE_INICIAL
        )
        # --- Fin Gestor de Perfiles de Ataque ---
        
        # Inicializar el CollisionHandler (para gestionar colisiones)
        self.collision_handler = CollisionHandler()
        
        # Atributos específicos del Jugador
        self.ultima_direccion_mov_x = 1 
        self.ultima_direccion_mov_y = 0
        
        self.dano_base_ataque = getattr(settings, 'JUGADOR_DANO_BASE_ATAQUE', 5)
        self.cooldown_general_ataque = getattr(settings, 'JUGADOR_COOLDOWN_ATAQUE', 700) 

        # Estado del ataque actual
        self.tiempo_inicio_ataque = 0
        self.esta_atacando = False
        self.ultimo_ataque_realizado = 0 
        self.enemigos_golpeados_este_ataque = set()
        self.hitbox_ataque_actual_rect = pygame.Rect(0, 0, 0, 0)

        # Ajuste específico del hitbox del Jugador si difiere de EntidadBase
        # Jugador original: hb_alto = self.rect.height - (self.hitbox_offset_y + 4)
        # EntidadBase lo calcula como: self.rect.height - (2 * self.hitbox_offset_y)
        # Si hitbox_offset_y_jugador es 6, EntidadBase usa 12. Jugador original usa 6+4=10.
        # Esto significa que el hitbox del jugador es 2 píxeles más alto (menos reducido abajo)
        # que si se usara la fórmula genérica de EntidadBase con offsets simétricos.
        # Recalculamos explícitamente la altura del hitbox aquí para el jugador.
        hb_ancho_jugador = self.rect.width - (2 * self.hitbox_offset_x) # Ancho es simétrico
        hb_alto_jugador_especifico = self.rect.height - (self.hitbox_offset_y + hitbox_ajuste_inferior_jugador)
        self.hitbox.size = (max(1, hb_ancho_jugador), max(1, hb_alto_jugador_especifico))
        self._actualizar_posicion_hitbox() # Re-posicionar con el nuevo tamaño si cambió.
        
        # Posiciones flotantes para movimiento preciso
        self.pos_x_flotante = float(self.hitbox.x)
        self.pos_y_flotante = float(self.hitbox.y)

        # Vector para acumular fuerzas de empuje en el frame actual
        self.fuerzas_de_empuje_acumuladas_frame = pygame.math.Vector2(0, 0)

        # Log de hitbox recalculado
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_mov_detalle", False):
            logger.debug(f"{self.nombre_log_entidad} Hitbox recalculado a: {self.hitbox}", extra={"categoria_log": "log_jugador_mov_detalle"})

    def aplicar_fuerza_de_empuje(self, vector_empuje: pygame.math.Vector2):
        """
        Aplica un vector de fuerza de empuje a las fuerzas acumuladas del jugador para este frame.
        Estas fuerzas se procesarán en la actualización de movimiento.

        Args:
            vector_empuje (pygame.math.Vector2): El vector de empuje a aplicar.
        """
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_mov_detalle", False): # Podríamos necesitar una nueva categoría de log para empujes
            logger.debug(f"{self.nombre_log_entidad} INICIO aplicar_fuerza_de_empuje. Acumulado actual: {self.fuerzas_de_empuje_acumuladas_frame}, Aplicando: {vector_empuje}", extra={"categoria_log": "log_jugador_mov_detalle"})

        if vector_empuje and isinstance(vector_empuje, pygame.math.Vector2):
            self.fuerzas_de_empuje_acumuladas_frame += vector_empuje
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_mov_detalle", False): # Podríamos necesitar una nueva categoría de log para empujes
                logger.debug(f"{self.nombre_log_entidad} Fuerza de empuje aplicada: {vector_empuje}. Acumulado AHORA: {self.fuerzas_de_empuje_acumuladas_frame}", extra={"categoria_log": "log_jugador_mov_detalle"})
        elif settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_mov_detalle", False):
             logger.warning(f"{self.nombre_log_entidad} Intento de aplicar fuerza de empuje no válida: {vector_empuje}", extra={"categoria_log": "log_jugador_mov_detalle"})

    # --- Métodos de Movimiento y Colisión (específicos o usan CollisionHandler) ---
    def _mover_y_colisionar(self, dx, dy, obstaculos, mundo_ancho, mundo_alto):
        print(f"DEBUG_JUGADOR: {self.nombre_log_entidad} - ENTRANDO A _mover_y_colisionar() con dx={dx}, dy={dy}, mundo_ancho={mundo_ancho}, mundo_alto={mundo_alto}")
        """
        Intenta mover la entidad y maneja las colisiones.
        Esta función llama al CollisionHandler y actualiza el rect y hitbox de la entidad.
        Devuelve el delta_x_real y delta_y_real del movimiento del hitbox.
        """
        dx_para_colision = int(round(dx))
        dy_para_colision = int(round(dy))

        delta_mov_x_hb = 0 # Inicializar deltas
        delta_mov_y_hb = 0

        if dx_para_colision != 0 or dy_para_colision != 0:
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_mov_detalle", False):
                logger.debug(f"Movimiento para CH: dx_int={dx_para_colision}, dy_int={dy_para_colision}. HB (antes CH): TL={self.hitbox.topleft}, Size={self.hitbox.size}", extra={"categoria_log": "log_jugador_mov_detalle"})

            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_mov_detalle", False):
                logger.debug(f"{self.nombre_log_entidad} INSPECCION_CH ANTES: self.collision_handler = {self.collision_handler}, type = {type(self.collision_handler)}", extra={"categoria_log": "log_jugador_mov_detalle"})
                if hasattr(self.collision_handler, 'gestionar_movimiento_y_colision'):
                    logger.debug(f"{self.nombre_log_entidad} CH tiene el método gestionar_movimiento_y_colision.", extra={"categoria_log": "log_jugador_mov_detalle"})
                else:
                    logger.warning(f"{self.nombre_log_entidad} CH NO TIENE el método gestionar_movimiento_y_colision.", extra={"categoria_log": "log_jugador_mov_detalle"})

            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler", False):
                 logger_ch_externo.critical(f"TEST LOG DESDE JUGADOR ({self.nombre_log_entidad}) USANDO LOGGER_CH_EXTERNO ANTES DE LLAMADA CH (_mover_y_colisionar).", extra={"categoria_log": "log_collision_handler"})
            
            print(f"DEBUG_JUGADOR: {self.nombre_log_entidad} - ANTES de llamar a collision_handler.gestionar_movimiento_y_colision") # <--- NUEVO PRINT DE CONTROL
            delta_mov_x_hb, delta_mov_y_hb = self.collision_handler.gestionar_movimiento_y_colision(
                self, self.hitbox, self.rect, self.hitbox_offset_x, self.hitbox_offset_y,
                dx_para_colision, dy_para_colision, obstaculos,
                mundo_ancho, mundo_alto # <--- ARGUMENTOS AÑADIDOS
            )
            print(f"DEBUG_JUGADOR: {self.nombre_log_entidad} - DESPUÉS de llamar a collision_handler.gestionar_movimiento_y_colision. Deltas HB: ({delta_mov_x_hb}, {delta_mov_y_hb})") # <--- NUEVO PRINT DE CONTROL

            if delta_mov_x_hb != 0:
                self.ultima_direccion_mov_x = 1 if delta_mov_x_hb > 0 else -1
                self.ultima_direccion_mov_y = 0
            elif delta_mov_y_hb != 0:
                self.ultima_direccion_mov_x = 0
                self.ultima_direccion_mov_y = 1 if delta_mov_y_hb > 0 else -1

            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_mov_detalle", False):
                logger.debug(f"HB (después CH en _mover_y_colisionar): TL={self.hitbox.topleft}, Size={self.hitbox.size}. Rect (después CH): TL={self.rect.topleft}", extra={"categoria_log": "log_jugador_mov_detalle"})

        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_mov_detalle", False): 
            if dx_para_colision != 0 or dy_para_colision != 0 or delta_mov_x_hb != 0 or delta_mov_y_hb != 0 :
                logger.debug(f"Movimiento REALIZADO por HB (_mover_y_colisionar): dx={delta_mov_x_hb}, dy={delta_mov_y_hb}. HB Final: {self.hitbox.topleft}. Rect Final: {self.rect.topleft}", extra={"categoria_log": "log_jugador_mov_detalle"})
        return delta_mov_x_hb, delta_mov_y_hb

    def actualizar_movimiento(self, teclas_presionadas, obstaculos, mundo_ancho, mundo_alto, delta_time):
        print(f"DEBUG_JUGADOR: {self.nombre_log_entidad} - INICIO actualizar_movimiento()") # PRINT 4
        mov_x_input_raw = 0 
        mov_y_input_raw = 0

        if teclas_presionadas[pygame.K_LEFT] or teclas_presionadas[pygame.K_a]:
            mov_x_input_raw = -self.velocidad
        if teclas_presionadas[pygame.K_RIGHT] or teclas_presionadas[pygame.K_d]:
            mov_x_input_raw = self.velocidad
        if teclas_presionadas[pygame.K_UP] or teclas_presionadas[pygame.K_w]:
            mov_y_input_raw = -self.velocidad
        if teclas_presionadas[pygame.K_DOWN] or teclas_presionadas[pygame.K_s]:
            mov_y_input_raw = self.velocidad
        
        print(f"DEBUG_JUGADOR: {self.nombre_log_entidad} - Después de procesar teclas, mov_input_raw=({mov_x_input_raw},{mov_y_input_raw})") # PRINT 5

        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_mov_detalle", False):
            logger.debug(f"{self.nombre_log_entidad} Input teclado procesado: mov_x_input_raw={mov_x_input_raw}, mov_y_input_raw={mov_y_input_raw}", extra={"categoria_log": "log_jugador_mov_detalle"})

        # ---- LOG ADICIONAL ----
        logger.critical(f"{self.nombre_log_entidad} INICIO ACTUALIZAR_MOVIMIENTO. Delta_time: {delta_time}")

        dx_flotante_intentado_input = mov_x_input_raw * delta_time
        dy_flotante_intentado_input = mov_y_input_raw * delta_time

        # ---- LOG DETALLADO DE COMPONENTES DE MOVIMIENTO ----
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_mov_detalle", True): # Temporalmente True para forzar el log
            logger.debug(f"{self.nombre_log_entidad} PRE-SUMA EMPUJE: dx_input={dx_flotante_intentado_input:.4f}, dy_input={dy_flotante_intentado_input:.4f}", extra={"categoria_log": "log_jugador_mov_detalle"})
            logger.debug(f"{self.nombre_log_entidad} PRE-SUMA EMPUJE: fuerzas_acumuladas_X={self.fuerzas_de_empuje_acumuladas_frame.x:.4f}, fuerzas_acumuladas_Y={self.fuerzas_de_empuje_acumuladas_frame.y:.4f}", extra={"categoria_log": "log_jugador_mov_detalle"})
        # ---- FIN LOG DETALLADO ----

        # Limitar la magnitud máxima del vector de empuje acumulado
        fuerza_max_empuje_por_frame = getattr(settings, "JUGADOR_MAX_FUERZA_EMPUJE_FRAME", 10.0) 
        if self.fuerzas_de_empuje_acumuladas_frame.length_squared() > fuerza_max_empuje_por_frame**2:
            magnitud_original = self.fuerzas_de_empuje_acumuladas_frame.length()
            self.fuerzas_de_empuje_acumuladas_frame.scale_to_length(fuerza_max_empuje_por_frame)
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_mov_detalle", False):
                logger.warning(f"{self.nombre_log_entidad} CLAMP aplicado a fuerzas de empuje. Original (mag: {magnitud_original:.2f}) > {fuerza_max_empuje_por_frame:.2f}. Nuevo: {self.fuerzas_de_empuje_acumuladas_frame} (mag: {self.fuerzas_de_empuje_acumuladas_frame.length():.2f})", extra={"categoria_log": "log_jugador_mov_detalle"})

        # Aplicar fuerzas de empuje acumuladas al movimiento flotante intentado
        # Estas fuerzas vienen de interacciones externas (ej. empujes de enemigos) y se acumulan durante el frame.
        print(f"DEBUG_JUGADOR: {self.nombre_log_entidad} - Antes de sumar fuerzas de empuje. dx_input={dx_flotante_intentado_input}, dy_input={dy_flotante_intentado_input}, empuje_acumulado={self.fuerzas_de_empuje_acumuladas_frame}")
        dx_flotante_intentado_total = dx_flotante_intentado_input + self.fuerzas_de_empuje_acumuladas_frame.x
        dy_flotante_intentado_total = dy_flotante_intentado_input + self.fuerzas_de_empuje_acumuladas_frame.y
        print(f"DEBUG_JUGADOR: {self.nombre_log_entidad} - Después de sumar fuerzas de empuje. dx_total={dx_flotante_intentado_total}, dy_total={dy_flotante_intentado_total}")
        
        # Resetear las fuerzas acumuladas para el próximo frame
        if self.fuerzas_de_empuje_acumuladas_frame.length_squared() > 0: # Log solo si hubo empuje
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_mov_detalle", False):
                logger.debug(f"{self.nombre_log_entidad} Fuerzas empuje aplicadas este frame: {self.fuerzas_de_empuje_acumuladas_frame}", extra={"categoria_log": "log_jugador_mov_detalle"})
        self.fuerzas_de_empuje_acumuladas_frame.xy = (0, 0) 

        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_mov_detalle", False):
            logger.debug(f"{self.nombre_log_entidad} Delta flotante (input): dx={dx_flotante_intentado_input:.4f}, dy={dy_flotante_intentado_input:.4f}", extra={"categoria_log": "log_jugador_mov_detalle"})
            logger.debug(f"{self.nombre_log_entidad} Delta flotante TOTAL (input+empuje): dx={dx_flotante_intentado_total:.4f}, dy={dy_flotante_intentado_total:.4f} (delta_time: {delta_time:.4f})", extra={"categoria_log": "log_jugador_mov_detalle"})

        # --- NUEVO ORDEN ---
        # 1. Intentar mover y colisionar con el delta total (input + empuje)
        # _mover_y_colisionar espera deltas enteros, así que redondeamos aquí.
        # El método _mover_y_colisionar actualizará self.hitbox y self.rect internamente.
        print(f"DEBUG_JUGADOR: {self.nombre_log_entidad} - Antes de llamar a self._mover_y_colisionar con dx_total={dx_flotante_intentado_total}, dy_total={dy_flotante_intentado_total}") # PRINT 6
        
        # ---- LLAMADA A _mover_y_colisionar ----
        # Asegurarse de que se pasan mundo_ancho y mundo_alto
        delta_hb_x, delta_hb_y = self._mover_y_colisionar(dx_flotante_intentado_total, dy_flotante_intentado_total, obstaculos, mundo_ancho, mundo_alto)
        # ---- FIN LLAMADA ----
        print(f"DEBUG_JUGADOR: {self.nombre_log_entidad} - Después de llamar a self._mover_y_colisionar. Movimiento real HB: ({delta_hb_x},{delta_hb_y})") # PRINT 7

        # 2. Sincronizar pos_flotante con la posición del hitbox DESPUÉS de la colisión
        # Esto es crucial porque _mover_y_colisionar puede haber ajustado la posición.
        self.pos_x_flotante = float(self.hitbox.x)
        self.pos_y_flotante = float(self.hitbox.y)

        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_mov_detalle", False):
            logger.debug(f"{self.nombre_log_entidad} Pos flotante (post-CH, pre-límites): ({self.pos_x_flotante:.4f}, {self.pos_y_flotante:.4f})", extra={"categoria_log": "log_jugador_mov_detalle"})

        # 3. Ahora, aplicar colisión con Límites del Mundo a pos_flotante
        pos_x_antes_limites = self.pos_x_flotante
        pos_y_antes_limites = self.pos_y_flotante

        if self.pos_x_flotante < 0: # No se necesita int() aquí, pos_flotante ya es numérico
            self.pos_x_flotante = 0.0
        elif self.pos_x_flotante + self.hitbox.width > mundo_ancho:
            self.pos_x_flotante = float(mundo_ancho - self.hitbox.width)
        
        if self.pos_y_flotante < 0:
            self.pos_y_flotante = 0.0
        elif self.pos_y_flotante + self.hitbox.height > mundo_alto:
            self.pos_y_flotante = float(mundo_alto - self.hitbox.height)

        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_mov_detalle", False):
            if self.pos_x_flotante != pos_x_antes_limites or self.pos_y_flotante != pos_y_antes_limites:
                logger.debug(f"{self.nombre_log_entidad} Pos flotante (post-límites): ({self.pos_x_flotante:.4f}, {self.pos_y_flotante:.4f}). ANTES: ({pos_x_antes_limites:.4f}, {pos_y_antes_limites:.4f})", extra={"categoria_log": "log_jugador_mov_detalle"})
            else:
                logger.debug(f"{self.nombre_log_entidad} Pos flotante (post-límites): ({self.pos_x_flotante:.4f}, {self.pos_y_flotante:.4f}) (sin cambios por límites)", extra={"categoria_log": "log_jugador_mov_detalle"})

        # 4. Sincronizar FINALMENTE el hitbox y el rect con pos_flotante (que ahora está limitado por el mundo)
        # Esto asegura que la representación visual y de colisión sea la final.
        self.hitbox.topleft = (round(self.pos_x_flotante), round(self.pos_y_flotante))
        self.rect.center = self.hitbox.center # O la lógica de alineación de rect que se prefiera

        # Log de la posición final del hitbox para este frame
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_mov_detalle", False):
            logger.debug(f"{self.nombre_log_entidad} Posición POST CH y Límites (actualizar_movimiento): HB: {self.hitbox.topleft}, PosFlotante: ({self.pos_x_flotante:.2f}, {self.pos_y_flotante:.2f})", extra={"categoria_log": "log_jugador_mov_detalle"})

        # Actualizar animación basado en si hubo movimiento REAL del hitbox
        # ---- LOG ADICIONAL ----
        logger.critical(f"{self.nombre_log_entidad} ANTES de setear self.estado_animacion. Movimiento real?: dx_hb_real={delta_hb_x}, dy_hb_real={delta_hb_y}")
        if delta_hb_x != 0 or delta_hb_y != 0:
            # self.estado_animacion = "corriendo" # Asumiendo que tienes una animación "corriendo"
            pass # Lógica de animación de movimiento aquí si es necesario
        else:
            self.estado_animacion = "descanso" # CORREGIDO
        
        # ---- LOG ADICIONAL ----
        logger.critical(f"{self.nombre_log_entidad} DESPUÉS de setear self.estado_animacion. Ahora es: {self.estado_animacion}")
        logger.critical(f"{self.nombre_log_entidad} ANTES de llamar a self.actualizar_animacion({delta_time})")

        self.actualizar_animacion(delta_time)
        print(f"DEBUG_JUGADOR: {self.nombre_log_entidad} - FIN actualizar_movimiento()") # PRINT 8

    def actualizar_posicion_y_limites_mundo(self, mundo_ancho, mundo_alto): # ESTA FUNCIÓN YA NO ES NECESARIA SI LA LÓGICA ESTÁ EN actualizar_movimiento
        """
        DEPRECATED: La lógica de límites del mundo se ha movido a actualizar_movimiento.
        Mantiene al jugador dentro de los límites del mundo del juego.
        Ajusta self.pos_x_flotante y self.pos_y_flotante.
        """
        # Esta función puede ser eliminada o dejada vacía si ya no se llama.
        # Por seguridad, si se llama, que no haga nada o loguee una advertencia.
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_general", True): # Temporalmente a True
            logger.warning(f"{self.nombre_log_entidad} actualizar_posicion_y_limites_mundo() fue llamada pero está DEPRECADA.", extra={"categoria_log": "log_jugador_general"})
        pass

    # --- Métodos de Ataque (usan AttackProfileManager) ---
    def atacar(self):
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_ataque_debug", False):
            logger.debug(f"{self.nombre_log_entidad} Entrando a atacar().", extra={"categoria_log": "log_jugador_ataque_debug"})
        
        ahora = pygame.time.get_ticks()
        cooldown_mod_fallback = getattr(settings, 'ATAQUE_BASE_COOLDOWN_MODIFICADOR', 1.0)
        
        cooldown_modificador = self.attack_profile_manager.get_parametro_ataque_activo('cooldown_modificador', cooldown_mod_fallback)
        cooldown_efectivo = self.cooldown_general_ataque * cooldown_modificador
        
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_ataque_debug", False):
            logger.debug(f"{self.nombre_log_entidad} Cooldown efectivo: {cooldown_efectivo}ms, Último ataque: {self.ultimo_ataque_realizado}, Ahora: {ahora}", extra={"categoria_log": "log_jugador_ataque_debug"})

        if ahora - self.ultimo_ataque_realizado > cooldown_efectivo:
            self.esta_atacando = True
            self.tiempo_inicio_ataque = ahora
            self.ultimo_ataque_realizado = ahora
            self.enemigos_golpeados_este_ataque.clear() 
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_ataque_debug", False):
                logger.debug(f"{self.nombre_log_entidad} ATAQUE INICIADO. esta_atacando=True, Perfil: '{self.attack_profile_manager.nombre_perfil_ataque_activo}'", extra={"categoria_log": "log_jugador_ataque_debug"})
        else:
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_ataque_debug", False):
                logger.debug(f"{self.nombre_log_entidad} Ataque en cooldown. Saliendo de atacar().", extra={"categoria_log": "log_jugador_ataque_debug"})
            pass

    def actualizar_ataque(self, enemigos):
        if not self.esta_atacando:
            return
        
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_ataque_debug", False):
            logger.debug(f"{self.nombre_log_entidad} Entrando a actualizar_ataque(). esta_atacando es True.", extra={"categoria_log": "log_jugador_ataque_debug"})

        offset_distancia_base = getattr(settings, 'ATAQUE_BASE_OFFSET_DISTANCIA', 25.0)
        extension_base = getattr(settings, 'ATAQUE_BASE_EXTENSION', 30.0)
        grosor_base = getattr(settings, 'ATAQUE_BASE_GROSOR', 15.0)
        duracion_total_ms_base = getattr(settings, 'ATAQUE_BASE_DURACION_TOTAL_MS', 300.0)
        plantilla_angulos_base = getattr(settings, 'ATAQUE_BASE_PLANTILLA_ANGULOS_GRADOS', [0])
        
        offset_distancia = self.attack_profile_manager.get_parametro_ataque_activo('offset_distancia', offset_distancia_base)
        extension_valor = self.attack_profile_manager.get_parametro_ataque_activo('extension', extension_base)
        grosor_valor = self.attack_profile_manager.get_parametro_ataque_activo('grosor', grosor_base)
        duracion_total_ms = self.attack_profile_manager.get_parametro_ataque_activo('duracion_total_ms', duracion_total_ms_base)
        plantilla_angulos_grados = self.attack_profile_manager.get_parametro_ataque_activo('plantilla_angulos_grados', plantilla_angulos_base)

        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_ataque_debug", False):
            logger.debug(f"{self.nombre_log_entidad} Params perfil ataque: Offset={offset_distancia}, Ext={extension_valor}, Grosor={grosor_valor}", extra={"categoria_log": "log_jugador_ataque_debug"})

        ahora = pygame.time.get_ticks()
        tiempo_transcurrido_ataque = ahora - self.tiempo_inicio_ataque
        
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_ataque_debug", False):
            logger.debug(f"{self.nombre_log_entidad} Duración ataque: {duracion_total_ms}ms, Tiempo inicio: {self.tiempo_inicio_ataque}, Ahora: {ahora}", extra={"categoria_log": "log_jugador_ataque_debug"})

        if tiempo_transcurrido_ataque > duracion_total_ms:
            self.esta_atacando = False
            self.hitbox_ataque_actual_rect.size = (0,0) # Resetear para que no se dibuje
            
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_ataque_debug", False):
                logger.debug(f"{self.nombre_log_entidad} ATAQUE FINALIZADO por duración.", extra={"categoria_log": "log_jugador_ataque_debug"})
            return

        vector_direccion_normalizado = [self.ultima_direccion_mov_x, self.ultima_direccion_mov_y]
        if vector_direccion_normalizado == [0, 0]:
            vector_direccion_normalizado = [1, 0] 

        centro_offset_x = vector_direccion_normalizado[0] * offset_distancia
        centro_offset_y = vector_direccion_normalizado[1] * offset_distancia
        centro_hitbox_ataque_x = self.hitbox.centerx + centro_offset_x
        centro_hitbox_ataque_y = self.hitbox.centery + centro_offset_y

        if abs(vector_direccion_normalizado[0]) > abs(vector_direccion_normalizado[1]):
            ancho_total_hb = extension_valor
            alto_total_hb = grosor_valor
        else: 
            ancho_total_hb = grosor_valor
            alto_total_hb = extension_valor
        
        self.hitbox_ataque_actual_rect = pygame.Rect(
            centro_hitbox_ataque_x - ancho_total_hb // 2,
            centro_hitbox_ataque_y - alto_total_hb // 2,
            ancho_total_hb,
            alto_total_hb
        )
        
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_ataque_calculo", False):
            logger.debug(f"{self.nombre_log_entidad} Hitbox ataque calculado: {self.hitbox_ataque_actual_rect}", extra={"categoria_log": "log_jugador_ataque_calculo"})
        
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_ataque_debug", False):
            logger.debug(f"{self.nombre_log_entidad} Hitbox ataque: {self.hitbox_ataque_actual_rect}, Dir: ({vector_direccion_normalizado[0]:.2f}, {vector_direccion_normalizado[1]:.2f})", extra={"categoria_log": "log_jugador_ataque_debug"})

        for enemigo in enemigos:
            if enemigo not in self.enemigos_golpeados_este_ataque:
                if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_ataque_debug", False):
                    logger.debug(f"{self.nombre_log_entidad} Verificando colisión con {enemigo.nombre_log_entidad} (HB: {enemigo.hitbox})", extra={"categoria_log": "log_jugador_ataque_debug"})
                if self.hitbox_ataque_actual_rect.colliderect(enemigo.hitbox):
                    dano_modificador_perfil = self.attack_profile_manager.get_parametro_ataque_activo('dano_modificador', settings.ATAQUE_BASE_DANO_MODIFICADOR)
                    dano_final = self.dano_base_ataque * dano_modificador_perfil
                    
                    if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_ataque_debug", False):
                        logger.debug(f"{self.nombre_log_entidad} ¡GOLPEÓ a {enemigo.nombre_log_entidad}! Daño base: {self.dano_base_ataque}, Mod: {dano_modificador_perfil}, Daño final: {dano_final}", extra={"categoria_log": "log_jugador_ataque_debug"})
                    enemigo.recibir_dano(dano_final, "ataque_jugador")
                    self.enemigos_golpeados_este_ataque.add(enemigo)
                elif settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_ataque_debug", False):
                    logger.debug(f"{self.nombre_log_entidad} NO colisión con {enemigo.nombre_log_entidad}", extra={"categoria_log": "log_jugador_ataque_debug"})

    def update(self, teclas_presionadas, obstaculos_solidos, enemigos_sprites_para_ataque, mundo_ancho, mundo_alto, delta_time):
        print(f"DEBUG_JUGADOR: {self.nombre_log_entidad} - INICIO update()") # PRINT 1
        if not self.ha_muerto:
            self.actualizar_movimiento(teclas_presionadas, obstaculos_solidos, mundo_ancho, mundo_alto, delta_time)
            print(f"DEBUG_JUGADOR: {self.nombre_log_entidad} - Después de llamar a self.actualizar_movimiento()") # PRINT 3
            
            self.actualizar_ataque(enemigos_sprites_para_ataque)
        else:
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_general", False):
                logger.debug(f"{self.nombre_log_entidad} Jugador está muerto, no se actualiza.", extra={"categoria_log":"log_jugador_general"})
            pass

    def dibujar(self, superficie):
        super().dibujar(superficie) # Si EntidadBase tiene un método dibujar, si no, pygame.sprite.Sprite no lo tiene.
        # Si se necesita dibujar algo más específico del jugador (ej: HUD de vida sobre la cabeza), hacerlo aquí.
        # Por ahora, la imagen y rect son manejados por el grupo de sprites y EntidadBase.

    def recibir_dano(self, cantidad, tipo_dano="generico"):
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_vida", False):
            logger.debug(f"{self.nombre_log_entidad} Jugador.recibir_dano llamado con cantidad {cantidad}", extra={"categoria_log": "log_jugador_vida"})
        
        super().recibir_dano(cantidad, tipo_dano)
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_vida", False):
            logger.debug(f"{self.nombre_log_entidad} recibió daño (post EntidadBase). Vida actual: {self.vida_actual}", extra={"categoria_log": "log_jugador_vida"})
        return True

    def dibujar_debug_ataque(self, superficie_destino, camara):
        if settings.DEBUG_VER_HITBOX_ATAQUE_JUGADOR and self.esta_atacando and self.hitbox_ataque_actual_rect.width > 0:
            # Ajustar las coordenadas del hitbox de ataque por la cámara
            hitbox_ataque_visible = camara.aplicar_offset_a_rect(self.hitbox_ataque_actual_rect)
            pygame.draw.rect(superficie_destino, settings.COLOR_HITBOX_ATAQUE_JUGADOR, hitbox_ataque_visible, settings.GROSOR_HITBOX_ATAQUE_DEBUG)
# Nueva línea al final para intentar limpiar posibles bytes nulos al final del archivo. 