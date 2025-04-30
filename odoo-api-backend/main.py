# === Import des modules nécessaires ===
import xmlrpc.client  # Pour communiquer avec l'API XML-RPC d'Odoo
from fastapi import FastAPI, HTTPException  # Pour créer des endpoints HTTP avec gestion des erreurs
from pydantic import BaseModel  # Pour la validation de données entrantes via modèles
from typing import List, Optional  # Types pour l'annotation

# === Configuration de la connexion Odoo ===
URL = "http://localhost:8069"  # URL du serveur Odoo
DB = "odoo_nostra"
USERNAME = "andrijzmurik@gmail.com"
PASSWORD = "NepTynS1.."

# Connexion aux services XML-RPC d'Odoo
common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
ud = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")


uid = common.authenticate(DB, USERNAME, PASSWORD, {})


if not uid:
    raise Exception("Erreur d'authentification Odoo")

# === Initialisation de FastAPI ===
app = FastAPI()

# Ajout du middleware CORS pour autoriser les requêtes front-end (React par ex.)
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Origine autorisée (React en local)
    allow_methods=["*"],  # Autorise toutes les méthodes HTTP
    allow_headers=["*"]   # Autorise tous les headers
)

# === Définition des modèles de données avec Pydantic ===

# Structure utilisée pour d’autres identifiants
class AccountAdditionalIds(BaseModel):
    id: Optional[str] = None
    guid: Optional[str] = None
    up_id: Optional[str] = None
    display_name: str

# Modèle utilisé pour créer un utilisateur
class UserCreate(BaseModel):
    login_name: str
    other_ids: AccountAdditionalIds  # Infos additionnelles comme le nom
    password: str
    groups: Optional[List[int]] = []  # Groupes (rôles) facultatifs

# Identique à UserCreate pour l'instant, mais pourrait être étendu
class UserUpdate(UserCreate):
    pass

# Modèle pour informations de groupes
class GroupInfo(BaseModel):
    external_name: str
    other_ids: dict

# === Endpoints FastAPI ===

# Création d'un utilisateur
@app.post("/users/")
def create_user(user: UserCreate):
    try:
        user_id = ud.execute_kw(DB, uid, PASSWORD, 'res.users', 'create', [{
            'name': user.other_ids.display_name,
            'login': user.login_name,
            'password': user.password,
            'groups_id': [(6, 0, user.groups)]  # Attribue les groupes spécifiés
        }])
        return {"user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Mise à jour d’un utilisateur
@app.put("/users/{user_id}")
def update_user(user_id: int, user: UserUpdate):
    values = {
        "name": user.other_ids.display_name,
        "login": user.login_name,
        "password": user.password,
        "groups_id": [(6, 0, user.groups)]
    }
    try:
        ud.execute_kw(DB, uid, PASSWORD, 'res.users', 'write', [[user_id], values])
        return {"message": "Utilisateur mis à jour"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Suppression d’un utilisateur
@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    try:
        ud.execute_kw(DB, uid, PASSWORD, 'res.users', 'unlink', [[user_id]])
        return {"message": "Utilisateur supprimé"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Création utilisateur avec groupes (identique à /users/ pour l’instant)
@app.post("/users/full")
def create_user_with_roles(user: UserCreate):
    return create_user(user)

# Récupération des groupes d’un utilisateur
@app.get("/users/{user_id}/roles")
def list_user_roles(user_id: int):
    try:
        user = ud.execute_kw(DB, uid, PASSWORD, 'res.users', 'read', [[user_id]], {'fields': ['groups_id']})
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        return {"user_id": user_id, "groups": user[0]["groups_id"]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Ajout de groupes à un utilisateur
@app.post("/users/{user_id}/roles")
def assign_roles(user_id: int, groups: List[int]):
    try:
        user = ud.execute_kw(DB, uid, PASSWORD, 'res.users', 'read', [[user_id]], {'fields': ['groups_id']})
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

        existing = user[0]["groups_id"]  # Groupes existants
        updated = list(set(existing + groups))  # Fusion sans doublons
        ud.execute_kw(DB, uid, PASSWORD, 'res.users', 'write', [[user_id], {'groups_id': [(6, 0, updated)]}])
        return {"message": "Groupes attribués", "groups": updated}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Suppression de certains groupes d’un utilisateur
@app.delete("/users/{user_id}/roles")
def remove_roles(user_id: int, groups: List[int]):
    try:
        user = ud.execute_kw(DB, uid, PASSWORD, 'res.users', 'read', [[user_id]], {'fields': ['groups_id']})
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

        current = user[0]["groups_id"]
        updated = [g for g in current if g not in groups]  # Retire les groupes à enlever
        ud.execute_kw(DB, uid, PASSWORD, 'res.users', 'write', [[user_id], {'groups_id': [(6, 0, updated)]}])
        return {"message": "Groupes retirés", "groups": updated}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Recherche d’un utilisateur par son login
@app.get("/users/get_id_by_login")
def get_user_id_by_login(login: str):
    try:
        user_ids = ud.execute_kw(DB, uid, PASSWORD, 'res.users', 'search', [[('login', '=', login)]])
        if user_ids:
            return {"id": user_ids[0]}
        else:
            return {"error": "Utilisateur non trouvé"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))