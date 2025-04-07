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
