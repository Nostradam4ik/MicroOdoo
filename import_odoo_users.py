import requests
import csv
import random
import string
from datetime import datetime
import xmlrpc.client

# ==== CONFIGURATION DE BASE ====
ODOO_URL = "http://localhost:8069"
ODOO_DB = "odoo_nostra"
ODOO_USER = "andrijzmurik@gmail.com"
ODOO_PASSWORD = "NepTynS1.."
CSV_FILE = "utilisateurs.csv"
LOG_FILE = "log_import.txt"
HEADERS = {'Content-Type': 'application/json'}

# ==== LOGGING ====
def log(message):
    """Écrit un message horodaté dans le fichier de log."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding='utf-8') as f:
        f.write(f"[{now}] {message}\n")

# ==== AUTHENTIFICATION JSON-RPC ====
def authenticate():
    """S'authentifie auprès d'Odoo via JSON-RPC et retourne l'UID."""
    url = f"{ODOO_URL}/jsonrpc"
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "common",
            "method": "authenticate",
            "args": [ODOO_DB, ODOO_USER, ODOO_PASSWORD, {}]
        },
        "id": 1
    }
    try:
        response = requests.post(url, json=payload, headers=HEADERS).json()
        uid = response.get("result")
        if uid:
            log(f"authenticate: SUCCÈS (UID: {uid})")
            return uid
        else:
            log(f"authenticate: ÉCHEC - {response}")
            return None
    except Exception as e:
        log(f"authenticate: ERREUR - {e}")
        return None

# ==== GÉNÉRATION DE MOT DE PASSE ====
def generate_password(length=12):
    """Génère un mot de passe aléatoire sécurisé."""
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choice(chars) for _ in range(length))

# ==== CRÉATION D'UN UTILISATEUR ====
def create_user(uid, user):
    """Crée un utilisateur Odoo avec les données fournies et retourne son ID."""
    password = generate_password()
    user['password'] = password  # Ajoute le mot de passe généré au dictionnaire

    data = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [ODOO_DB, uid, ODOO_PASSWORD, "res.users", "create", [{
                "name": f"{user['prenom']} {user['nom']}",
                "login": user['login'],
                "email": user['email'],
                "password": password,
                "active": True
            }]]
        },
        "id": 2
    }

    try:
        response = requests.post(f"{ODOO_URL}/jsonrpc", json=data, headers=HEADERS).json()
        user_id = response.get("result")
        if user_id:
            log(f"create_user: SUCCÈS - {user['login']} (ID: {user_id})")
        else:
            log(f"create_user: ÉCHEC - {user['login']} | {response}")
        return user_id
    except Exception as e:
        log(f"create_user: ERREUR - {user['login']} | {e}")
        return None

# ==== LECTURE DU CSV ====
def read_users_from_csv(csv_file):
    """Lit le fichier CSV et retourne une liste de dictionnaires utilisateurs."""
    users = []
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            users.append({
                'nom': row['nom'],
                'prenom': row['prenom'],
                'login': row['login'],
                'email': row['email'],
                'droits': row['droits']
            })
    return users

# ==== RÉCUPÉRATION ID DE GROUPE ====
def get_group_id(uid, group_name):
    """Retourne l'ID du groupe Odoo correspondant au nom donné."""
    data = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [ODOO_DB, uid, ODOO_PASSWORD, "res.groups", "search", [[("name", "=", group_name)]]]
        },
        "id": 3
    }
    response = requests.post(f"{ODOO_URL}/jsonrpc", json=data, headers=HEADERS).json()
    group_ids = response.get("result")
    return group_ids[0] if group_ids else None

# ==== ASSIGNATION DES DROITS ====
def assign_permissions(uid, user_id, group_id):
    """Assigne un groupe à un utilisateur donné via son ID."""
    data = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [ODOO_DB, uid, ODOO_PASSWORD, "res.users", "write", [[user_id], {"groups_id": [(4, group_id)]}]]
        },
        "id": 4
    }
    response = requests.post(f"{ODOO_URL}/jsonrpc", json=data, headers=HEADERS).json()
    log(f"assign_permissions: utilisateur ID {user_id} -> groupe ID {group_id} | Résultat: {response}")

# ==== VÉRIFIE SI UTILISATEUR EXISTE ====
def find_user_id(uid, login):
    """Recherche un utilisateur par login, retourne son ID s'il existe."""
    data = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [ODOO_DB, uid, ODOO_PASSWORD, "res.users", "search", [[("login", "=", login)]]]
        },
        "id": 5
    }
    response = requests.post(f"{ODOO_URL}/jsonrpc", json=data, headers=HEADERS).json()
    user_ids = response.get("result")
    return user_ids[0] if user_ids else None

# ==== IMPORT DEPUIS CSV ====
def import_accounts_from_csv():
    """Importe tous les utilisateurs du CSV dans Odoo, en évitant les doublons."""
    uid = authenticate()
    if not uid:
        print("Échec de l'authentification")
        return

    users = read_users_from_csv(CSV_FILE)
    for user in users:
        existing_user_id = find_user_id(uid, user['login'])
        if existing_user_id:
            print(f"Utilisateur {user['login']} existe déjà. Ignoré.")
            log(f"import_accounts_from_csv: EXISTE - {user['login']} (ID: {existing_user_id})")
            continue

        user_id = create_user(uid, user)
        if user_id:
            group_id = get_group_id(uid, user['droits'])
            if group_id:
                assign_permissions(uid, user_id, group_id)
                print(f"{user['prenom']} {user['nom']} -> Groupe: {user['droits']}")
            else:
                print(f"Groupe non trouvé: {user['droits']}")
        else:
            print(f"Échec création: {user['prenom']} {user['nom']}")

# ==== CONNEXION XML-RPC POUR GESTION MANUELLE ====
common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")
uid_xmlrpc = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})

def find_user_id_xmlrpc(username):
    """Retourne l'ID de l'utilisateur via XML-RPC."""
    user_ids = models.execute_kw(ODOO_DB, uid_xmlrpc, ODOO_PASSWORD, 'res.users', 'search', [[('login', '=', username)]])
    return user_ids[0] if user_ids else None

def update_user_info(user_id, new_email=None, new_password=None):
    """Met à jour l'email et/ou mot de passe d'un utilisateur."""
    values = {}
    if new_email:
        values['email'] = new_email
    if new_password:
        values['password'] = new_password
    if values:
        models.execute_kw(ODOO_DB, uid_xmlrpc, ODOO_PASSWORD, 'res.users', 'write', [[user_id], values])
        print(f"Utilisateur {user_id} mis à jour : {values}")
    else:
        print("Aucune donnée à mettre à jour.")

def get_user_groups(user_id):
    """Retourne la liste des IDs de groupes assignés à un utilisateur."""
    user = models.execute_kw(ODOO_DB, uid_xmlrpc, ODOO_PASSWORD, 'res.users', 'read', [user_id], {'fields': ['groups_id']})
    return user[0]['groups_id'] if user else []

def modify_user_groups(user_id, group_ids_to_add=[], group_ids_to_remove=[]):
    """Ajoute ou retire des groupes à un utilisateur."""
    current_groups = get_user_groups(user_id)
    for group_id in group_ids_to_add:
        if group_id not in current_groups:
            current_groups.append(group_id)
    for group_id in group_ids_to_remove:
        if group_id in current_groups:
            current_groups.remove(group_id)
    models.execute_kw(ODOO_DB, uid_xmlrpc, ODOO_PASSWORD, 'res.users', 'write', [[user_id], {'groups_id': [(6, 0, current_groups)]}])
    print(f"Groupes mis à jour pour utilisateur {user_id} : {current_groups}")

def delete_user_xmlrpc(user_id):
    """Supprime un utilisateur via XML-RPC."""
    models.execute_kw(ODOO_DB, uid_xmlrpc, ODOO_PASSWORD, 'res.users', 'unlink', [[user_id]])
    print(f"Utilisateur {user_id} supprimé.")

# ==== MENU INTERACTIF POUR LA GESTION MANUELLE ====
def menu_gestion_utilisateur():
    """Menu CLI pour gérer les utilisateurs existants (édition/suppression/groupes)."""
    while True:
        print("\n--- MENU GESTION UTILISATEUR ODOO ---")
        print("1. Modifier email et/ou mot de passe")
        print("2. Ajouter/retirer des groupes")
        print("3. Supprimer un utilisateur")
        print("4. Quitter")
        choix = input("Choix (1-4) : ")

        if choix == "1":
            login = input("Login de l'utilisateur (ex: jean.dupont@iutcv.fr) : ")
            user_id = find_user_id_xmlrpc(login)
            if user_id:
                new_email = input("Nouvel email (laisser vide pour ne pas changer) : ")
                new_password = input("Nouveau mot de passe (laisser vide pour ne pas changer) : ")
                update_user_info(user_id, new_email or None, new_password or None)

        elif choix == "2":
            login = input("Login de l'utilisateur : ")
            user_id = find_user_id_xmlrpc(login)
            if user_id:
                ajout = input("ID(s) de groupe à AJOUTER (séparés par des virgules) : ")
                retrait = input("ID(s) de groupe à RETIRER (séparés par des virgules) : ")

                group_ids_to_add = [int(x.strip()) for x in ajout.split(",") if x.strip().isdigit()]
                group_ids_to_remove = [int(x.strip()) for x in retrait.split(",") if x.strip().isdigit()]

                modify_user_groups(user_id, group_ids_to_add, group_ids_to_remove)

        elif choix == "3":
            login = input("Login de l'utilisateur à supprimer : ")
            user_id = find_user_id_xmlrpc(login)
            if user_id:
                confirm = input(f"⚠️ Confirmer suppression de {login} ? (o/n) : ")
                if confirm.lower() == "o":
                    delete_user_xmlrpc(user_id)
                else:
                    print("Suppression annulée.")
            else:
                print("Utilisateur introuvable.")

        elif choix == "4":
            print("Fermeture du menu.")
            break
        else:
            print("Choix invalide. Veuillez réessayer.")

# ==== POINT D'ENTRÉE PRINCIPAL ====
if __name__ == "__main__":
    uid = authenticate()
    if uid:
        print(f"Authentification réussie, UID: {uid}")
        while True:
            print("\nQue veux-tu faire ?")
            print("1. Importer les utilisateurs depuis le CSV")
            print("2. Gérer manuellement les utilisateurs (modifier/supprimer)")
            print("3. Quitter")
            choix = input("Choix (1-3) : ")

            if choix == "1":
                import_accounts_from_csv()
            elif choix == "2":
                menu_gestion_utilisateur()
            elif choix == "3":
                print("Fermeture.")
                break
            else:
                print("Choix invalide.")
    else:
        print("Échec de l'authentification. Vérifie le fichier log_import.txt.")