from fastapi import FastAPI, Header, HTTPException, Depends, Path
import firebase_admin
from firebase_admin import credentials, firestore as admin_firestore, auth 
import os
from dataTypes.dataModels import Task, User
from dotenv import load_dotenv
import os, json, base64
load_dotenv() 

#RESOLVE SOBRE O REARER E MUDAR A ESTRUTURA DO PROJETO PARA RECEBER O UID INVES DO TOKEN

#firebase_admin.initialize_app(cred)

#pip freeze > requirements.txt = pra fazer o txt que o render vai baixar pra fazer a api rodar
#base64 -w0 C:/Users/u24308/Documents/GitHub/fireHelper/mk39.json > credential.b64

b64 = os.environ.get("CREDENTIAL_CERTIFICATE_B64")
b64 += "=" * ((4 - len(b64) % 4) % 4)
json_str = base64.b64decode(b64).decode("utf-8")
cred_dict = json.loads(json_str)
cred = credentials.Certificate(cred_dict)

firebase_admin.initialize_app(cred)

admin_db = admin_firestore.client()
app = FastAPI()

"""def verify_token(id_token: str):

    try:
        #verifica o token com firebase admin com a função oficial
        decoded_token = auth.verify_id_token(id_token)
        user_id = decoded_token['uid']  #o uid do usuário
        return user_id

    except Exception as e:

        raise HTTPException(status_code=401, detail="Invalid token")"""

"""def get_token_from_header(user_id: str = Header(...)):
    #if not authorization.startswith("Bearer"):
    #    raise HTTPException(status_code=401, detail="Invalid authorization header")

    token = user_id.split(" ")[1]
    return token"""

"""def require_user_id(token: str = Header(...)):
    return token"""



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
async def create_user(user_info : User, user_uid: str = Header(...) ): #depends faz com que a função seja chamada antes da função que está chamando ela, 
                                                                            #e o retorno dela é passado como parametro para a função que está chamando
                                                                            #e é uma boa verificar o token assim pq nao precisa fazer o decode do token toda vez no Header
    try:
        if not user_uid:
            return {
                "success": False,
                "message": "User login data is required"
            }

        user_ref = admin_db.collection("users").document(user_uid)
        user_ref.set({
            "name": user_info.name,
            "exp": 0,
            "level": 1,
        })

        task_ref = admin_db.collection("tasks").document(user_uid)
        
        task_ref.set({
            "tasks": []
        })

        return {
            "success": True,
            "message": "User created successfully!"
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Error trying to create user: {str(e)}"
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

app.patch("/users/exp/{exp}")
async def update_user_exp(exp: int = Path(...), user_uid: str = Header(...) ):

    try:

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
async def create_task(task : Task, user_uid: str = Header(...)  ):

    try:
        
        task_ref = admin_db.collection("tasks").document(user_uid)
        task_ref.set({
            "tasks": {
                task.date: admin_firestore.firestore.ArrayUnion([task.model_dump()])   
            }
        }, merge=True) #faz com que nao apague os outros registros naquela data

        return {
            "success": True,
            "message": f"Task {task.name} created for user {user_uid}"
        }
    
    except Exception as e:  
        return {
            "success": False,
            "message": f"Failed to create task: {str(e)}"
        }

