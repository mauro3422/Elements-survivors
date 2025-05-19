import pygame
import os
import settings
import math
import logging
from collision_handler import CollisionHandler
from entidad_base import EntidadBase
from attack_profile_manager import AttackProfileManager

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
            settings.RUTA_BASE_PROYECTO, 
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
    def atacar(self): # Ya no necesita grupo_enemigos aquí
        ahora = pygame.time.get_ticks()
        # Usar la constante de settings como fallback para el cooldown_modificador
        cooldown_mod_fallback = getattr(settings, 'ATAQUE_BASE_COOLDOWN_MODIFICADOR', 1.0)
        cooldown_mod = self.attack_profile_manager.get_parametro_ataque_activo("cooldown_modificador", cooldown_mod_fallback)
        cooldown_ataque_actual = self.cooldown_general_ataque * float(cooldown_mod) # Asegurar float
        
        if ahora - self.ultimo_ataque_realizado > cooldown_ataque_actual:
            if not self.esta_atacando:
                self.esta_atacando = True
                self.tiempo_inicio_ataque = ahora
                self.ultimo_ataque_realizado = ahora
                self.enemigos_golpeados_este_ataque.clear()
                logger.info(f"{self.nombre_log_entidad} Inicia ATAQUE perfil '{self.attack_profile_manager.nombre_perfil_ataque_activo}'.", extra={"categoria_log": "log_jugador_general"})
                if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_cmb", False):
                    logger.debug(f"{self.nombre_log_entidad} Estado ataque: esta_atacando={self.esta_atacando}, t_inicio={self.tiempo_inicio_ataque}, t_ult_ataque={self.ultimo_ataque_realizado}", extra={"categoria_log": "log_jugador_cmb"})
        else:
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_cmb", False):
                logger.debug(f"{self.nombre_log_entidad} Intento de ataque en cooldown. Ahora: {ahora}, Ultimo: {self.ultimo_ataque_realizado}, CD: {cooldown_ataque_actual:.0f}", extra={"categoria_log": "log_jugador_cmb"})

    def actualizar_ataque(self, enemigos):
        if not self.esta_atacando:
            if self.hitbox_ataque_actual_rect.size != (0,0):
                 if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_cmb", False):
                    logger.debug(f"{self.nombre_log_entidad} Fin de ataque (no self.esta_atacando). Reseteando HB ataque de {self.hitbox_ataque_actual_rect.size}", extra={"categoria_log": "log_jugador_cmb"})
            self.hitbox_ataque_actual_rect.size = (0,0) 
            return

        # Obtener parámetros del perfil activo a través del manager, usando constantes de settings como fallback
        offset_dist_fallback = getattr(settings, 'ATAQUE_BASE_OFFSET_DISTANCIA', 25.0)
        extension_fallback = getattr(settings, 'ATAQUE_BASE_EXTENSION', 30.0)
        grosor_fallback = getattr(settings, 'ATAQUE_BASE_GROSOR', 15.0)
        duracion_total_ms_fallback = getattr(settings, 'ATAQUE_BASE_DURACION_TOTAL_MS', 300.0)
        plantilla_angulos_fallback = getattr(settings, 'ATAQUE_BASE_PLANTILLA_ANGULOS_GRADOS', [0])
        dano_mod_fallback = getattr(settings, 'ATAQUE_BASE_DANO_MODIFICADOR', 1.0)

        offset_dist = float(self.attack_profile_manager.get_parametro_ataque_activo("offset_distancia", offset_dist_fallback))
        extension = float(self.attack_profile_manager.get_parametro_ataque_activo("extension", extension_fallback))
        grosor = float(self.attack_profile_manager.get_parametro_ataque_activo("grosor", grosor_fallback))
        duracion_total_ms = float(self.attack_profile_manager.get_parametro_ataque_activo("duracion_total_ms", duracion_total_ms_fallback))
        plantilla_angulos = self.attack_profile_manager.get_parametro_ataque_activo("plantilla_angulos_grados", plantilla_angulos_fallback)
        dano_mod = float(self.attack_profile_manager.get_parametro_ataque_activo("dano_modificador", dano_mod_fallback))
        dano_actual = self.dano_base_ataque * dano_mod
        
        # Obtener valores calculados del manager
        num_segmentos = self.attack_profile_manager.num_segmentos_barrido_activo
        dur_segmento = self.attack_profile_manager.duracion_segmento_barrido_activo

        ahora = pygame.time.get_ticks()
        tiempo_transcurrido_ataque = ahora - self.tiempo_inicio_ataque

        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_cmb", False):
             logger.debug(f"{self.nombre_log_entidad} Actualizando tick de ataque. Transcurrido: {tiempo_transcurrido_ataque:.0f}/{duracion_total_ms:.0f} ms. Segs: {num_segmentos}, DurSeg: {dur_segmento:.2f}", extra={"categoria_log": "log_jugador_cmb"})

        if tiempo_transcurrido_ataque <= duracion_total_ms and num_segmentos > 0 and dur_segmento > 0:
            segmento_actual_indice = int(tiempo_transcurrido_ataque / dur_segmento)
            segmento_actual_indice = min(segmento_actual_indice, num_segmentos - 1)
            
            if not plantilla_angulos or not isinstance(plantilla_angulos, list) or segmento_actual_indice >= len(plantilla_angulos) or segmento_actual_indice < 0:
                logger.warning(f"{self.nombre_log_entidad} Índice de segmento ({segmento_actual_indice}) fuera de rango para plantilla de ángulos. Usando ángulo 0.", extra={"categoria_log": "log_jugador_cmb"})
                angulo_offset_grados = 0
            else:
                angulo_offset_grados = float(plantilla_angulos[segmento_actual_indice])

            ataque_es_principalmente_horizontal = (self.ultima_direccion_mov_x != 0)
            angulo_base_direccion_grados = 0
            if ataque_es_principalmente_horizontal:
                if self.ultima_direccion_mov_x > 0: angulo_base_direccion_grados = 0
                else: angulo_base_direccion_grados = 180
            else: 
                if self.ultima_direccion_mov_y < 0: angulo_base_direccion_grados = -90 
                else: angulo_base_direccion_grados = 90 
            
            angulo_total_segmento_grados = angulo_base_direccion_grados + angulo_offset_grados
            angulo_total_segmento_rad = math.radians(angulo_total_segmento_grados)
            centro_segmento_x = self.rect.centerx + offset_dist * math.cos(angulo_total_segmento_rad)
            centro_segmento_y = self.rect.centery + offset_dist * math.sin(angulo_total_segmento_rad)
            
            cos_abs = abs(math.cos(angulo_total_segmento_rad))
            sin_abs = abs(math.sin(angulo_total_segmento_rad))
            epsilon = 0.0001 
            
            if ataque_es_principalmente_horizontal:
                if cos_abs >= sin_abs - epsilon: 
                    final_ancho = extension; final_alto = grosor
                else: 
                    final_ancho = grosor; final_alto = extension
            else: 
                if sin_abs >= cos_abs - epsilon: 
                    final_ancho = grosor; final_alto = extension
                else: 
                    final_ancho = extension; final_alto = grosor
            
            self.hitbox_ataque_actual_rect.width = int(final_ancho)
            self.hitbox_ataque_actual_rect.height = int(final_alto)
            self.hitbox_ataque_actual_rect.center = (int(centro_segmento_x), int(centro_segmento_y))

            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_cmb", False):
                logger.debug(f"{self.nombre_log_entidad} Tick ataque: SegIdx:{segmento_actual_indice}, AngBase:{angulo_base_direccion_grados}, AngOff:{angulo_offset_grados:.1f}, AngTotal:{angulo_total_segmento_grados:.1f}", extra={"categoria_log": "log_jugador_cmb"})
                logger.debug(f"{self.nombre_log_entidad} HB Ataque generado: {self.hitbox_ataque_actual_rect}, Centro PJ: {self.rect.center}", extra={"categoria_log": "log_jugador_cmb"})

            for enemigo in enemigos:
                if enemigo not in self.enemigos_golpeados_este_ataque:
                    if self.hitbox_ataque_actual_rect.colliderect(enemigo.hitbox):
                        if hasattr(enemigo, 'recibir_dano'):
                            tipo_dano_str = f"ataque_jugador_{self.attack_profile_manager.nombre_perfil_ataque_activo}"
                            enemigo.recibir_dano(dano_actual, tipo_dano=tipo_dano_str)
                            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_cmb", False):
                                logger.debug(f"{self.nombre_log_entidad} GOLPEÓ a Enemigo_{enemigo.id_entidad} con {dano_actual:.2f} de daño ({tipo_dano_str}).", extra={"categoria_log": "log_jugador_cmb"})
                        self.enemigos_golpeados_este_ataque.add(enemigo)
        else:
            # Log si se va a resetear un hitbox que no era cero
            if self.hitbox_ataque_actual_rect.size != (0,0):
                 if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_cmb", False):
                    logger.debug(f"{self.nombre_log_entidad} Reseteando hitbox_ataque_actual_rect de {self.hitbox_ataque_actual_rect.size} a (0,0)", extra={"categoria_log": "log_jugador_cmb"})
            self.esta_atacando = False
            self.hitbox_ataque_actual_rect.size = (0,0)

    # --- Método de Actualización Principal ---    
    def update(self, teclas_presionadas, obstaculos_solidos, enemigos_sprites_para_ataque, mundo_ancho, mundo_alto, delta_time):
        """Actualiza el estado completo del jugador en cada frame."""
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_general", False): # O una categoría más específica si se crea para "actualizaciones de entidad"
            logger.debug(f"{self.nombre_log_entidad} Inicio Update. Vida: {self.vida_actual}/{self.vida_maxima}", extra={"categoria_log": "log_jugador_general"})

        # Actualizar animación (ahora en EntidadBase, pero se puede llamar explícitamente si es necesario aquí)
        # super().update(delta_time) # Si EntidadBase.update toma delta_time y lo usa para animaciones
        self.actualizar_animacion() # Pasar delta_time a EntidadBase para la animación

        # Actualizar lógica de movimiento
        # self.actualizar_movimiento(teclas_presionadas, obstaculos_solidos, mundo_ancho, mundo_alto) # <--- Llamada original
        self.actualizar_movimiento(teclas_presionadas, obstaculos_solidos, mundo_ancho, mundo_alto, delta_time) # <--- Pasar delta_time

        # Actualizar lógica de ataque
        self.actualizar_ataque(enemigos_sprites_para_ataque) # Asumimos que ataque no es frame-dependant en su lógica principal de cooldown/duración

        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_general", False):
            logger.debug(f"{self.nombre_log_entidad} Fin Update.", extra={"categoria_log": "log_jugador_general"})

    def dibujar(self, superficie):
        """Dibuja el sprite actual del jugador. Podría ser obsoleto si la cámara lo maneja."""
        # Este método es estándar en pygame.sprite.Sprite, pero si la cámara dibuja todos
        # los sprites directamente usando sprite.image y sprite.rect, este podría no ser llamado.
        # Lo mantenemos por si acaso o para depuración directa.
        superficie.blit(self.image, self.rect)
        # Opcional: Dibujar el hitbox para depuración aquí si no lo hace la cámara
        # if settings.DEBUG_VER_HITBOXES:
        #     pygame.draw.rect(superficie, (255,0,0), self.hitbox, 1)

    def recibir_dano(self, cantidad):
        super().recibir_dano(cantidad) # Llama al método de EntidadBase
        logger.info(f"{self.nombre_log_entidad} recibió {cantidad} de daño. Vida restante: {self.vida_actual}/{self.vida_maxima}", extra={"categoria_log": "log_jugador_general"})
        if self.vida_actual <= 0:
            logger.warning(f"{self.nombre_log_entidad} ha sido derrotado.", extra={"categoria_log": "log_jugador_general"})
            self.kill() # Eliminar el sprite de todos los grupos

    def dibujar_debug_ataque(self, superficie_destino, camara):
        if self.esta_atacando and self.hitbox_ataque_actual_rect.size != (0,0):
            if settings.DEBUG_VER_HITBOXES:
                # Dibujar el hitbox de ataque
                #logger_cmb.debug(f"Dibujando hitbox ataque: {self.hitbox_ataque_actual_rect}")
                if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_cmb", False):
                     logger.debug(f"Dibujando hitbox ataque: {self.hitbox_ataque_actual_rect}", extra={"categoria_log": "log_jugador_cmb"})

                color_ataque_hb = getattr(settings, 'COLOR_ATAQUE_HITBOX', (255, 255, 0)) # Amarillo por defecto
                grosor_ataque_hb = getattr(settings, 'GROSOR_HITBOX_ATAQUE_DEBUG', 2)