import pygame
import os
from src.config import settings
import math
import logging
from src.entidades.entidad_base import EntidadBase
from src.sistemas.attack_profile_manager import AttackProfileManager
from src.sistemas.collision_handler import CollisionHandler
from src.utils import utils
from src.sistemas.motor_fisica import MotorFisica

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

        # Instancia de MotorFisica para gestionar el empuje
        factor_friccion_cfg = getattr(settings, "FACTOR_FRICCION_EMPUJE_JUGADOR", 0.85)
        umbral_fuerza_cfg = getattr(settings, "UMBRAL_FUERZA_EMPUJE_MINIMA_JUGADOR", 0.5)
        self.motor_fisica_empuje = MotorFisica(
            factor_friccion=factor_friccion_cfg, 
            umbral_fuerza_minima=umbral_fuerza_cfg,
            nombre_entidad_log=self.nombre_log_entidad + "_MFEmpuje"
        )

        # Log de hitbox recalculado
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_mov_detalle", False):
            logger.debug(f"{self.nombre_log_entidad} Hitbox recalculado a: {self.hitbox}", extra={"categoria_log": "log_jugador_mov_detalle"})

    def aplicar_fuerza_de_empuje(self, vector_empuje: pygame.math.Vector2):
        """
        Agrega un vector de fuerza de empuje al MotorFisica del jugador.
        Estas fuerzas, gestionadas por MotorFisica (con fricción y umbral),
        contribuirán al movimiento en frames subsecuentes.

        Args:
            vector_empuje (pygame.math.Vector2): El vector de empuje a aplicar.
        """
        if not isinstance(vector_empuje, pygame.math.Vector2):
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_empuje", False):
                 logger.warning(f"{self.nombre_log_entidad} Intento de aplicar fuerza de empuje NO VÁLIDA (no es Vector2): {vector_empuje}", extra={"categoria_log": "log_jugador_empuje"})
            return

        if vector_empuje.length_squared() == 0:
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_empuje_verbose", False): # Usar verbose para no saturar
                 logger.info(f"{self.nombre_log_entidad} Intento de aplicar fuerza de empuje CERO. No se acumula. Vector: {vector_empuje}", extra={"categoria_log": "log_jugador_empuje_verbose"})
            return

        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_empuje", False):
            logger.info(f"{self.nombre_log_entidad} RECIBIENDO FUERZA EMPUJE para MotorFisica. Aplicando AHORA: {vector_empuje}", extra={"categoria_log": "log_jugador_empuje"})

        self.motor_fisica_empuje.agregar_fuerza(vector_empuje)
        
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_empuje", False):
            logger.info(f"{self.nombre_log_entidad} FUERZA EMPUJE APLICADA a MotorFisica. MotorFisica acumulado: {self.motor_fisica_empuje.fuerzas_acumuladas}", extra={"categoria_log": "log_jugador_empuje"})

    # --- Métodos de Movimiento y Colisión (específicos o usan CollisionHandler) ---
    def _mover_y_colisionar(self, dx, dy, obstaculos, mundo_ancho, mundo_alto):
        if settings.DEBUG_JUGADOR_MOVIMIENTO:
            print(f"DEBUG_JUGADOR: {self.nombre_log_entidad} - ENTRANDO A _mover_y_colisionar() con dx={dx}, dy={dy}, mundo_ancho={mundo_ancho}, mundo_alto={mundo_alto}")
        
        # Convertido a log:
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_mov_input", False):
            logger.debug(f"{self.nombre_log_entidad} Entrando a _mover_y_colisionar. Input: dx={dx:.2f}, dy={dy:.2f}. Mundo: ({mundo_ancho}, {mundo_alto})", extra={"categoria_log": "log_jugador_mov_input"})
        """
        Intenta mover la entidad y maneja las colisiones.
        Esta función llama al CollisionHandler y actualiza el rect y hitbox de la entidad.
        Devuelve el delta_x_real y delta_y_real del movimiento del hitbox.
        """
        # dx_para_colision = int(round(dx))
        # dy_para_colision = int(round(dy))

        # Nueva lógica para convertir deltas flotantes a enteros para colisión usando la utilidad
        dx_para_colision, dy_para_colision = utils.convertir_deltas_a_enteros_para_colision(
            dx, dy, settings.UMBRAL_MOV_FLOTANTE_ENTIDAD_PARA_COLISION
        )

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

            # Convertido a log:
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_mov_debug", False):
                logger.debug(f"{self.nombre_log_entidad} ANTES de llamar a collision_handler.gestionar_movimiento_y_colision", extra={"categoria_log": "log_jugador_mov_debug"})
            
            delta_mov_x_hb, delta_mov_y_hb = self.collision_handler.gestionar_movimiento_y_colision(
                self, self.hitbox, self.rect, self.hitbox_offset_x, self.hitbox_offset_y,
                dx_para_colision, dy_para_colision, obstaculos,
                mundo_ancho, mundo_alto # <--- ARGUMENTOS AÑADIDOS
            )

            # Convertido a log:
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_mov_debug", False):
                logger.debug(f"{self.nombre_log_entidad} DESPUÉS de llamar a collision_handler.gestionar_movimiento_y_colision. Deltas HB: ({delta_mov_x_hb}, {delta_mov_y_hb})", extra={"categoria_log": "log_jugador_mov_debug"})

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
        """
        Actualiza el movimiento del jugador basado en el input del teclado y las fuerzas de empuje.

        Primero, actualiza el estado de las fuerzas de empuje en el MotorFisica (aplicando fricción/umbral).
        Luego, obtiene el vector de movimiento resultante del empuje para este frame.
        Combina el movimiento del input del teclado con el movimiento por empuje.
        La posición flotante del jugador se actualiza con este movimiento total.
        Finalmente, se llama a _mover_y_colisionar para manejar las colisiones con obstáculos y límites del mundo,
        y la posición flotante se sincroniza con la posición final del hitbox.

        Args:
            teclas_presionadas: Estado de las teclas presionadas.
            obstaculos: Grupo de sprites de obstáculos sólidos.
            mundo_ancho (int): Ancho total del mundo del juego.
            mundo_alto (int): Alto total del mundo del juego.
            delta_time (float): Tiempo transcurrido desde el último frame.
        """
        # Convertido a log:
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_mov_input", False):
            logger.debug(f"{self.nombre_log_entidad} Inicio actualizar_movimiento(). Delta_time: {delta_time:.4f}", extra={"categoria_log": "log_jugador_mov_input"})
        
        # Actualizar el estado de las fuerzas de empuje (aplicar fricción, umbral)
        self.motor_fisica_empuje.actualizar_estado_fuerzas(delta_time)
        
        # Obtener el vector de movimiento resultante del empuje para este frame
        vector_mov_empuje = self.motor_fisica_empuje.get_vector_movimiento_resultante_del_frame(delta_time)

        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_empuje", False):
            if vector_mov_empuje.length_squared() > 0:
                logger.debug(f"{self.nombre_log_entidad} Vector de empuje de MotorFisica para este frame: {vector_mov_empuje} (Velocidad por empuje)", extra={"categoria_log": "log_jugador_empuje"})
            elif self.motor_fisica_empuje.tiene_fuerzas_activas(): # Loguear si tiene fuerzas pero el delta es 0 (por delta_time = 0?)
                logger.debug(f"{self.nombre_log_entidad} MotorFisica tiene fuerzas ({self.motor_fisica_empuje.fuerzas_acumuladas}) pero el mov_empuje del frame es {vector_mov_empuje}", extra={"categoria_log": "log_jugador_empuje"})

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

        dx_input_con_velocidad = mov_x_input_raw * delta_time
        dy_input_con_velocidad = mov_y_input_raw * delta_time

        # Sumar el movimiento por empuje al movimiento por input
        dx_total_flotante_frame = dx_input_con_velocidad + vector_mov_empuje.x
        dy_total_flotante_frame = dy_input_con_velocidad + vector_mov_empuje.y

        # Convertido a log:
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_mov_debug", False):
            logger.debug(f"{self.nombre_log_entidad} Actualizar_mov: Input(dx,dy):({dx_input_con_velocidad:.4f}, {dy_input_con_velocidad:.4f}), Empuje(dx,dy):({vector_mov_empuje.x:.4f}, {vector_mov_empuje.y:.4f}), TotalFrame(dx,dy):({dx_total_flotante_frame:.4f}, {dy_total_flotante_frame:.4f})", extra={"categoria_log": "log_jugador_mov_debug"})

        self.pos_x_flotante += dx_total_flotante_frame
        self.pos_y_flotante += dy_total_flotante_frame

        # Convertido a log:
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_mov_debug", False):
            logger.debug(f"{self.nombre_log_entidad} Pos flotante (post-input y empuje): ({self.pos_x_flotante:.4f}, {self.pos_y_flotante:.4f})", extra={"categoria_log": "log_jugador_mov_debug"})

        # Restaurar la posición del hitbox a la posición flotante antes de la colisión
        # Esto es crucial porque _mover_y_colisionar espera que el hitbox esté en la posición "actual"
        # antes de calcular el delta que realmente se puede mover.
        hitbox_x_original_antes_de_colision = self.hitbox.x
        hitbox_y_original_antes_de_colision = self.hitbox.y

        self.hitbox.x = int(round(self.pos_x_flotante - dx_total_flotante_frame)) 
        self.hitbox.y = int(round(self.pos_y_flotante - dy_total_flotante_frame)) 
        
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_mov_detalle", False):
            logger.debug(f"{self.nombre_log_entidad} Hitbox REAJUSTADO a pos flotante ANTERIOR al frame actual, ANTES de _mover_y_colisionar: TL={self.hitbox.topleft}", extra={"categoria_log": "log_jugador_mov_detalle"})

        delta_x_movido_hb, delta_y_movido_hb = self._mover_y_colisionar(
            dx_total_flotante_frame, 
            dy_total_flotante_frame, 
            obstaculos, 
            mundo_ancho, 
            mundo_alto
        )

        # Actualizar la posición flotante final basada en cuánto se movió realmente el hitbox
        # Esto asegura que la posición flotante refleje la posición real después de las colisiones.
        self.pos_x_flotante = float(self.hitbox.x) 
        self.pos_y_flotante = float(self.hitbox.y)

        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_mov_detalle", False):
            logger.debug(f"{self.nombre_log_entidad} Pos flotante FINAL (post _m_y_c y sinc con HB): ({self.pos_x_flotante:.4f}, {self.pos_y_flotante:.4f}). HB Final: {self.hitbox.topleft}", extra={"categoria_log": "log_jugador_mov_detalle"})

        # Mantener al jugador dentro de los límites del mundo (aplicado al hitbox)
        self.hitbox.clamp_ip(pygame.Rect(0, 0, mundo_ancho, mundo_alto)) 
        self._actualizar_posicion_rect_desde_hitbox()
        # Sincronizar pos_flotante nuevamente si clamp_ip hizo algún cambio
        if self.hitbox.x != self.pos_x_flotante or self.hitbox.y != self.pos_y_flotante:
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_mov_clamp", False):
                logger.debug(f"{self.nombre_log_entidad} CLAMP Limites Mundo: HB cambió de ({self.pos_x_flotante},{self.pos_y_flotante}) a ({self.hitbox.x},{self.hitbox.y}). Resincronizando pos_flotante.", extra={"categoria_log": "log_jugador_mov_clamp"})
            self.pos_x_flotante = float(self.hitbox.x)
            self.pos_y_flotante = float(self.hitbox.y)

        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_mov_detalle", False):
            logger.debug(f"{self.nombre_log_entidad} FIN actualizar_movimiento. Pos Flotante Final: ({self.pos_x_flotante:.2f}, {self.pos_y_flotante:.2f}). HB: {self.hitbox.topleft}", extra={"categoria_log": "log_jugador_mov_detalle"})

        # Actualizar animación basado en si hubo movimiento REAL del hitbox
        # ---- LOG ADICIONAL ----
        logger.critical(f"{self.nombre_log_entidad} ANTES de setear self.estado_animacion. Movimiento real?: dx_hb_real={delta_x_movido_hb}, dy_hb_real={delta_y_movido_hb}")
        if delta_x_movido_hb != 0 or delta_y_movido_hb != 0:
            # self.estado_animacion = "corriendo" # Asumiendo que tienes una animación "corriendo"
            pass # Lógica de animación de movimiento aquí si es necesario
        else:
            self.estado_animacion = "descanso" # CORREGIDO
        
        # ---- LOG ADICIONAL ----
        logger.critical(f"{self.nombre_log_entidad} DESPUÉS de setear self.estado_animacion. Ahora es: {self.estado_animacion}")
        logger.critical(f"{self.nombre_log_entidad} ANTES de llamar a self.actualizar_animacion({delta_time})")

        self.actualizar_animacion(delta_time)
        # Convertido a log:
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_mov_debug", False):
            logger.debug(f"{self.nombre_log_entidad} FIN actualizar_movimiento()", extra={"categoria_log": "log_jugador_mov_debug"})

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