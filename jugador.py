import pygame
import os
import settings

class Jugador(pygame.sprite.Sprite):
    def __init__(self, x, y, ruta_assets):
        """Constructor de la clase Jugador.

        Args:
            x (int): Posición inicial en el eje X del jugador en el mundo del juego.
            y (int): Posición inicial en el eje Y del jugador en el mundo del juego.
            ruta_assets (str): Ruta a la carpeta principal de 'assets'.
        """
        super().__init__()
        self.ruta_assets = ruta_assets
        self.animaciones = {}
        self._cargar_animaciones()

        # Estado inicial de la animación
        self.estado_animacion = "descanso"
        self.indice_fotograma = 0
        if self.animaciones.get(self.estado_animacion):
            self.image = self.animaciones[self.estado_animacion][self.indice_fotograma]
        else:
            print(f"Error: Animación '{self.estado_animacion}' no encontrada para el Jugador. Usando placeholder.")
            self.image = pygame.Surface((32, 32))
            self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # --- Definición del Hitbox Personalizado ---
        self.hitbox_offset_x = 4
        self.hitbox_offset_y = 6
        hb_ancho = self.rect.width - (2 * self.hitbox_offset_x)
        hb_alto = self.rect.height - (self.hitbox_offset_y + 4)
        
        hb_ancho = max(1, hb_ancho)
        hb_alto = max(1, hb_alto)

        self.hitbox = pygame.Rect(0, 0, hb_ancho, hb_alto)
        self.hitbox.topleft = (self.rect.x + self.hitbox_offset_x, self.rect.y + self.hitbox_offset_y)
        
        self.velocidad = 3
        self.tiempo_ultimo_fotograma = pygame.time.get_ticks()
        self.retraso_animacion = 150 # Milisegundos entre fotogramas (ajustar según sea necesario)

    def _cargar_animaciones(self):
        """Carga los fotogramas para las animaciones del jugador.
        Por ahora, solo carga la animación de "descanso".
        """
        ruta_anim_descanso = os.path.join(self.ruta_assets, "character", "animaciones", "Player", "reposo")
        self.animaciones["descanso"] = []
        for i in range(1, 5): # Asumiendo 4 fotogramas: 1.png, 2.png, 3.png, 4.png
            try:
                img_path = os.path.join(ruta_anim_descanso, f"{i}.png")
                imagen = pygame.image.load(img_path).convert_alpha()
                # Escalar si es necesario, por ejemplo a 32x32
                # imagen = pygame.transform.scale(imagen, (32, 32))
                self.animaciones["descanso"].append(imagen)
            except pygame.error as e:
                print(f"Error al cargar la imagen de animación del jugador {img_path}: {e}")
                # Podríamos añadir una imagen placeholder si falla la carga
                placeholder = pygame.Surface((32,32))
                placeholder.fill((255,0,0)) # Rojo
                self.animaciones["descanso"].append(placeholder)
        
        if not self.animaciones["descanso"]:
            print("CRITICAL: No se cargaron fotogramas para la animación de descanso del Jugador.")
            placeholder = pygame.Surface((32,32)); placeholder.fill((255,0,0))
            self.animaciones["descanso"] = [placeholder]

    def actualizar_animacion(self):
        """Actualiza el fotograma actual de la animación del jugador basado en el tiempo.
        Se llama en cada fotograma del bucle principal del juego.
        """
        ahora = pygame.time.get_ticks()
        if ahora - self.tiempo_ultimo_fotograma > self.retraso_animacion:
            self.tiempo_ultimo_fotograma = ahora
            self.indice_fotograma = (self.indice_fotograma + 1) % len(self.animaciones[self.estado_animacion])
            self.image = self.animaciones[self.estado_animacion][self.indice_fotograma]

    def _actualizar_posicion_hitbox(self):
        self.hitbox.topleft = (self.rect.x + self.hitbox_offset_x, self.rect.y + self.hitbox_offset_y)

    def _mover_y_colisionar(self, dx, dy, obstaculos):
        # Guardar la posición original por si necesitamos revertir completamente un movimiento
        # (aunque con la corrección por ejes, esto es menos crucial aquí que en colisiones más simples)
        # pos_original_x = self.rect.x
        # pos_original_y = self.rect.y

        # --- Movimiento y colisiones en Eje X ---
        self.rect.x += dx
        self._actualizar_posicion_hitbox() # Actualizar hitbox a la nueva posición tentativa X

        # Comprobar límites del mundo en X
        if self.hitbox.left < 0:
            # El hitbox ha cruzado el borde izquierdo del mundo (0)
            # Ajustamos self.rect.x para que self.hitbox.left sea 0
            self.rect.x = 0 - self.hitbox_offset_x 
        elif self.hitbox.right > settings.ANCHO_MUNDO_JUEGO:
            # El hitbox ha cruzado el borde derecho del mundo
            # Ajustamos self.rect.x para que self.hitbox.right sea ANCHO_MUNDO_JUEGO
            self.rect.x = settings.ANCHO_MUNDO_JUEGO - self.hitbox_offset_x - self.hitbox.width
        self._actualizar_posicion_hitbox() # Re-sincronizar hitbox después de corrección de límites en X

        # Comprobar colisiones con obstáculos en X
        for obstaculo in obstaculos:
            if self.hitbox.colliderect(obstaculo.rect):
                if dx > 0: # Moviéndose a la derecha, choca con el lado izquierdo del obstáculo
                    self.rect.x = obstaculo.rect.left - self.hitbox_offset_x - self.hitbox.width
                elif dx < 0: # Moviéndose a la izquierda, choca con el lado derecho del obstáculo
                    self.rect.x = obstaculo.rect.right - self.hitbox_offset_x
                self._actualizar_posicion_hitbox() # Re-sincronizar hitbox después de la corrección por colisión en X
        
        # --- Movimiento y colisiones en Eje Y ---
        self.rect.y += dy
        self._actualizar_posicion_hitbox() # Actualizar hitbox a la nueva posición tentativa Y

        # Comprobar límites del mundo en Y
        if self.hitbox.top < 0:
            # El hitbox ha cruzado el borde superior del mundo (0)
            # Ajustamos self.rect.y para que self.hitbox.top sea 0
            self.rect.y = 0 - self.hitbox_offset_y
        elif self.hitbox.bottom > settings.ALTO_MUNDO_JUEGO:
            # El hitbox ha cruzado el borde inferior del mundo
            # Ajustamos self.rect.y para que self.hitbox.bottom sea ALTO_MUNDO_JUEGO
            self.rect.y = settings.ALTO_MUNDO_JUEGO - self.hitbox_offset_y - self.hitbox.height
        self._actualizar_posicion_hitbox() # Re-sincronizar hitbox después de corrección de límites en Y

        # Comprobar colisiones con obstáculos en Y
        for obstaculo in obstaculos:
            if self.hitbox.colliderect(obstaculo.rect):
                if dy > 0: # Moviéndose hacia abajo, choca con la parte superior del obstáculo
                    self.rect.y = obstaculo.rect.top - self.hitbox_offset_y - self.hitbox.height
                elif dy < 0: # Moviéndose hacia arriba, choca con la parte inferior del obstáculo
                    self.rect.y = obstaculo.rect.bottom - self.hitbox_offset_y
                self._actualizar_posicion_hitbox() # Re-sincronizar hitbox después de la corrección por colisión en Y

    def actualizar_movimiento(self, teclas_presionadas, obstaculos):
        """Actualiza la posición del jugador basándose en las teclas presionadas.
        Se llama en cada fotograma del bucle principal.

        Args:
            teclas_presionadas: Un diccionario o secuencia de booleanos de pygame.key.get_pressed()
                    que indica el estado de todas las teclas.
        """
        mov_x_final = 0
        mov_y_final = 0

        if teclas_presionadas[pygame.K_LEFT] or teclas_presionadas[pygame.K_a]:
            mov_x_final = -self.velocidad
        if teclas_presionadas[pygame.K_RIGHT] or teclas_presionadas[pygame.K_d]:
            mov_x_final = self.velocidad
        if teclas_presionadas[pygame.K_UP] or teclas_presionadas[pygame.K_w]:
            mov_y_final = -self.velocidad
        if teclas_presionadas[pygame.K_DOWN] or teclas_presionadas[pygame.K_s]:
            mov_y_final = self.velocidad
        
        if mov_x_final != 0 or mov_y_final != 0:
            self._mover_y_colisionar(mov_x_final, mov_y_final, obstaculos)
        
        # # --- AÑADIMOS MOVIMIENTO SIMPLE SIN COLISIÓN ---
        # self.rect.x += mov_x_final
        # self.rect.y += mov_y_final
        # # self._actualizar_posicion_hitbox() 

    def dibujar(self, superficie):
        """Dibuja el sprite actual del jugador en la superficie dada.
        Nota: Con el sistema de cámara, este método se vuelve menos relevante si la cámara
        dibuja directamente el jugador.image. Sin embargo, es una buena práctica tenerlo.

        Args:
            superficie (pygame.Surface): La superficie donde se dibujará el jugador.
        """
        superficie.blit(self.image, self.rect)
        # Opcional: Dibujar el hitbox para depuración
        # pygame.draw.rect(superficie, (255,0,0), self.hitbox, 1) 