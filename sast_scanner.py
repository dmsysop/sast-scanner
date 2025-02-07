import os
import sys
import json
import hashlib
import subprocess
from pathlib import Path

destination = sys.argv[1]

if len(sys.argv) < 2:
    print("❌ Erro: Caminho do projeto não informado.")
    sys.exit(1)

# Diretório onde os arquivos do projeto serão montados
SCAN_DIR = f"/app/{destination}"
CACHE_FILE = "/app/cache.json"

print(f"Scanning directory: {SCAN_DIR}")

# Função para calcular o hash de um arquivo
def calculate_hash(file_path):
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        hasher.update(f.read())
    return hasher.hexdigest()

# Carrega ou inicializa o cache
def load_cache():
    if not Path(CACHE_FILE).exists():
        with open(CACHE_FILE, "w") as f:
            json.dump({}, f)
    with open(CACHE_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            print(f"⚠ Erro ao ler o arquivo de cache {CACHE_FILE}, inicializando cache vazio.")
            return {}

def save_cache(cache):
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=4)

# Função para executar comandos e capturar saída
def run_command(command):
    try:
        result = subprocess.run(command, shell=False, check=True, capture_output=True, text=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"⚠ Erro ao executar o comando {' '.join(command)}: {e.stderr}")

# Executa análise nos arquivos modificados
def run_sast_scan():
    if not Path(SCAN_DIR).exists():
        print(f"❌ Erro: Nenhum diretório montado em /app/{destination}")
        return
    
    cache = load_cache()
    new_cache = {}

    # Análise para arquivos Python com Bandit
    for file_path in Path(SCAN_DIR).rglob("*.py"):
        file_hash = calculate_hash(file_path)
        if cache.get(str(file_path)) != file_hash:
            print(f"🔍 Escaneando {file_path}...")
            run_command(["bandit", "-r", str(file_path)])
        else:
            print(f"✅ Ignorando {file_path} (sem mudanças)")
        new_cache[str(file_path)] = file_hash

    # Análise para arquivos PHP com PHPStan e Psalm
    for file_path in Path(SCAN_DIR).rglob("*.php"):
        file_hash = calculate_hash(file_path)
        if cache.get(str(file_path)) != file_hash:
            print(f"🔍 Escaneando {file_path}...")
            run_command(["phpstan", "analyse", str(file_path)])
            # run_command(["psalm", "--root=" + str(SCAN_DIR), str(file_path)])
        else:
            print(f"✅ Ignorando {file_path} (sem mudanças)")
        new_cache[str(file_path)] = file_hash

    # Análise para arquivos JavaScript/TypeScript com njsscan
    for file_path in Path(SCAN_DIR).rglob("*.js"):
        file_hash = calculate_hash(file_path)
        if cache.get(str(file_path)) != file_hash:
            print(f"🔍 Escaneando {file_path} com njsscan...")
            run_command(['njsscan', str(file_path), '--json'])
        else:
            print(f"✅ Ignorando {file_path} (sem mudanças)")
        new_cache[str(file_path)] = file_hash
    
    for file_path in Path(SCAN_DIR).rglob("*.ts"):
        file_hash = calculate_hash(file_path)
        if cache.get(str(file_path)) != file_hash:
            print(f"🔍 Escaneando {file_path} com njsscan...")
            run_command(['njsscan', str(file_path), '--json'])
        else:
            print(f"✅ Ignorando {file_path} (sem mudanças)")
        new_cache[str(file_path)] = file_hash

    # # 🔍 **Análise avançada de SQL Injection com Semgrep**
    # print("🔍 Rodando Semgrep para SQL Injection...")
    # run_command([
    #     "semgrep", "scan",
    #     "--config=https://semgrep.dev/p/sql-injection",
    #     "--json",
    #     "--metrics=off",
    #     str(SCAN_DIR)
    # ])

    # # Verificação das TOP 25 CWEs
    # print("🔍 Rodando Semgrep para CWE TOP 25...")   
    # run_command([
    #     "semgrep", "scan",
    #     "--config=https://semgrep.dev/p/cwe-top-25",
    #     "--json",
    #     "--metrics=off",
    #     str(SCAN_DIR)
    # ])    

    # # Análise com Semgrep Secure Defaults
    # print("🔍 Rodando Semgrep...")
    # run_command([
    #     "semgrep", "scan",
    #     "--config=https://semgrep.dev/p/secure-defaults",
    #     "--json",
    #     "--metrics=off",
    #     str(SCAN_DIR)
    # ])    

    # Garante que o diretório seja tratado como seguro pelo Git
    run_command(["git", "config", "--global", "--add", "safe.directory", SCAN_DIR])

    # Análise com Semgrep
    print("🔍 Rodando Semgrep...")
    try:
        subprocess.run(["semgrep", "ci"], cwd=SCAN_DIR, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"⚠ Erro ao executar Semgrep CI: {e.stderr}")


    # Salvando o cache atualizado
    save_cache(new_cache)
    print("✅ Análise concluída!")

if __name__ == "__main__":
    run_sast_scan()