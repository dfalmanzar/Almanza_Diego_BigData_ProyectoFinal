# Violencia armada: conflicto global y homicidios en Colombia
**Gerencia y almacenamiento en Big Data — Proyecto final** · Diego Almanza

Pipeline de Big Data completo (CRISP-DM, ETL, OLAP, Machine Learning, MongoDB, reporte PDF y dashboard web), empaquetado en Docker y ejecutable con un solo comando.

**Pregunta de negocio.** ¿Dónde es más densa la violencia armada organizada en el mundo y cómo ha cambiado el homicidio en Colombia? ¿Se puede estimar, a partir de dónde, cuándo y con qué arma ocurrió un homicidio, a qué tipo de violencia pertenece (conflicto armado, crimen organizado y sicariato, riñas o delincuencia común)?

**Video de sustentación:** _(pegar aquí el enlace al video)_

## Datos
Fuentes oficiales y públicas, sin datos sintéticos:

| Fuente | Periodo | Registros | Página web | Descarga usada por el script |
|---|---|---|---|---|
| UCDP Georeferenced Event Dataset 26.1 (Uppsala University) | 1989–2025 | 417.968 eventos | [ucdp.uu.se/downloads](https://ucdp.uu.se/downloads/) | [ged261-csv.zip](https://ucdp.uu.se/downloads/ged/ged261-csv.zip) |
| UCDP Candidate Events 26.01.26.09 | ene–sep 2026 | 16.633 eventos | [ucdp.uu.se/downloads](https://ucdp.uu.se/downloads/) | [GEDEvent_v26_01_26_09.csv](https://ucdp.uu.se/downloads/candidateged/GEDEvent_v26_01_26_09.csv) |
| Homicidios — Ministerio de Defensa Nacional (datos.gov.co `m8fd-ahd9`) | 2003–sep 2026 | 345.195 filas | [datos.gov.co/d/m8fd-ahd9](https://www.datos.gov.co/d/m8fd-ahd9) | API CSV de datos.gov.co |
| Límites de países Natural Earth 1:50m v5.1.2 (solo para el mapa) | — | 241 países | [naturalearthdata.com](https://www.naturalearthdata.com/) | GeoJSON del repositorio oficial |

**Total: 779.796 registros reales.** Los datos crudos no están en el repositorio (pesan unos 400 MB): se descargan solos al levantar el proyecto.

## Dashboard
Aplicación Streamlit en http://localhost:8501 con cinco secciones: **Resumen** (mapamundi en proyección de áreas iguales con las muertes por cada 1.000 km² y selector de años), **Datos** (tabla filtrable, descarga CSV y tablas dinámicas OLAP), **Visualizaciones** (gráficas interactivas del mundo y de Colombia con filtros), **Modelo** (métricas, comparación con la línea base, matriz de confusión y formulario de predicción) e **Insights y reporte** (leídos desde MongoDB, con descarga del PDF). El sistema visual está documentado en [`DESIGN.md`](DESIGN.md).

| Resumen | Modelo |
|---|---|
| ![Resumen con el mapamundi](evidencias/capturas/resumen_mapa.png) | ![Página del modelo](evidencias/capturas/modelo.png) |
| ![Detalle de un país](evidencias/capturas/resumen_tooltip.png) | ![Visualizaciones de Colombia](evidencias/capturas/visualizaciones_colombia.png) |

## Requisitos
- Docker Desktop (o Docker Engine) con Docker Compose v2
- Unos 2 GB libres de RAM para los contenedores y 1 GB de disco para los datos
- Python 3.10+ en el equipo solo si se quiere ejecutar el script de descarga fuera de Docker

## Cómo ejecutar
1. Clonar el repositorio y copiar las credenciales de ejemplo (luego cambiar los valores dentro de `.env`):
   ```bash
   git clone https://github.com/dfalmanzar/Almanza_Diego_BigData_ProyectoFinal.git
   cd Almanza_Diego_BigData_ProyectoFinal
   cp .env.example .env
   ```
   En Windows (CMD o PowerShell) el último comando es `copy .env.example .env`.
2. Levantar todo con un solo comando:
   ```bash
   docker compose up --build
   ```
   El servicio `pipeline` (`src/pipeline.py`) hace el procesamiento completo y termina; el dashboard arranca cuando el pipeline sale sin errores:
   1. descarga los datos crudos en `data/raw/` (`src/descargar_datos.py`);
   2. ejecuta el notebook de principio a fin en un kernel limpio (equivalente a *Restart & Run All*): ETL, OLAP, modelo, documento en MongoDB y reporte PDF;
   3. prepara `data/processed/mapa_mundo.json` para el mapamundi (`src/mapa_mundo.py`).

   La primera vez tarda unos 10 minutos (descarga de unos 100 MB, ejecución del notebook y entrenamiento del modelo). Las siguientes veces cada paso comprueba si sus resultados ya existen y se omite, así que todo queda arriba en segundos. Para rehacer todo: `PIPELINE_FORZAR=1` en el `.env`, o `docker compose run --rm pipeline python src/pipeline.py --forzar`.
3. Abrir el dashboard en http://localhost:8501.
4. (Opcional) Explorar el notebook en JupyterLab: http://localhost:8888, con el valor de `JUPYTER_TOKEN` del `.env` como token.

**Evidencia:** [`evidencias/docker_compose_up_desde_cero.log`](evidencias/docker_compose_up_desde_cero.log) guarda los logs de una ejecución desde cero (sin datos, modelo, reporte ni MongoDB): descarga en 77 s, notebook completo en 493 s, mapa en 25 s, pipeline con código 0, un documento de análisis en MongoDB y el dashboard respondiendo HTTP 200.

Para seguir el avance del pipeline en otra terminal: `docker compose logs -f pipeline`. Tras editar `app/componentes/mapa_hero.html` hay que reiniciar el dashboard (`docker compose restart app`), porque el HTML del mapa queda en caché.

### Puertos
| Servicio | Contenedor | Puerto en el equipo | Puerto interno |
|---|---|---|---|
| Pipeline (se ejecuta y termina) | `va-pipeline` | — | — |
| JupyterLab (procesamiento) | `va-procesamiento` | 8888 (`JUPYTER_PUERTO_HOST`) | 8888 |
| MongoDB | `va-mongo` | 27018 (`MONGO_PUERTO_HOST`) | 27017 |
| Dashboard Streamlit | `va-app` | 8501 (`APP_PUERTO_HOST`) | 8501 |

Dentro de la red de Docker, el notebook se conecta a Mongo con `mongodb://usuario:clave@mongo:27017/` (variable `MONGO_URI`), es decir, por el nombre del servicio y no por `localhost`.

### Cómo verificar que todo funciona
```bash
docker compose ps -a
```
`va-mongo` debe aparecer `healthy`, `va-app` `healthy`, `va-procesamiento` `running` y `va-pipeline` como `Exited (0)` (terminó sin errores).

El documento de análisis debe existir en MongoDB:
```bash
docker compose exec mongo sh -c 'mongosh -u "$MONGO_INITDB_ROOT_USERNAME" -p "$MONGO_INITDB_ROOT_PASSWORD" --quiet --eval "db.getSiblingDB(\"violencia_armada\").analisis.countDocuments()"'
```
Debe responder `1`. El reporte PDF queda en `reports/reporte_violencia_armada.pdf` y se puede regenerar desde MongoDB sin volver a ejecutar el notebook:
```bash
docker compose exec procesamiento python src/generar_reporte.py
```

### Qué produce el pipeline
| Carpeta | Contenido |
|---|---|
| `data/processed/` | Parquet limpios: homicidios, eventos UCDP, cubos OLAP y panel mensual UCDP; `mapa_mundo.json` para el mapamundi del dashboard |
| `models/` | Modelo Random Forest (`modelo_categoria_violencia.joblib`, 76 MB: no se sube a GitHub y el pipeline lo vuelve a entrenar) y `metadatos_modelo.json` |
| `reports/` | Reporte PDF generado desde MongoDB y las figuras en `reports/figuras/` |
| MongoDB `violencia_armada.analisis` | Documento con metadata, calidad, estadísticas, agregaciones, modelo, insights, visualizaciones y recomendaciones |

## Estructura
```
Almanza_Diego_BigData_ProyectoFinal/
├── README.md
├── docker-compose.yml       # mongo, pipeline, procesamiento (Jupyter) y app
├── .env.example             # Plantilla de credenciales (el .env real no se sube)
├── DESIGN.md / PRODUCT.md   # Sistema visual y contexto de producto del dashboard
├── docker/procesamiento/    # Dockerfile y requirements del servicio Jupyter
├── data/
│   ├── raw/                 # Vacía en la entrega; la llena src/descargar_datos.py
│   └── processed/           # Parquet limpio y mapa_mundo.json
├── notebooks/
│   └── Almanza_Diego_BigData_ProyectoFinal.ipynb
├── src/                     # pipeline.py, descarga, ETL, modelo, OLAP, mapa y PDF
├── models/                  # Modelo entrenado
├── reports/                 # Reporte PDF y figuras
├── evidencias/              # Logs de docker compose y capturas del dashboard
└── app/                     # Dashboard Streamlit: app.py, tema.py, datos.py, paginas/, componentes/ (mapa), static/ (fuentes y marca)
```

## Problemas de infraestructura documentados
### 1. Docker Desktop no arranca: sockets huérfanos que Windows no deja borrar
**Síntoma.** Docker Desktop 4.76 abría una ventana de error con solo dos opciones (*Quit* y *Reset to factory defaults*). `docker info` se quedaba colgado y `wsl -l -v` mostraba la máquina `docker-desktop` en estado `Stopped`.

**Diagnóstico paso a paso.**
1. El log del backend (`%LOCALAPPDATA%\Docker\log\host\com.docker.backend.exe.log`) mostraba el error real:
   `initializing Inference manager: listening on unix://...\Docker\run\dockerInference: remove ...: The file cannot be accessed by the system`.
2. En `%LOCALAPPDATA%\Docker\run\` había tres archivos de 0 bytes del 1 de septiembre de 2026 con atributo `ReparsePoint`. Son *sockets Unix* (AF_UNIX) que Docker crea al arrancar y que quedaron huérfanos tras un cierre forzado.
3. `fsutil reparsepoint query` devolvía `Error 1920: El sistema no tiene acceso al archivo`, y ni `Remove-Item -Force` ni `del /f` podían borrarlos. Docker intenta borrarlos antes de crear uno nuevo y, al fallar, cancela todo el arranque.
4. Al saltar ese error apareció el mismo problema en `%LOCALAPPDATA%\docker-secrets-engine\engine.sock`. Se buscaron todos los archivos `ReparsePoint` en las carpetas de Docker para encontrarlos de una vez.

**Solución.**
1. Cerrar Docker Desktop.
2. Como Windows no deja borrar los sockets pero sí renombrar la carpeta que los contiene, renombrar `%LOCALAPPDATA%\Docker\run` y `%LOCALAPPDATA%\docker-secrets-engine` (por ejemplo, con el sufijo `_viejo`).
3. Volver a abrir Docker Desktop: crea carpetas nuevas y limpias, y el motor arranca (Docker Engine 29.5.2).

**Prevención.** Cerrar Docker Desktop siempre con *Quit Docker Desktop* desde el ícono de la bandeja, no matando el proceso. Un socket creado justo antes de un cierre forzado quedó igual de bloqueado durante las pruebas.

### 2. El notebook muere sin mensaje de error: Spark retiene memoria después de `spark.stop()`
**Síntoma.** La ejecución completa del notebook (`jupyter nbconvert --execute`) duró 40 minutos y terminó sin guardar resultados ni mostrar error. El contenedor seguía activo (`OOMKilled=false`), pero el proceso de ejecución había muerto.

**Diagnóstico paso a paso.**
1. Se ejecutó por separado solo la parte de Machine Learning con un script que mide tiempo y memoria (`/proc/meminfo` y `resource.getrusage`). Los tres modelos entrenaron en menos de un minuto cada uno, con un pico de 0,95 GB: el modelo no era el problema.
2. Como la diferencia con el notebook era la sección de Spark, se midió la memoria de los procesos Java (`ps -eo rss,comm`) en tres momentos: con Spark activo, 950 MB; **después de `spark.stop()`, 947 MB**; y después de cerrar el puente Py4J, ningún proceso Java.
3. Conclusión: `spark.stop()` detiene el contexto pero no termina la JVM que lanzó PySpark. Esos ~930 MB retenidos, sumados a los DataFrames del ETL y al entrenamiento (con `n_jobs=-1`), superaban los 3,7 GB del contenedor. El sistema empezó a usar memoria de intercambio (de ahí los 40 minutos) y terminó matando el proceso.

**Solución.**
- Después de `spark.stop()`, cerrar el puente Py4J y terminar el proceso Java (`SparkContext._gateway.shutdown()` y `proc.kill()`). El notebook imprime la memoria de Java antes y después para dejar la evidencia.
- Limitar el Random Forest a `n_jobs=4` para reducir el pico de memoria del entrenamiento.
