FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

# Install Python3, pip, node, npm, and typescript
RUN apt-get update
RUN apt-get install -y python3 python3-pip nodejs npm
RUN apt-get clean

# Install dependencies for pyenv
RUN apt-get install -y make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python-openssl git

# Install pyenv
RUN curl https://pyenv.run | bash

# Set environment variables for pyenv
ENV PATH="/root/.pyenv/bin:/root/.pyenv/shims:$PATH"
RUN echo 'export PYENV_ROOT="$HOME/.pyenv"' >>~/.bashrc
RUN echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >>~/.bashrc
RUN echo 'eval "$(pyenv init --path)"' >>~/.bashrc
RUN echo 'eval "$(pyenv init -)"' >>~/.bashrc

# Install Python 3.9.6 using pyenv
RUN pyenv install 3.9.6
RUN pyenv global 3.9.6

# Update node to v20.10.0
RUN npm install -g n
RUN n 20.10.0
RUN npm install -g typescript

WORKDIR /app
COPY . /app
COPY .dockerignore /app/.dockerignore

RUN chmod +x install.sh
RUN ./install.sh
