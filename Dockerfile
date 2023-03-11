FROM python:3.8.3-slim

WORKDIR /bot
COPY . .

RUN apt update

RUN pip install --upgrade pip
RUN apt install libpq-dev gcc -y

RUN pip install telethon==1.24.0
RUN pip install flask
RUN pip install psycopg2


CMD ["python", "./spy.py"]
