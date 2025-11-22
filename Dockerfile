#FROM python:3.11-slim
FROM alpine:3.18

WORKDIR /app

RUN apk add --no-cache python3 py3-pip

COPY requirements.txt .


RUN pip install --no-cache-dir -r requirements.txt


COPY app.py .
COPY database.py .
COPY routes/ ./routes/
COPY services/ ./services/
COPY templates/ ./templates/  
COPY library.db .
COPY banner.png .
#COPY catalog_verification_failure .

EXPOSE 5000

#CMD ["python", "app.py"]

ENV FLASK_APP=app.py

CMD ["flask", "run", "--host=127.0.0.1", "--port=5000"]