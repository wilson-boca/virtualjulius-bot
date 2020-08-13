# Dockerfile
FROM python:3.7-stretch
RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential
RUN apt-get install tesseract-ocr -y
RUN apt-get install tesseract-ocr-dev -y
RUN apt-get install tesseract-ocr-eng -y

COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt

ENV PORT 8080
ENV URL https://myfirstbot-jrjizbmqqa-uc.a.run.app/

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 app:app