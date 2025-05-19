# hud.py
import pygame
import settings
import logging # Para el logger del HUD

logger = logging.getLogger("juego.hud")
if not logger.handlers: # Evitar duplicación de handlers si el módulo se recarga
    logger.setLevel(logging.DEBUG) # Permitir que pasen mensajes DEBUG
    # La salida a consola/archivo será manejada por el logger raíz y su configuración

class DebugHUD:
    def __init__(self, jugador, fuente=None):
        self.jugador = jugador
        self.fuente = fuente if fuente else pygame.font.Font(None, 24) # Fuente por defecto si no se provee
        self.color_texto = settings.BLANCO
        self.color_activo = settings.VERDE
        self.color_inactivo = settings.ROJO
        self.categorias_log_list = list(settings.LOG_CATEGORIAS.keys()) # Mantener un orden

        # Mapeo de teclas numéricas a índices de categorías (0-9)
        self.mapa_teclas_log = {
            pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2, pygame.K_4: 3, pygame.K_5: 4,
            pygame.K_6: 5, pygame.K_7: 6, pygame.K_8: 7, pygame.K_9: 8, pygame.K_0: 9,
            # Podríamos añadir más con Shift o F-keys si es necesario
        }
        # Tecla para alternar MODO_DEBUG_LOGS global
        self.tecla_toggle_modo_debug_global = pygame.K_F11 # Ejemplo, F11

    def manejar_input_hud(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == self.tecla_toggle_modo_debug_global:
                settings.MODO_DEBUG_LOGS = not settings.MODO_DEBUG_LOGS
                if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_general", False) : # Solo loguear si la categoría general está activa
                    logger.info(f"MODO_DEBUG_LOGS global cambiado a: {settings.MODO_DEBUG_LOGS}")
                # Actualizar la configuración del logger raíz si es necesario (esto es complejo desde aquí)
                # Por ahora, el cambio en MODO_DEBUG_LOGS será recogido por los 'if' en los puntos de log.
                # La reconfiguración del logger raíz en main.py solo ocurre al inicio.
                # Para un cambio dinámico del nivel de consola, necesitaríamos una función en main o un sistema de signals.
                # De momento, el file logger sí se activará/desactivará en la siguiente ejecución de main.py.
                # Y los 'if' en el código de logueo respetarán el cambio inmediatamente.

            if event.key in self.mapa_teclas_log:
                indice_cat = self.mapa_teclas_log[event.key]
                if 0 <= indice_cat < len(self.categorias_log_list):
                    nombre_cat = self.categorias_log_list[indice_cat]
                    settings.LOG_CATEGORIAS[nombre_cat] = not settings.LOG_CATEGORIAS[nombre_cat]
                    if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_general", False): # Solo loguear si la categoría general está activa
                        logger.debug(f"Categoría de log '{nombre_cat}' cambiada a: {settings.LOG_CATEGORIAS[nombre_cat]}")

    def update(self):
        # Por ahora, el HUD no necesita actualizar su estado de forma independiente.
        # La lógica de obtención de datos está en draw().
        pass

    def draw(self, superficie, zoom_actual, perfiles_disponibles, nombre_perfil_activo):
        lineas_info_juego = []
        if self.jugador: # Solo mostrar info del jugador si existe
            apm = self.jugador.attack_profile_manager
            offset_hud = apm.get_parametro_ataque_activo("offset_distancia", "N/A")
            extension_hud = apm.get_parametro_ataque_activo("extension", "N/A")
            grosor_hud = apm.get_parametro_ataque_activo("grosor", "N/A")
            duracion_hud = apm.get_parametro_ataque_activo("duracion_total_ms", "N/A")
            dano_mod_hud = apm.get_parametro_ataque_activo("dano_modificador", "N/A")
            cd_mod_hud = apm.get_parametro_ataque_activo("cooldown_modificador", "N/A")
            
            try: dano_mod_str = f"{float(dano_mod_hud):.2f}" 
            except ValueError: dano_mod_str = str(dano_mod_hud)
            try: cd_mod_str = f"{float(cd_mod_hud):.2f}"
            except ValueError: cd_mod_str = str(cd_mod_hud)

            lineas_info_juego = [
                f"Jugador Pos: ({self.jugador.rect.x:.1f}, {self.jugador.rect.y:.1f})",
                f"Jugador HB: ({self.jugador.hitbox.x:.1f}, {self.jugador.hitbox.y:.1f}, {self.jugador.hitbox.w}, {self.jugador.hitbox.h})",
                f"Zoom (Rueda): {zoom_actual:.2f}",
                f"Perfil Activo (PgUp/PgDn): {nombre_perfil_activo}",
                f"  Perfiles Totales: {len(perfiles_disponibles) if perfiles_disponibles else '0'}",
                f"Offset (F1/F2): {offset_hud}",
                f"Extension (F3/F4): {extension_hud}",
                f"Grosor (F5/F6): {grosor_hud}",
                f"Duracion Total (F7/F8): {duracion_hud}ms",
                f"  Dur Segmento: {apm.duracion_segmento_barrido_activo:.2f}ms",
                f"  Num Segmentos: {apm.num_segmentos_barrido_activo}",
                f"  Dano Mod: {dano_mod_str}",
                f"  CD Mod: {cd_mod_str}",
                f"Guardar Perfiles (F12)"
            ]

        y_offset = 10
        x_offset = 10
        for i, linea in enumerate(lineas_info_juego):
            img_texto = self.fuente.render(linea, True, self.color_texto)
            superficie.blit(img_texto, (x_offset, y_offset + i * 20))
        
        # Dibujar estado de MODO_DEBUG_LOGS y categorías
        y_offset += (len(lineas_info_juego) + 1) * 20 # Espacio después de la info del juego
        
        # Estado global MODO_DEBUG_LOGS
        texto_modo_global = f"MODO DEBUG GLOBAL (F11): {'ON' if settings.MODO_DEBUG_LOGS else 'OFF'}"
        color_modo_global = self.color_activo if settings.MODO_DEBUG_LOGS else self.color_inactivo
        img_modo_global = self.fuente.render(texto_modo_global, True, color_modo_global)
        superficie.blit(img_modo_global, (x_offset, y_offset))
        y_offset += 25 # Siguiente línea

        # Categorías de Logs
        superficie.blit(self.fuente.render("Categorías de Log (Teclas 1-0):", True, self.color_texto), (x_offset, y_offset))
        y_offset += 20

        for i, nombre_cat in enumerate(self.categorias_log_list):
            if i < 10: # Solo mostrar las primeras 10 que tienen mapeo de tecla por ahora
                estado_cat = settings.LOG_CATEGORIAS.get(nombre_cat, False)
                texto_cat = f"{i+1 if i < 9 else 0}: {nombre_cat} - {'ON' if estado_cat else 'OFF'}"
                color_cat = self.color_activo if estado_cat else self.color_inactivo
                img_cat = self.fuente.render(texto_cat, True, color_cat)
                superficie.blit(img_cat, (x_offset, y_offset))
                y_offset += 20
            if i == 9 and len(self.categorias_log_list) > 10: # Indicador si hay más categorías
                 superficie.blit(self.fuente.render("...", True, self.color_texto), (x_offset, y_offset))
                 y_offset += 20
                 break # Salir del bucle para no dibujar más de 10 por ahora 