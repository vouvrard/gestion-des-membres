FROM python:3.10-slim-buster

RUN mkdir /usr/src/keycloakapp/

WORKDIR /usr/src/keycloakapp/
COPY keycloakapp/ ./keycloakapp/
COPY run.py .
COPY .docker/requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

CMD ["python3", "run.py"]
