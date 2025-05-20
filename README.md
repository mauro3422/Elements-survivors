# Juego Pygame Modular

**Nota Importante:** Este README es un documento vivo y evoluciona con el proyecto. Se actualizará continuamente para reflejar los cambios más recientes en la arquitectura, funcionalidades clave, y las mejores prácticas aprendidas. Se espera que futuras IAs y desarrolladores consulten y contribuyan a este documento.

## Pautas de Colaboración y Desarrollo Detalladas

**Para asegurar una colaboración efectiva, un desarrollo coherente y el mantenimiento de la calidad del código, todas las guías, reglas, protocolos de depuración, convenciones y procedimientos de contribución se han centralizado en un documento dedicado.**

**Por favor, consulta el archivo [`DEVELOPMENT_PROTOCOLS.md`](DEVELOPMENT_PROTOCOLS.md) para obtener toda la información detallada sobre cómo trabajar en este proyecto.**

Este documento (`README.md`) ahora se enfoca en la descripción general del proyecto, su estructura y cómo empezar a utilizarlo.

## Diccionario de Código / Mapa Conceptual de Módulos

*   **Propósito:** Esta sección describe un archivo complementario, `mapa_conceptual_modulos.py`, que sirve como un glosario o "mapa conceptual" de los principales módulos, clases y sistemas del juego. Su objetivo es proporcionar una visión general rápida que facilite la incorporación de nuevos colaboradores y la comprensión de la arquitectura del código.
*   **Ubicación y Formato:** El mapa conceptual detallado se encuentra en el archivo `mapa_conceptual_modulos.py`, ubicado en la raíz del proyecto. Este archivo Python contiene un diccionario principal llamado `MAPA_MODULOS_POR_CATEGORIA`. Las claves de este diccionario son cadenas que representan las categorías lógicas del proyecto (ej. "Core", "Entidades", "Sistemas"), que idealmente se alinearán con la estructura de carpetas del código fuente (ej. `src/core`, `src/entidades`). El valor asociado a cada clave de categoría es una lista de diccionarios, donde cada diccionario representa un módulo específico y típicamente incluye claves como:
    *   `nombre_modulo`: Nombre del archivo del módulo (ej. "juego.py").
    *   `categoria`: (Duplica la clave del diccionario padre para referencia interna si es útil, aunque la agrupación ya está dada por la estructura).
    *   `ruta_relativa`: Ruta al archivo desde la raíz del proyecto (ej. "juego.py" o, después de la reestructuración, "src/core/juego.py").
    *   `responsabilidad_principal`: Descripción concisa de lo que hace el módulo.
    *   `interacciones_principales`: Un diccionario con listas `entrantes` (módulos que lo usan o de los que depende) y `salientes` (módulos que usa o de los que depende).
    *   `componentes_clave_internos`: Lista de las clases o funciones más importantes dentro del módulo.
    *   `notas_adicionales`: Cualquier otra información relevante.
*   **Mantenimiento:** Este diccionario en `mapa_conceptual_modulos.py` es un esfuerzo manual y colaborativo.
    *   **Cuándo actualizar:** Se debe actualizar siempre que:
        *   Se añada un nuevo módulo principal al proyecto.
        *   Se elimine un módulo principal existente.
        *   Se refactorice un módulo existente de tal manera que su propósito central, sus responsabilidades clave o sus interacciones principales con otros módulos cambien significativamente.
        La actualización de esta sección debe considerarse parte integral del conjunto de cambios (commit/pull request) que introduce la modificación en el código. No se recomienda un umbral numérico fijo (ej. "cada X cambios"), sino un juicio basado en el impacto del cambio en la arquitectura general.
    *   **Qué actualizar (Nivel de Detalle):** El foco debe estar en:
        *   La **responsabilidad principal** del módulo (ej. "¿Qué hace `collision_handler.py`?\").
        *   Sus **interacciones clave** con otros módulos principales (ej. \"`collision_handler.py` es utilizado por `juego.py` y opera sobre instancias de `entidad_base.py`\").
        No es necesario ni recomendable listar todas las funciones internas, clases secundarias o variables de un módulo. El objetivo es mantener una visión general conceptual, no un reflejo detallado del código fuente.

## Estructura del Proyecto

### Módulos Principales

#### Core
- `main.py`: Punto de entrada principal del juego
- `juego.py`: Clase principal que maneja el bucle del juego
- `settings.py`: Configuraciones globales del juego (ruta: `src/config/settings.py`)
- `config_logging.py`: Configuración del sistema de logging (ruta: `src/config/config_logging.py`)

#### Entidades
- `entidad_base.py`: Clase base para todas las entidades del juego
- `jugador.py`: Implementación del jugador
- `enemigo.py`: Implementación de enemigos
- `entorno.py`: Elementos del entorno del juego

#### Sistemas
- `collision_handler.py`: Sistema de detección y resolución de colisiones
- `gestor_eventos.py`: Sistema de manejo de eventos
- `gestor_estado.py`: Sistema de estados del juego
- `gestor_nivel.py`: Sistema de gestión de niveles
- `attack_profile_manager.py`: Sistema de perfiles de ataque

#### Renderizado
- `renderer.py`: Sistema de renderizado
- `hud.py`: Interfaz de usuario
- `camara.py`: Sistema de cámara

#### Utilidades
- `utils.py`: Funciones de utilidad comunes
- `asset_manager.py`: Gestión de recursos (imágenes, sonidos, etc.)

### Estructura de Carpetas
```
├── assets/              # Recursos del juego
│   ├── images/         # Imágenes y sprites
│   ├── sounds/         # Efectos de sonido y música
│   └── fonts/          # Fuentes
├── src/                # Código fuente
└── tests/             # Pruebas unitarias
```

## Instalación y Ejecución

1. **Requisitos**:
   - Python 3.8+
   - Pygame 2.0+
   - Dependencias listadas en requirements.txt

2. **Instalación**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Ejecución**:
   ```bash
   python main.py
   ``` 