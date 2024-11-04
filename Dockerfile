FROM ubuntu:20.04

# Install Python3, pip, node, npm, and typescript
RUN apt-get update
RUN apt-get install -y python3 python3-pip nodejs npm
RUN npm install -g typescript
RUN apt-get clean

WORKDIR /app
COPY . /app
COPY .dockerignore /app/.dockerignore

RUN chmod +x install.sh
RUN ./install.sh
