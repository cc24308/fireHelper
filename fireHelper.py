from fastapi import FastAPI, Header, Path, HTTPException
import firebase_admin
from firebase_admin import credentials, firestore as admin_firestore, auth 
import os
from dataTypes.Task import Task
#pip freeze > requirements.txt = pra fazer o txt que o render vai baixar pra fazer a api rodar

#cred = credentials.Certificate(os.environ["CREDENTIAL_CERTIFICATE"])

cred = {
    "type": os.environ["TYPE"],
  "project_id": os.environ["PROJECT_ID"],
  "private_key_id": os.environ["PRIVATE_KEY_ID"],
  "private_key": os.environ["PRIVATE_KEY"].replace("\\n","\n"), #pode dar erro por causa das quebras de linha
  "client_email": os.environ["CLIENT_EMAIL"],
  "client_id": os.environ["CLIENT_ID"],
  "auth_uri": os.environ["AUTH_URI"],
  "token_uri": os.environ["TOKEN_URI"],
  "auth_provider_x509_cert_url": os.environ["AUTH_PROVIDER_X509_CERT_URL"],
  "client_x509_cert_url": os.environ["CLIENT_X509_CERT_URL"],
  "universe_domain": os.environ["UNIVERSE_DOMAIN"],
}

firebase_admin.initialize_app(cred)

admin_db = admin_firestore.client()
app = FastAPI()

@app.get("/")
async def root():

    return {"message": "Firebase API running"}

@app.get("/users")
async def get_users():

    try:
        users_ref = admin_db.collection("users")
        docs = users_ref.stream()
        users = [{"id": doc.id, **doc.to_dict()} for doc in docs]

        return {
            "users": users,
            "apiResponse": {
                "success": True,
                "message": "Users successfully returned!"
            }
        }
    except Exception as e:
        return {
            "apiResponse": {
                "success": False,
                "message": f"Failed to load users: {str(e)}"
            }
        }

#TODO: fazer com que essa função ja crie um documeneto na coleção "Tasks" com o id do usuario na hora de criar o usuario para melhor manipulação de dados
@app.post("/users")
async def create_user(user: dict):

    try:
        if not user:

            return {
                "success": False,
                "message": "User login data is required"
            }

        # cria o usuário no firestore com o add
        user_ref = admin_db.collection("users").add(user)

        # pega o ID do documento criado
        user_id = user_ref.id

        # cria o documento de tarefas para o usuário
        admin_db.collection("tasks").add({
            "user_id": user_id,
            "tasks": []
        })

        return {
            "success": True,
            "message": "Usuário criado com sucesso!"
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Erro ao criar usuário: {str(e)}"
        }


@app.delete("/users")
async def delete_user(user: dict):

    try:
        name = user.get("name")
        if not name:
            return {"success": False, "message": "Name is required in the request body"}

        retorno = admin_db.collection("users").where("name", "==", name).stream()

        deleted_any = False
        for doc in retorno:
            admin_db.collection("users").document(doc.id).delete()
            deleted_any = True

        if deleted_any:
            return {
                "success": True,
                "message": f"User(s) with name '{name}' deleted"
            }
        else:
            return {
                "success": False,
                "message": f"No user with name '{name}' found"
            }

    except Exception as e:
        return {
            "success": False,
            "message": f"User could not be safely deleted: {str(e)}"
        }

@app.delete("/users")
async def safe_delete_user(user: dict):

    try:
        name = user.get("name")
        if not name:
            return {"success": False, "message": "Name is required in the request body"}

        retorno = admin_db.collection("users").where("name", "==", name).stream()

        deleted_any = False
        for doc in retorno:
            admin_db.collection("users").document(doc.id).delete()
            deleted_any = True

        if deleted_any:
            return {
                "success": True,
                "message": f"User(s) with name '{name}' deleted"
            }
        else:
            return {
                "success": False,
                "message": f"No user with name '{name}' found"
            }

    except Exception as e:
        return {
            "success": False,
            "message": f"User could not be safely deleted: {str(e)}"
        }

app.patch("/users/exp/{exp}")
async def update_user_exp(exp: int = Path(...), id_token: str = Header(...) ):

    try:

        user_uid = verify_token(id_token)

        user_ref = admin_db.collection("users").document(user_uid)
        # collection(user) = buscar a coleção com o nome passado no parametro
        # document(user_id) = busca o documento que tem o id passado na função
        user_doc = user_ref.get()
        # get() = pega os dados salvos naquele documento

        if not user_doc.exists:
            return {
                "success": False,
                "message": f"User {user_uid} not found"
            }
        # exists = verifica se o documento existe

        current_exp = user_doc.to_dict().get("exp", 0)
        # to_dict() = converte os dados para dicionário
        # get("exp", 0) = pega o valor da chave exp, se não existir retorna 0

        exp_sum = current_exp + exp

        user_ref.update({"exp": exp_sum})
        # update() = atualiza os dados do documento
        # {"exp": exp} = atualiza a chave exp com o valor passado na função
        # user_ref.set({"exp": exp}) = sobrescreve os dados do documento
        # user_ref.set({"exp": exp}, merge=True) = atualiza os dados do documento, mantendo os dados existentes

        return {
            "success": True,
            "message": f"User {user_uid} updated with exp {exp}"
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to update user: {str(e)}"
        }

@app.post("/tasks")
async def create_task(task : Task ,id_token: str = Header(...)  ):

    try:
        user_uid = verify_token(id_token)

        task_ref = admin_db.collection("tasks").document(user_uid)
        task_ref.update({
            "tasks": admin_firestore.firestore.ArrayUnion([task.dict()])
        })

        return {
            "success": True,
            "message": f"Task {task.name} created for user {user_uid}"
        }
    
    except Exception as e:  
        return {
            "success": False,
            "message": f"Failed to create task: {str(e)}"
        }



def verify_token(id_token: str):

    try:
        #verifica o token com firebase admin com a função oficial
        decoded_token = auth.verify_id_token(id_token)
        user_id = decoded_token['uid']  #o uid do usuário
        return user_id

    except Exception as e:

        raise HTTPException(status_code=401, detail="Invalid token")