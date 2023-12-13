import os

from keycloak import KeycloakOpenID
from keycloak import KeycloakAdmin
from keycloak import KeycloakOpenIDConnection

from .tools import getsecret

try:
    keycloak_connection = KeycloakOpenIDConnection(
                        server_url = os.environ['KEYCLOAK_SERVER_URL'],
                        username = '',
                        password = '',
                        realm_name = os.environ['KEYCLOAK_REALM'],
                        user_realm_name = "",
                        client_id = os.environ['KEYCLOAK_CLIENT'],
                        client_secret_key = getsecret(name='keycloak_secret_key'),
                        verify = True)
except Exception as err:
    print("[ERROR] - Connexion au serveur keycloak impossible - ", err)
else:
    print("[INFO] - Connexion au serveur Keycloak - " + os.environ['KEYCLOAK_SERVER_URL'])
    
    keycloak_admin = KeycloakAdmin(connection=keycloak_connection)

#-----------------------------------------------------------------------------------------#
# adduser
#
# email
# firstname
# lastname
# credentials {value}
# attributes {id, 
#             adresse.adresse, 
#             adresse.code_postal, 
#             adresse.ville, genre, 
#             fullName, 
#             telephone, 
#             locale, 
#             date_naissance, 
#             statut}
#-----------------------------------------------------------------------------------------#
def adduser(email, firstName, lastName, attributes):
    try:
        user = keycloak_admin.create_user({ "email": email,
                                            "username": email,
                                            "enabled": True,
                                            "firstName": firstName,
                                            "lastName": lastName,
                                            "credentials": [{"value" : "azerty"}],
                                            "requiredActions": ["VERIFY_EMAIL", "UPDATE_PASSWORD"],
                                            "attributes": attributes })
        payload = { "message": "", "content": user }
    except Exception as err:
        print("[ERROR] - adduser - ", err)
        payload = { "message": "error", "content": str(err) }
        
    return payload

#-----------------------------------------------------------------------------------------#
# Update User
#
# userId
# payload {'firstName': 'Example Update'}
#
#-----------------------------------------------------------------------------------------#
def updateuser(userId, payload):
    try:
        response = keycloak_admin.update_user(  user_id = userId,
                                                payload = payload)
        return response
    except Exception as err:
        print("[ERROR] - updateuser - Connexion au serveur keycloak impossible - ", err)
        return "error"

#-----------------------------------------------------------------------------------------#
# Enable or Disable a User
#
# activation
# userId
#
#-----------------------------------------------------------------------------------------#
def activation(activation, userId):
    if activation == "disable":
        payload = {"enabled": False}
    else:
        payload = {"enabled": True}

    try:
        response = keycloak_admin.update_user(  user_id = userId,
                                                payload = payload)
        return response
    except Exception as err:
        print("[ERROR] - activation - Connexion au serveur keycloak impossible - ", err)
        return "error"
       
# ****** TEST ******#
def getallusers():
    try:
        users = keycloak_admin.get_users()
        if users: 
            payload = { "message": "", "users": users }
        else:
            payload = { "message": "Pas de réponse à votre requête", "users": users }
    except Exception as err:
        payload = { "message": "Erreur de connexion au serveur Keycloak", "users": []}
        print("[ERROR] - getusers - Connexion au serveur keycloak impossible - ", err)
    
    return payload
#--------------------#

def getusers(lastName, firstName, query):
    #query = "id:" + appId

    try:
        users = keycloak_admin.get_users({"lastName" : lastName, "firstName" : firstName, "q" : query })
        if users: 
            payload = { "message": "", "users": users }
        else:
            payload = { "message": "Pas de réponse à votre requête", "users": users }
    except Exception as err:
        payload = { "message": "Erreur de connexion au serveur Keycloak", "users": []}
        print("[ERROR] - getusers - Connexion au serveur keycloak impossible - ", err)
    
    return payload

def getusers4autocomplete(search):
    #query = "id:" + appId

    try:
        users = keycloak_admin.get_users({"search" : search })
        if users: 
            payload = { "message": "", "users": users }
        else:
            payload = { "message": "Pas de réponse à votre requête", "users": users }
    except Exception as err:
        payload = { "message": "Erreur de connexion au serveur Keycloak", "users": []}
        print("[ERROR] - getusers - Connexion au serveur keycloak impossible - ", err)
    
    return payload

def getgroupsbyuser(userid):
    try:
        groups = keycloak_admin.get_user_groups(userid)
        payload = { "message": "", "groups": groups }
    except Exception as err:
        payload = { "message": "Erreur de connexion au serveur Keycloak", "groups": []}
        print("[ERROR] - getgroupsbyuser - Connexion au serveur keycloak impossible - ", err)

    return payload

def getGroups():
    try:
        groups = keycloak_admin.get_groups()
        payload = { "message": "", "groups": groups }
    except Exception as err:
        payload = { "message": "Erreur de connexion au serveur Keycloak", "groups": []}
        print("[ERROR] - getGroups - Connexion au serveur keycloak impossible - ", err)

    return payload

# Get group by name
def getGroupsByName(path):
    try:
        groups = keycloak_admin.get_group_by_path(path = path)
        payload = { "message": "", "groups": groups }
    except Exception as err:
        payload = { "message": "Erreur de connexion au serveur Keycloak", "groups": [] }
        print("[ERROR] - getGroupsByName - Connexion au serveur keycloak impossible - ", err)

    return payload

# Add group to a user
def addGroup(userId, groupId):
    response = keycloak_admin.group_user_add(userId, groupId)
    print(response)

# Remove group to a user
def removeGroup(userId, groupId):
    response = keycloak_admin.group_user_remove(userId, groupId)
    print(response)