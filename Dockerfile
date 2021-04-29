FROM python:3.7-alpine
LABEL maintainer="Tru Inc."

# docker specific environment variable for python to prevent buffering
ENV PYTHONUNBUFFERED 1

# install requirements / dependencies
COPY ./requirements.txt /requirements.txt
RUN apk add --update --no-cache postgresql-client
RUN apk add --update --no-cache --virtual .tmp-build-deps \
        gcc libc-dev linux-headers postgresql-dev
RUN pip install -r /requirements.txt
RUN apk del .tmp-build-deps

# Setup directories
RUN mkdir /app
WORKDIR /app
COPY ./app /app

# Create low priv user
RUN adduser -D appuser
USER appuser