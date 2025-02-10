#!/bin/bash

# Carregar as variáveis do .env
export $(grep -v '^#' .env | xargs)

# Construir a imagem, passando as variáveis como build args
docker build --build-arg SEMGREP_APP_TOKEN=$SEMGREP_APP_TOKEN -t sast-scanner .
