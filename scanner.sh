#!/bin/bash

#ESTE SCRIPT DEVE FICAR NA RAIZ ONDE SEUS PROJETOS ESTÃO LOCALIZADOS
#COPIE-O PARA SUA PASTA RAIZ (Ex. /home/usuario/Projetos) E CONCEDA PERMISSÃO DE EXECUÇÃO
# - chmod +x scanner.sh
#EXECUTE O SCRIPT ./scanner.sh projeto (onde projeto é sua pasta onde o projeto está localizado)

# Verifica se um argumento foi passado
if [ -z "$1" ]; then
    echo "Uso: $0 <nome_do_diretorio>"
    exit 1
fi

# Define a variável com o nome do diretório
DIR_NAME="$1"

# Executa o comando Docker com o diretório informado
docker run --rm -v "$(pwd)/$DIR_NAME:/app/$DIR_NAME" sast-scanner scan "$DIR_NAME"