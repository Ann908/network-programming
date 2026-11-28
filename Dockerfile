FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN useradd --create-home appuser && install -d -o appuser -g appuser /app/instance
COPY lab3_v2.py wsgi.py ./

USER appuser
EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--preload", "--workers", "2", "wsgi:app"]