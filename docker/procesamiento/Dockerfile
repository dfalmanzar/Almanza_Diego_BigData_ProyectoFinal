# Servicio de procesamiento: JupyterLab + pandas + PySpark + scikit-learn
FROM python:3.12-slim-bookworm

# Java es necesario para PySpark (se usa para comparar tiempos pandas vs Spark)
RUN apt-get update \
    && apt-get install -y --no-install-recommends openjdk-17-jre-headless procps \
    && rm -rf /var/lib/apt/lists/*
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /proyecto
COPY docker/procesamiento/requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

EXPOSE 8888
CMD ["sh", "-c", "jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root --ServerApp.root_dir=/proyecto --IdentityProvider.token=${JUPYTER_TOKEN}"]
