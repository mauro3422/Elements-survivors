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
        
        # Esta es la superficie donde se dibujará todo lo que la cámara "ve" en el mundo,
        # antes de ser escalada a la pantalla principal.
        self.surface = pygame.Surface((self.ancho_vista_mundo, self.alto_vista_mundo))
        
        # Coordenadas (x,y) de la esquina superior izquierda de la vista de la cámara DENTRO del mundo del juego.
        # Estas coordenadas cambian a medida que la cámara sigue al jugador.
        self.cam_mundo_x = 0
        self.cam_mundo_y = 0

    def actualizar_dimensiones_vista(self, nuevo_ancho_vista, nuevo_alto_vista):
        """Actualiza las dimensiones de la vista de la cámara y redimensiona su superficie interna.
        Llamado desde main.py cuando el FACTOR_ZOOM cambia.
        """
        self.ancho_vista_mundo = nuevo_ancho_vista
        self.alto_vista_mundo = nuevo_alto_vista
        try:
            # Intenta crear la nueva superficie. Puede fallar si las dimensiones son demasiado pequeñas o inválidas.
            self.surface = pygame.Surface((int(self.ancho_vista_mundo), int(self.alto_vista_mundo)))
        except pygame.error as e:
            print(f"Error al redimensionar la superficie de la cámara a ({self.ancho_vista_mundo}, {self.alto_vista_mundo}): {e}")
            # Fallback: mantener las dimensiones anteriores o unas mínimas seguras.
            # Por simplicidad, aquí no hacemos un fallback complejo, pero en un juego robusto lo considerarías.
            # Si esto falla consistentemente, es un problema con los límites de zoom o el cálculo.
            pass # Dejar que la superficie antigua persista si la nueva falla

    def actualizar_posicion(self, target_rect_mundo):
        """Centra la vista de la cámara en el target_rect_mundo (normalmente el rect del jugador).

        Args:
            target_rect_mundo (pygame.Rect): El rectángulo del objeto que la cámara debe seguir en el mundo.
        """
        # Calcula la posición X de la cámara para que el CENTRO del target_rect_mundo
        # coincida con el CENTRO de la vista de la cámara (self.ancho_vista_mundo / 2).
        self.cam_mundo_x = target_rect_mundo.centerx - (self.ancho_vista_mundo / 2)
        
        # Calcula la posición Y de la cámara de forma similar.
        self.cam_mundo_y = target_rect_mundo.centery - (self.alto_vista_mundo / 2)
        
        # --- Opcional: Limitar el scroll de la cámara --- 
        # Si tu mundo tuviera límites definidos (ej: un mapa de 2000x2000 píxeles),
        # podrías añadir lógica aquí para que la cámara no se "salga" de esos límites.
        # Ejemplo (necesitarías ANCHO_MUNDO_JUEGO y ALTO_MUNDO_JUEGO definidos en settings):
        # self.cam_mundo_x = max(0, self.cam_mundo_x) # No ir más a la izquierda que 0
        # self.cam_mundo_y = max(0, self.cam_mundo_y) # No ir más arriba que 0
        # self.cam_mundo_x = min(self.cam_mundo_x, settings.ANCHO_MUNDO_JUEGO - self.ancho_vista_mundo) # No ir más a la derecha del límite
        # self.cam_mundo_y = min(self.cam_mundo_y, settings.ALTO_MUNDO_JUEGO - self.alto_vista_mundo)   # No ir más abajo del límite

    def dibujar_escena(self, pantalla_destino_final, 
                       textura_fondo, ancho_textura_tile, alto_textura_tile, 
                       jugador, grupo_otros_sprites, grupo_enemigos):
        """Dibuja toda la escena (fondo, sprites, jugador) en la superficie interna de la cámara
        y luego escala esa superficie a la pantalla_destino_final.

        Args:
            pantalla_destino_final (pygame.Surface): La pantalla principal del juego donde se mostrará el resultado.
            textura_fondo (pygame.Surface): La imagen original de la textura del fondo (tile).
            ancho_textura_tile (int): Ancho de la textura_fondo.
            alto_textura_tile (int): Alto de la textura_fondo.
            jugador (Jugador): La instancia del objeto jugador.
            grupo_otros_sprites (pygame.sprite.Group): Grupo que contiene sprites como los árboles.
            grupo_enemigos (pygame.sprite.Group): Grupo que contiene los sprites de los enemigos.
        """
        
        # 1. Limpiar la superficie interna de la cámara (rellenar con un color base)
        # AZUL_PRUEBA = (0, 0, 255) # Ya no es azul de prueba
        try:
            if self.surface: # Asegurarse que self.surface existe y no es None
                self.surface.fill(settings.NEGRO) # Restaurado a NEGRO
            else:
                print("ERROR CAMARA: self.surface no existe en dibujar_escena")
                # Como fallback, intentar dibujar NEGRO directamente en la pantalla final si self.surface falla
                pantalla_destino_final.fill(settings.NEGRO) 
                return 
        except Exception as e:
            print(f"ERROR CAMARA: Excepción al llenar self.surface: {e}")
            pantalla_destino_final.fill(settings.NEGRO) # Fallback
            return

        # 2. Dibujar el fondo tileado en la superficie de la cámara (RESTAURADO)
        try: # Añadido try-except para el dibujado del fondo
            if textura_fondo and self.surface:
                # `offset_fondo_x/y` calcula cuánto se ha desplazado el fondo debido al movimiento de la cámara.
                # El operador módulo (%) asegura que el offset siempre esté dentro del rango de una tile,
                # creando un efecto de scroll infinito y correcto para el tileado.
                offset_fondo_x = -self.cam_mundo_x % ancho_textura_tile
                offset_fondo_y = -self.cam_mundo_y % alto_textura_tile

                # Bucles para dibujar los tiles del fondo. Se dibuja un poco más allá de los bordes
                # de self.ancho_vista_mundo y self.alto_vista_mundo para asegurar que no haya espacios vacíos
                # al hacer el scroll, especialmente con el offset.
                for x_tile in range(int(-ancho_textura_tile + offset_fondo_x), int(self.ancho_vista_mundo + ancho_textura_tile), ancho_textura_tile):
                    for y_tile in range(int(-alto_textura_tile + offset_fondo_y), int(self.alto_vista_mundo + alto_textura_tile), alto_textura_tile):
                        # Añadida comprobación para textura_fondo.get_width/height > 0 y existencia de textura_fondo
                        if textura_fondo.get_width() > 0 and textura_fondo.get_height() > 0:
                            self.surface.blit(textura_fondo, (x_tile, y_tile))
                        # else: # Podríamos loguear un error si la textura del fondo tiene dimensiones 0
                            # print("Advertencia CAMARA: Textura de fondo con dimensiones 0x0 no se dibujará.") 
            elif not self.surface:
                print("ERROR CAMARA: self.surface es None antes de dibujar fondo.")
            elif not textura_fondo:
                print("ERROR CAMARA: textura_fondo es None antes de dibujar fondo.")
        except Exception as e:
            print(f"ERROR CAMARA: Excepción al dibujar el fondo tileado: {e}")

        # 3. Dibujar todos los sprites del `grupo_otros_sprites` (ej: árboles) (RESTAURADO)
        try: # Añadido try-except para el dibujado de los sprites
            if grupo_otros_sprites and self.surface:
                for sprite in grupo_otros_sprites:
                    if sprite and hasattr(sprite, 'image') and hasattr(sprite, 'rect'):
                        sprite_cam_x = sprite.rect.x - self.cam_mundo_x
                        sprite_cam_y = sprite.rect.y - self.cam_mundo_y
                        self.surface.blit(sprite.image, (sprite_cam_x, sprite_cam_y))

                        # DEBUG: Dibujar rect/hitbox de los sprites (árboles)
                        if settings.DEBUG_VER_HITBOXES:
                            # Si el sprite tiene un hitbox personalizado, lo usamos. Si no, usamos su rect.
                            debug_rect_a_dibujar = sprite.hitbox if hasattr(sprite, 'hitbox') else sprite.rect
                            
                            debug_rect_cam_x = debug_rect_a_dibujar.x - self.cam_mundo_x
                            debug_rect_cam_y = debug_rect_a_dibujar.y - self.cam_mundo_y
                            pygame.draw.rect(self.surface, settings.VERDE, # Color VERDE para estos
                                             (debug_rect_cam_x, debug_rect_cam_y, debug_rect_a_dibujar.width, debug_rect_a_dibujar.height), 1)
                    else:
                        print("ERROR CAMARA: Sprite en grupo_otros_sprites o sus atributos (image/rect) es None.")
            elif not self.surface:
                 print("ERROR CAMARA: self.surface es None antes de dibujar grupo_otros_sprites.")
        except Exception as e:
            print(f"ERROR CAMARA: Excepción al dibujar grupo_otros_sprites: {e}")

        # DIBUJAR ENEMIGOS (similar a grupo_otros_sprites)
        try:
            if grupo_enemigos and self.surface:
                for enemigo_sprite in grupo_enemigos: # Iterar sobre el nuevo grupo
                    if enemigo_sprite and hasattr(enemigo_sprite, 'image') and hasattr(enemigo_sprite, 'rect'):
                        sprite_cam_x = enemigo_sprite.rect.x - self.cam_mundo_x
                        sprite_cam_y = enemigo_sprite.rect.y - self.cam_mundo_y
                        self.surface.blit(enemigo_sprite.image, (sprite_cam_x, sprite_cam_y))

                        # DEBUG: Dibujar rect/hitbox de los enemigos
                        if settings.DEBUG_VER_HITBOXES:
                            debug_rect_a_dibujar = enemigo_sprite.hitbox if hasattr(enemigo_sprite, 'hitbox') else enemigo_sprite.rect
                            
                            debug_rect_cam_x = debug_rect_a_dibujar.x - self.cam_mundo_x
                            debug_rect_cam_y = debug_rect_a_dibujar.y - self.cam_mundo_y
                            pygame.draw.rect(self.surface, settings.VERDE, # Mismo color VERDE para debug de rects
                                             (debug_rect_cam_x, debug_rect_cam_y, debug_rect_a_dibujar.width, debug_rect_a_dibujar.height), 1)
                    else:
                        print("ERROR CAMARA: Sprite en grupo_enemigos o sus atributos (image/rect) es None.")
            elif not self.surface:
                 print("ERROR CAMARA: self.surface es None antes de dibujar grupo_enemigos.")
        except Exception as e:
            print(f"ERROR CAMARA: Excepción al dibujar grupo_enemigos: {e}")

        # 4. Dibujar al jugador (RESTAURADO)
        try: # Añadido try-except para el dibujado del jugador
            if jugador and hasattr(jugador, 'image') and hasattr(jugador, 'rect') and self.surface:
                jugador_cam_x = jugador.rect.x - self.cam_mundo_x
                jugador_cam_y = jugador.rect.y - self.cam_mundo_y
                self.surface.blit(jugador.image, (jugador_cam_x, jugador_cam_y))
            else:
                print("ERROR CAMARA: Jugador o sus atributos (image/rect) o self.surface es None al intentar dibujar jugador.")
        except Exception as e:
            print(f"ERROR CAMARA: Excepción al dibujar al jugador: {e}")

        # DEBUG: Dibujar hitbox del jugador (AHORA CONDICIONAL)
        if settings.DEBUG_VER_HITBOXES: # Solo si la depuración está activa
            try:
                if hasattr(jugador, 'hitbox') and self.surface: # Comprobar si el jugador tiene hitbox y la superficie existe
                    # Calcular la posición del hitbox RELATIVA a la vista de la cámara.
                    hitbox_cam_x = jugador.hitbox.x - self.cam_mundo_x
                    hitbox_cam_y = jugador.hitbox.y - self.cam_mundo_y
                    
                    # Dibuja un rectángulo rojo delgado (grosor 1) que representa el hitbox.
                    pygame.draw.rect(self.surface, settings.ROJO, 
                                     (hitbox_cam_x, hitbox_cam_y, jugador.hitbox.width, jugador.hitbox.height), 1)
                # else: Podríamos añadir un print si no se dibuja el hitbox por no tener el atributo o self.surface
                #   if not hasattr(jugador, 'hitbox'): print("DEBUG CAMARA: Jugador no tiene atributo 'hitbox'.")
                #   if not self.surface: print("DEBUG CAMARA: self.surface es None, no se puede dibujar hitbox.")
            except Exception as e:
                print(f"ERROR CAMARA: Excepción al dibujar el hitbox del jugador: {e}")

        # 5. Escalar la `self.surface` (la superficie de la cámara que contiene toda la escena dibujada)
        # a las dimensiones de la pantalla_destino_final. Esto aplica el zoom.
        try:
            if self.surface: # Solo escalar si self.surface es válida
                dimensiones_pantalla_final = pantalla_destino_final.get_size()
                pygame.transform.scale(self.surface, dimensiones_pantalla_final, pantalla_destino_final)
            # else: ya se manejó arriba, no es necesario hacer nada más aquí.
        except Exception as e:
            print(f"ERROR CAMARA: Excepción al escalar self.surface a pantalla_destino_final: {e}")
            AZUL_PRUEBA = (0,0,255) # Re-definir por si acaso
            pantalla_destino_final.fill(AZUL_PRUEBA)