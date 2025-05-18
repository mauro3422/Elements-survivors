import pygame
import settings # Importa todas las constantes de settings.py (ANCHO_PANTALLA, FPS, RUTA_ASSETS, etc.)
from jugador import Jugador # Importa la clase Jugador desde jugador.py
from entorno import Arbol   # Importa la clase Arbol desde entorno.py
from enemigo import Enemigo # <--- IMPORTAR ENEMIGO
from camara import Camara   # Importa la clase Camara desde camara.py
import os                   # Módulo del sistema operativo, usado aquí para os.path.join
import random               # Para generar números aleatorios (posiciones de los árboles)
import math                 # Para usar funciones matemáticas


# --- Inicialización de Pygame ---
pygame.init() # ¡Fundamental! Inicializa todos los módulos de Pygame (sonido, gráficos, etc.)
pygame.font.init() # Inicializar explícitamente el módulo de fuentes

# --- Configuración de la Pantalla Principal ---
# Crea la ventana principal del juego con las dimensiones de settings.py
pantalla = pygame.display.set_mode((settings.ANCHO_PANTALLA, settings.ALTO_PANTALLA))
# Establece el título que aparecerá en la barra de la ventana.
pygame.display.set_caption("Avatar Survivors") # ¡Puedes cambiar este nombre!

# --- Variables de Zoom Dinámico ---
factor_zoom_actual = settings.FACTOR_ZOOM_INICIAL
# Calculamos las dimensiones iniciales de la vista de la cámara
camara_ancho_vista_actual = settings.ANCHO_PANTALLA / factor_zoom_actual
camara_alto_vista_actual = settings.ALTO_PANTALLA / factor_zoom_actual

# --- Creación de la Cámara ---
# Se crea una instancia de la clase Camara.
# Se le pasan las dimensiones de la "vista" que la cámara tendrá del mundo ANTES del zoom.
# Estas dimensiones (CAMARA_ANCHO, CAMARA_ALTO) vienen de settings.py y dependen del FACTOR_ZOOM.
camara = Camara(camara_ancho_vista_actual, camara_alto_vista_actual)

# --- Carga de Recursos (Texturas, Sprites) ---

# Cargar textura de fondo (el tile de tierra)
try:
    # os.path.join une partes de una ruta de forma inteligente.
    # Se carga la imagen T_Tierra32x32.png desde assets/scenary/texture/
    textura_fondo_original = pygame.image.load(os.path.join(settings.RUTA_ASSETS, "scenary", "texture", "T_Tierra32x32.png")).convert()
    # .convert() optimiza la imagen para dibujarla más rápido (pierde transparencia, bien para fondo opaco).
    ANCHO_TEXTURA_FONDO, ALTO_TEXTURA_FONDO = textura_fondo_original.get_size() # Obtiene las dimensiones del tile.
except pygame.error as e:
    # Si hay un error al cargar, se imprime el error y se usa un fallback.
    print(f"Error al cargar la textura del fondo: {e}")
    textura_fondo_original = pygame.Surface((32,32)); textura_fondo_original.fill(settings.NEGRO)
    ANCHO_TEXTURA_FONDO, ALTO_TEXTURA_FONDO = 32,32 # Dimensiones del fallback.

# Crear instancia del Jugador
# Se le pasa su posición inicial (centro de la pantalla), y la RUTA_ASSETS.
# El (-16) es para ajustar la posición inicial basado en un tamaño de sprite de 32x32, para centrarlo.
jugador = Jugador(settings.ANCHO_PANTALLA // 2 - 16, 
                  settings.ALTO_PANTALLA // 2 - 16, 
                  settings.RUTA_ASSETS)

# Crear Árboles
arboles_sprites = pygame.sprite.Group() # Un grupo para manejar todos los árboles.
                                       # Facilita actualizarlos y dibujarlos todos a la vez.

# Definir el tamaño esperado de los árboles después del reescalado en entorno.py
ANCHO_ARBOL_ESCALADO = 45 
ALTO_ARBOL_ESCALADO = 45

try:
    # Ya no necesitamos cargar la imagen aquí solo para las dimensiones,
    # ya que las conocemos por el reescalado en la clase Arbol.
    # Sin embargo, si quisiéramos verificar que el archivo base existe, podríamos hacerlo.
    # Por simplicidad, ahora usaremos las dimensiones escaladas directamente.

    for _ in range(3):
        spawn_x = random.randint(0, settings.ANCHO_PANTALLA - ANCHO_ARBOL_ESCALADO) 
        spawn_y = random.randint(0, settings.ALTO_PANTALLA - ALTO_ARBOL_ESCALADO)
        # Asegurarse de que los árboles no spawneen encima del jugador inicialmente (simple chequeo)
        # Esto es muy básico, se podría mejorar para evitar solapamientos con otros árboles también.
        rect_arbol_propuesto = pygame.Rect(spawn_x, spawn_y, ANCHO_ARBOL_ESCALADO, ALTO_ARBOL_ESCALADO)
        if not rect_arbol_propuesto.colliderect(jugador.rect):
            arbol = Arbol(spawn_x, spawn_y, settings.RUTA_ASSETS)
            arboles_sprites.add(arbol)
        # else: podrías reintentar buscar una nueva posición o simplemente no spawnear este árbol
except Exception as e: # Captura una excepción más general por si algo más falla aquí
    print(f"Error al crear árboles: {e}")

# Crear Enemigos
enemigos_sprites = pygame.sprite.Group() # Grupo para manejar todos los enemigos

# Configuración para el spawn de enemigos
NUMERO_ENEMIGOS_A_SPAWNEAR = 5
RADIO_SPAWN_ENEMIGO_MIN = 50  # Píxeles mínimos desde el centro del jugador
RADIO_SPAWN_ENEMIGO_MAX = 150 # Píxeles máximos desde el centro del jugador

for _ in range(NUMERO_ENEMIGOS_A_SPAWNEAR):
    # Elegir un ángulo aleatorio y una distancia aleatoria dentro del rango
    angulo = random.uniform(0, 2 * math.pi) # Ángulo en radianes
    radio = random.uniform(RADIO_SPAWN_ENEMIGO_MIN, RADIO_SPAWN_ENEMIGO_MAX)
    
    # Calcular la posición relativa al jugador
    offset_x = radio * math.cos(angulo)
    offset_y = radio * math.sin(angulo)
    
    # Posición absoluta del enemigo
    # Asegúrate de que el jugador ya esté inicializado para usar jugador.rect.centerx/centery
    pos_enemigo_x = jugador.rect.centerx + offset_x
    pos_enemigo_y = jugador.rect.centery + offset_y

    try:
        nuevo_enemigo = Enemigo(pos_enemigo_x, pos_enemigo_y) # Usa el nombre de archivo por defecto "chicken.png"
        enemigos_sprites.add(nuevo_enemigo)
    except Exception as e:
        print(f"Error al crear un enemigo: {e}")

# --- Reloj del Juego ---
# Se usa para controlar los FPS (fotogramas por segundo).
reloj = pygame.time.Clock()

# --- Configuración del HUD de Depuración ---
fuente_hud = pygame.font.SysFont("Arial", 18) # O "Consolas", "Courier New"

# --- Bucle Principal del Juego --- 
ejecutando = True # Variable que controla si el bucle sigue o el juego termina.
while ejecutando:
    zoom_cambio = False # Flag para saber si el zoom cambió en este fotograma
    # --- 1. Manejo de Eventos ---
    # pygame.event.get() obtiene una lista de todos los eventos que han ocurrido.
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT: # Si el usuario cerró la ventana...
            ejecutando = False       # ...se pone `ejecutando` a False para salir del bucle.
        if evento.type == pygame.MOUSEWHEEL: # Evento de la rueda del mouse
            # evento.y es positivo si la rueda va "hacia arriba/adelante" (zoom in)
            # y negativo si va "hacia abajo/atrás" (zoom out)
            if evento.y > 0: # Zoom in
                factor_zoom_actual += settings.FACTOR_ZOOM_PASO
            elif evento.y < 0: # Zoom out
                factor_zoom_actual -= settings.FACTOR_ZOOM_PASO
            
            # Aplicar límites al zoom
            factor_zoom_actual = max(settings.FACTOR_ZOOM_MIN, factor_zoom_actual)
            factor_zoom_actual = min(settings.FACTOR_ZOOM_MAX, factor_zoom_actual)
            zoom_cambio = True
        
        # Evento para el ataque del jugador
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE:
                jugador.atacar(enemigos_sprites)
            
            # Teclas para ajustar parámetros del ataque del jugador (HUD)
            if settings.DEBUG_VER_HITBOXES: # Solo si estamos en modo debug
                incremento = settings.INCREMENTO_AJUSTE_DEBUG
                if evento.key == pygame.K_F1:
                    jugador.modificar_ataque_offset(-incremento)
                if evento.key == pygame.K_F2:
                    jugador.modificar_ataque_offset(incremento)
                if evento.key == pygame.K_F3:
                    jugador.modificar_ataque_extension(-incremento)
                if evento.key == pygame.K_F4:
                    jugador.modificar_ataque_extension(incremento)
                if evento.key == pygame.K_F5:
                    jugador.modificar_ataque_grosor(-incremento)
                if evento.key == pygame.K_F6:
                    jugador.modificar_ataque_grosor(incremento)
                if evento.key == pygame.K_F12: # Tecla para guardar configuración de ataque
                    jugador.guardar_config_ataque_actual()

    if zoom_cambio:
        # Recalcular las dimensiones de la vista de la cámara basadas en el nuevo zoom
        nuevo_camara_ancho_vista = settings.ANCHO_PANTALLA / factor_zoom_actual
        nuevo_camara_alto_vista = settings.ALTO_PANTALLA / factor_zoom_actual
        # Actualizar la cámara con las nuevas dimensiones
        camara.actualizar_dimensiones_vista(nuevo_camara_ancho_vista, nuevo_camara_alto_vista)
        # print(f"Zoom: {factor_zoom_actual:.2f}, Vista Cámara: {nuevo_camara_ancho_vista:.0f}x{nuevo_camara_alto_vista:.0f}") # Para depuración

    # --- 2. Actualizaciones de Lógica del Juego ---
    # Obtener el estado de todas las teclas del teclado.
    teclas = pygame.key.get_pressed()
    
    # Actualizar al jugador
    jugador.actualizar_movimiento(teclas, arboles_sprites)
    jugador.actualizar_animacion()
    
    # Actualizar todos los sprites en el grupo `arboles_sprites`.
    # Esto llamará al método `update()` de cada `Arbol`.
    arboles_sprites.update()

    # Actualizar enemigos
    enemigos_sprites.update(jugador.rect) # Llama al método update() de cada Enemigo, pasando el rect del jugador

    # Actualizar estado del ataque con espada del jugador
    jugador.actualizar_ataque_espada(enemigos_sprites)

    # --- COLISIONES JUGADOR vs ENEMIGOS ---
    # Iteramos manualmente para usar el hitbox del jugador y el rect del enemigo.
    # Esto permite que el hitbox del jugador sea más preciso que su rect general.
    # ahora = pygame.time.get_ticks() # Ya no es necesario aquí si el jugador ataca explícitamente

    for enemigo in enemigos_sprites:
        if jugador.hitbox.colliderect(enemigo.rect):
            # El enemigo intenta atacar al jugador (daño por contacto)
            # El jugador ya tiene un cooldown interno en su método recibir_dano()
            jugador.recibir_dano(enemigo.dano_ataque)
            
            # Ya no hacemos que el jugador dañe automáticamente al enemigo aquí.
            # El daño del jugador se maneja a través del método jugador.atacar()
            
            # Consideraciones adicionales:
            # - Empuje: Podríamos mover ligeramente al jugador o al enemigo.
            # - Efectos visuales: Chispas, sonido de golpe.
            # - Si el enemigo muere por este golpe, se eliminará en su próximo enemigo.update().
            # - Si el jugador muere, su método morir() se llamará.

    # Actualizar la posición de la cámara para que siga al jugador.
    camara.actualizar_posicion(jugador.rect)

    # --- 3. Renderizado / Dibujado ---
    camara.dibujar_escena(pantalla,             
                          textura_fondo_original, 
                          ANCHO_TEXTURA_FONDO, ALTO_TEXTURA_FONDO,
                          jugador,                
                          arboles_sprites,
                          enemigos_sprites)
    
    # --- Dibujar HUD de Depuración (si está activado) ---
    if settings.DEBUG_VER_HITBOXES:
        y_offset_hud = 10
        textos_hud = [
            f"Offset Ataque (F1/F2): {jugador.ataque_offset_distancia}",
            f"Extension Ataque (F3/F4): {jugador.ataque_extension}",
            f"Grosor Ataque (F5/F6): {jugador.ataque_grosor}",
            f"Zoom (Rueda): {factor_zoom_actual:.2f}",
            f"Guardar config: F12"
        ]
        for i, texto_str in enumerate(textos_hud):
            texto_surface = fuente_hud.render(texto_str, True, settings.COLOR_HUD_TEXTO)
            pantalla.blit(texto_surface, (10, y_offset_hud + i * 20))

    pygame.display.flip()

    # --- 4. Control de FPS ---
    # `reloj.tick(settings.FPS)` hace una pausa para que el juego no corra
    # a más de los FPS definidos.
    reloj.tick(settings.FPS)

# --- Finalización de Pygame ---
# Cuando el bucle `while ejecutando:` termina.
pygame.quit() # Desinicializa todos los módulos de Pygame.
# import sys # Opcional: forzar salida del programa
# sys.exit()