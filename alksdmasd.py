import os
from dotenv import load_dotenv
import json

load_dotenv() 

private_key = os.getenv("PRIVATE_KEY").strip('"').replace("\\n", "\n")
# Lê a variável de ambiente

# Substitui as quebras de linha reais por 'quebralinha'

print(private_key)
