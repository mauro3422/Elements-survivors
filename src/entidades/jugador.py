import pygame
import os
from src.config import settings
import math
import logging
from src.entidades.entidad_base import EntidadBase
from src.sistemas.attack_profile_manager import AttackProfileManager
from src.sistemas.collision_handler import CollisionHandler

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

        # Log de hitbox recalculado
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_mov", False):
            logger.debug(f"{self.nombre_log_entidad} Hitbox recalculado a: {self.hitbox}", extra={"categoria_log": "log_jugador_mov"})

    # --- Métodos de Movimiento y Colisión (específicos o usan CollisionHandler) ---
    def _mover_y_colisionar(self, dx, dy, obstaculos):
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_col", False):
            logger.debug(f"{self.nombre_log_entidad} Iniciando gestión de colisión con dx={dx}, dy={dy}. Hitbox actual: {self.hitbox.topleft}", extra={"categoria_log": "log_jugador_col"})

        CollisionHandler.gestionar_movimiento_y_colision(
            self.hitbox, 
            self.rect, 
            self.hitbox_offset_x, 
            self.hitbox_offset_y, 
            dx, 
            dy, 
            obstaculos
        )

    def actualizar_movimiento(self, teclas_presionadas, obstaculos, mundo_ancho, mundo_alto, delta_time):
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
        
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_input", False):
            logger.debug(f"{self.nombre_log_entidad} Input teclado procesado: mov_x_input_raw={mov_x_input_raw}, mov_y_input_raw={mov_y_input_raw}", extra={"categoria_log": "log_input"})

        dx_flotante_intentado = mov_x_input_raw * delta_time
        dy_flotante_intentado = mov_y_input_raw * delta_time

        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_mov", False):
            logger.debug(f"{self.nombre_log_entidad} Delta flotante intentado: dx={dx_flotante_intentado:.4f}, dy={dy_flotante_intentado:.4f} (delta_time: {delta_time:.4f})", extra={"categoria_log": "log_jugador_mov"})

        self.pos_x_flotante += dx_flotante_intentado
        self.pos_y_flotante += dy_flotante_intentado
        
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_mov", False):
            logger.debug(f"{self.nombre_log_entidad} Pos flotante (pre-límites): ({self.pos_x_flotante:.4f}, {self.pos_y_flotante:.4f})", extra={"categoria_log": "log_jugador_mov"})

        # --- Colisión con Límites del Mundo (ajustando directamente pos_flotante) ---
        if int(self.pos_x_flotante) < 0:
            self.pos_x_flotante = 0.0
        elif int(self.pos_x_flotante) + self.hitbox.width > mundo_ancho:
            self.pos_x_flotante = float(mundo_ancho - self.hitbox.width)
        
        if int(self.pos_y_flotante) < 0:
            self.pos_y_flotante = 0.0
        elif int(self.pos_y_flotante) + self.hitbox.height > mundo_alto:
            self.pos_y_flotante = float(mundo_alto - self.hitbox.height)
        # --- Fin Colisión con Límites ---

        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_mov", False):
            logger.debug(f"{self.nombre_log_entidad} Pos flotante (post-límites): ({self.pos_x_flotante:.4f}, {self.pos_y_flotante:.4f})", extra={"categoria_log": "log_jugador_mov"})

        # Guardar la posición actual del hitbox para referencia
        hitbox_x_actual = self.hitbox.x
        hitbox_y_actual = self.hitbox.y

        # Calcular el delta flotante total desde la posición actual del hitbox
        delta_x_flotante_total = self.pos_x_flotante - hitbox_x_actual
        delta_y_flotante_total = self.pos_y_flotante - hitbox_y_actual

        # Determinar el movimiento entero para la colisión de forma simétrica
        dx_para_colision = 0
        if delta_x_flotante_total > settings.UMBRAL_MOV_FLOTANTE_ENTIDAD: # Usar constante
            dx_para_colision = math.ceil(delta_x_flotante_total)
        elif delta_x_flotante_total < -settings.UMBRAL_MOV_FLOTANTE_ENTIDAD: # Usar constante
            dx_para_colision = math.floor(delta_x_flotante_total)

        dy_para_colision = 0
        if delta_y_flotante_total > settings.UMBRAL_MOV_FLOTANTE_ENTIDAD: # Usar constante
            dy_para_colision = math.ceil(delta_y_flotante_total)
        elif delta_y_flotante_total < -settings.UMBRAL_MOV_FLOTANTE_ENTIDAD: # Usar constante
            dy_para_colision = math.floor(delta_y_flotante_total)
        
        if dx_para_colision != 0 or dy_para_colision != 0:
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_mov", False):
                logger.debug(f"{self.nombre_log_entidad} Movimiento para CH: dx_int={dx_para_colision}, dy_int={dy_para_colision}. HB (antes CH): {self.hitbox.topleft}, PosFlotante: ({self.pos_x_flotante:.4f},{self.pos_y_flotante:.4f})", extra={"categoria_log": "log_jugador_mov"})

            # Actualizar la última dirección de movimiento basada en el input procesado
            if dx_para_colision != 0: 
                self.ultima_direccion_mov_x = 1 if dx_para_colision > 0 else -1
                self.ultima_direccion_mov_y = 0 # Priorizar X si hay movimiento en ambos (raro con input normal)
            elif dy_para_colision != 0: # Solo si no hubo movimiento en X
                self.ultima_direccion_mov_x = 0
                self.ultima_direccion_mov_y = 1 if dy_para_colision > 0 else -1
            
            # Aplicar el movimiento y manejar colisiones
            # El CollisionHandler modificará self.hitbox directamente
            self._mover_y_colisionar(dx_para_colision, dy_para_colision, obstaculos)

            # Resincronizar las posiciones flotantes con la posición final del hitbox
            self.pos_x_flotante = float(self.hitbox.x)
            self.pos_y_flotante = float(self.hitbox.y)

            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_mov", False):
                logger.debug(f"{self.nombre_log_entidad} Posición POST CH: HB: {self.hitbox.topleft}, PosFlotante: ({self.pos_x_flotante:.2f}, {self.pos_y_flotante:.2f})", extra={"categoria_log": "log_jugador_mov"})
        else:
            # Si no hay delta entero, no llamamos a CH.
            # El hitbox no se mueve, pero pos_flotante puede tener decimales.
            # No es necesario actualizar self.hitbox.x/y aquí porque no hubo movimiento entero.
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_mov", False):
                logger.debug(f"{self.nombre_log_entidad} Sin mov. para CH (delta_int fue 0). HB: {self.hitbox.topleft}, PosFlotante: ({self.pos_x_flotante:.4f}, {self.pos_y_flotante:.4f})", extra={"categoria_log": "log_jugador_mov"})

        # Actualizar el rect visual principal de la entidad basado en la posición final del hitbox
        self.rect.topleft = (self.hitbox.x - self.hitbox_offset_x, self.hitbox.y - self.hitbox_offset_y)
        
        self.actualizar_animacion()

    # --- Métodos de Ataque (usan AttackProfileManager) ---
    def atacar(self):
        # print(f"DEBUG_JUGADOR: {self.nombre_log_entidad} Entrando a atacar().") # PRINT DESACTIVADO
        ahora = pygame.time.get_ticks()
        cooldown_mod_fallback = getattr(settings, 'ATAQUE_BASE_COOLDOWN_MODIFICADOR', 1.0)
        perfil_actual = self.attack_profile_manager.get_active_profile()
        if not perfil_actual:
            # print(f"DEBUG_JUGADOR: {self.nombre_log_entidad} No hay perfil de ataque activo. Saliendo de atacar().") # PRINT DESACTIVADO
            return

        # Aplicar modificador de cooldown del perfil, si existe, si no, usar el base del APM (1.0)
        cooldown_modificador = perfil_actual.get('cooldown_modificador', cooldown_mod_fallback)
        cooldown_efectivo = self.cooldown_general_ataque * cooldown_modificador
        # print(f"DEBUG_JUGADOR: {self.nombre_log_entidad} Cooldown efectivo: {cooldown_efectivo}ms, Último ataque: {self.ultimo_ataque_realizado}, Ahora: {ahora}") # PRINT DESACTIVADO

        if ahora - self.ultimo_ataque_realizado > cooldown_efectivo:
            self.esta_atacando = True
            self.tiempo_inicio_ataque = ahora
            self.ultimo_ataque_realizado = ahora
            self.enemigos_golpeados_este_ataque.clear() 
            # print(f"DEBUG_JUGADOR: {self.nombre_log_entidad} ATAQUE INICIADO. esta_atacando=True, Perfil: '{self.attack_profile_manager.nombre_perfil_activo}'") # PRINT DESACTIVADO
        else:
            # print(f"DEBUG_JUGADOR: {self.nombre_log_entidad} Ataque en cooldown. Saliendo de atacar().") # PRINT DESACTIVADO
            pass

    def actualizar_ataque(self, enemigos):
        if not self.esta_atacando:
            return
        
        # print(f"DEBUG_JUGADOR: {self.nombre_log_entidad} Entrando a actualizar_ataque(). esta_atacando es True.") # PRINT DESACTIVADO

        perfil_actual = self.attack_profile_manager.get_active_profile()
        if not perfil_actual:
            # print(f"DEBUG_JUGADOR: {self.nombre_log_entidad} No hay perfil de ataque activo en actualizar_ataque. Terminando ataque.") # PRINT DESACTIVADO
            self.esta_atacando = False
            return

        # Usar valores base de settings como fallback si no están en el perfil
        offset_distancia_base = getattr(settings, 'ATAQUE_BASE_OFFSET_DISTANCIA', 25.0)
        extension_base = getattr(settings, 'ATAQUE_BASE_EXTENSION', 30.0)
        grosor_base = getattr(settings, 'ATAQUE_BASE_GROSOR', 15.0)
        duracion_total_ms_base = getattr(settings, 'ATAQUE_BASE_DURACION_TOTAL_MS', 300.0)
        plantilla_angulos_base = getattr(settings, 'ATAQUE_BASE_PLANTILLA_ANGULOS_GRADOS', [0])
        
        # Obtener parámetros del perfil, usando fallbacks si es necesario
        offset_distancia = perfil_actual.get('offset_distancia', offset_distancia_base)
        extension_valor = perfil_actual.get('extension', extension_base)
        grosor_valor = perfil_actual.get('grosor', grosor_base)
        duracion_total_ms = perfil_actual.get('duracion_total_ms', duracion_total_ms_base)
        plantilla_angulos_grados = perfil_actual.get('plantilla_angulos_grados', plantilla_angulos_base)

        # print(f"DEBUG_JUGADOR: {self.nombre_log_entidad} Params perfil ataque: Offset={offset_distancia}, Ext={extension_valor}, Grosor={grosor_valor}") # PRINT DESACTIVADO

        ahora = pygame.time.get_ticks()
        tiempo_transcurrido_ataque = ahora - self.tiempo_inicio_ataque
        # print(f"DEBUG_JUGADOR: {self.nombre_log_entidad} Duración ataque: {duracion_total_ms}ms, Tiempo inicio: {self.tiempo_inicio_ataque}, Ahora: {ahora}") # PRINT DESACTIVADO

        if tiempo_transcurrido_ataque > duracion_total_ms:
            self.esta_atacando = False
            self.hitbox_ataque_actual_rect.size = (0,0) # Resetear para que no se dibuje
            # print(f"DEBUG_JUGADOR: {self.nombre_log_entidad} ATAQUE FINALIZADO por duración.") # PRINT DESACTIVADO
            return

        # Calcular el ángulo base del ataque (hacia donde mira el jugador)
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
        # print(f"DEBUG_JUGADOR: {self.nombre_log_entidad} Hitbox ataque calculado: {self.hitbox_ataque_actual_rect}") # PRINT DESACTIVADO
        if settings.DEBUG_PRINT_JUGADOR_ATAQUE_CALCULO:
            print(f"DEBUG_JUGADOR: {self.nombre_log_entidad} Hitbox ataque calculado: {self.hitbox_ataque_actual_rect}")

        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_cmb", False):
            logger.debug(f"{self.nombre_log_entidad} Hitbox ataque: {self.hitbox_ataque_actual_rect}, Dir: ({vector_direccion_normalizado[0]:.2f}, {vector_direccion_normalizado[1]:.2f})", extra={"categoria_log": "log_jugador_cmb"})

        for enemigo in enemigos:
            if enemigo not in self.enemigos_golpeados_este_ataque:
                # print(f"DEBUG_JUGADOR: {self.nombre_log_entidad} Verificando colisión con {enemigo.nombre_log_entidad} (HB: {enemigo.hitbox})") # PRINT DESACTIVADO
                if self.hitbox_ataque_actual_rect.colliderect(enemigo.hitbox):
                    dano_modificador_perfil = perfil_actual.get('dano_modificador', settings.ATAQUE_BASE_DANO_MODIFICADOR)
                    dano_final = self.dano_base_ataque * dano_modificador_perfil
                    # print(f"DEBUG_JUGADOR: {self.nombre_log_entidad} ¡GOLPEÓ a {enemigo.nombre_log_entidad}! Daño base: {self.dano_base_ataque}, Mod: {dano_modificador_perfil}, Daño final: {dano_final}") # PRINT DESACTIVADO
                    enemigo.recibir_dano(dano_final, "ataque_jugador")
                    self.enemigos_golpeados_este_ataque.add(enemigo)
                # else: # PRINT DESACTIVADO
                    # print(f"DEBUG_JUGADOR: {self.nombre_log_entidad} NO colisión con {enemigo.nombre_log_entidad}") # PRINT DESACTIVADO

    def update(self, teclas_presionadas, obstaculos_solidos, enemigos_sprites_para_ataque, mundo_ancho, mundo_alto, delta_time):
        if not self.ha_muerto:
            self.actualizar_movimiento(teclas_presionadas, obstaculos_solidos, mundo_ancho, mundo_alto, delta_time)
            self.actualizar_ataque(enemigos_sprites_para_ataque) # Actualizar lógica de ataque
            # La llamada a actualizar_animacion() ya está en actualizar_movimiento()
        else:
            # Lógica para cuando el jugador está muerto (si aplica)
            pass 

    def dibujar(self, superficie):
        super().dibujar(superficie) # Si EntidadBase tiene un método dibujar, si no, pygame.sprite.Sprite no lo tiene.
        # Si se necesita dibujar algo más específico del jugador (ej: HUD de vida sobre la cabeza), hacerlo aquí.
        # Por ahora, la imagen y rect son manejados por el grupo de sprites y EntidadBase.

    def recibir_dano(self, cantidad, tipo_dano="generico"):
        # print(f"DEBUG_JUGADOR: {self.nombre_log_entidad} Jugador.recibir_dano llamado con cantidad {cantidad}") # PRINT DESACTIVADO
        if settings.DEBUG_PRINT_JUGADOR_RECIBIR_DANO_INFO:
            print(f"DEBUG_JUGADOR: {self.nombre_log_entidad} Jugador.recibir_dano llamado con cantidad {cantidad}")
        super().recibir_dano(cantidad, tipo_dano)
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_cmb", False):
            logger.debug(f"{self.nombre_log_entidad} recibió daño (post EntidadBase). Vida actual: {self.vida_actual}", extra={"categoria_log": "log_jugador_cmb"})
        # Si el jugador muere, game over se maneja en GestorEstado probablemente.
        return True

    def dibujar_debug_ataque(self, superficie_destino, camara):
        if settings.DEBUG_VER_HITBOX_ATAQUE_JUGADOR and self.esta_atacando and self.hitbox_ataque_actual_rect.width > 0:
            # Ajustar las coordenadas del hitbox de ataque por la cámara
            hitbox_ataque_visible = camara.aplicar_offset_a_rect(self.hitbox_ataque_actual_rect)
            pygame.draw.rect(superficie_destino, settings.COLOR_HITBOX_ATAQUE_JUGADOR, hitbox_ataque_visible, settings.GROSOR_HITBOX_ATAQUE_DEBUG)
# Nueva línea al final para intentar limpiar posibles bytes nulos al final del archivo. 