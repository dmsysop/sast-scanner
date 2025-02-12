FROM python:3.11-slim

ARG SEMGREP_APP_TOKEN
ENV SEMGREP_APP_TOKEN=$SEMGREP_APP_TOKEN

# Instala dependências do sistema, incluindo Node.js e npm
RUN apt-get update && apt-get install -y \
    curl \
    git \
    php-cli \
    jq \
    composer \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Instala Gitleaks
RUN curl -sSL https://github.com/zricethezav/gitleaks/releases/download/v8.16.1/gitleaks-linux-amd64 -o /usr/local/bin/gitleaks \
    && chmod +x /usr/local/bin/gitleaks

COPY requirements.txt /app/requirements.txt

#Atualiza a versão do PIP
RUN pip install --upgrade pip

# Instala dependências do Python, incluindo pymongo e dotenv
RUN pip install --no-cache-dir -r /app/requirements.txt pymongo python-dotenv

# Instala ferramentas de SAST
RUN pip install bandit semgrep njsscan

# Garante a atualização do Semgrep
RUN pip install --upgrade semgrep

# Instalar dependências do Composer
RUN composer global require --dev phpstan/phpstan

# Garantir que o diretório global do Composer esteja no PATH
ENV PATH="$PATH:/root/.config/composer/vendor/bin"

# Copia os arquivos do scanner para dentro do container
WORKDIR /app
COPY .env /app/.env
COPY sast_scanner.py /app/sast_scanner.py
COPY entrypoint.sh /app/entrypoint.sh

# Garante que o entrypoint tenha permissões de execução
RUN chmod +x /app/entrypoint.sh

# Faz login no Semgrep CLI
RUN SEMGREP_APP_TOKEN=$SEMGREP_APP_TOKEN semgrep login

# Define o entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
