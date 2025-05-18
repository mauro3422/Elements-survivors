import pygame
import os
import settings # Necesario para RUTA_ASSETS si no se usa AssetManager, pero ahora sí

class Arbol(pygame.sprite.Sprite):
    def __init__(self, x, y, asset_manager_instance):
        super().__init__()
        self.asset_manager = asset_manager_instance
        self.animaciones = {}
        self._cargar_animaciones()

        self.estado_animacion = "idle" # Solo un estado por ahora
        self.indice_fotograma = 0
        self.tiempo_ultimo_fotograma = pygame.time.get_ticks()
        self.retraso_animacion = 200 # Milisegundos por fotograma, ajustar según sea necesario

        if self.animaciones.get(self.estado_animacion) and self.animaciones[self.estado_animacion]:
            self.image_original = self.animaciones[self.estado_animacion][self.indice_fotograma]
        else:
            # Fallback si la animación no se carga
            self.image_original = pygame.Surface((32,32))
            self.image_original.fill(settings.ROJO_ERROR_ASSET if hasattr(settings, 'ROJO_ERROR_ASSET') else (255,0,0))
            print(f"Error: Animación '{self.estado_animacion}' no encontrada para el Árbol. Usando placeholder.")

        # Escalar la imagen (ejemplo de escalado, puedes ajustarlo o quitarlo)
        self.ancho_escalado = 45 
        self.alto_escalado = 45  
        self.image = pygame.transform.scale(self.image_original, (self.ancho_escalado, self.alto_escalado))

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # --- Hitbox del Árbol ---
        self.hitbox_offset_x = 5  
        self.hitbox_offset_y = 10 
        
        hb_ancho = self.rect.width - (2 * self.hitbox_offset_x)
        hb_alto = self.rect.height - (2 * self.hitbox_offset_y) 
        
        hb_ancho = max(1, hb_ancho)
        hb_alto = max(1, hb_alto)

        self.hitbox = pygame.Rect(0, 0, hb_ancho, hb_alto)
        self._actualizar_posicion_hitbox()

    def _cargar_animaciones(self):
        """Carga los fotogramas para las animaciones del árbol usando AssetManager."""
        self.animaciones["idle"] = []
        for i in range(1, 7): # Cargar 6 fotogramas: tree_frame_1 a tree_frame_6
            clave_asset = f"tree_frame_{i}"
            imagen = self.asset_manager.get_image(clave_asset)
            self.animaciones["idle"].append(imagen)
        
        if not self.animaciones["idle"] or all(img.get_width() == 32 and img.get_height() == 32 for img in self.animaciones["idle"]):
            # Esto es una heurística para detectar si solo se cargaron placeholders
            # Podría mejorarse si AssetManager devuelve una bandera específica o si el placeholder tiene un color único
            print("ADVERTENCIA: No se cargaron fotogramas válidos para la animación 'idle' del Árbol o solo se cargaron placeholders.")
            # Asegurarse de que haya al menos un placeholder si todo falló gravemente.
            if not self.animaciones["idle"]:
                placeholder_surface = pygame.Surface((32,32))
                placeholder_surface.fill(settings.ROJO_ERROR_ASSET if hasattr(settings, 'ROJO_ERROR_ASSET') else (255,0,0))
                self.animaciones["idle"] = [placeholder_surface]

    def _actualizar_posicion_hitbox(self):
        """Actualiza la posición del hitbox basándose en el rect principal."""
        self.hitbox.topleft = (
            self.rect.x + self.hitbox_offset_x,
            self.rect.y + self.hitbox_offset_y
        )

    def update(self):
        """Actualiza la animación del árbol."""
        ahora = pygame.time.get_ticks()
        if self.animaciones.get(self.estado_animacion) and self.animaciones[self.estado_animacion]:
            if ahora - self.tiempo_ultimo_fotograma > self.retraso_animacion:
                self.tiempo_ultimo_fotograma = ahora
                self.indice_fotograma = (self.indice_fotograma + 1) % len(self.animaciones[self.estado_animacion])
                self.image_original = self.animaciones[self.estado_animacion][self.indice_fotograma]
                # Re-escalar la nueva imagen original
                self.image = pygame.transform.scale(self.image_original, (self.ancho_escalado, self.alto_escalado))
        # No es necesario actualizar el rect aquí ya que la posición del árbol es estática.
        # El hitbox tampoco necesita actualizarse a menos que el tamaño del sprite cambie drásticamente con la animación,
        # lo cual no es común para este tipo de objeto.

    def dibujar_hitbox(self, superficie_camara, cam_mundo_x, cam_mundo_y):
        """
        Dibuja el hitbox del árbol en coordenadas de cámara para depuración.
        Este método sería llamado por la Cámara si se implementa.
        """
        if settings.DEBUG_VER_HITBOXES and hasattr(self, 'hitbox'):
            # Convertir coordenadas del hitbox del mundo a coordenadas de la cámara/pantalla
            hitbox_cam_x = self.hitbox.x - cam_mundo_x
            hitbox_cam_y = self.hitbox.y - cam_mundo_y
            
            # Crear un Rect temporal para dibujar en la posición correcta de la cámara
            rect_a_dibujar_en_cam = pygame.Rect(hitbox_cam_x, hitbox_cam_y, self.hitbox.width, self.hitbox.height)
            
            # Dibujar el hitbox en la superficie de la cámara
            pygame.draw.rect(superficie_camara, settings.VERDE_DEBUG, rect_a_dibujar_en_cam, 1) # Borde delgado