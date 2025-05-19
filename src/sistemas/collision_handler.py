import pygame
import logging
from src.config import settings # MODIFICADO: Importación de settings actualizada

# Cambiar nombre del logger y eliminar setLevel
# logger_ch = logging.getLogger("log_collision_handler")
# logger_ch.setLevel(logging.DEBUG)
logger = logging.getLogger("collision_handler")

class CollisionHandler:
    @staticmethod
    def _resolver_solapamientos_estaticos_eje(entidad_hitbox, entidad_rect, hitbox_offset_x, hitbox_offset_y, obstaculos, eje, movimiento_input_en_eje):
        log_habilitado = settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler", False)

        # if not (settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler", False)):
            # Si la categoría está desactivada, esta función interna no necesita ejecutarse con logs.
            # La lógica de resolución sí debe ejecutarse siempre.
            # Considerar si los logs son esenciales para la función o si la función puede operar sin ellos.
            # Por ahora, se asume que la función puede operar y solo se omiten los logs.
        #    pass # Esto es solo para la condición del log, la lógica sigue

        if log_habilitado:
            # Reemplazar logger_ch por logger y añadir extra
            logger.debug(f"    --- CH: Inicio _resolver_solapamientos_estaticos_eje ({eje}--- Input: {movimiento_input_en_eje}, HB_in: {entidad_hitbox.topleft}", extra={"categoria_log": "log_collision_handler"})
        for pasada in range(settings.MAX_PASADAS_RESOLUCION_ESTATICA):
            colision_resuelta_en_pasada = False
            if log_habilitado:
                # Reemplazar logger_ch por logger y añadir extra
                logger.debug(f"      CH: Pasada {pasada + 1} res. estática eje {eje}", extra={"categoria_log": "log_collision_handler"})

            for i, obstaculo in enumerate(obstaculos):
                rect_colision_obstaculo = obstaculo.hitbox if hasattr(obstaculo, 'hitbox') else obstaculo.rect
                # Usar nombre_log_entidad si existe, sino un fallback descriptivo.
                obst_id_log = getattr(obstaculo, 'nombre_log_entidad', f"{type(obstaculo).__name__}_idx{i}")

                if entidad_hitbox.colliderect(rect_colision_obstaculo):
                    if log_habilitado:
                        # Reemplazar logger_ch por logger y añadir extra
                        logger.debug(f"        CH: SOLAP. ESTÁTICO EJE {eje} con {obst_id_log} (Pasada {pasada+1}). HB_Ent: {entidad_hitbox.topleft}, HB_Obs: {rect_colision_obstaculo.topleft}", extra={"categoria_log": "log_collision_handler"})
                    
                    hitbox_modificado_este_obstaculo = False
                    if eje == 'x':
                        x_antes = entidad_hitbox.x
                        # Determinar la dirección del solapamiento basado en los centros
                        # Si el centro de la entidad está a la izquierda del centro del obstáculo,
                        # el solapamiento probable es del lado derecho de la entidad con el lado izquierdo del obstáculo.
                        if entidad_hitbox.centerx < rect_colision_obstaculo.centerx:
                            overlap = entidad_hitbox.right - rect_colision_obstaculo.left
                            if overlap > 0: # Hay solapamiento real en este lado
                                if log_habilitado:
                                    # Reemplazar logger_ch por logger y añadir extra
                                    logger.debug(f"          CH: Estático EJE X vs {obst_id_log}: Entidad a la IZQ del Obs. Overlap (Ent.R - Obs.L): {overlap:.2f}. Ajustando Ent.Right.", extra={"categoria_log": "log_collision_handler"})
                                entidad_hitbox.right = rect_colision_obstaculo.left
                        else: # El centro de la entidad está a la derecha (o coincidecon el centro del obstáculo
                              # el solapamiento probable es del lado izquierdo de la entidad con el lado derecho del obstáculo.
                            overlap = rect_colision_obstaculo.right - entidad_hitbox.left
                            if overlap > 0: # Hay solapamiento real en este lado
                                if log_habilitado:
                                    # Reemplazar logger_ch por logger y añadir extra
                                    logger.debug(f"          CH: Estático EJE X vs {obst_id_log}: Entidad a la DER del Obs. Overlap (Obs.R - Ent.L): {overlap:.2f}. Ajustando Ent.Left.", extra={"categoria_log": "log_collision_handler"})
                                entidad_hitbox.left = rect_colision_obstaculo.right
                        
                        if entidad_hitbox.x != x_antes: 
                            hitbox_modificado_este_obstaculo = True
                            if log_habilitado:
                                # Reemplazar logger_ch por logger y añadir extra
                                logger.debug(f"          CH: Estático EJE X vs {obst_id_log}: Cambio aplicado. HB_Ent.x antes: {x_antes:.2f}, después: {entidad_hitbox.x:.2f}", extra={"categoria_log": "log_collision_handler"})
                                
                    elif eje == 'y':
                        y_antes = entidad_hitbox.y
                        # Determinar la dirección del solapamiento basado en los centros
                        # Si el centro de la entidad está arriba del centro del obstáculo,
                        # el solapamiento probable es del lado inferior de la entidad con el lado superior del obstáculo.
                        if entidad_hitbox.centery < rect_colision_obstaculo.centery:
                            overlap = entidad_hitbox.bottom - rect_colision_obstaculo.top
                            if overlap > 0: # Hay solapamiento real en este lado
                                if log_habilitado:
                                    # Reemplazar logger_ch por logger y añadir extra
                                    logger.debug(f"          CH: Estático EJE Y vs {obst_id_log}: Entidad ARRIBA del Obs. Overlap (Ent.B - Obs.T): {overlap:.2f}. Ajustando Ent.Bottom.", extra={"categoria_log": "log_collision_handler"})
                                entidad_hitbox.bottom = rect_colision_obstaculo.top
                        else: # El centro de la entidad está abajo (o coincide) con el centro del obstáculo
                              # el solapamiento probable es del lado superior de la entidad con el lado inferior del obstáculo.
                            overlap = rect_colision_obstaculo.bottom - entidad_hitbox.top
                            if overlap > 0: # Hay solapamiento real en este lado
                                if log_habilitado:
                                    # Reemplazar logger_ch por logger y añadir extra
                                    logger.debug(f"          CH: Estático EJE Y vs {obst_id_log}: Entidad ABAJO del Obs. Overlap (Obs.B - Ent.T): {overlap:.2f}. Ajustando Ent.Top.", extra={"categoria_log": "log_collision_handler"})
                                entidad_hitbox.top = rect_colision_obstaculo.bottom

                        if entidad_hitbox.y != y_antes:
                            hitbox_modificado_este_obstaculo = True
                            if log_habilitado:
                                # Reemplazar logger_ch por logger y añadir extra
                                logger.debug(f"          CH: Estático EJE Y vs {obst_id_log}: Cambio aplicado. HB_Ent.y antes: {y_antes:.2f}, después: {entidad_hitbox.y:.2f}", extra={"categoria_log": "log_collision_handler"})

                    if hitbox_modificado_este_obstaculo:
                        colision_resuelta_en_pasada = True
                        if log_habilitado:
                            # Reemplazar logger_ch por logger y añadir extra
                            logger.debug(f"          CH: Post-Pre-Corrección EJE {eje} (estática) vs {obst_id_log}: HB_Ent: {entidad_hitbox.topleft}", extra={"categoria_log": "log_collision_handler"})
            
            if not colision_resuelta_en_pasada: 
                if log_habilitado:
                    # Reemplazar logger_ch por logger y añadir extra
                    logger.debug(f"      CH: No más solapamientos estáticos eje {eje} en pasada {pasada + 1}. Saliendo.", extra={"categoria_log": "log_collision_handler"})
                break 
        
        if log_habilitado:
            # Reemplazar logger_ch por logger y añadir extra
            logger.debug(f"    --- CH: Fin _resolver_solapamientos_estaticos_eje ({eje}) --- HB_out: {entidad_hitbox.topleft}", extra={"categoria_log": "log_collision_handler"})

    @staticmethod
    def _aplicar_movimiento_y_colision_eje_x(entidad_hitbox, dx_aplicado, obstaculos):
        log_habilitado = settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler", False)
        if log_habilitado:
            # Reemplazar logger_ch por logger y añadir extra
            logger.debug(f"    --- CH: Inicio _aplicar_movimiento_y_colision_eje_x --- dx: {dx_aplicado}, HB_in: {entidad_hitbox.topleft}", extra={"categoria_log": "log_collision_handler"})
        
        x_original_hb = entidad_hitbox.x # Guardar para comparar

        if dx_aplicado != 0:
            # entidad_hitbox.x += dx_aplicado # Asignación directa anterior
            entidad_hitbox.x = int(x_original_hb + dx_aplicado)# Truncamiento explícito
            
            if log_habilitado:
                # Reemplazar logger_ch por logger y añadir extra
                logger.debug(f"      CH: Fase 2 (X): dx_aplicado={dx_aplicado:.4f}. HB.x original={x_original_hb}, HB.x post-int-trunc={entidad_hitbox.x}", extra={"categoria_log": "log_collision_handler"})

            for obstaculo in obstaculos:
                rect_colision_obstaculo = obstaculo.hitbox if hasattr(obstaculo, 'hitbox') else obstaculo.rect
                if entidad_hitbox.colliderect(rect_colision_obstaculo):
                    obst_id_log = getattr(obstaculo, 'nombre_log_entidad', f"{type(obstaculo).__name__}_Desconocido")
                    if log_habilitado:
                        # Reemplazar logger_ch por logger y añadir extra
                        logger.debug(f"      CH: Fase 2 (X): Colisión X detectada con {obst_id_log} después de mov. tentativo. HB_Ent: {entidad_hitbox.topleft}, HB_Obs: {rect_colision_obstaculo.topleft}", extra={"categoria_log": "log_collision_handler"})
                    
                    if dx_aplicado > 0: # Se movía hacia la derecha y colisionó
                        entidad_hitbox.right = rect_colision_obstaculo.left
                        if log_habilitado:
                            # Reemplazar logger_ch por logger y añadir extra
                            logger.debug(f"        CH: Fase 2 (X): Ajustado. Entidad mov. a DER. HB_Ent.right = Obs.left ({entidad_hitbox.right:.2f})", extra={"categoria_log": "log_collision_handler"})
                    elif dx_aplicado < 0: # Se movía hacia la izquierda y colisionó
                        entidad_hitbox.left = rect_colision_obstaculo.right
                        if log_habilitado:
                            # Reemplazar logger_ch por logger y añadir extra
                            logger.debug(f"        CH: Fase 2 (X): Ajustado. Entidad mov. a IZQ. HB_Ent.left = Obs.right ({entidad_hitbox.left:.2f})", extra={"categoria_log": "log_collision_handler"})
                    # Una vez que se maneja una colisión en este eje, rompemos el bucle de obstáculos.
                    # La posición ya está ajustada al primer obstáculo encontrado en la dirección del movimiento.
                    break 
        
        if log_habilitado:
            # Reemplazar logger_ch por logger y añadir extra
            logger.debug(f"    --- CH: Fin _aplicar_movimiento_y_colision_eje_x --- HB_out X: {entidad_hitbox.x:.2f}", extra={"categoria_log": "log_collision_handler"})

    @staticmethod
    def _aplicar_movimiento_y_colision_eje_y(entidad_hitbox, dy_aplicado, obstaculos):
        log_habilitado = settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler", False)
        if log_habilitado:
            # Reemplazar logger_ch por logger y añadir extra
            logger.debug(f"    --- CH: Inicio _aplicar_movimiento_y_colision_eje_y --- dy: {dy_aplicado}, HB_in: {entidad_hitbox.topleft}", extra={"categoria_log": "log_collision_handler"})
        
        y_original_hb = entidad_hitbox.y # Guardar para comparar

        if dy_aplicado != 0:
            # entidad_hitbox.y += dy_aplicado # Asignación directa anterior
            entidad_hitbox.y = int(y_original_hb + dy_aplicado)# Truncamiento explícito

            if log_habilitado:
                # Reemplazar logger_ch por logger y añadir extra
                logger.debug(f"      CH: Fase 2 (Y): dy_aplicado={dy_aplicado:.4f}. HB.y original={y_original_hb}, HB.y post-int-trunc={entidad_hitbox.y}", extra={"categoria_log": "log_collision_handler"})

            for obstaculo in obstaculos:
                rect_colision_obstaculo = obstaculo.hitbox if hasattr(obstaculo, 'hitbox') else obstaculo.rect
                if entidad_hitbox.colliderect(rect_colision_obstaculo):
                    obst_id_log = getattr(obstaculo, 'nombre_log_entidad', f"{type(obstaculo).__name__}_Desconocido")
                    if log_habilitado:
                        # Reemplazar logger_ch por logger y añadir extra
                        logger.debug(f"      CH: Fase 2 (Y): Colisión Y detectada con {obst_id_log} después de mov. tentativo. HB_Ent: {entidad_hitbox.topleft}, HB_Obs: {rect_colision_obstaculo.topleft}", extra={"categoria_log": "log_collision_handler"})

                    if dy_aplicado > 0: # Se movía hacia abajo y colisionó
                        entidad_hitbox.bottom = rect_colision_obstaculo.top
                        if log_habilitado:
                            # Reemplazar logger_ch por logger y añadir extra
                            logger.debug(f"        CH: Fase 2 (Y): Ajustado. Entidad mov. ABAJO. HB_Ent.bottom = Obs.top ({entidad_hitbox.bottom:.2f})", extra={"categoria_log": "log_collision_handler"})
                    elif dy_aplicado < 0: # Se movía hacia arriba y colisionó
                        entidad_hitbox.top = rect_colision_obstaculo.bottom
                        if log_habilitado:
                            # Reemplazar logger_ch por logger y añadir extra
                            logger.debug(f"        CH: Fase 2 (Y): Ajustado. Entidad mov. ARRIBA. HB_Ent.top = Obs.bottom ({entidad_hitbox.top:.2f})", extra={"categoria_log": "log_collision_handler"})
                    # Una vez que se maneja una colisión en este eje, rompemos el bucle de obstáculos.
                    break

        if log_habilitado:
            # Reemplazar logger_ch por logger y añadir extra
            logger.debug(f"    --- CH: Fin _aplicar_movimiento_y_colision_eje_y --- HB_out Y: {entidad_hitbox.y:.2f}", extra={"categoria_log": "log_collision_handler"})

    @staticmethod
    def _verificar_y_revertir_colision_post_fase2(entidad_hitbox, obstaculos, pos_segura_fase1_x, pos_segura_fase1_y, 
                                               pos_original_global_x, pos_original_global_y):
        log_habilitado = settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler", False)
        if log_habilitado:
            # Reemplazar logger_ch por logger y añadir extra
            logger.debug(f"    --- CH: Inicio _verificar_y_revertir_colision_post_fase2 --- HB_in: {entidad_hitbox.topleft}", extra={"categoria_log": "log_collision_handler"})
        
        colision_global_tras_fase2, obstaculo_colisionante_global = False, None
        for obstaculo in obstaculos:
            rect_colision_obstaculo = obstaculo.hitbox if hasattr(obstaculo, 'hitbox') else obstaculo.rect
            if entidad_hitbox.colliderect(rect_colision_obstaculo):
                colision_global_tras_fase2, obstaculo_colisionante_global = True, obstaculo
                break
        
        hubo_reversion_global = False
        if colision_global_tras_fase2:
            # Estos son WARNING y CRITICAL, se loguearán más fácilmente si MODO_DEBUG_LOGS está activo
            # pero también si su categoría específica está activa, o siempre si se decide así para niveles altos.
            # Por ahora, los dejamos condicionados a la categoría "log_collision_handler" también para verbosidad.
            if log_habilitado:
                # Usar nombre_log_entidad si existe, sino un fallback descriptivo.
                obst_id_log = getattr(obstaculo_colisionante_global, 'nombre_log_entidad', f"{type(obstaculo_colisionante_global).__name__}_Desconocido")
                # Reemplazar logger_ch por logger y añadir extra
                logger.warning(f"CH WARN Global (post-F2): Entidad AÑ colisiona con {obst_id_log} DESPUÉS de Fase 2. HB_Ent: {entidad_hitbox.topleft}. Revertiendo a Fase 1: ({pos_segura_fase1_x}, {pos_segura_fase1_y})", extra={"categoria_log": "log_collision_handler"})
            entidad_hitbox.x, entidad_hitbox.y = pos_segura_fase1_x, pos_segura_fase1_y
            hubo_reversion_global = True
            if log_habilitado:
                # Reemplazar logger_ch por logger y añadir extra
                 logger.warning(f"  CH WARN Global (post-F2): Posición REVERTIDA A FASE 1. HB_Ent: {entidad_hitbox.topleft}", extra={"categoria_log": "log_collision_handler"})

            col_aun_despues_rev_f1, obst_critico_final = False, None
            for obst_check_critico in obstaculos:
                if entidad_hitbox.colliderect(obst_check_critico.hitbox if hasattr(obst_check_critico, 'hitbox') else obst_check_critico.rect):
                    col_aun_despues_rev_f1, obst_critico_final = True, obst_check_critico
                    break
            
            if col_aun_despues_rev_f1:
                if log_habilitado:
                    # Usar nombre_log_entidad si existe, sino un fallback descriptivo.
                    obst_id_log_crit = getattr(obst_critico_final, 'nombre_log_entidad', f"{type(obst_critico_final).__name__}_Desconocido")
                    # Reemplazar logger_ch por logger y añadir extra
                    logger.critical(f"CH CRITICAL POST-REVERSION (Fase1): Entidad AÑ COLISIONA con {obst_id_log_crit} DESPUÉS de revertir a Fase 1 ({entidad_hitbox.topleft}). Revertiendo a ORIGINAL GLOBAL: ({pos_original_global_x}, {pos_original_global_y})", extra={"categoria_log": "log_collision_handler"})
                entidad_hitbox.x, entidad_hitbox.y = pos_original_global_x, pos_original_global_y
                if log_habilitado:
                    # Reemplazar logger_ch por logger y añadir extra
                    logger.critical(f"  CH CRITICAL: Posición REVERTIDA A ORIGINAL GLOBAL. HB_Ent: {entidad_hitbox.topleft}", extra={"categoria_log": "log_collision_handler"})
        
        if log_habilitado:
            # Reemplazar logger_ch por logger y añadir extra
            logger.debug(f"    --- CH: Fin _verificar_y_revertir_colision_post_fase2 --- HB_out: {entidad_hitbox.topleft}, ReversionGlobal: {hubo_reversion_global}", extra={"categoria_log": "log_collision_handler"})
        return hubo_reversion_global

    @staticmethod
    def _prevenir_teletransportacion(entidad_hitbox, dx_solicitado, dy_solicitado, pos_segura_fase1_x, pos_segura_fase1_y):
        log_habilitado = settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler", False)
        # Esta función es principalmente para logs CRITICAL, así que se loguearán si la categoría está activa.
        if not log_habilitado:
            return False # No hacer nada si los logs están desactivados

        # Umbral de detección de teletransportación (ejemplo, ajustable)
        UMBRAL_TELETRANSPORTACION_X = entidad_hitbox.width * 1.5
        UMBRAL_TELETRANSPORTACION_Y = entidad_hitbox.height * 1.5

        # Comprobar si el movimiento solicitado excede el umbral
        teletransportacion_detectada_x = abs(dx_solicitado) > UMBRAL_TELETRANSPORTACION_X
        teletransportacion_detectada_y = abs(dy_solicitado) > UMBRAL_TELETRANSPORTACION_Y

        # Comprobar si la posición después de la Fase 1 es drásticamente diferente (implica un gran ajuste)
        # Esto es más un indicador de que la Fase 1 tuvo que trabajar mucho.
        ajuste_drastico_f1_x = abs(entidad_hitbox.x - pos_segura_fase1_x) > UMBRAL_TELETRANSPORTACION_X / 2 # Umbral más pequeño aquí
        ajuste_drastico_f1_y = abs(entidad_hitbox.y - pos_segura_fase1_y) > UMBRAL_TELETRANSPORTACION_Y / 2

        if teletransportacion_detectada_x or teletransportacion_detectada_y:
            logger.critical(f"CH CRITICAL - POSIBLE TELETRANSPORTACIÓN: Movimiento solicitado ({dx_solicitado:.2f}, {dy_solicitado:.2f}) excede umbral. HB_Ent: {entidad_hitbox.topleft}", extra={"categoria_log": "log_collision_handler"})
            # Podría añadirse lógica aquí para revertir o limitar el movimiento si esto se considera un error irrecuperable.
            # Por ahora, solo se loguea.
            return True # Indica que se detectó una teletransportación potencial.

        if ajuste_drastico_f1_x or ajuste_drastico_f1_y:
            logger.warning(f"CH WARNING - AJUSTE DRÁSTICO FASE 1: HB_Ent después de F1 ({pos_segura_fase1_x:.2f}, {pos_segura_fase1_y:.2f}) difiere significativamente de HB original ({entidad_hitbox.x:.2f}, {entidad_hitbox.y:.2f}). Mov. Solicitado: ({dx_solicitado:.2f}, {dy_solicitado:.2f})", extra={"categoria_log": "log_collision_handler"})
            # No necesariamente una 'teletransportación' por input, pero indica un gran ajuste en pre-resolución.
            # No se retorna True aquí ya que es más una advertencia sobre la resolución de solapamientos.
        
        return False # No se detectó teletransportación por input directo.

    @staticmethod
    def gestionar_movimiento_y_colision(entidad_hitbox, entidad_rect, hitbox_offset_x, hitbox_offset_y, dx, dy, obstaculos):
        log_habilitado = settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler", False)
        # El logger ya no se pasa, CollisionHandler usa su propio logger_ch.
        # (El comentario anterior es obsoleto, se usa `logger` ahora)
        
        if log_habilitado:
            logger.debug(f"CH: Inicio gestionar_movimiento_y_colision. dx={dx:.4f}, dy={dy:.4f}. HB_in: {entidad_hitbox.topleft}, Rect_in: {entidad_rect.topleft}", extra={"categoria_log": "log_collision_handler"})

        # Guardar la posición original global de la hitbox para una posible reversión crítica.
        pos_original_global_hb_x, pos_original_global_hb_y = entidad_hitbox.x, entidad_hitbox.y

        # --- FASE 1: Resolver solapamientos estáticos ANTES de mover ---
        # Esto maneja casos donde la entidad ya podría estar solapada al inicio del frame.
        if log_habilitado:
            logger.debug("  CH: Fase 1 - Resolviendo solapamientos estáticos (Eje X)...", extra={"categoria_log": "log_collision_handler"})
        CollisionHandler._resolver_solapamientos_estaticos_eje(entidad_hitbox, entidad_rect, hitbox_offset_x, hitbox_offset_y, obstaculos, 'x', dx)
        
        if log_habilitado:
            logger.debug("  CH: Fase 1 - Resolviendo solapamientos estáticos (Eje Y)...", extra={"categoria_log": "log_collision_handler"})
        CollisionHandler._resolver_solapamientos_estaticos_eje(entidad_hitbox, entidad_rect, hitbox_offset_x, hitbox_offset_y, obstaculos, 'y', dy)
        
        # Guardar la posición 'segura' después de la Fase 1. Esta es la posición a la que revertiremos
        # si la Fase 2 (movimiento + colisión) resulta en un estado de colisión irresoluble.
        pos_segura_fase1_hb_x, pos_segura_fase1_hb_y = entidad_hitbox.x, entidad_hitbox.y
        if log_habilitado:
            logger.debug(f"  CH: Fase 1 - Fin. Posición segura HB: ({pos_segura_fase1_hb_x}, {pos_segura_fase1_hb_y})", extra={"categoria_log": "log_collision_handler"})

        # --- Diagnóstico: Prevenir teletransportación por input excesivo o grandes ajustes en Fase 1 ---
        # (Esta llamada se realiza ANTES de aplicar el movimiento de Fase 2, usando el dx, dy originales)
        CollisionHandler._prevenir_teletransportacion(entidad_hitbox, dx, dy, pos_segura_fase1_hb_x, pos_segura_fase1_hb_y)

        # --- FASE 2: Aplicar movimiento y resolver colisiones (eje por eje) ---
        # Mover en X y resolver colisiones en X
        if log_habilitado:
            logger.debug("  CH: Fase 2 - Aplicando movimiento y colisión (Eje X)...", extra={"categoria_log": "log_collision_handler"})
        CollisionHandler._aplicar_movimiento_y_colision_eje_x(entidad_hitbox, dx, obstaculos)
        
        # Mover en Y y resolver colisiones en Y
        if log_habilitado:
            logger.debug("  CH: Fase 2 - Aplicando movimiento y colisión (Eje Y)...", extra={"categoria_log": "log_collision_handler"})
        CollisionHandler._aplicar_movimiento_y_colision_eje_y(entidad_hitbox, dy, obstaculos)
        if log_habilitado:
            logger.debug(f"  CH: Fase 2 - Fin. Posición HB post-mov: {entidad_hitbox.topleft}", extra={"categoria_log": "log_collision_handler"})

        # --- FASE 3: Verificación y Reversión Post-Fase 2 (Capa de Seguridad Adicional) ---
        # Verifica si, después de todo el proceso de la Fase 2, la entidad AÚN está colisionando.
        # Si es así, revierte a la posición segura de la Fase 1.
        # Si incluso eso falla (caso crítico), revierte a la posición original global.
        if log_habilitado:
            logger.debug("  CH: Fase 3 - Verificando y revirtiendo colisión post-Fase 2...", extra={"categoria_log": "log_collision_handler"})
        hubo_reversion = CollisionHandler._verificar_y_revertir_colision_post_fase2(
            entidad_hitbox, obstaculos, 
            pos_segura_fase1_hb_x, pos_segura_fase1_hb_y,
            pos_original_global_hb_x, pos_original_global_hb_y
        )
        if log_habilitado:
             logger.debug(f"  CH: Fase 3 - Fin. Hubo reversión: {hubo_reversion}. Posición HB final: {entidad_hitbox.topleft}", extra={"categoria_log": "log_collision_handler"})

        # --- FASE 4: Actualizar la posición del rect visual de la entidad ---
        # El rect de la entidad (usado para el dibujo) debe reflejar la posición final de la hitbox.
        entidad_rect.x = entidad_hitbox.x - hitbox_offset_x
        entidad_rect.y = entidad_hitbox.y - hitbox_offset_y
        
        if log_habilitado:
            logger.debug(f"CH: Fin gestionar_movimiento_y_colision. HB_out: {entidad_hitbox.topleft}, Rect_out: {entidad_rect.topleft}", extra={"categoria_log": "log_collision_handler"})

    @staticmethod
    def resolver_colisiones_dinamicas_entidad_a_entidad(entidad_actual, otra_entidad):
        log_habilitado = settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler", False)
        # Obtener las hitboxes de ambas entidades
        hitbox_actual = entidad_actual.hitbox
        hitbox_otra = otra_entidad.hitbox

        if hitbox_actual.colliderect(hitbox_otra):
            if log_habilitado:
                # Usar nombre_log_entidad si existe para ambas entidades
                nombre_actual = getattr(entidad_actual, 'nombre_log_entidad', f"{type(entidad_actual).__name__}_Desconocido")
                nombre_otra = getattr(otra_entidad, 'nombre_log_entidad', f"{type(otra_entidad).__name__}_Desconocido")
                logger.info(f"CH INFO: Colisión dinámica detectada entre {nombre_actual} (HB: {hitbox_actual.topleft}) y {nombre_otra} (HB: {hitbox_otra.topleft})", extra={"categoria_log": "log_collision_handler"})
            
            # TODO: Implementar lógica de resolución si es necesario (ej. empujar, detener, etc.)
            # Por ahora, solo detecta y loguea. Podría devolver las entidades involucradas o un objeto de colisión.
            return True
        
        return False
    # Fin def resolver_colisiones_dinamicas_entidad_a_entidad 