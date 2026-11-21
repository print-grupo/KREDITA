FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 DATABASE_URL=/app/data/kredita.db
WORKDIR /app/backend

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn==23.0.0 \
    && useradd --system --no-create-home kredita \
    && mkdir -p /app/data && chown kredita:kredita /app/data

COPY backend/app.py backend/consultas.py backend/importar_kredita.py ./
COPY backend/dados/ dados/
COPY backend/banco_de_dados/ banco_de_dados/
COPY --chown=kredita:kredita frontend/ /app/frontend/

USER kredita
EXPOSE 8080
CMD ["sh", "-ec", "python importar_kredita.py && exec gunicorn --bind 0.0.0.0:8080 --workers 2 app:app"]
