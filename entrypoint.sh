#!/bin/sh

# Diretório onde o código será montado
SCAN_DIR="/app/code"
CACHE_FILE="/app/cache.json"

# Garante que o diretório de código foi montado
if [ ! -d "$SCAN_DIR" ]; then
    echo "❌ Erro: Nenhum diretório montado em $SCAN_DIR"
    exit 1
fi

# Inicializa o cache se não existir
if [ ! -f "$CACHE_FILE" ]; then
    echo "{}" > "$CACHE_FILE"
fi

# Função para calcular hash de arquivos
calculate_hash() {
    sha256sum "$1" | awk '{print $1}'
}

# Carrega cache
CACHE=$(cat "$CACHE_FILE")
NEW_CACHE="{}"

# Verifica e escaneia arquivos modificados
for FILE in $(find "$SCAN_DIR" -type f -name "*.py" -o -name "*.php"); do
    FILE_HASH=$(calculate_hash "$FILE")
    STORED_HASH=$(echo "$CACHE" | jq -r --arg f "$FILE" '.[$f] // empty')
    
    if [ "$FILE_HASH" != "$STORED_HASH" ]; then
        echo "🔍 Escaneando $FILE..."
        if echo "$FILE" | grep -q "\.py$"; then
            bandit -r "$FILE"
        elif echo "$FILE" | grep -q "\.php$"; then
            phpstan analyse "$FILE"
            psalm --root="$SCAN_DIR" "$FILE"
        fi
    else
        echo "✅ Ignorando $FILE (sem mudanças)"
    fi
    NEW_CACHE=$(echo "$NEW_CACHE" | jq --arg f "$FILE" --arg h "$FILE_HASH" '. + {($f): $h}')

done

# Salva o novo cache
echo "$NEW_CACHE" > "$CACHE_FILE"

# Executa Semgrep para análise genérica
echo "🔍 Rodando Semgrep..."
semgrep scan --config=auto "$SCAN_DIR"

# Finaliza
echo "✅ Análise concluída!"