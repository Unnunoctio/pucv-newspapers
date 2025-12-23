# Crawler de Periódicos (PUCV Newspapers)

Este proyecto es un sistema de web scraping diseñado para extraer artículos de noticias de diversos periódicos chilenos (como Cooperativa, El Desconcierto, El Mostrador, Radio UChile, TVN, Ciper, Emol, etc.). Permite la ejecución manual o programada de crawlers para recopilar titulares, autores, fechas, etiquetas y contenido de las noticias, almacenándolos en una base de datos MongoDB o exportándolos a Excel.

## Requisitos Previos

- Python 3.8 o superior.
- Acceso a internet.
- (Opcional) Acceso a una base de datos MongoDB si se usa el modo de almacenamiento en base de datos.
- (Opcional) Google Chrome instalado si algún crawler requiere selenium (aunque la configuración actual parece usar peticiones HTTP directas o APIs).

## Instalación

1.  **Clonar el repositorio** (si aún no lo has hecho):
    ```bash
    git clone https://github.com/Unnunoctio/pucv-newspapers.git
    cd pucv-newspapers
    ```

2.  **Crear un entorno virtual** (recomendado):
    ```bash
    # En Windows
    python -m venv venv
    .\venv\Scripts\activate

    # En macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Instalar dependencias**:
    ```bash
    pip install -r requirements.txt
    ```

## Configuración

La configuración del proyecto se divide principalmente en dos archivos: `src/config.yaml` para la definición de los crawlers y `src/index.py` para la lógica de ejecución.

### 1. Configuración de Crawlers (`src/config.yaml`)

Este archivo define CÓMO se extrae la información de cada sitio web. Aquí puedes ajustar selectores CSS, URLs base y comportamientos de paginación.

Estructura básica para un sitio estático:
```yaml
crawlers:
  - name: NOMBRE_DEL_MEDIO
    type: STATIC_WEBSITE # o API
    base_urls:
      - https://www.ejemplo.cl/seccion
    
    requests_config:
      retry_delay: 60 # Tiempo de espera entre reintentos
      requests_per_minute: 1800 # Límite de peticiones
    
    pages_config:
      url_pattern: ... # Regex para identificar URLs válidas
      pagination: ... # Selectores para la paginación
    
    articles_list_config: ... # Selectores para encontrar la lista de artículos
    
    article_config: ... # Selectores para título, autor, fecha, cuerpo, etc.
```
Si un sitio cambia su diseño, deberás actualizar los selectores en este archivo.

### 2. Configuración de Ejecución (`src/index.py`)

Este archivo controla QUÉ crawlers se ejecutan y DÓNDE se guardan los datos.

#### Selección de Crawlers
En la variable `CRAWLERS_TO_RUN`, cambia `True` o `False` para activar/desactivar periódicos específicos:
```python
CRAWLERS_TO_RUN = {
    # "ADN_RADIO": False,
    "COOPERATIVA": False,
    "TVN_ACTUALIDAD": True, # Este se ejecutará
    # ...
}
```

#### Modos de Ejecución
Existen dos modos controlados por la variable `IS_MANUAL`:

**A. Modo Manual (`IS_MANUAL = True`)**
- Útil para extracciones puntuales o pruebas.
- Define el rango de fechas en `START_DATE` y `END_DATE`.
- Los datos se guardan usando `DataStorage("EXCEL")` (por defecto exporta a Excel, revisa `services/data_storage.py` para detalles).

**B. Modo Automático / Programado (`IS_MANUAL = False`)**
- Diseñado para ejecución continua (servidor).
- Se conecta a MongoDB. Configura tu URI en `MONGO_URI` y el nombre de la base de datos en `MONGO_DATABASE`.
- Utiliza `APScheduler` para ejecutar la tarea periódicamente según `CRON_SCHEDULE` (por defecto a las 8:00 AM todos los días).
- En este modo, el sistema verifica la última fecha guardada en la base de datos para cada crawler y continúa desde ahí hasta la fecha actual.

## Ejecución

Para iniciar el programa, asegúrate de estar en la raíz del proyecto y con el entorno virtual activado:

```bash
python src/index.py
```

- Si está en modo **Manual**, el script se ejecutará una vez y terminará.
- Si está en modo **Automático**, el script se mantendrá en ejecución esperando la hora programada en el cron.

## Ejecución con Docker

### Construir la imagen

```bash
docker build -t pucv-newspapers .
```

### Correr el contenedor

**Modo Manual (para pruebas):**
```bash
docker run --rm -v $(pwd)/newspapers:/app/newspapers pucv-newspapers
```
*Esto montará la carpeta local `newspapers` para que los archivos generados persistan en tu máquina.*

**Modo Servicio (Automático):**
```bash
docker run -d --name pucv-bot -v $(pwd)/newspapers:/app/newspapers pucv-newspapers
```
*Asegúrate de configurar `IS_MANUAL = False` y la conexión a MongoDB en `src/index.py` (o pasar variables de entorno si se adaptara el código).*

## Estructura del Proyecto

*   `newspapers/`: Directorio donde se guardan los archivos Excel generados en modo manual.
*   `src/`: Código fuente.
    *   `config.yaml`: Configuración de selectores y sitios.
    *   `index.py`: Punto de entrada principal.
    *   `crawlers/`: Lógica base de los crawlers.
    *   `db/`: Conexión y manejo de base de datos (MongoDB).
    *   `services/`: Servicios de negocio (CrawlerService, DataStorage).
    *   `utils/`: Utilidades varias.
