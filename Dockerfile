FROM python:3.9-alpine

WORKDIR /app

COPY requierments.txt .
RUN ["pip","install","-r","requierments.txt"]

COPY . .

ARG DEFAULT_PORT=8000

EXPOSE ${DEFAULT_PORT}

CMD ["python3","manage.py","runserver","0.0.0.0:8000"]
 