FROM python:3.10.19-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements/base.txt requirements/base.txt
RUN pip install --no-cache-dir -r requirements/base.txt

COPY app app
COPY server.py server.py

EXPOSE 8000

CMD ["python", "-m", "app.main"]
