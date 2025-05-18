import pygame
import os
import settings # Para RUTA_ASSETS
import math # Para cálculos de distancia y vectores

class Enemigo(pygame.sprite.Sprite):
    def __init__(self, x, y, nombre_archivo_imagen="chicken.png"):
        """Constructor de la clase Enemigo.

        Args:
            x (int): Posición inicial en el eje X del enemigo.
            y (int): Posición inicial en el eje Y del enemigo.
            nombre_archivo_imagen (str): Nombre del archivo de imagen para este enemigo
                                         (ej: "chicken.png") dentro de la carpeta de enemigos.
        """
        super().__init__()

        self.ruta_base_enemigos = os.path.join(settings.RUTA_ASSETS, "character", "animaciones", "Enemy")
        
        try:
            # Construir la ruta completa a la imagen del enemigo
            ruta_imagen = os.path.join(self.ruta_base_enemigos, nombre_archivo_imagen)
            self.image = pygame.image.load(ruta_imagen).convert_alpha()
            # Podríamos añadir escalado aquí si es necesario, ej:
            # self.image = pygame.transform.scale(self.image, (NUEVO_ANCHO, NUEVO_ALTO))
        except pygame.error as e:
            print(f"Error al cargar la imagen del enemigo {ruta_imagen}: {e}")
            # Fallback a una superficie simple si la imagen no carga
            self.image = pygame.Surface((30, 30)) # Tamaño de fallback
            self.image.fill(settings.ROJO) # Color de fallback (rojo)
            pygame.draw.circle(self.image, settings.NEGRO, (15,15), 10) # Un círculo negro para distinguirlo

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

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
        self.distancia_minima_al_jugador = 20 # Para evitar que se solape temblando

    def update(self, jugador_rect):
        """Actualiza la lógica del enemigo.
        Por ahora, los enemigos estáticos no hacen nada en su update.
        Se podría añadir movimiento, IA, etc. aquí en el futuro.
        """
        if self.vida_actual <= 0:
            self.morir()
            return # No hacer más lógica si está muerto

        # Lógica de seguimiento (aggro)
        dx_al_jugador = jugador_rect.centerx - self.rect.centerx
        dy_al_jugador = jugador_rect.centery - self.rect.centery
        
        distancia_al_jugador = math.sqrt(dx_al_jugador**2 + dy_al_jugador**2)

        if distancia_al_jugador < self.rango_agro and distancia_al_jugador > self.distancia_minima_al_jugador:
            # Normalizar el vector de dirección
            if distancia_al_jugador > 0: # Evitar división por cero si está exactamente en el mismo punto
                dir_x = dx_al_jugador / distancia_al_jugador
                dir_y = dy_al_jugador / distancia_al_jugador
            else:
                dir_x, dir_y = 0, 0 # No moverse si ya está encima

            # Mover enemigo
            self.rect.x += dir_x * self.velocidad_movimiento
            self.rect.y += dir_y * self.velocidad_movimiento
        
        # (Aquí iría la lógica de ataque si el enemigo está lo suficientemente cerca después de moverse)

    def recibir_dano(self, cantidad):
        self.vida_actual -= cantidad
        print(f"Enemigo ({self.rect.center}) recibe {cantidad} de daño. Vida restante: {self.vida_actual}")
        # No necesita cooldown de recibir daño si el jugador tiene cooldown de atacar.

    def morir(self):
        print(f"Enemigo en ({self.rect.centerx},{self.rect.centery}) ha muerto!")
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
