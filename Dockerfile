FROM python:3.11-slim

ARG SEMGREP_APP_TOKEN
ENV SEMGREP_APP_TOKEN=$SEMGREP_APP_TOKEN

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

# Garante que o entrypoint tenha permissões de execução
RUN chmod +x /app/entrypoint.sh

# Faz login no Semgrep CLI
RUN SEMGREP_APP_TOKEN=$SEMGREP_APP_TOKEN semgrep login

# Define o entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
