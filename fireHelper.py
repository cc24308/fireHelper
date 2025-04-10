from fastapi import FastAPI
import firebase_admin
from firebase_admin import credentials, firestore as admin_firestore
import os

cred = credentials.Certificate(os.environ["CREDENTIAL_CERTIFICATE"])
firebase_admin.initialize_app(cred)

admin_db = admin_firestore.client()
app = FastAPI()

#dfsdf
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

@app.post("/users")
async def create_user(user: dict):
    try:
        admin_db.collection("users").add(user)
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