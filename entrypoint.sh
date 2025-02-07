#!/bin/bash
set -e

# Função para extrair automaticamente o nome do diretório montado
get_mounted_dir() {
    local mounted_path
    mounted_path=$(find /app -mindepth 1 -maxdepth 1 -type d | head -n 1)

    if [ -z "$mounted_path" ]; then
        echo "❌ Erro: Nenhum diretório válido encontrado dentro de /app. Certifique-se de montar um volume corretamente."
        exit 1
    fi

    echo "$(basename "$mounted_path")"
}

# Verifica se o primeiro argumento é "scan"
if [ "$1" == "scan" ]; then
    # Obtém o nome do diretório montado automaticamente
    SCAN_TARGET=$(get_mounted_dir)

    echo "🚀 Iniciando o SAST Scanner no diretório: /app/$SCAN_TARGET"
    python3 /app/sast_scanner.py "$SCAN_TARGET"
else
    echo "🔹 Modo interativo ativado. Acesse o container normalmente."
    exec "$@"
fi
