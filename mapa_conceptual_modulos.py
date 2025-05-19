# mapa_conceptual_modulos.py
# Este archivo contiene una representación estructurada de los módulos principales
# del proyecto, sus responsabilidades e interacciones, agrupados por categoría.
# Sirve como un "mapa conceptual" para ayudar a entender la arquitectura del juego.

MAPA_MODULOS_POR_CATEGORIA = {
    "Core": [
        {
            "nombre_modulo": "main.py",
            "categoria": "Core", # Aunque 'main.py' quedará en la raíz, conceptualmente es el núcleo.
            "ruta_relativa": "main.py", # Esta ruta se actualizará si main.py se moviera (pero no lo hará).
            "responsabilidad_principal": "Punto de entrada de la aplicación. Inicializa el sistema de logging y el juego, y maneja el bucle principal de alto nivel.",
            "interacciones_principales": {
                "entrantes": [], # Es el punto de partida
                "salientes": ["config_logging.py", "juego.py", "settings.py"]
            },
            "componentes_clave_internos": ["Función main()"],
            "notas_adicionales": "Es el primer script que se ejecuta. Asegura que la RUTA_BASE_PROYECTO esté en sys.path si es necesario (lógica a revisar con la estructura src/)."
        },
        {
            "nombre_modulo": "juego.py",
            "categoria": "Core",
            "ruta_relativa": "juego.py", # Se actualizará a "src/core/juego.py"
            "responsabilidad_principal": "Clase principal que orquesta el flujo del juego. Maneja el bucle de juego, los estados (a través de gestor_estado), eventos (gestor_eventos), actualizaciones de entidades, renderizado (renderer) y colisiones (collision_handler).",
            "interacciones_principales": {
                "entrantes": ["main.py"],
                "salientes": [
                    "settings.py", "game_initializer.py", "gestor_eventos.py",
                    "gestor_estado.py", "gestor_nivel.py", "asset_manager.py", "renderer.py",
                    "hud.py", "camara.py", "collision_handler.py", "jugador.py",
                    "enemigo.py", "entorno.py"
                ]
            },
            "componentes_clave_internos": ["Clase Juego", "método run()", "método _manejar_eventos()", "método _actualizar()", "método _renderizar()"],
            "notas_adicionales": "Contiene el bucle de juego principal y coordina la mayoría de los sistemas y entidades."
        },
        {
            "nombre_modulo": "settings.py",
            "categoria": "Core", # O podría ser "Config" si creamos esa carpeta específica.
            "ruta_relativa": "settings.py", # Se actualizará a "src/config/settings.py" o similar.
            "responsabilidad_principal": "Contiene todas las constantes globales, configuraciones del juego (dimensiones de pantalla, FPS, rutas, categorías de log, etc.) y parámetros de balanceo del juego.",
            "interacciones_principales": {
                "entrantes": ["Prácticamente todos los módulos del proyecto para acceder a configuraciones y constantes."],
                "salientes": [] # Solo define datos.
            },
            "componentes_clave_internos": [
                "Variables de configuración (ej. ANCHO_PANTALLA, ALTO_PANTALLA, FPS)",
                "Rutas (ej. RUTA_ASSETS, RUTA_IMAGENES)",
                "Configuraciones de logging (ej. LOG_CATEGORIAS, MODULOS_CON_LOG_PROPIO)"
            ],
            "notas_adicionales": "Archivo crítico para la configuración global. Se debe revisar y actualizar cuidadosamente."
        },
        # Futuras entradas para config_logging.py, config.py, game_initializer.py aquí
    ],
    "Entidades": [
        {
            "nombre_modulo": "jugador.py",
            "categoria": "Entidades",
            "ruta_relativa": "src/entidades/jugador.py",
            "responsabilidad_principal": "Representa al personaje principal controlado por el usuario. Gestiona su movimiento, animaciones (heredadas de EntidadBase), colisiones, y la iniciación y lógica de ataques a través del AttackProfileManager.",
            "interacciones_principales": {
                "entrantes": ["juego.py (para creación y updates)", "gestor_estado.py (para updates)"],
                "salientes": [
                    "entidad_base.py (herencia)",
                    "settings.py (configuraciones, incluyendo DEBUG_PRINT_JUGADOR_ATAQUE_CALCULO, DEBUG_PRINT_JUGADOR_RECIBIR_DANO_INFO)",
                    "asset_manager.py (para assets de animación)",
                    "collision_handler.py (para movimiento y colisión)",
                    "attack_profile_manager.py (para gestionar perfiles y parámetros de ataque)",
                    "enemigo.py (para aplicar daño a instancias de Enemigo)"
                ]
            },
            "componentes_clave_internos": [
                "Clase Jugador(EntidadBase)",
                "__init__(self, x, y, asset_manager_instance): Inicialización, carga de animaciones, configuración de hitbox específico, inicialización del AttackProfileManager.",
                "actualizar_movimiento(self, teclas_presionadas, obstaculos, mundo_ancho, mundo_alto, delta_time): Procesa input, calcula movimiento flotante, maneja colisiones con límites y llama a _mover_y_colisionar.",
                "_mover_y_colisionar(self, dx, dy, obstaculos): Wrapper para CollisionHandler.gestionar_movimiento_y_colision.",
                "atacar(self): Inicia una secuencia de ataque si no está en cooldown, usando AttackProfileManager.",
                "actualizar_ataque(self, enemigos): Gestiona la lógica de un ataque en curso, calcula hitbox de ataque, detecta colisiones con enemigos y aplica daño.",
                "update(self, teclas_presionadas, obstaculos_solidos, enemigos_sprites_para_ataque, mundo_ancho, mundo_alto, delta_time): Método principal de actualización que llama a actualizar_movimiento y actualizar_ataque.",
                "recibir_dano(self, cantidad, tipo_dano): Sobrescribe para manejar daño específico al jugador (y llama a super).",
                "dibujar_debug_ataque(self, superficie_destino, camara): Dibuja el hitbox de ataque para depuración.",
                "Variables de estado importantes: self.esta_atacando, self.pos_x_flotante, self.pos_y_flotante, self.attack_profile_manager (instancia)"
            ],
            "funciones_clave_publicas": {
                "update": "Punto de entrada principal para actualizar el estado del jugador (movimiento, ataque).",
                "atacar": "Inicia la lógica de ataque del jugador.",
                "recibir_dano": "Procesa el daño recibido por el jugador.",
                "dibujar_debug_ataque": "Visualiza el hitbox de ataque para fines de depuración."
            },
            "notas_adicionales": "Su hitbox tiene un ajuste específico en la parte inferior. Utiliza posiciones flotantes para un movimiento más preciso antes de aplicar colisiones con deltas enteros."
        },
        {
            "nombre_modulo": "entidad_base.py",
            "categoria": "Entidades",
            "ruta_relativa": "src/entidades/entidad_base.py",
            "responsabilidad_principal": "Clase base abstracta para todas las entidades interactivas del juego (Jugador, Enemigo, etc.). Proporciona funcionalidad común como ID, gestión de assets (imagen/animación), rect, hitbox, atributos de combate (vida, velocidad), recepción de daño y estado de muerte.",
            "interacciones_principales": {
                "entrantes": ["Subclases como jugador.py, enemigo.py (por herencia)", "game_initializer.py o gestor_nivel.py (para instanciación)"],
                "salientes": [
                    "asset_manager.py (para cargar imágenes/animaciones)",
                    "settings.py (para configuraciones por defecto, categorías de log)",
                    "logging (para registrar eventos y depuración)"
                ]
            },
            "componentes_clave_internos": [
                "pygame.sprite.Sprite (clase base)",
                "id_entidad (único por instancia)",
                "nombre_log_entidad (para logs)",
                "asset_manager (instancia)",
                "animaciones (dict)",
                "estado_animacion",
                "image, rect, hitbox",
                "vida_maxima, vida_actual, velocidad",
                "ha_muerto (bool)",
                "Método _cargar_animaciones_desde_config()",
                "Método _actualizar_posicion_hitbox()",
                "Método actualizar_animacion()",
                "Método recibir_dano()",
                "Método morir()",
                "Método update() (generalmente para animación)",
                "Método dibujar_hitbox() (para depuración)"
            ],
            "variables_config_clave_settings": [
                "MODO_DEBUG_LOGS",
                "LOG_CATEGORIAS",
                "DEBUG_VER_HITBOXES",
                "DEBUG_PRINT_GESTION_DANO"
            ],
            "notas_adicionales": "Gestiona el ciclo de vida básico (daño, muerte) y la actualización de animaciones. El posicionamiento del hitbox por defecto es topleft del rect + offset. La lógica de movimiento es responsabilidad de las subclases."
        },
        {
            "nombre_modulo": "enemigo.py",
            "categoria": "Entidades",
            "ruta_relativa": "src/entidades/enemigo.py",
            "responsabilidad_principal": "Representa a las entidades hostiles del juego. Implementa IA básica de seguimiento, manejo de colisiones y atributos de combate. Hereda de EntidadBase.",
            "interacciones_principales": {
                "entrantes": [
                    "gestor_estado.py (para creación, updates y gestión de su ciclo de vida)",
                    "game_initializer.py o gestor_nivel.py (para instanciación)"
                ],
                "salientes": [
                    "entidad_base.py (herencia)",
                    "settings.py (para configuraciones específicas del enemigo como vida, velocidad, IA)",
                    "collision_handler.py (para gestionar movimiento y colisiones con obstáculos y jugador)",
                    "jugador.py (indirectamente, al obtener el rect del jugador como objetivo)"
                ]
            },
            "componentes_clave_internos": [
                "Clase Enemigo(EntidadBase)",
                "Método update(objetivo_rect, grupo_obstaculos, delta_time): Lógica de IA y movimiento.",
                "Método _actualizar_posicion_hitbox(): Sobrescribe para centrar el hitbox.",
                "Método _mover_y_colisionar_con_obstaculos(...): Maneja la lógica de movimiento aplicando colisiones."
            ],
            "variables_config_clave_settings": [
                "ENEMIGO_VIDA_MAXIMA",
                "ENEMIGO_VELOCIDAD",
                "ENEMIGO_HITBOX_OFFSET_X",
                "ENEMIGO_HITBOX_OFFSET_Y",
                "ENEMIGO_DANO_ATAQUE",
                "ENEMIGO_RANGO_AGRO",
                "ENEMIGO_DIST_MIN_JUGADOR"
            ],
            "notas_adicionales": "Actualmente utiliza una imagen estática, pero la herencia de EntidadBase permitiría añadir animaciones. Su hitbox se centra en el rect, a diferencia del comportamiento por defecto de EntidadBase. El método dibujar() es redundante si se usa con un Sprite Group."
        },
        {
            "nombre_modulo": "entorno.py",
            "categoria": "Entidades",
            "ruta_relativa": "src/entidades/entorno.py",
            "responsabilidad_principal": "Define clases para los elementos del entorno del juego, principalmente obstáculos. Proporciona una clase base 'Obstaculo' para manejar características comunes como carga de assets, animación simple, escalado y hitboxes.",
            "interacciones_principales": {
                "entrantes": [
                    "gestor_nivel.py o game_initializer.py (para instanciación y colocación en el nivel)",
                    "collision_handler.py (los hitboxes de estos elementos son considerados obstáculos)",
                    "renderer.py (para dibujarlos)"
                ],
                "salientes": [
                    "pygame.sprite.Sprite (herencia para la clase Obstaculo)",
                    "asset_manager.py (para cargar las imágenes/frames de los elementos)",
                    "settings.py (para configuraciones como DEBUG_VER_HITBOXES, DEBUG_PRINT_ENTORNO, categorías de log, etc.)"
                ]
            },
            "componentes_clave_internos": [
                "Clase Obstaculo(pygame.sprite.Sprite): Clase base para elementos estáticos del entorno. Gestiona assets, animación básica, escalado y hitbox.",
                "  Método Obstaculo._cargar_y_escalar_animacion(): Carga y escala frames una vez.",
                "  Método Obstaculo.update(): Actualiza la animación.",
                "  Método Obstaculo.dibujar_hitbox(): Dibuja el hitbox para depuración.",
                "Clase Arbol(Obstaculo): Representa un árbol, especialización de Obstaculo."
            ],
            "variables_config_clave_settings": [
                "MODO_DEBUG_LOGS",
                "LOG_CATEGORIAS (para 'log_entorno')",
                "DEBUG_VER_HITBOXES",
                "DEBUG_PRINT_ENTORNO",
                "DEBUG_PRINT_ENTORNO_ANIM",
                "ROJO_ERROR_ASSET"
            ],
            "notas_adicionales": "Diseñado para ser extensible con más tipos de obstáculos heredando de 'Obstaculo'. El escalado de imágenes se realiza una vez al cargar para optimizar."
        }
    ],
    "Sistemas": [
        {
            "nombre_modulo": "collision_handler.py",
            "categoria": "Sistemas",
            "ruta_relativa": "src/sistemas/collision_handler.py",
            "responsabilidad_principal": "Gestiona la detección y resolución de colisiones entre entidades móviles y obstáculos estáticos del entorno. Proporciona un sistema de movimiento seguro en varias fases para evitar que las entidades atraviesen objetos sólidos. También incluye una función básica para detectar colisiones entre dos entidades dinámicas.",
            "interacciones_principales": {
                "entrantes": [
                    "jugador.py (y otras entidades móviles como enemigo.py) para solicitar movimiento y resolución de colisiones.",
                    "juego.py (potencialmente, si se centraliza la lógica de colisión de ataques u otras interacciones)"
                ],
                "salientes": [
                    "settings.py (para acceder a MODO_DEBUG_LOGS, LOG_CATEGORIAS['log_collision_handler'], MAX_PASADAS_RESOLUCION_ESTATICA)",
                    "logging (para un registro detallado del proceso de colisión)",
                    "Entidades (accede a sus 'hitbox' y 'rect')",
                    "Obstaculos (accede a sus 'hitbox' o 'rect')"
                ]
            },
            "componentes_clave_internos": [
                "Clase CollisionHandler (contiene métodos estáticos)",
                "Método estático principal: gestionar_movimiento_y_colision(entidad_hitbox, entidad_rect, hitbox_offset_x, hitbox_offset_y, dx, dy, obstaculos)",
                "  Fase 1: _resolver_solapamientos_estaticos_eje (pre-movimiento, iterativo)",
                "  Fase 2: _aplicar_movimiento_y_colision_eje_x / _aplicar_movimiento_y_colision_eje_y (movimiento y ajuste por eje)",
                "  Fase 3: _verificar_y_revertir_colision_post_fase2 (capa de seguridad, revierte a Fase 1 o posición original si es necesario)",
                "  Fase 4: Sincronización del rect visual de la entidad con la hitbox ajustada.",
                "Método estático: resolver_colisiones_dinamicas_entidad_a_entidad(entidad_actual, otra_entidad) (detección simple, sin resolución)",
                "Otros métodos estáticos privados de apoyo: _prevenir_teletransportacion (logging de movimientos grandes)."
            ],
            "variables_config_clave_settings": [
                "MODO_DEBUG_LOGS",
                "LOG_CATEGORIAS['log_collision_handler']",
                "MAX_PASADAS_RESOLUCION_ESTATICA"
            ],
            "notas_adicionales": "Utiliza un enfoque de resolución de colisiones por fases, separando el movimiento en ejes X e Y y aplicando correcciones. Incluye múltiples capas de seguridad para evitar que las entidades se atasquen o atraviesen obstáculos. El movimiento se aplica con truncamiento a entero. El logging es muy detallado si está activado."
        },
        {
            "nombre_modulo": "gestor_eventos.py",
            "categoria": "Sistemas",
            "ruta_relativa": "src/sistemas/gestor_eventos.py",
            "responsabilidad_principal": "Maneja todos los eventos de entrada del usuario (teclado, ratón, cierre de ventana) de Pygame. Traduce estos eventos en acciones como movimiento, ataque, zoom, cambio de perfiles de ataque y solicitud de salida del juego.",
            "interacciones_principales": {
                "entrantes": [
                    "juego.py (recibe la lista de eventos de Pygame y consulta si debe salir)"
                ],
                "salientes": [
                    "jugador.py (para iniciar ataques, acceder y modificar AttackProfileManager)",
                    "hud.py (para pasarle eventos y que el HUD los maneje)",
                    "juego.py (para actualizar el factor de zoom)",
                    "settings.py (para configuraciones de zoom, logging y teclas F)",
                    "logging (para registrar eventos procesados)"
                ]
            },
            "componentes_clave_internos": [
                "Clase GestorEventos",
                "  __init__(jugador, hud, juego_ref): Guarda referencias a jugador, HUD y la instancia del juego.",
                "  procesar_eventos(eventos_pygame): Itera sobre eventos de Pygame y dispara acciones.",
                "    Manejo de pygame.QUIT y K_ESCAPE para self.solicitud_salir.",
                "    Manejo de pygame.MOUSEWHEEL para el zoom (usa juego_ref.actualizar_factor_zoom).",
                "    Manejo de K_SPACE para jugador.atacar().",
                "    Manejo de K_PAGEUP, K_PAGEDOWN para cambiar perfiles de ataque del jugador.",
                "    Manejo de teclas F1-F10 para modificar parámetros del perfil de ataque activo (usa jugador.attack_profile_manager).",
                "  debe_salir(): Devuelve self.solicitud_salir.",
                "Atributo: solicitud_salir (bool)"
            ],
            "variables_config_clave_settings": [
                "MODO_DEBUG_LOGS",
                "LOG_CATEGORIAS['log_event_handler']",
                "LOG_CATEGORIAS['log_event_handler_verbose']",
                "FACTOR_ZOOM_PASO",
                "FACTOR_ZOOM_MIN",
                "FACTOR_ZOOM_MAX"
            ],
            "notas_adicionales": "Centraliza el manejo de input. La lógica de modificación de parámetros con teclas F es detallada. Introduce nuevas categorías de log para controlar la verbosidad de los eventos."
        },
        {
            "nombre_modulo": "gestor_estado.py",
            "categoria": "Sistemas",
            "ruta_relativa": "src/sistemas/gestor_estado.py",
            "responsabilidad_principal": "Mantiene y actualiza el estado de todas las entidades del juego (jugador, enemigos, proyectiles, etc.). Gestiona la creación y eliminación de entidades, y las interacciones básicas entre ellas como el daño por contacto.",
            "interacciones_principales": {
                "entrantes": ["juego.py (para inicialización y llamadas de update)"],
                "salientes": [
                    "settings.py", 
                    "jugador.py", "enemigo.py", "entidad_base.py", "entorno.py", 
                    "collision_handler.py (para obtener colisiones específicas)",
                    "pygame.sprite (para gestión de grupos)",
                    "logging"
                ]
            },
            "componentes_clave_internos": [
                "self.jugador (instancia)",
                "self.todos_los_sprites (pygame.sprite.Group)",
                "self.enemigos (pygame.sprite.Group)",
                "self.obstaculos (pygame.sprite.Group)",
                "self.proyectiles (pygame.sprite.Group)",
                "método actualizar_entidades()",
                "método _eliminar_entidades_muertas()",
                "método _manejar_colision_jugador_enemigo_contacto() (usa settings.ENEMIGO_DANO_CONTACTO_DEFAULT)"
            ],
            "variables_config_clave_settings": [
                "MODO_DEBUG_LOGS", "LOG_CATEGORIAS ('log_gestor_estado', 'log_gestor_estado_detalle')",
                "ANCHO_MUNDO_JUEGO", "ALTO_MUNDO_JUEGO",
                "ENEMIGO_DANO_CONTACTO_DEFAULT"
            ],
            "notas_adicionales": "Centraliza la lógica de 'quién está dónde' y 'qué está pasando'. La detección de daño por contacto entre jugador y enemigo está implementada pero puede activarse/desactivarse fácilmente. Pendiente: Optimizar la creación del grupo de obstáculos para cada enemigo si es necesario."
        }
        # Futuras entradas para gestor_nivel.py, etc. aquí
    ],
    "Renderizado": [
        # Futuras entradas para renderer.py, hud.py, camara.py aquí
    ],
    "Utilidades": [
        # Futuras entradas para utils.py aquí (asset_manager.py podría ir aquí o en Sistemas)
    ]
}

if __name__ == '__main__':
    # Ejemplo de cómo se podría acceder y usar esta información
    for categoria, modulos in MAPA_MODULOS_POR_CATEGORIA.items():
        print(f"Categoría: {categoria}")
        for modulo in modulos:
            print(f"  Módulo: {modulo['nombre_modulo']}")
            # print(f"    Ruta: {modulo['ruta_relativa']}")
            # print(f"    Responsabilidad: {modulo['responsabilidad_principal']}")
        print("-" * 20) 