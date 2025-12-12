FROM python:3.14-slim

LABEL org.opencontainers.image.source="https://github.com/JarydMeek/Bumprr"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-u",  "bumprr/main.py"]