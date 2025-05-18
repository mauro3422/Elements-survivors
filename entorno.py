import pygame
import os 
# settings no se importa directamente ya que RUTA_ASSETS se pasa al constructor.

class Arbol(pygame.sprite.Sprite): # Hereda de pygame.sprite.Sprite
    def __init__(self, x, y, ruta_assets):
        # --- Constructor de la clase Arbol ---
        # Args:
        #     x (int): Posición en el eje X del árbol en el mundo del juego.
        #     y (int): Posición en el eje Y del árbol en el mundo del juego.
        #     ruta_assets (str): Ruta a la carpeta principal de 'assets'.
        
        super().__init__() # Llama al constructor de la clase padre (pygame.sprite.Sprite)

        self.ruta_assets = ruta_assets
        self.animacion_idle = [] # Lista para guardar los fotogramas de la animación "idle" (reposo/viento)
        self._cargar_animaciones()   # Llama al método para cargar las imágenes

        # --- Estado de Animación Inicial ---
        self.indice_fotograma = 0
        if self.animacion_idle: # Comprueba si se cargaron fotogramas
            self.image = self.animacion_idle[self.indice_fotograma] # Imagen actual del sprite
            self.rect = self.image.get_rect() # Rectángulo del sprite
            self.rect.x = x
            self.rect.y = y
        else:
            # Fallback: si no se cargaron las imágenes, crea un placeholder verde
            # Esto evita que el juego crashee si faltan los sprites del árbol.
            print(f"Error: Animación 'idle' no encontrada para el Arbol en ({x},{y}). Usando placeholder.")
            self.image = pygame.Surface((45, 45)) # Placeholder ahora de 45x45
            self.image.fill((0,255,0)) # Verde brillante como placeholder
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y
            
        # --- Atributos de Animación ---
        self.tiempo_ultimo_fotograma = pygame.time.get_ticks() # Para controlar la velocidad de la animación
        # Retraso más largo para el árbol, para una animación de viento más sutil
        self.retraso_animacion = 200 # Milisegundos entre fotogramas de la animación del árbol

    def _cargar_animaciones(self):
        # --- Carga los fotogramas para la animación del árbol. ---
        ruta_anim = os.path.join(self.ruta_assets, "scenary", "animaciones", "tree")
        # self.animacion_idle = [] # Se inicializa en __init__
        
        nuevo_ancho_arbol = 45 # 32 * 1.4 redondeado
        nuevo_alto_arbol = 45  # 32 * 1.4 redondeado

        # Bucle para cargar las imágenes (Tree_idle_1.png a Tree_idle_6.png)
        for i in range(1, 7): # Son 6 fotogramas
            img_path = os.path.join(ruta_anim, f"Tree_idle_{i}.png")
            try:
                imagen_original = pygame.image.load(img_path).convert_alpha() # Carga con transparencia
                # Reescalar la imagen a un 40% más grande
                imagen_reescalada = pygame.transform.scale(imagen_original, (nuevo_ancho_arbol, nuevo_alto_arbol))
                self.animacion_idle.append(imagen_reescalada) # Añade a la lista de fotogramas
            except pygame.error as e:
                print(f"Error al cargar o reescalar la imagen de animación del árbol {img_path}: {e}")
                # Si falla una imagen, no se añade y la animación tendrá menos fotogramas (o ninguno).

        # Si después de intentar cargar, la lista animacion_idle está vacía,
        # se crea un placeholder para evitar errores.
        if not self.animacion_idle:
            print("CRITICAL: No se cargaron fotogramas para la animación idle del Arbol. Usando placeholder único.")
            placeholder = pygame.Surface((nuevo_ancho_arbol, nuevo_alto_arbol)); placeholder.fill((0,255,0))
            self.animacion_idle = [placeholder] # Asegura que haya al menos un fotograma.


    def update(self):
        # --- Actualiza la animación del árbol. ---
        # Este método es llamado automáticamente por `grupo_sprites.update()` en main.py
        # para cada Arbol en el grupo.
        
        ahora = pygame.time.get_ticks()
        if ahora - self.tiempo_ultimo_fotograma > self.retraso_animacion:
            self.tiempo_ultimo_fotograma = ahora
            # Solo animar si hay fotogramas (la lista no debería estar vacía por el fallback)
            if self.animacion_idle: 
                self.indice_fotograma = (self.indice_fotograma + 1) % len(self.animacion_idle)
                self.image = self.animacion_idle[self.indice_fotograma]