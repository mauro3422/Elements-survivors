# hud.py
import pygame
import settings
import logging # Para el logger del HUD

logger = logging.getLogger("hud")
# if not logger.handlers: # Evitar duplicación de handlers si el módulo se recarga
# logger.setLevel(logging.DEBUG) # Permitir que pasen mensajes DEBUG
# La configuración centralizada de logging ya se encarga del nivel.

class DebugHUD:
    def __init__(self, jugador, fuente=None, juego_ref=None): # Añadir juego_ref para zoom
        self.jugador = jugador
        self.juego_ref = juego_ref # Para acceder al zoom_actual u otros datos de Juego
        self.fuente = fuente if fuente else pygame.font.Font(None, 24)
        self.color_texto = settings.BLANCO
        self.color_activo = settings.VERDE
        self.color_inactivo = settings.ROJO
        self.categorias_log_list = list(settings.LOG_CATEGORIAS.keys())

        self.mapa_teclas_log = {
            pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2, pygame.K_4: 3, pygame.K_5: 4,
            pygame.K_6: 5, pygame.K_7: 6, pygame.K_8: 7, pygame.K_9: 8, pygame.K_0: 9,
        }
        self.tecla_toggle_modo_debug_global = pygame.K_F11

        # Atributos para almacenar datos actualizados
        self._zoom_actual_cache = 1.0
        self._perfiles_disponibles_cache = []
        self._nombre_perfil_activo_cache = "N/A"
        self._apm_parametros_cache = {} # Para offset_distancia, extension, etc.
        self._jugador_pos_cache = "(N/A, N/A)"
        self._jugador_hb_cache = "(N/A, N/A, N/A, N/A)"


    def manejar_input_hud(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == self.tecla_toggle_modo_debug_global:
                settings.MODO_DEBUG_LOGS = not settings.MODO_DEBUG_LOGS
                if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_general", False):
                    logger.info(f"MODO_DEBUG_LOGS global cambiado a: {settings.MODO_DEBUG_LOGS}", extra={"categoria_log": "log_general"})

            if event.key in self.mapa_teclas_log:
                indice_cat = self.mapa_teclas_log[event.key]
                if 0 <= indice_cat < len(self.categorias_log_list):
                    nombre_cat = self.categorias_log_list[indice_cat]
                    settings.LOG_CATEGORIAS[nombre_cat] = not settings.LOG_CATEGORIAS[nombre_cat]
                    if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_general", False):
                        logger.debug(f"Categoría de log '{nombre_cat}' cambiada a: {settings.LOG_CATEGORIAS[nombre_cat]}", extra={"categoria_log": "log_general"})

    def update(self):
        # Recolectar y almacenar la información necesaria para dibujar.
        if self.juego_ref:
            self._zoom_actual_cache = self.juego_ref.factor_zoom_actual
        
        if self.jugador:
            self._jugador_pos_cache = f"({self.jugador.rect.x:.1f}, {self.jugador.rect.y:.1f})"
            self._jugador_hb_cache = f"({self.jugador.hitbox.x:.1f}, {self.jugador.hitbox.y:.1f}, {self.jugador.hitbox.w}, {self.jugador.hitbox.h})"
            
            if hasattr(self.jugador, 'attack_profile_manager'):
                apm = self.jugador.attack_profile_manager
                self._perfiles_disponibles_cache = apm.get_nombres_perfiles_disponibles()
                self._nombre_perfil_activo_cache = apm.nombre_perfil_ataque_activo
                
                # Cachear parámetros del APM
                params_a_cachear = ["offset_distancia", "extension", "grosor", 
                                    "duracion_total_ms", "dano_modificador", "cooldown_modificador"]
                self._apm_parametros_cache = {k: apm.get_parametro_ataque_activo(k, "N/A") for k in params_a_cachear}
                self._apm_parametros_cache["duracion_segmento_barrido_activo"] = f"{apm.duracion_segmento_barrido_activo:.2f}ms"
                self._apm_parametros_cache["num_segmentos_barrido_activo"] = apm.num_segmentos_barrido_activo

    def draw(self, superficie): # <--- Firma simplificada
        lineas_info_juego = []
        if self.jugador:
            # Usar datos cacheados
            dano_mod_hud = self._apm_parametros_cache.get("dano_modificador", "N/A")
            cd_mod_hud = self._apm_parametros_cache.get("cooldown_modificador", "N/A")

            try: dano_mod_str = f"{float(dano_mod_hud):.2f}" 
            except (ValueError, TypeError): dano_mod_str = str(dano_mod_hud)
            try: cd_mod_str = f"{float(cd_mod_hud):.2f}"
            except (ValueError, TypeError): cd_mod_str = str(cd_mod_hud)

            lineas_info_juego = [
                f"Jugador Pos: {self._jugador_pos_cache}",
                f"Jugador HB: {self._jugador_hb_cache}",
                f"Zoom (Rueda): {self._zoom_actual_cache:.2f}",
                f"Perfil Activo (PgUp/PgDn): {self._nombre_perfil_activo_cache}",
                f"  Perfiles Totales: {len(self._perfiles_disponibles_cache) if self._perfiles_disponibles_cache else '0'}",
                f"Offset (F1/F2): {self._apm_parametros_cache.get('offset_distancia', 'N/A')}",
                f"Extension (F3/F4): {self._apm_parametros_cache.get('extension', 'N/A')}",
                f"Grosor (F5/F6): {self._apm_parametros_cache.get('grosor', 'N/A')}", # Asumiendo que 'grosor' es un param
                f"Duracion Total (F7/F8): {self._apm_parametros_cache.get('duracion_total_ms', 'N/A')}ms",
                f"  Dur Segmento: {self._apm_parametros_cache.get('duracion_segmento_barrido_activo', 'N/A')}",
                f"  Num Segmentos: {self._apm_parametros_cache.get('num_segmentos_barrido_activo', 'N/A')}",
                f"  Dano Mod: {dano_mod_str}",
                f"  CD Mod: {cd_mod_str}",
                f"Guardar Perfiles (F12)"
            ]

        y_offset = settings.HUD_PADDING_Y
        x_offset = settings.HUD_PADDING_X
        for i, linea in enumerate(lineas_info_juego):
            img_texto = self.fuente.render(linea, True, self.color_texto)
            superficie.blit(img_texto, (x_offset, y_offset + i * settings.HUD_LINE_HEIGHT))
        
        y_offset += (len(lineas_info_juego)) * settings.HUD_LINE_HEIGHT # No sumar +1 aquí si la siguiente sección tiene su propio espacio
        y_offset += settings.HUD_ESPACIO_ENTRE_SECCIONES # Espacio antes de la sección de logs globales
        
        texto_modo_global = f"MODO DEBUG GLOBAL (F11): {'ON' if settings.MODO_DEBUG_LOGS else 'OFF'}"
        color_modo_global = self.color_activo if settings.MODO_DEBUG_LOGS else self.color_inactivo
        img_modo_global = self.fuente.render(texto_modo_global, True, color_modo_global)
        superficie.blit(img_modo_global, (x_offset, y_offset))
        y_offset += settings.HUD_ESPACIO_ENTRE_SECCIONES # Espacio antes del título de categorías de log

        superficie.blit(self.fuente.render("Categorías de Log (Teclas 1-0):", True, self.color_texto), (x_offset, y_offset))
        y_offset += settings.HUD_LINE_HEIGHT # Espacio después del título de categorías

        for i, nombre_cat in enumerate(self.categorias_log_list):
            if i < 10:
                estado_cat = settings.LOG_CATEGORIAS.get(nombre_cat, False)
                texto_cat = f"{i+1 if i < 9 else 0}: {nombre_cat} - {'ON' if estado_cat else 'OFF'}"
                color_cat = self.color_activo if estado_cat else self.color_inactivo
                img_cat = self.fuente.render(texto_cat, True, color_cat)
                superficie.blit(img_cat, (x_offset, y_offset))
                y_offset += settings.HUD_LINE_HEIGHT
            if i == 9 and len(self.categorias_log_list) > 10:
                 superficie.blit(self.fuente.render("...", True, self.color_texto), (x_offset, y_offset))
                 y_offset += settings.HUD_LINE_HEIGHT # Mantener consistencia de espaciado
                 break 