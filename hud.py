# hud.py
import pygame
import settings

class DebugHUD:
    def __init__(self, jugador_ref, fuente_hud):
        self.jugador = jugador_ref
        self.fuente = fuente_hud

    def draw(self, pantalla, factor_zoom_actual, perfiles_disponibles_nombres, nombre_perfil_activo):
        if not settings.DEBUG_VER_HITBOXES:
            return

        y_offset_hud = 10
        # Obtener parámetros del perfil activo para el HUD directamente del jugador
        offset_hud = self.jugador.get_parametro_ataque_activo("offset_distancia", "N/A")
        extension_hud = self.jugador.get_parametro_ataque_activo("extension", "N/A")
        grosor_hud = self.jugador.get_parametro_ataque_activo("grosor", "N/A")
        duracion_total_hud = self.jugador.get_parametro_ataque_activo("duracion_total_ms", "N/A")
        dano_mod_hud = self.jugador.get_parametro_ataque_activo("dano_modificador", "N/A")
        cd_mod_hud = self.jugador.get_parametro_ataque_activo("cooldown_modificador", "N/A")

        textos_hud = [
            f"Perfil Activo (PgUp/PgDn): {nombre_perfil_activo}",
            f"Offset (F1/F2): {offset_hud}",
            f"Extension (F3/F4): {extension_hud}",
            f"Grosor (F5/F6): {grosor_hud}",
            f"Duracion Total (F7/F8): {duracion_total_hud}ms",
            f"  Dur Segmento: {self.jugador.duracion_segmento_barrido_activo:.2f}ms",
            f"  Num Segmentos: {self.jugador.num_segmentos_barrido_activo}", # Añadido para más claridad
            f"  Dano Mod: {dano_mod_hud:.2f}",
            f"  CD Mod: {cd_mod_hud:.2f}",
            f"Zoom (Rueda): {factor_zoom_actual:.2f}",
            f"Guardar Perfiles (F12)"
        ]

        for i, texto_str in enumerate(textos_hud):
            texto_surface = self.fuente.render(texto_str, True, settings.COLOR_HUD_TEXTO)
            pantalla.blit(texto_surface, (10, y_offset_hud + i * 20)) 