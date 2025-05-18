import pygame
import os
import settings
import json

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

        # Dirección del último movimiento (para orientar ataques, etc.)
        # (1, 0) -> Derecha; (-1, 0) -> Izquierda; (0, -1) -> Arriba; (0, 1) -> Abajo
        self.ultima_direccion_mov_x = 1 # Por defecto, mirando a la derecha
        self.ultima_direccion_mov_y = 0

        # Atributos de combate
        self.vida_maxima = 10
        self.vida_actual = self.vida_maxima
        self.ultimo_ataque_recibido = 0 # Tiempo del último golpe recibido (para cooldown)
        self.cooldown_dano = 1000 # 1 segundo de invencibilidad después de ser golpeado

        # Atributos para el ataque con espada
        self.dano_espada = 5
        self.cooldown_ataque_espada = 700 # Milisegundos
        self.duracion_hitbox_ataque_espada = 200 # Milisegundos que el hitbox está activo
        self.tiempo_inicio_ataque_espada = 0
        self.esta_atacando_espada = False
        self.ultimo_ataque_realizado = 0 # Para el cooldown general de ataques
        self.enemigos_golpeados_este_ataque = set()

        # Valores por defecto para las dimensiones del hitbox de ataque
        self.default_ataque_offset_distancia = 10
        self.default_ataque_extension = 40
        self.default_ataque_grosor = self.rect.height if self.rect else 32 # Usar altura del rect si está disponible

        # Dimensiones y offset del hitbox de la espada (AJUSTABLES)
        self.ataque_offset_distancia = self.default_ataque_offset_distancia
        self.ataque_extension = self.default_ataque_extension
        self.ataque_grosor = self.default_ataque_grosor
        self._cargar_config_ataque() # Intentar cargar desde archivo, sobrescribe si tiene éxito
        
        self.hitbox_ataque_espada_rect = pygame.Rect(0, 0, 0, 0)

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
        
        # Actualizar la última dirección de movimiento solo si hay movimiento efectivo
        if mov_x_final != 0 or mov_y_final != 0:
            # Priorizar horizontal si hay movimiento en ambos ejes para la última dirección principal
            # Esto es una simplificación; podría ser más complejo para 8 direcciones si es necesario.
            if mov_x_final != 0:
                self.ultima_direccion_mov_x = int(mov_x_final / self.velocidad) # Normalizar a 1 o -1
                self.ultima_direccion_mov_y = 0 # Si hay mov X, se considera la dirección principal
            elif mov_y_final != 0: # Solo si no hay mov_x_final
                self.ultima_direccion_mov_x = 0
                self.ultima_direccion_mov_y = int(mov_y_final / self.velocidad) # Normalizar a 1 o -1
            
            # Si se permite movimiento diagonal y se quiere guardar la componente diagonal exacta:
            # if mov_x_final != 0:
            #     self.ultima_direccion_mov_x = int(mov_x_final / self.velocidad)
            # else:
            #     self.ultima_direccion_mov_x = 0 # Mantener en 0 si no hay input horizontal
            # if mov_y_final != 0:
            #     self.ultima_direccion_mov_y = int(mov_y_final / self.velocidad)
            # else:
            #     self.ultima_direccion_mov_y = 0 # Mantener en 0 si no hay input vertical
            
            # Corregir si ambos son cero por alguna razón (aunque la condición externa lo evita)
            # if self.ultima_direccion_mov_x == 0 and self.ultima_direccion_mov_y == 0:
                # Forzar una dirección por defecto si se queda en (0,0) después de moverse
                # self.ultima_direccion_mov_x = 1 # Derecha por defecto

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

    def recibir_dano(self, cantidad):
        ahora = pygame.time.get_ticks()
        if ahora - self.ultimo_ataque_recibido > self.cooldown_dano:
            self.vida_actual -= cantidad
            self.ultimo_ataque_recibido = ahora
            print(f"Jugador recibe {cantidad} de daño. Vida restante: {self.vida_actual}")
            if self.vida_actual <= 0:
                self.morir()
        # else: print("Jugador en cooldown, daño ignorado") # Para depuración

    def morir(self):
        print("Jugador ha muerto!")
        # Por ahora, solo un print. Podríamos hacer que el juego termine, reiniciar, etc.
        # self.kill() # Si quisiéramos que el sprite del jugador desaparezca (podría no ser deseable)
        # O cambiar su estado a "muerto" para una animación de muerte, etc.
        pass 

    def atacar(self, grupo_enemigos):
        ahora = pygame.time.get_ticks()
        if ahora - self.ultimo_ataque_realizado > self.cooldown_ataque_espada:
            if not self.esta_atacando_espada: # Solo iniciar si no está ya atacando
                self.esta_atacando_espada = True
                self.tiempo_inicio_ataque_espada = ahora
                self.ultimo_ataque_realizado = ahora # Actualiza el cooldown general
                self.enemigos_golpeados_este_ataque.clear()
                print("Jugador inicia ataque con espada!") # Mensaje de depuración
                # Aquí podríamos cambiar el estado de animación a "atacando_espada"
                # self.estado_animacion = "atacando_espada"
                # self.indice_fotograma = 0
        # else:
            # print("Ataque con espada en cooldown")

    def actualizar_ataque_espada(self, enemigos):
        if not self.esta_atacando_espada:
            return

        ahora = pygame.time.get_ticks()
        
        # Comprobar si la duración del hitbox activo ha pasado
        if ahora - self.tiempo_inicio_ataque_espada <= self.duracion_hitbox_ataque_espada:
            # Usar los nuevos atributos ajustables para dimensiones
            current_hitbox_extension = self.ataque_extension
            current_hitbox_grosor = self.ataque_grosor

            # Lógica de posicionamiento y dimensionamiento basada en la última dirección
            if self.ultima_direccion_mov_x > 0: # Derecha
                pos_x_hitbox = self.rect.right + self.ataque_offset_distancia
                pos_y_hitbox = self.rect.centery - current_hitbox_grosor // 2 # Centrar verticalmente
                final_ancho = current_hitbox_extension
                final_alto = current_hitbox_grosor
            elif self.ultima_direccion_mov_x < 0: # Izquierda
                pos_x_hitbox = self.rect.left - self.ataque_offset_distancia - current_hitbox_extension
                pos_y_hitbox = self.rect.centery - current_hitbox_grosor // 2 # Centrar verticalmente
                final_ancho = current_hitbox_extension
                final_alto = current_hitbox_grosor
            elif self.ultima_direccion_mov_y > 0: # Abajo
                # Para ataques verticales, la "extensión" es vertical, el "grosor" es horizontal
                pos_x_hitbox = self.rect.centerx - current_hitbox_grosor // 2 # Centrar horizontalmente
                pos_y_hitbox = self.rect.bottom + self.ataque_offset_distancia
                final_ancho = current_hitbox_grosor # Grosor se vuelve ancho
                final_alto = current_hitbox_extension # Extensión se vuelve alto
            elif self.ultima_direccion_mov_y < 0: # Arriba
                pos_x_hitbox = self.rect.centerx - current_hitbox_grosor // 2 # Centrar horizontalmente
                pos_y_hitbox = self.rect.top - self.ataque_offset_distancia - current_hitbox_extension
                final_ancho = current_hitbox_grosor # Grosor se vuelve ancho
                final_alto = current_hitbox_extension # Extensión se vuelve alto
            else: # Por defecto (derecha)
                pos_x_hitbox = self.rect.right + self.ataque_offset_distancia
                pos_y_hitbox = self.rect.centery - current_hitbox_grosor // 2
                final_ancho = current_hitbox_extension
                final_alto = current_hitbox_grosor
            
            self.hitbox_ataque_espada_rect.x = pos_x_hitbox
            self.hitbox_ataque_espada_rect.y = pos_y_hitbox
            self.hitbox_ataque_espada_rect.width = final_ancho
            self.hitbox_ataque_espada_rect.height = final_alto

            # Comprobar colisiones con enemigos
            for enemigo in enemigos:
                if enemigo not in self.enemigos_golpeados_este_ataque: # Solo golpear una vez
                    if self.hitbox_ataque_espada_rect.colliderect(enemigo.rect): # Usar enemigo.rect por ahora
                        print(f"ESPADA golpea a enemigo en {enemigo.rect} con hitbox {self.hitbox_ataque_espada_rect}")
                        enemigo.recibir_dano(self.dano_espada)
                        self.enemigos_golpeados_este_ataque.add(enemigo)
        else:
            # El tiempo del hitbox activo ha terminado, pero la animación de ataque podría continuar.
            # Por ahora, simplemente desactivamos el estado de ataque y el hitbox.
            self.esta_atacando_espada = False
            self.hitbox_ataque_espada_rect.size = (0,0) # Encoger para evitar colisiones accidentales
            # print("Fin de la ventana activa del hitbox de espada.")
            # Aquí se podría volver al estado de animación "descanso" si la animación de ataque ha terminado
            # if self.estado_animacion == "atacando_espada":
            # self.estado_animacion = "descanso"
            # self.indice_fotograma = 0

    def _cargar_config_ataque(self):
        try:
            ruta_completa_config = os.path.join(settings.RUTA_BASE_PROYECTO, settings.ARCHIVO_CONFIG_ATAQUE)
            with open(ruta_completa_config, 'r') as f:
                config = json.load(f)
                self.ataque_offset_distancia = config.get('ataque_offset_distancia', self.default_ataque_offset_distancia)
                self.ataque_extension = config.get('ataque_extension', self.default_ataque_extension)
                self.ataque_grosor = config.get('ataque_grosor', self.default_ataque_grosor)
                print(f"Configuración de ataque cargada desde {settings.ARCHIVO_CONFIG_ATAQUE}")
        except FileNotFoundError:
            print(f"Archivo de configuración de ataque '{settings.ARCHIVO_CONFIG_ATAQUE}' no encontrado. Usando valores por defecto.")
        except json.JSONDecodeError:
            print(f"Error al decodificar JSON en '{settings.ARCHIVO_CONFIG_ATAQUE}'. Usando valores por defecto.")
        except Exception as e:
            print(f"Error inesperado al cargar configuración de ataque: {e}. Usando valores por defecto.")

    def guardar_config_ataque_actual(self):
        config_data = {
            'ataque_offset_distancia': self.ataque_offset_distancia,
            'ataque_extension': self.ataque_extension,
            'ataque_grosor': self.ataque_grosor
        }
        try:
            ruta_completa_config = os.path.join(settings.RUTA_BASE_PROYECTO, settings.ARCHIVO_CONFIG_ATAQUE)
            with open(ruta_completa_config, 'w') as f:
                json.dump(config_data, f, indent=4)
            print(f"Configuración de ataque guardada en {settings.ARCHIVO_CONFIG_ATAQUE}")
        except Exception as e:
            print(f"Error al guardar configuración de ataque: {e}")

    # --- Métodos para ajustar parámetros de ataque en tiempo real ---
    def modificar_ataque_offset(self, cantidad):
        self.ataque_offset_distancia += cantidad
        print(f"Nuevo ataque_offset_distancia: {self.ataque_offset_distancia}")

    def modificar_ataque_extension(self, cantidad):
        self.ataque_extension += cantidad
        self.ataque_extension = max(1, self.ataque_extension) # Evitar tamaño cero o negativo
        print(f"Nuevo ataque_extension: {self.ataque_extension}")

    def modificar_ataque_grosor(self, cantidad):
        self.ataque_grosor += cantidad
        self.ataque_grosor = max(1, self.ataque_grosor) # Evitar tamaño cero o negativo
        print(f"Nuevo ataque_grosor: {self.ataque_grosor}")