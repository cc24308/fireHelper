import os
from dotenv import load_dotenv

# Carregar variáveis do arquivo .env
load_dotenv()

# Pegar a chave privada
private_key = os.environ["PRIVATE_KEY"]

# Verificar a chave carregada
print("Chave privada:", repr(private_key))
print("Comprimento da chave:", len(private_key))
