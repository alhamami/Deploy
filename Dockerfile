# syntax=docker/dockerfile:1
FROM python:3.7-alpine
WORKDIR /
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
RUN apk add --no-cache gcc musl-dev linux-headers
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y
EXPOSE 5000
COPY . .
CMD ["flask", "run"]


