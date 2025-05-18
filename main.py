import pygame
import settings # Importa todas las constantes de settings.py (ANCHO_PANTALLA, FPS, RUTA_ASSETS, etc.)
from jugador import Jugador # Importa la clase Jugador desde jugador.py
from entorno import Arbol   # Importa la clase Arbol desde entorno.py
from enemigo import Enemigo # <--- IMPORTAR ENEMIGO
from camara import Camara   # Importa la clase Camara desde camara.py
from hud import DebugHUD    # <--- IMPORTAR DebugHUD
import os                   # Módulo del sistema operativo, usado aquí para os.path.join
import random               # Para generar números aleatorios (posiciones de los árboles)
import math                 # Para usar funciones matemáticas

def inicializar_juego():
    """Inicializa Pygame, la pantalla, y otros elementos básicos del juego."""
    pygame.init()
    pygame.font.init()
    pantalla = pygame.display.set_mode((settings.ANCHO_PANTALLA, settings.ALTO_PANTALLA))
    pygame.display.set_caption("Avatar Survivors")
    reloj = pygame.time.Clock()
    
    try:
        textura_fondo_original = pygame.image.load(os.path.join(settings.RUTA_ASSETS, "scenary", "texture", "T_Tierra32x32.png")).convert()
        ancho_textura_fondo, alto_textura_fondo = textura_fondo_original.get_size()
    except pygame.error as e:
        print(f"Error al cargar la textura del fondo: {e}")
        textura_fondo_original = pygame.Surface((32,32)); textura_fondo_original.fill(settings.NEGRO)
        ancho_textura_fondo, alto_textura_fondo = 32,32
        
    fuente_hud_obj = pygame.font.SysFont("Arial", 18)
    
    return pantalla, reloj, textura_fondo_original, ancho_textura_fondo, alto_textura_fondo, fuente_hud_obj

def crear_entidades_juego():
    """Crea y devuelve el jugador, los árboles y los enemigos."""
    jugador = Jugador(settings.ANCHO_PANTALLA // 2 - 16, 
                      settings.ALTO_PANTALLA // 2 - 16, 
                      settings.RUTA_ASSETS)

    arboles_sprites = pygame.sprite.Group()
    ANCHO_ARBOL_ESCALADO = 45 
    ALTO_ARBOL_ESCALADO = 45
    try:
        for _ in range(3): #settings.NUM_ARBOLES_INICIALES
            spawn_x = random.randint(0, settings.ANCHO_MUNDO_JUEGO - ANCHO_ARBOL_ESCALADO) 
            spawn_y = random.randint(0, settings.ALTO_MUNDO_JUEGO - ALTO_ARBOL_ESCALADO)
            rect_arbol_propuesto = pygame.Rect(spawn_x, spawn_y, ANCHO_ARBOL_ESCALADO, ALTO_ARBOL_ESCALADO)
            # Sería mejor comprobar colisión con el hitbox del jugador si ya está definido
            if not rect_arbol_propuesto.colliderect(jugador.rect): 
                arbol = Arbol(spawn_x, spawn_y, settings.RUTA_ASSETS)
                arboles_sprites.add(arbol)
    except Exception as e:
        print(f"Error al crear árboles: {e}")

    enemigos_sprites = pygame.sprite.Group()
    NUMERO_ENEMIGOS_A_SPAWNEAR = 7
    RADIO_SPAWN_ENEMIGO_MIN = 50
    RADIO_SPAWN_ENEMIGO_MAX = 150
    for _ in range(NUMERO_ENEMIGOS_A_SPAWNEAR):
        angulo = random.uniform(0, 2 * math.pi)
        radio = random.uniform(RADIO_SPAWN_ENEMIGO_MIN, RADIO_SPAWN_ENEMIGO_MAX)
        offset_x = radio * math.cos(angulo)
        offset_y = radio * math.sin(angulo)
        pos_enemigo_x = jugador.rect.centerx + offset_x
        pos_enemigo_y = jugador.rect.centery + offset_y
        try:
            nuevo_enemigo = Enemigo(pos_enemigo_x, pos_enemigo_y)
            enemigos_sprites.add(nuevo_enemigo)
        except Exception as e:
            print(f"Error al crear un enemigo: {e}")
            
    return jugador, arboles_sprites, enemigos_sprites

def manejar_eventos(eventos, jugador, factor_zoom_actual, camara):
    """Maneja los eventos de Pygame (teclado, ratón, etc.).
    Devuelve el estado de 'ejecutando' y el 'factor_zoom_actual' y 'perfiles_disponibles_nombres'.
    """
    ejecutando_local = True
    zoom_cambio = False
    # Obtener/actualizar nombres de perfiles aquí para que esté al día
    perfiles_disponibles_nombres = list(jugador.perfiles_de_ataque.keys())


    for evento in eventos:
        if evento.type == pygame.QUIT:
            ejecutando_local = False
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                ejecutando_local = False
            if evento.key == pygame.K_SPACE:
                jugador.atacar(None) # El argumento enemigos_sprites ya no se usa en atacar directamente

            if evento.key == pygame.K_PAGEUP:
                if perfiles_disponibles_nombres:
                    # Asegurar que el perfil activo actual exista en la lista (podría haber cambiado)
                    if jugador.nombre_perfil_ataque_activo not in perfiles_disponibles_nombres:
                         perfiles_disponibles_nombres = list(jugador.perfiles_de_ataque.keys()) # Recargar
                         # Si sigue sin estar, o no hay perfiles, intentar seleccionar el primero si existe
                         if jugador.nombre_perfil_ataque_activo not in perfiles_disponibles_nombres and perfiles_disponibles_nombres:
                             jugador.seleccionar_perfil_ataque(perfiles_disponibles_nombres[0])
                         elif not perfiles_disponibles_nombres:
                             continue 

                    # Solo proceder si hay perfiles y el activo es válido
                    if perfiles_disponibles_nombres and jugador.nombre_perfil_ataque_activo in perfiles_disponibles_nombres:
                        indice_actual = perfiles_disponibles_nombres.index(jugador.nombre_perfil_ataque_activo)
                        nuevo_indice = (indice_actual - 1 + len(perfiles_disponibles_nombres)) % len(perfiles_disponibles_nombres)
                        jugador.seleccionar_perfil_ataque(perfiles_disponibles_nombres[nuevo_indice])

            if evento.key == pygame.K_PAGEDOWN:
                if perfiles_disponibles_nombres:
                    if jugador.nombre_perfil_ataque_activo not in perfiles_disponibles_nombres:
                         perfiles_disponibles_nombres = list(jugador.perfiles_de_ataque.keys()) # Recargar
                         if jugador.nombre_perfil_ataque_activo not in perfiles_disponibles_nombres and perfiles_disponibles_nombres:
                             jugador.seleccionar_perfil_ataque(perfiles_disponibles_nombres[0])
                         elif not perfiles_disponibles_nombres:
                             continue
                    
                    if perfiles_disponibles_nombres and jugador.nombre_perfil_ataque_activo in perfiles_disponibles_nombres:
                        indice_actual = perfiles_disponibles_nombres.index(jugador.nombre_perfil_ataque_activo)
                        nuevo_indice = (indice_actual + 1) % len(perfiles_disponibles_nombres)
                        jugador.seleccionar_perfil_ataque(perfiles_disponibles_nombres[nuevo_indice])
            
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
                    # Actualizar la lista de perfiles disponibles en caso de que se cree uno nuevo
                    perfiles_disponibles_nombres = list(jugador.perfiles_de_ataque.keys())

        if evento.type == pygame.MOUSEWHEEL: 
            if evento.y > 0: factor_zoom_actual += settings.FACTOR_ZOOM_PASO
            elif evento.y < 0: factor_zoom_actual -= settings.FACTOR_ZOOM_PASO
            factor_zoom_actual = max(settings.FACTOR_ZOOM_MIN, min(settings.FACTOR_ZOOM_MAX, factor_zoom_actual))
            zoom_cambio = True

    if zoom_cambio:
        nuevo_camara_ancho_vista = settings.ANCHO_PANTALLA / factor_zoom_actual
        nuevo_camara_alto_vista = settings.ALTO_PANTALLA / factor_zoom_actual
        camara.actualizar_dimensiones_vista(nuevo_camara_ancho_vista, nuevo_camara_alto_vista)
        
    return ejecutando_local, factor_zoom_actual, perfiles_disponibles_nombres

def actualizar_estado_juego(jugador, arboles_sprites, enemigos_sprites, teclas_presionadas):
    """Actualiza el estado de todos los elementos del juego."""
    obstaculos_solidos_para_jugador = pygame.sprite.Group()
    obstaculos_solidos_para_jugador.add(arboles_sprites.sprites()) 
    obstaculos_solidos_para_jugador.add(enemigos_sprites.sprites()) 

    jugador.actualizar_movimiento(teclas_presionadas, obstaculos_solidos_para_jugador)
    jugador.actualizar_animacion()
    jugador.actualizar_ataque(enemigos_sprites)
    
    arboles_sprites.update()
    # enemigos_sprites.update(jugador.hitbox, arboles_sprites) # <--- LÍNEA ORIGINAL

    # Nueva lógica para actualizar enemigos con colisiones entre ellos y con árboles
    for enemigo_actualizado in enemigos_sprites:
        # Crear un grupo de obstáculos para ESTE enemigo
        # que incluya todos los árboles y TODOS LOS DEMÁS enemigos.
        obstaculos_para_este_enemigo = pygame.sprite.Group()
        obstaculos_para_este_enemigo.add(arboles_sprites.sprites())
        for otro_enemigo in enemigos_sprites:
            if otro_enemigo != enemigo_actualizado: # Un enemigo no colisiona consigo mismo
                obstaculos_para_este_enemigo.add(otro_enemigo)
        
        enemigo_actualizado.update(jugador.hitbox, obstaculos_para_este_enemigo)


    for enemigo in enemigos_sprites:
        if jugador.hitbox.colliderect(enemigo.hitbox):
            jugador.recibir_dano(enemigo.dano_ataque)

def renderizar_juego(pantalla, camara, textura_fondo_original, ancho_textura_fondo, alto_textura_fondo, 
                     jugador, arboles_sprites, enemigos_sprites, debug_hud, 
                     factor_zoom_actual, perfiles_disponibles_nombres, nombre_perfil_activo):
    """Dibuja todos los elementos del juego en la pantalla."""
    camara.actualizar_posicion(jugador.rect)
    camara.dibujar_escena(pantalla, textura_fondo_original, ancho_textura_fondo, alto_textura_fondo,
                          jugador, arboles_sprites, enemigos_sprites)
    
    if settings.DEBUG_VER_HITBOXES:
        debug_hud.draw(pantalla, factor_zoom_actual, perfiles_disponibles_nombres, nombre_perfil_activo)

    pygame.display.flip()

# --- Bucle Principal del Juego ---
def main():
    pantalla, reloj, textura_fondo, ancho_text_fondo, alto_text_fondo, fuente_hud = inicializar_juego()
    jugador, arboles_sprites, enemigos_sprites = crear_entidades_juego()

    factor_zoom_actual = settings.FACTOR_ZOOM_INICIAL
    camara_ancho_vista_actual = settings.ANCHO_PANTALLA / factor_zoom_actual
    camara_alto_vista_actual = settings.ALTO_PANTALLA / factor_zoom_actual
    camara = Camara(camara_ancho_vista_actual, camara_alto_vista_actual)
    
    debug_hud = DebugHUD(jugador, fuente_hud)
    
    # Inicializar perfiles_disponibles_nombres aquí una vez, manejar_eventos lo actualizará si es necesario
    perfiles_disponibles_nombres = list(jugador.perfiles_de_ataque.keys())

    ejecutando = True
    while ejecutando:
        eventos_actuales = pygame.event.get()
        
        ejecutando, factor_zoom_actual, perfiles_disponibles_nombres_actualizados = manejar_eventos(eventos_actuales, jugador, factor_zoom_actual, camara)
        # Actualizar la lista principal si cambió dentro de manejar_eventos (por ej. al guardar)
        if perfiles_disponibles_nombres_actualizados is not None:
            perfiles_disponibles_nombres = perfiles_disponibles_nombres_actualizados

        teclas_presionadas = pygame.key.get_pressed()
        actualizar_estado_juego(jugador, arboles_sprites, enemigos_sprites, teclas_presionadas)
        
        renderizar_juego(pantalla, camara, textura_fondo, ancho_text_fondo, alto_text_fondo,
                         jugador, arboles_sprites, enemigos_sprites, debug_hud,
                         factor_zoom_actual, perfiles_disponibles_nombres, jugador.nombre_perfil_ataque_activo)

        reloj.tick(settings.FPS)

    pygame.quit()

if __name__ == '__main__':
    main()