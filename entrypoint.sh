#!/bin/bash
set -e

# Verifica se o primeiro argumento é "scan"
if [ "$1" == "scan" ]; then
    echo "🚀 Iniciando o SAST Scanner..."
    python3 /app/sast_scanner.py $2
else
    # Se não for "scan", executa o comando passado ou inicia um shell interativo
    echo "🔹 Modo interativo ativado. Acesse o container normalmente."
    exec "$@"
fi
