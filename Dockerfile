FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

COPY api ./api

EXPOSE 8080

CMD ["python", "api/index.py"]
