import pygame
import os
import settings # Para RUTA_ASSETS
import math # Para cálculos de distancia y vectores
import logging # <--- AÑADIR IMPORT

# Obtener el mismo logger que usa el jugador para que todo vaya al mismo archivo
logger = logging.getLogger('movimiento_jugador') # <--- OBTENER LOGGER

class Enemigo(pygame.sprite.Sprite):
    id_counter = 0 # <--- CONTADOR DE CLASE PARA ID ÚNICO

    def __init__(self, x, y, nombre_archivo_imagen="chicken.png"):
        """Constructor de la clase Enemigo.

        Args:
            x (int): Posición inicial en el eje X del enemigo.
            y (int): Posición inicial en el eje Y del enemigo.
            nombre_archivo_imagen (str): Nombre del archivo de imagen para este enemigo
                                         (ej: "chicken.png") dentro de la carpeta de enemigos.
        """
        super().__init__()

        self.id_enemigo = Enemigo.id_counter # <--- ASIGNAR ID ÚNICO
        Enemigo.id_counter += 1
        logger.debug(f"[Enemigo_{self.id_enemigo}] Creado en ({x}, {y})") # <--- LOG CREACIÓN

        self.ruta_base_enemigos = os.path.join(settings.RUTA_ASSETS, "character", "animaciones", "Enemy")
        
        try:
            ruta_imagen = os.path.join(self.ruta_base_enemigos, nombre_archivo_imagen)
            self.image = pygame.image.load(ruta_imagen).convert_alpha()
        except pygame.error as e:
            logger.error(f"[Enemigo_{self.id_enemigo}] Error al cargar imagen {ruta_imagen}: {e}") # <--- LOG ERROR
            self.image = pygame.Surface((30, 30))
            self.image.fill(settings.ROJO)
            pygame.draw.circle(self.image, settings.NEGRO, (15,15), 10)

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # --- Definición del Hitbox del Enemigo (similar al jugador) ---
        # Estos valores pueden necesitar ajuste según el sprite del enemigo.
        self.hitbox_offset_x = 3 
        self.hitbox_offset_y = 3
        hb_ancho = self.rect.width - (2 * self.hitbox_offset_x)
        hb_alto = self.rect.height - (2 * self.hitbox_offset_y)
        
        # Asegurarse de que el hitbox tenga al menos 1x1 de tamaño
        hb_ancho = max(1, hb_ancho) 
        hb_alto = max(1, hb_alto)

        self.hitbox = pygame.Rect(0, 0, hb_ancho, hb_alto)
        self._actualizar_posicion_hitbox() # Posicionar hitbox inicial

        # Atributos de combate
        self.vida_maxima = 5
        self.vida_actual = self.vida_maxima
        self.dano_ataque = 1
        # self.tiempo_creacion = pygame.time.get_ticks() # Ya no tan relevante para aggro simple
        # self.cooldown_ataque_jugador = 500 
        # self.ultimo_ataque_al_jugador = 0

        # Atributos de movimiento y aggro
        self.velocidad_movimiento = 1.5 # Más lento que el jugador
        self.rango_agro = 200 # Píxeles de distancia para empezar a seguir
        self.distancia_minima_al_jugador = 22 # Reducido desde 35, basado en análisis de hitboxes

    def _actualizar_posicion_hitbox(self):
        """Actualiza la posición del hitbox basándose en la posición del rect principal."""
        self.hitbox.centerx = self.rect.centerx
        self.hitbox.centery = self.rect.centery
        # O si prefieres basarlo en topleft con offsets:
        # self.hitbox.topleft = (self.rect.x + self.hitbox_offset_x, self.rect.y + self.hitbox_offset_y)

    def _mover_y_colisionar_con_obstaculos(self, dx, dy, obstaculos):
        # logger.debug(f"    [Enemigo_{self.id_enemigo}] _mover_y_colisionar_con_obstaculos: dx={dx:.2f}, dy={dy:.2f}")
        original_rect_x = self.rect.x
        original_rect_y = self.rect.y
        original_hitbox_x = self.hitbox.x
        original_hitbox_y = self.hitbox.y

        # Mover en X
        if dx != 0:
            self.hitbox.x += dx
            for obstaculo in obstaculos:
                rect_colision_obstaculo = obstaculo.hitbox if hasattr(obstaculo, 'hitbox') else obstaculo.rect
                if self.hitbox.colliderect(rect_colision_obstaculo):
                    # logger.debug(f"      [Enemigo_{self.id_enemigo}] Colisión X con {type(obstaculo).__name__}_{getattr(obstaculo, 'id_enemigo', 'N/A')}")
                    if dx > 0: # Moviéndose a la derecha
                        self.hitbox.right = rect_colision_obstaculo.left
                    elif dx < 0: # Moviéndose a la izquierda
                        self.hitbox.left = rect_colision_obstaculo.right
            self.rect.x = self.hitbox.left - self.hitbox_offset_x # Ajustar rect basado en hitbox

        # Mover en Y
        if dy != 0:
            self.hitbox.y += dy
            for obstaculo in obstaculos:
                rect_colision_obstaculo = obstaculo.hitbox if hasattr(obstaculo, 'hitbox') else obstaculo.rect
                if self.hitbox.colliderect(rect_colision_obstaculo):
                    # logger.debug(f"      [Enemigo_{self.id_enemigo}] Colisión Y con {type(obstaculo).__name__}_{getattr(obstaculo, 'id_enemigo', 'N/A')}")
                    if dy > 0: # Moviéndose hacia abajo
                        self.hitbox.bottom = rect_colision_obstaculo.top
                    elif dy < 0: # Moviéndose hacia arriba
                        self.hitbox.top = rect_colision_obstaculo.bottom
            self.rect.y = self.hitbox.top - self.hitbox_offset_y # Ajustar rect basado en hitbox
        
        # # Log si hubo cambio significativo (opcional, para reducir spam)
        # if abs(self.hitbox.x - original_hitbox_x) > 0.1 or abs(self.hitbox.y - original_hitbox_y) > 0.1 :
        #     logger.debug(f"    [Enemigo_{self.id_enemigo}] Pos DESPUÉS colisiones: Hitbox: {self.hitbox.topleft}, Rect: {self.rect.topleft}")
        # else: # Si no hubo cambio aparente, se puede omitir el log de "después de colisiones"
        #     pass

    def update(self, objetivo_rect, grupo_obstaculos):
        """Actualiza la lógica del enemigo, incluyendo movimiento y IA básica.

        Args:
            objetivo_rect (pygame.Rect): El rect del objetivo (ej. hitbox del jugador) para seguir.
            grupo_obstaculos (pygame.sprite.Group): Grupo de sprites de obstáculos para evitar (árboles y otros enemigos).
        """
        logger.debug(f"--- Inicio Update Enemigo_{self.id_enemigo} ---")
        logger.debug(f"[Enemigo_{self.id_enemigo}] Pos ANTES update: Rect: {self.rect.topleft}, Hitbox: {self.hitbox.topleft}")

        if self.vida_actual <= 0:
            self.morir()
            return

        dx_al_objetivo = objetivo_rect.centerx - self.hitbox.centerx
        dy_al_objetivo = objetivo_rect.centery - self.hitbox.centery
        
        distancia_al_objetivo = math.sqrt(dx_al_objetivo**2 + dy_al_objetivo**2)
        
        logger.debug(f"[Enemigo_{self.id_enemigo}] Target (Jugador): {objetivo_rect.center}, Dist: {distancia_al_objetivo:.2f}, dx_obj: {dx_al_objetivo:.2f}, dy_obj: {dy_al_objetivo:.2f}")

        mov_x = 0
        mov_y = 0

        if distancia_al_objetivo < self.rango_agro and distancia_al_objetivo > self.distancia_minima_al_jugador:
            if distancia_al_objetivo > 0: # Evitar división por cero si ya está en el objetivo
                dir_x = dx_al_objetivo / distancia_al_objetivo
                dir_y = dy_al_objetivo / distancia_al_objetivo
                mov_x = dir_x * self.velocidad_movimiento
                mov_y = dir_y * self.velocidad_movimiento
        
        logger.debug(f"[Enemigo_{self.id_enemigo}] Movimiento calculado (antes de colisión): mov_x={mov_x:.2f}, mov_y={mov_y:.2f}")
        
        # Mover enemigo y manejar colisiones con obstáculos (árboles y otros enemigos)
        self._mover_y_colisionar_con_obstaculos(mov_x, mov_y, grupo_obstaculos)
        
        # Ya no se necesita la actualización directa de rect y hitbox aquí,
        # porque _mover_y_colisionar_con_obstaculos ya actualiza self.rect y self.hitbox.
        # self.rect.x += mov_x  # <-- ELIMINADO
        # self.rect.y += mov_y  # <-- ELIMINADO
        # self._actualizar_posicion_hitbox() # <-- ELIMINADO (o se asegura que _mover_y_colisionar actualice el hitbox correctamente)
        # NOTA: _actualizar_posicion_hitbox() se llama dentro de _mover_y_colisionar_con_obstaculos
        #       si la lógica de mover el rect se basa en el hitbox después de la corrección.
        #       En mi implementación de _mover_y_colisionar_con_obstaculos, actualizo self.rect.x/y
        #       basado en el hitbox.hitbox.left/top, lo que es correcto.

        logger.debug(f"[Enemigo_{self.id_enemigo}] Pos DESPUÉS de _mover_y_colisionar_con_obstaculos: Rect: {self.rect.topleft}, Hitbox: {self.hitbox.topleft}")
        logger.debug(f"--- Fin Update Enemigo_{self.id_enemigo} ---")

    def recibir_dano(self, cantidad):
        self.vida_actual -= cantidad
        logger.info(f"[Enemigo_{self.id_enemigo}] ({self.rect.center}) recibe {cantidad} de daño. Vida restante: {self.vida_actual}")
        # No necesita cooldown de recibir daño si el jugador tiene cooldown de atacar.

    def morir(self):
        logger.info(f"[Enemigo_{self.id_enemigo}] en ({self.rect.centerx},{self.rect.centery}) ha muerto!")
        self.kill() # Elimina el sprite de todos los grupos a los que pertenece.

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
