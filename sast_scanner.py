import os
import json
import hashlib
import subprocess
from pathlib import Path

# Diretório onde os arquivos do projeto serão montados
SCAN_DIR = "/app/code"
CACHE_FILE = "/app/cache.json"

# Função para calcular o hash de um arquivo
def calculate_hash(file_path):
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        hasher.update(f.read())
    return hasher.hexdigest()

# Carrega ou inicializa o cache
def load_cache():
    if Path(CACHE_FILE).exists():
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=4)

# Função para executar comandos e capturar saída
def run_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"⚠ Erro ao executar {command}: {e.stderr}")

# Executa análise nos arquivos modificados
def run_sast_scan():
    if not Path(SCAN_DIR).exists():
        print("❌ Erro: Nenhum diretório montado em /app/code")
        return
    
    cache = load_cache()
    new_cache = {}
    
    for file_path in Path(SCAN_DIR).rglob("*.py"):
        file_hash = calculate_hash(file_path)
        if cache.get(str(file_path)) != file_hash:
            print(f"🔍 Escaneando {file_path}...")
            run_command(f"bandit -r {file_path}")
        else:
            print(f"✅ Ignorando {file_path} (sem mudanças)")
        new_cache[str(file_path)] = file_hash
    
    for file_path in Path(SCAN_DIR).rglob("*.php"):
        file_hash = calculate_hash(file_path)
        if cache.get(str(file_path)) != file_hash:
            print(f"🔍 Escaneando {file_path}...")
            run_command(f"phpstan analyse {file_path}")
            run_command(f"psalm --root={SCAN_DIR} {file_path}")
        else:
            print(f"✅ Ignorando {file_path} (sem mudanças)")
        new_cache[str(file_path)] = file_hash
    
    save_cache(new_cache)
    print("🔍 Rodando Semgrep...")
    run_command(f"semgrep scan --config=auto {SCAN_DIR}")
    print("✅ Análise concluída!")

if __name__ == "__main__":
    run_sast_scan()
