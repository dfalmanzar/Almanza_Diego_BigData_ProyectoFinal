# Servicio app: dashboard Streamlit (solo lee resultados ya procesados; no repite el ETL ni reentrena)
FROM python:3.12-slim-bookworm

ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
# Se ejecuta desde la raíz del proyecto, igual que en Streamlit Community Cloud
WORKDIR /proyecto

COPY app/requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

COPY src /proyecto/src
COPY app /proyecto/app
COPY .streamlit /proyecto/.streamlit

EXPOSE 8501
HEALTHCHECK --interval=15s --timeout=5s --retries=10 CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')"
CMD ["streamlit", "run", "app/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
