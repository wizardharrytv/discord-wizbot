FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["watchmedo", "auto-restart", \
     "--directory=/app", \
     "--pattern=*.py", \
     "--recursive", \
     "--", \
     "python", "main.py"]
