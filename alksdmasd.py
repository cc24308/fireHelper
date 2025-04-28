import os

# Lê a variável de ambiente
private_key = os.environ["PRIVATE_KEY"]

# Substitui as quebras de linha reais por 'quebralinha'
private_key = private_key.replace("\\n", "\n")

print("Com 'quebralinha':", private_key)
