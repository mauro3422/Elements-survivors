import pygame
import settings # Para acceder a ANCHO_PANTALLA, ALTO_PANTALLA, NEGRO, etc.

class Camara:
    def __init__(self, ancho_vista_inicial, alto_vista_inicial):
        """Constructor de la clase Camara.

        Args:
            ancho_vista_inicial (float): Ancho inicial de la vista de la cámara en el mundo.
            alto_vista_inicial (float): Alto inicial de la vista de la cámara en el mundo.
        """
        self.ancho_vista_mundo = ancho_vista_inicial
        self.alto_vista_mundo = alto_vista_inicial
        
        # La `camara_surface` es la superficie interna donde se dibuja la escena del tamaño del "mundo visible".
        # Se crea con pygame.SRCALPHA para soportar transparencia si algún sprite la usa.
        self.camara_surface = pygame.Surface((self.ancho_vista_mundo, self.alto_vista_mundo), pygame.SRCALPHA)
        
        # Coordenadas de la esquina superior izquierda de la cámara en el mundo del juego.
        # Estas determinan qué parte del mundo se está viendo.
        self.cam_mundo_x = 0
        self.cam_mundo_y = 0
        
        # El offset es simplemente el negativo de cam_mundo_x y cam_mundo_y. Se usa para dibujar.
        self.offset_camara = pygame.math.Vector2(0, 0)

    def actualizar_dimensiones_vista(self, nuevo_ancho_vista, nuevo_alto_vista):
        """Actualiza las dimensiones de la vista de la cámara y recrea la superficie interna."""
        self.ancho_vista_mundo = nuevo_ancho_vista
        self.alto_vista_mundo = nuevo_alto_vista
        self.camara_surface = pygame.Surface((self.ancho_vista_mundo, self.alto_vista_mundo), pygame.SRCALPHA)
        # Es importante re-calcular la posición de la cámara para que no se "salte"
        # o se salga de los límites al cambiar el zoom. Esto se maneja en actualizar_posicion.

    def actualizar_posicion(self, rect_objetivo):
        """Actualiza la posición de la cámara para que siga al rect_objetivo (normalmente el jugador).
        El objetivo es mantener el centro del rect_objetivo en el centro de la vista de la cámara.
        También se asegura de que la cámara no se mueva fuera de los límites del mundo del juego.
        """
        # Posición X: Centra el objetivo en la cámara.
        # La posición de la cámara (cam_mundo_x) es la esquina superior izquierda de su vista.
        # Para centrar el objetivo (rect_objetivo.centerx) en la cámara (ancho_vista_mundo / 2),
        # la fórmula es: cam_mundo_x = rect_objetivo.centerx - (ancho_vista_mundo / 2)
        self.cam_mundo_x = rect_objetivo.centerx - (self.ancho_vista_mundo / 2)
        
        # Posición Y: Similar para el eje Y.
        self.cam_mundo_y = rect_objetivo.centery - (self.alto_vista_mundo / 2)

        # Aplicar límites para que la cámara no se salga del mundo del juego.
        # Límite izquierdo (la cámara no puede ir más a la izquierda que x=0 del mundo)
        self.cam_mundo_x = max(0, self.cam_mundo_x)
        # Límite superior (la cámara no puede ir más arriba que y=0 del mundo)
        self.cam_mundo_y = max(0, self.cam_mundo_y)
        # Límite derecho (la esquina derecha de la cámara no puede superar el ancho del mundo)
        # Esquina derecha de la cámara = cam_mundo_x + ancho_vista_mundo
        self.cam_mundo_x = min(self.cam_mundo_x, settings.ANCHO_MUNDO_JUEGO - self.ancho_vista_mundo)
        # Límite inferior (la esquina inferior de la cámara no puede superar el alto del mundo)
        self.cam_mundo_y = min(self.cam_mundo_y, settings.ALTO_MUNDO_JUEGO - self.alto_vista_mundo)

        # El offset es el negativo de la posición de la cámara, se usa para dibujar los sprites.
        self.offset_camara.x = self.cam_mundo_x
        self.offset_camara.y = self.cam_mundo_y

    def _dibujar_sprite_en_camara(self, sprite, offset_camara):
        """Dibuja un sprite individual en la camara_surface, aplicando el offset de la cámara."""
        # El rect del sprite está en coordenadas del mundo.
        # Lo movemos por el negativo del offset de la cámara para obtener su posición en la camara_surface.
        rect_en_camara = sprite.rect.move(-offset_camara.x, -offset_camara.y)
        self.camara_surface.blit(sprite.image, rect_en_camara)

    def dibujar_rect_debug(self, rect_mundo, color, offset_camara):
        """Dibuja un rectángulo (dado en coordenadas del mundo) en la camara_surface.
           El color puede ser RGBA para transparencia.
        """
        temp_surface = pygame.Surface((rect_mundo.width, rect_mundo.height), pygame.SRCALPHA)
        pygame.draw.rect(temp_surface, color, (0,0, rect_mundo.width, rect_mundo.height), 2) # Grosor 2
        rect_en_camara = rect_mundo.move(-offset_camara.x, -offset_camara.y)
        self.camara_surface.blit(temp_surface, rect_en_camara.topleft)

    def dibujar_escena(self, pantalla_destino_final, 
                         textura_fondo, ancho_textura_tile, alto_textura_tile, 
                         jugador, grupo_arboles, grupo_enemigos):
        """Dibuja toda la escena (fondo, sprites) en la camara_surface y luego la escala a la pantalla_destino_final."""
        
        # --- 1. Dibujar el Fondo Tileado en la camara_surface ---
        # Optimización: solo dibujar los tiles visibles por la cámara.
        # Calcular el rango de tiles que son (parcialmente) visibles.
        start_col = int(self.cam_mundo_x // ancho_textura_tile)
        end_col = int((self.cam_mundo_x + self.ancho_vista_mundo) // ancho_textura_tile) + 1
        start_row = int(self.cam_mundo_y // alto_textura_tile)
        end_row = int((self.cam_mundo_y + self.alto_vista_mundo) // alto_textura_tile) + 1

        for row in range(start_row, end_row):
            for col in range(start_col, end_col):
                # Calcular la posición del tile en coordenadas del mundo.
                x_mundo_tile = col * ancho_textura_tile
                y_mundo_tile = row * alto_textura_tile
                
                # Convertir la posición del tile a coordenadas de la camara_surface.
                # Esto es, restar el offset de la cámara (cam_mundo_x, cam_mundo_y).
                x_cam_tile = x_mundo_tile - self.cam_mundo_x
                y_cam_tile = y_mundo_tile - self.cam_mundo_y
                
                self.camara_surface.blit(textura_fondo, (x_cam_tile, y_cam_tile))

        # --- 2. Dibujar Sprites en la camara_surface ---
        # El orden de dibujado importa (los últimos dibujados aparecen encima).

        # Dibujar todos los árboles en la camara_surface, ajustados por el offset
        for arbol in grupo_arboles:
            self._dibujar_sprite_en_camara(arbol, self.offset_camara)

        # Dibujar todos los enemigos en la camara_surface, ajustados por el offset
        for enemigo in grupo_enemigos:
            self._dibujar_sprite_en_camara(enemigo, self.offset_camara)

        # Dibujar al jugador en la camara_surface, ajustado por el offset
        self._dibujar_sprite_en_camara(jugador, self.offset_camara)

        # --- Dibujar Hitboxes para Depuración (si está activado) ---
        if settings.DEBUG_VER_HITBOXES:
            # Hitbox del cuerpo del jugador
            if hasattr(jugador, 'hitbox'):
                self.dibujar_rect_debug(jugador.hitbox, settings.ROJO, self.offset_camara)
            
            # Hitbox del ataque ACTIVO del jugador
            if hasattr(jugador, 'esta_atacando') and jugador.esta_atacando:
                if hasattr(jugador, 'hitbox_ataque_actual_rect') and jugador.hitbox_ataque_actual_rect.width > 0 and jugador.hitbox_ataque_actual_rect.height > 0:
                    self.dibujar_rect_debug(jugador.hitbox_ataque_actual_rect, settings.VERDE_DEBUG, self.offset_camara)
            
            # Hitbox de los enemigos (usando su rect por ahora)
            for enemigo in grupo_enemigos:
                self.dibujar_rect_debug(enemigo.rect, settings.ROJO, self.offset_camara)
            
            # Hitbox de los árboles (usando su rect por ahora)
            # for arbol in grupo_arboles:
            #     self.dibujar_rect_debug(arbol.rect, settings.ROJO, self.offset_camara)

        # --- 3. Escalar la camara_surface a la Pantalla Principal ---
        # La camara_surface (que contiene la vista del mundo) se escala al tamaño completo 
        # de la pantalla_destino_final para lograr el efecto de zoom.
        pygame.transform.scale(self.camara_surface, pantalla_destino_final.get_size(), pantalla_destino_final)