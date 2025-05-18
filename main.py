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
ejecutando = True 
perfiles_disponibles_nombres = list(jugador.perfiles_de_ataque.keys()) # Obtener nombres para selección

while ejecutando:
    zoom_cambio = False
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False
        if evento.type == pygame.MOUSEWHEEL: 
            if evento.y > 0: factor_zoom_actual += settings.FACTOR_ZOOM_PASO
            elif evento.y < 0: factor_zoom_actual -= settings.FACTOR_ZOOM_PASO
            factor_zoom_actual = max(settings.FACTOR_ZOOM_MIN, min(settings.FACTOR_ZOOM_MAX, factor_zoom_actual))
            zoom_cambio = True
        
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE:
                jugador.atacar(enemigos_sprites) # El argumento enemigos_sprites ya no se usa en atacar directamente
            
            # Teclas para cambiar perfil de ataque activo
            if evento.key == pygame.K_PAGEUP:
                if perfiles_disponibles_nombres:
                    indice_actual = perfiles_disponibles_nombres.index(jugador.nombre_perfil_ataque_activo)
                    nuevo_indice = (indice_actual - 1 + len(perfiles_disponibles_nombres)) % len(perfiles_disponibles_nombres)
                    jugador.seleccionar_perfil_ataque(perfiles_disponibles_nombres[nuevo_indice])
            if evento.key == pygame.K_PAGEDOWN:
                if perfiles_disponibles_nombres:
                    indice_actual = perfiles_disponibles_nombres.index(jugador.nombre_perfil_ataque_activo)
                    nuevo_indice = (indice_actual + 1) % len(perfiles_disponibles_nombres)
                    jugador.seleccionar_perfil_ataque(perfiles_disponibles_nombres[nuevo_indice])
            
            # Teclas para ajustar parámetros del perfil de ataque ACTIVO (HUD)
            if settings.DEBUG_VER_HITBOXES: 
                if evento.key == pygame.K_F1: jugador.modificar_ataque_offset(-settings.INCREMENTO_AJUSTE_DEBUG)
                if evento.key == pygame.K_F2: jugador.modificar_ataque_offset(settings.INCREMENTO_AJUSTE_DEBUG)
                if evento.key == pygame.K_F3: jugador.modificar_ataque_extension(-settings.INCREMENTO_AJUSTE_DEBUG)
                if evento.key == pygame.K_F4: jugador.modificar_ataque_extension(settings.INCREMENTO_AJUSTE_DEBUG)
                if evento.key == pygame.K_F5: jugador.modificar_ataque_grosor(-settings.INCREMENTO_AJUSTE_DEBUG)
                if evento.key == pygame.K_F6: jugador.modificar_ataque_grosor(settings.INCREMENTO_AJUSTE_DEBUG)
                if evento.key == pygame.K_F7: jugador.modificar_duracion_ataque_total(-settings.INCREMENTO_DURACION_DEBUG)
                if evento.key == pygame.K_F8: jugador.modificar_duracion_ataque_total(settings.INCREMENTO_DURACION_DEBUG)
                if evento.key == pygame.K_F12: 
                    jugador.guardar_todos_perfiles_ataque()
                    # Actualizar la lista de perfiles disponibles por si se creó uno nuevo (aunque no se hace ahora)
                    perfiles_disponibles_nombres = list(jugador.perfiles_de_ataque.keys())

    if zoom_cambio:
        nuevo_camara_ancho_vista = settings.ANCHO_PANTALLA / factor_zoom_actual
        nuevo_camara_alto_vista = settings.ALTO_PANTALLA / factor_zoom_actual
        camara.actualizar_dimensiones_vista(nuevo_camara_ancho_vista, nuevo_camara_alto_vista)

    teclas = pygame.key.get_pressed()
    jugador.actualizar_movimiento(teclas, arboles_sprites)
    jugador.actualizar_animacion()
    jugador.actualizar_ataque(enemigos_sprites) # Nombre de método actualizado
    
    arboles_sprites.update()
    enemigos_sprites.update(jugador.rect)

    for enemigo in enemigos_sprites:
        if jugador.hitbox.colliderect(enemigo.rect):
            jugador.recibir_dano(enemigo.dano_ataque)

    camara.actualizar_posicion(jugador.rect)
    camara.dibujar_escena(pantalla, textura_fondo_original, ANCHO_TEXTURA_FONDO, ALTO_TEXTURA_FONDO,
                          jugador, arboles_sprites, enemigos_sprites)
    
    # --- Dibujar HUD de Depuración (si está activado) ---
    if settings.DEBUG_VER_HITBOXES:
        y_offset_hud = 10
        # Obtener parámetros del perfil activo para el HUD
        offset_hud = jugador.get_parametro_ataque_activo("offset_distancia", "N/A")
        extension_hud = jugador.get_parametro_ataque_activo("extension", "N/A")
        grosor_hud = jugador.get_parametro_ataque_activo("grosor", "N/A")
        duracion_total_hud = jugador.get_parametro_ataque_activo("duracion_total_ms", "N/A")
        dano_mod_hud = jugador.get_parametro_ataque_activo("dano_modificador", "N/A")
        cd_mod_hud = jugador.get_parametro_ataque_activo("cooldown_modificador", "N/A")

        textos_hud = [
            f"Perfil Activo (PgUp/PgDn): {jugador.nombre_perfil_ataque_activo}",
            f"Offset (F1/F2): {offset_hud}",
            f"Extension (F3/F4): {extension_hud}",
            f"Grosor (F5/F6): {grosor_hud}",
            f"Duracion Total (F7/F8): {duracion_total_hud}ms",
            f"  Dur Segmento: {jugador.duracion_segmento_barrido_activo:.2f}ms",
            f"  Dano Mod: {dano_mod_hud:.2f}",
            f"  CD Mod: {cd_mod_hud:.2f}",
            f"Zoom (Rueda): {factor_zoom_actual:.2f}",
            f"Guardar Perfiles: F12"
        ]
        for i, texto_str in enumerate(textos_hud):
            texto_surface = fuente_hud.render(texto_str, True, settings.COLOR_HUD_TEXTO)
            pantalla.blit(texto_surface, (10, y_offset_hud + i * 20))

    pygame.display.flip()
    reloj.tick(settings.FPS)

pygame.quit()