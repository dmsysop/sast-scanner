import os
import sys
import json
import atexit
import hashlib
import subprocess
from pathlib import Path
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

destination = sys.argv[1]

if len(sys.argv) < 2:
    print("❌ Erro: Caminho do projeto não informado.")
    sys.exit(1)

SCAN_DIR = f"/app/{destination}"

# Definir configurações do MongoDB
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "sast_cache")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "cache")

# Inicializar variáveis
client = None
db = None
cache_collection = None

IGNORED_DIRS = {"node_modules", "venv", "__pycache__", "vendor"}

if MONGO_URI:
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        db = client.get_database(MONGO_DB_NAME)
        
        # Criar o nome da coleção com base no destino
        collection_name = f"{destination}_{MONGO_COLLECTION}"
        
        # Verificar o comprimento do nome da coleção e garantir que não ultrapasse 255 caracteres
        if len(collection_name) > 255:
            raise ValueError(f"Nome da coleção `{collection_name}` excede o limite de 255 caracteres.")
        
        cache_collection = db.get_collection(collection_name)

        # Verificar se a coleção existe e está vazia
        if cache_collection.count_documents({}) == 0:
            print(f"⚠ Criando a coleção `{collection_name}`")
        else:
            print(f"⚠ Coleção `{collection_name}` encontrada!")


        # Testar a conexão
        client.server_info()  # Isso força uma conexão para validar a URI
        print("✅ Conectado ao MongoDB Atlas")

    except Exception as e:
        print(f"⚠ Erro ao conectar ao MongoDB: {e}")
        cache_collection = None
else:
    print("⚠ MongoDB não configurado. Cache será ignorado.")

# Garantir fechamento da conexão ao encerrar o script
def close_mongo_connection():
    if client:
        client.close()
        print("🔌 Conexão com MongoDB fechada.")
atexit.register(close_mongo_connection)

def calculate_hash(file_path):
    # Verifica se o caminho é um arquivo regular e não um diretório
    if not os.path.isfile(file_path):
        print(f"⚠ Ignorando diretório: {file_path}")
        return None  # Retorna None ou outro valor adequado para indicar que o hash não foi calculado

    # Se for um arquivo, calcula o hash
    hasher = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            hasher.update(f.read())
        return hasher.hexdigest()
    except Exception as e:
        print(f"❌ Erro ao calcular hash para o arquivo {file_path}: {e}")
        return None
    
# Definindo a função para verificar a conexão
def check_conn():
    if cache_collection is None:
        print("⚠ Aviso: `cache_collection` está None. O cache não será salvo!")
        return
    # Testando a conexão com o MongoDB
    print("🔬 Testando leitura do MongoDB...")
    try:
        cache_collection.count_documents({})
    except Exception as e:
        print(f"❌ Erro ao ler MongoDB: {e}")
    
def get_cache():
    if cache_collection is None:
        print("⚠ Aviso: `cache_collection` está None. O cache não será salvo!")
        return {}
    
    # Carregar o cache como um dicionário, onde a chave é o file_path e o valor é o hash
    return {doc["file_path"]: doc["hash"] for doc in cache_collection.find({}, {"_id": 0, "file_path": 1, "hash": 1})}

def update_cache(file_path, file_hash):
    if cache_collection is not None:
        # relative_path = os.path.relpath(file_path, SCAN_DIR)
        print(f"📝 Atualizando cache no MongoDB: {file_path} -> {file_hash}")  # <--- DEBUG
        cache_collection.update_one(
            {"file_path": file_path}, 
            {"$set": {"hash": file_hash}}, 
            upsert=True
        )
    else:
        print("⚠ Aviso: `cache_collection` está None. O cache não será salvo!")

def run_command(command, cwd=None):
    try:
        result = subprocess.run(command, shell=False, check=True, capture_output=True, text=True, cwd=cwd)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"⚠ Erro ao executar o comando {' '.join(command)}: {e.stderr}")

def install_dependencies():
    if Path(SCAN_DIR, "requirements.txt").exists():
        print("📦 Instalando dependências Python (pip)...")
        run_command(["pip", "install", "-r", "requirements.txt"], cwd=SCAN_DIR)
    elif Path(SCAN_DIR, "pyproject.toml").exists():
        print("📦 Instalando dependências Python (Poetry)...")
        run_command(["poetry", "install"], cwd=SCAN_DIR)
    elif Path(SCAN_DIR, "Pipfile").exists():
        print("📦 Instalando dependências Python (Pipenv)...")
        run_command(["pipenv", "install"], cwd=SCAN_DIR)
    else:
        print("⚠ Nenhum arquivo de dependências encontrado para Python. Pulando instalação.")
    
    if Path(SCAN_DIR, "package.json").exists():
        print("📦 Instalando dependências Node.js...")
        run_command(["npm", "install"], cwd=SCAN_DIR)
    
    if Path(SCAN_DIR, "composer.json").exists():
        print("📦 Instalando dependências PHP...")
        run_command(["composer", "install"], cwd=SCAN_DIR)

def run_sast_scan():
    if not Path(SCAN_DIR).exists():
        print(f"❌ Erro: Nenhum diretório montado em /app/{destination}")
        return
    
    install_dependencies()
    check_conn()
    cache = get_cache()

    for file_path in Path(SCAN_DIR).rglob("*.py"):
        if any(ignored in file_path.parts for ignored in IGNORED_DIRS):
            continue
        file_hash = calculate_hash(file_path)
        cache = get_cache()
        if cache.get(str(file_path)) != file_hash:
            print(f"🔍 Escaneando {file_path} com bandit...")
            run_command(["bandit", "-r", str(file_path)])
            update_cache(str(file_path), file_hash)
        else:
            print(f"✅ Ignorando {file_path} (sem mudanças)")

    for file_path in Path(SCAN_DIR).rglob("*.php"):
        if any(ignored in file_path.parts for ignored in IGNORED_DIRS):
            continue
        file_hash = calculate_hash(file_path)
        cache = get_cache()
        if cache.get(str(file_path)) != file_hash:
            print(f"🔍 Escaneando {file_path} com phpstan...")
            run_command(["phpstan", "analyse", str(file_path), "--level", "4"])
            update_cache(str(file_path), file_hash)
        else:
            print(f"✅ Ignorando {file_path} (sem mudanças)")

    for file_path in Path(SCAN_DIR).rglob("*.js"):
        if any(ignored in file_path.parts for ignored in IGNORED_DIRS):
            continue
        file_hash = calculate_hash(file_path)
        cache = get_cache()
        if cache.get(str(file_path)) != file_hash:
            print(f"🔍 Escaneando {file_path} com njsscan...")
            run_command(['njsscan', str(file_path), '--json'])
            update_cache(str(file_path), file_hash)
        else:
            print(f"✅ Ignorando {file_path} (sem mudanças)")

    run_command(["git", "config", "--global", "--add", "safe.directory", SCAN_DIR])

    # print("🔍 Rodando Semgrep...")
    # try:
    #     subprocess.run(["semgrep", "ci"], cwd=SCAN_DIR, check=True, capture_output=True, text=True)
    # except subprocess.CalledProcessError as e:
    #     print(f"⚠ Erro ao executar Semgrep CI: {e.stderr}")

    print("✅ Análise concluída!")

if __name__ == "__main__":
    run_sast_scan()
