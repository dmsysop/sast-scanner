FROM python:3.11-slim

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    curl \
    git \
    php-cli \
    jq \
    composer \
    && rm -rf /var/lib/apt/lists/*

# Instala Gitleaks
RUN curl -sSL https://github.com/zricethezav/gitleaks/releases/download/v8.16.1/gitleaks-linux-amd64 -o /usr/local/bin/gitleaks \
    && chmod +x /usr/local/bin/gitleaks

# Instala ferramentas de SAST
RUN pip install bandit semgrep njsscan

# Instala PHPStan globalmente
RUN composer global require phpstan/phpstan

# Configura o PATH do Composer global
ENV PATH="/root/.composer/vendor/bin:$PATH"

# Copia os arquivos do scanner para dentro do container
WORKDIR /app
COPY cache.json /app/cache.json
COPY sast_scanner.py /app/sast_scanner.py
COPY entrypoint.sh /app/entrypoint.sh
COPY .env /app/.env

# Garante que o entrypoint tenha permissões de execução
RUN chmod +x /app/entrypoint.sh

# Faz login no Semgrep CLI
RUN SEMGREP_APP_TOKEN=ee8efe4b184c0a545ff78dd9496ea4997db56eaa40b7ee38e9cd2afbf1a40f11 semgrep login

# Define o entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
