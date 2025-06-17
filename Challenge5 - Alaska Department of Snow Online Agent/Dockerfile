FROM python:3.10-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

# Streamlit must listen on port 8080, not 8501 (Cloud Run requirement)
ENV PORT = 8080

CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.enableCORS=false"]

