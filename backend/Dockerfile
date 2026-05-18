FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Instala dependências
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copia o backend
COPY backend /app

ENV PORT=8000
EXPOSE 8000

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
