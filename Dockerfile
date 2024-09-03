FROM python:3.10-slim

# Install supervisor
RUN apt-get update && apt-get install -y supervisor
RUN apt-get -y install git

RUN mkdir app

RUN cd app

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

# TODO: Add all your environment variables here
ARG DATABASE_URI
ENV DATABASE_URI=${DATABASE_URI}

ARG OPENAI_API_KEY
ENV OPENAI_API_KEY=${OPENAI_API_KEY}

# RUN flask db upgrade

EXPOSE 80

CMD bash -c "supervisord -c supervisord.conf"