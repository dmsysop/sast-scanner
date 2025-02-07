FROM python:3.11-slim

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    curl \
    git \
    php-cli \
    jq \
    composer \
    && rm -rf /var/lib/apt/lists/*

# Instala ferramentas de SAST
RUN pip install bandit semgrep
RUN composer global require phpstan/phpstan vimeo/psalm

# Configura o PATH do Composer global
ENV PATH="/root/.composer/vendor/bin:$PATH"

# Copia os arquivos do scanner para dentro do contêiner
WORKDIR /app
COPY psalm/psalm.xml.dist /app/psalm.xml.dist
COPY sast_scanner.py /app/sast_scanner.py
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Define o entrypoint
ENTRYPOINT ["/bin/sh", "/app/entrypoint.sh"]
