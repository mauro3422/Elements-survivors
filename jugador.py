import pygame
import os
import settings
import math
import logging
from collision_handler import CollisionHandler
from entidad_base import EntidadBase
from attack_profile_manager import AttackProfileManager

# --- Loggers Categóricos ---
# Es importante que estos loggers se definan UNA VEZ, por eso están a nivel de módulo.
# Sus niveles se establecen en DEBUG para que no filtren mensajes internamente.
# La decisión final de si un mensaje se muestra/registra dependerá de:
# 1. settings.MODO_DEBUG_LOGS (interruptor global)
# 2. settings.LOG_CATEGORIAS[categoria_especifica] (interruptor de categoría)
# 3. La configuración del logger raíz (nivel de consola, file handler) hecha en main.py

logger_mov = logging.getLogger("log_jugador_mov")
# Asegurarse de que el logger permita pasar mensajes DEBUG
if not logger_mov.level == logging.DEBUG: # Comprobar si ya tiene el nivel para no cambiarlo innecesariamente
    logger_mov.setLevel(logging.DEBUG)

logger_col = logging.getLogger("log_jugador_col")
if not logger_col.level == logging.DEBUG:
    logger_col.setLevel(logging.DEBUG)

logger_cmb = logging.getLogger("log_jugador_cmb")
if not logger_cmb.level == logging.DEBUG:
    logger_cmb.setLevel(logging.DEBUG)

# Logger para mensajes generales (INFO, WARNING, etc.) específicos del jugador
logger_jugador_general = logging.getLogger("juego.jugador.general")
if not logger_jugador_general.level == logging.INFO: # Por defecto para INFO o superior
    logger_jugador_general.setLevel(logging.INFO)

class Jugador(EntidadBase):
    def __init__(self, x, y, asset_manager_instance):
        vida_maxima_jugador = getattr(settings, 'VIDA_MAXIMA_JUGADOR', 100)
        velocidad_jugador = getattr(settings, 'VELOCIDAD_JUGADOR', 3)
        hitbox_offset_x_jugador = getattr(settings, 'JUGADOR_HITBOX_OFFSET_X', 4)
        hitbox_offset_y_jugador = getattr(settings, 'JUGADOR_HITBOX_OFFSET_Y', 6)
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
        hb_alto_jugador_especifico = self.rect.height - (self.hitbox_offset_y + 4) 
        self.hitbox.size = (max(1, hb_ancho_jugador), max(1, hb_alto_jugador_especifico))
        self._actualizar_posicion_hitbox() # Re-posicionar con el nuevo tamaño si cambió.
        
        # Log de hitbox recalculado
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_mov", False):
            logger_mov.debug(f"{self.nombre_log_entidad} Hitbox recalculado a: {self.hitbox}")

    # --- Métodos de Movimiento y Colisión (específicos o usan CollisionHandler) ---
    def _mover_y_colisionar(self, dx, dy, obstaculos):
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_col", False):
            logger_col.debug(f"{self.nombre_log_entidad} Iniciando gestión de colisión con dx={dx}, dy={dy}. Hitbox actual: {self.hitbox.topleft}")

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
        mov_x_input = 0 # Movimiento basado en input directo
        mov_y_input = 0 # Movimiento basado en input directo

        if teclas_presionadas[pygame.K_LEFT] or teclas_presionadas[pygame.K_a]:
            mov_x_input = -self.velocidad
        if teclas_presionadas[pygame.K_RIGHT] or teclas_presionadas[pygame.K_d]:
            mov_x_input = self.velocidad
        if teclas_presionadas[pygame.K_UP] or teclas_presionadas[pygame.K_w]:
            mov_y_input = -self.velocidad
        if teclas_presionadas[pygame.K_DOWN] or teclas_presionadas[pygame.K_s]:
            mov_y_input = self.velocidad
        
        # Log de input (categoría "log_input" o "log_jugador_mov")
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_input", False):
            logger_mov.debug(f"{self.nombre_log_entidad} Input teclado procesado: mov_x_input={mov_x_input}, mov_y_input={mov_y_input}")

        # Aplicar delta_time al movimiento basado en input
        mov_x_final = mov_x_input * delta_time
        mov_y_final = mov_y_input * delta_time

        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_mov", False):
            logger_mov.debug(f"{self.nombre_log_entidad} Movimiento con delta_time (antes de límites): dx={mov_x_final:.4f}, dy={mov_y_final:.4f} (delta_time: {delta_time:.4f})")

        # --- Inicio: Lógica de colisión con límites del mundo ---
        # Esta lógica se aplica ANTES de gestionar colisiones con otros obstáculos.
        # Se ajusta mov_x_final y mov_y_final para que el JUGADOR no salga del mundo.
        
        # Futura posición X del hitbox si se aplica mov_x_final
        next_hitbox_x = self.hitbox.x + mov_x_final
        # Futura posición Y del hitbox si se aplica mov_y_final
        next_hitbox_y = self.hitbox.y + mov_y_final

        # Comprobar y ajustar para el eje X
        if next_hitbox_x < 0:
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_col", False):
                logger_col.debug(f"{self.nombre_log_entidad} Colisión borde IZQUIERDO. HB.x: {self.hitbox.x}, mov_x: {mov_x_final} -> ajustado.")
            mov_x_final = -self.hitbox.x # Evita que hitbox.x sea < 0
        elif next_hitbox_x + self.hitbox.width > mundo_ancho:
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_col", False):
                logger_col.debug(f"{self.nombre_log_entidad} Colisión borde DERECHO. HB.right: {self.hitbox.right}, W: {mundo_ancho}, mov_x: {mov_x_final} -> ajustado.")
            mov_x_final = mundo_ancho - (self.hitbox.x + self.hitbox.width) # Evita que hitbox.right sea > mundo_ancho
        # Comprobar y ajustar para el eje Y
        if next_hitbox_y < 0:
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_col", False):
                logger_col.debug(f"{self.nombre_log_entidad} Colisión borde SUPERIOR. HB.y: {self.hitbox.y}, mov_y: {mov_y_final} -> ajustado.")
            mov_y_final = -self.hitbox.y # Evita que hitbox.y sea < 0
        elif next_hitbox_y + self.hitbox.height > mundo_alto:
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_col", False):
                logger_col.debug(f"{self.nombre_log_entidad} Colisión borde INFERIOR. HB.bottom: {self.hitbox.bottom}, H: {mundo_alto}, mov_y: {mov_y_final} -> ajustado.")
            mov_y_final = mundo_alto - (self.hitbox.y + self.hitbox.height) # Evita que hitbox.bottom sea > mundo_alto
        # --- Fin: Lógica de colisión con límites del mundo ---
        
        if mov_x_final != 0 or mov_y_final != 0:
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_mov", False):
                logger_mov.debug(f"{self.nombre_log_entidad} Movimiento neto (pre-colisión obstáculos): dx={mov_x_final:.2f}, dy={mov_y_final:.2f}")

            if mov_x_final != 0:
                self.ultima_direccion_mov_x = int(mov_x_final / abs(mov_x_final)) if mov_x_final != 0 else 0
                self.ultima_direccion_mov_y = 0
            elif mov_y_final != 0: # Usar elif para que la dirección no se sobreescriba si hay movimiento diagonal (prioridad a X)
                self.ultima_direccion_mov_x = 0
                self.ultima_direccion_mov_y = int(mov_y_final / abs(mov_y_final)) if mov_y_final != 0 else 0
            
            self._mover_y_colisionar(mov_x_final, mov_y_final, obstaculos)

            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_mov", False):
                logger_mov.debug(f"{self.nombre_log_entidad} Posición POST-mov/colisión: HB: {self.hitbox.topleft}, Rect: {self.rect.topleft}")
        else:
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_mov", False):
                logger_mov.debug(f"{self.nombre_log_entidad} Sin movimiento solicitado este frame.")

        self.actualizar_animacion() # Pasar delta_time a EntidadBase para la animación

    # --- Métodos de Ataque (usan AttackProfileManager) ---
    def atacar(self): # Ya no necesita grupo_enemigos aquí
        ahora = pygame.time.get_ticks()
        cooldown_mod = self.attack_profile_manager.get_parametro_ataque_activo("cooldown_modificador", 1.0)
        cooldown_ataque_actual = self.cooldown_general_ataque * float(cooldown_mod) # Asegurar float
        
        if ahora - self.ultimo_ataque_realizado > cooldown_ataque_actual:
            if not self.esta_atacando:
                self.esta_atacando = True
                self.tiempo_inicio_ataque = ahora
                self.ultimo_ataque_realizado = ahora
                self.enemigos_golpeados_este_ataque.clear()
                logger_jugador_general.info(f"{self.nombre_log_entidad} Inicia ATAQUE perfil '{self.attack_profile_manager.nombre_perfil_ataque_activo}'.")
                if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_cmb", False):
                    logger_cmb.debug(f"{self.nombre_log_entidad} Estado ataque: esta_atacando={self.esta_atacando}, t_inicio={self.tiempo_inicio_ataque}, t_ult_ataque={self.ultimo_ataque_realizado}")
        else:
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_cmb", False):
                logger_cmb.debug(f"{self.nombre_log_entidad} Intento de ataque en cooldown. Ahora: {ahora}, Ultimo: {self.ultimo_ataque_realizado}, CD: {cooldown_ataque_actual:.0f}")

    def actualizar_ataque(self, enemigos):
        if not self.esta_atacando:
            if self.hitbox_ataque_actual_rect.size != (0,0):
                 if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_cmb", False):
                    logger_cmb.debug(f"{self.nombre_log_entidad} Fin de ataque (no self.esta_atacando). Reseteando HB ataque de {self.hitbox_ataque_actual_rect.size}")
            self.hitbox_ataque_actual_rect.size = (0,0) 
            return

        # Obtener parámetros del perfil activo a través del manager
        offset_dist = float(self.attack_profile_manager.get_parametro_ataque_activo("offset_distancia", 25))
        extension = float(self.attack_profile_manager.get_parametro_ataque_activo("extension", 30))
        grosor = float(self.attack_profile_manager.get_parametro_ataque_activo("grosor", 15))
        duracion_total_ms = float(self.attack_profile_manager.get_parametro_ataque_activo("duracion_total_ms", 300))
        plantilla_angulos = self.attack_profile_manager.get_parametro_ataque_activo("plantilla_angulos_grados", [0])
        dano_mod = float(self.attack_profile_manager.get_parametro_ataque_activo("dano_modificador", 1.0))
        dano_actual = self.dano_base_ataque * dano_mod
        
        # Obtener valores calculados del manager
        num_segmentos = self.attack_profile_manager.num_segmentos_barrido_activo
        dur_segmento = self.attack_profile_manager.duracion_segmento_barrido_activo

        ahora = pygame.time.get_ticks()
        tiempo_transcurrido_ataque = ahora - self.tiempo_inicio_ataque

        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_cmb", False) and self.esta_atacando:
             logger_cmb.debug(f"{self.nombre_log_entidad} Actualizando tick de ataque. Transcurrido: {tiempo_transcurrido_ataque:.0f}/{duracion_total_ms:.0f} ms. Segs: {num_segmentos}, DurSeg: {dur_segmento:.2f}")

        if tiempo_transcurrido_ataque <= duracion_total_ms and num_segmentos > 0 and dur_segmento > 0:
            segmento_actual_indice = int(tiempo_transcurrido_ataque / dur_segmento)
            segmento_actual_indice = min(segmento_actual_indice, num_segmentos - 1)
            
            if not plantilla_angulos or not isinstance(plantilla_angulos, list) or segmento_actual_indice >= len(plantilla_angulos) or segmento_actual_indice < 0:
                logger_jugador_general.warning(f"{self.nombre_log_entidad} Índice de segmento ({segmento_actual_indice}) fuera de rango para plantilla de ángulos. Usando ángulo 0.")
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
                logger_cmb.debug(f"{self.nombre_log_entidad} Tick ataque: SegIdx:{segmento_actual_indice}, AngBase:{angulo_base_direccion_grados}, AngOff:{angulo_offset_grados:.1f}, AngTotal:{angulo_total_segmento_grados:.1f}")
                logger_cmb.debug(f"{self.nombre_log_entidad} HB Ataque generado: {self.hitbox_ataque_actual_rect}, Centro PJ: {self.rect.center}")

            for enemigo in enemigos:
                if enemigo not in self.enemigos_golpeados_este_ataque:
                    if self.hitbox_ataque_actual_rect.colliderect(enemigo.hitbox):
                        if hasattr(enemigo, 'recibir_dano'):
                            tipo_dano_str = f"ataque_jugador_{self.attack_profile_manager.nombre_perfil_ataque_activo}"
                            enemigo.recibir_dano(dano_actual, tipo_dano=tipo_dano_str)
                            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_cmb", False):
                                logger_cmb.debug(f"{self.nombre_log_entidad} GOLPEÓ a Enemigo_{enemigo.id_entidad} con {dano_actual:.2f} de daño ({tipo_dano_str}).")
                        self.enemigos_golpeados_este_ataque.add(enemigo)
        else:
            # Log si se va a resetear un hitbox que no era cero
            if self.hitbox_ataque_actual_rect.size != (0,0):
                 if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_mov", False):
                    logger_mov.debug(f"{self.nombre_log_entidad} Reseteando hitbox_ataque_actual_rect de {self.hitbox_ataque_actual_rect.size} a (0,0)")
            self.esta_atacando = False
            self.hitbox_ataque_actual_rect.size = (0,0)

    # --- Método de Actualización Principal ---    
    def update(self, teclas_presionadas, obstaculos_solidos, enemigos_sprites_para_ataque, mundo_ancho, mundo_alto, delta_time):
        """Actualiza el estado completo del jugador en cada frame."""
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_general", False): # O una categoría más específica si se crea para "actualizaciones de entidad"
            logger_jugador_general.debug(f"{self.nombre_log_entidad} Inicio Update. Vida: {self.vida_actual}/{self.vida_maxima}")

        # Actualizar animación (ahora en EntidadBase, pero se puede llamar explícitamente si es necesario aquí)
        # super().update(delta_time) # Si EntidadBase.update toma delta_time y lo usa para animaciones
        self.actualizar_animacion() # Pasar delta_time a EntidadBase para la animación

        # Actualizar lógica de movimiento
        # self.actualizar_movimiento(teclas_presionadas, obstaculos_solidos, mundo_ancho, mundo_alto) # <--- Llamada original
        self.actualizar_movimiento(teclas_presionadas, obstaculos_solidos, mundo_ancho, mundo_alto, delta_time) # <--- Pasar delta_time

        # Actualizar lógica de ataque
        self.actualizar_ataque(enemigos_sprites_para_ataque) # Asumimos que ataque no es frame-dependant en su lógica principal de cooldown/duración

        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_general", False):
            logger_jugador_general.debug(f"{self.nombre_log_entidad} Fin Update.")

    def dibujar(self, superficie):
        """Dibuja el sprite actual del jugador. Podría ser obsoleto si la cámara lo maneja."""
        # Este método es estándar en pygame.sprite.Sprite, pero si la cámara dibuja todos
        # los sprites directamente usando sprite.image y sprite.rect, este podría no ser llamado.
        # Lo mantenemos por si acaso o para depuración directa.
        superficie.blit(self.image, self.rect)
        # Opcional: Dibujar el hitbox para depuración aquí si no lo hace la cámara
        # if settings.DEBUG_VER_HITBOXES:
        #     pygame.draw.rect(superficie, (255,0,0), self.hitbox, 1)