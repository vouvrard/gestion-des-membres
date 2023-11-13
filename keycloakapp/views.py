import os
import json

from flask import Flask, render_template, redirect, request, session
from flask_session import Session
from werkzeug.middleware.proxy_fix import ProxyFix
from keycloak import KeycloakOpenID

from .services import getusers, getgroupsbyuser, getGroupsByName, addGroup, removeGroup, adduser, updateuser
from .tools import getsecret

#
#--- Fonction pour le tri des noms ---#
#
def get_lastName(item):
     lastName = item[1]['user']['lastName']

     return lastName

#
#--- Début du programme principal ---#
#
app = Flask(__name__)

#- Pour forcer le retour des url en https -#
app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)

#app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

version = os.environ['APP_VERSION']

Session(app)

keycloak_openid =  KeycloakOpenID(
                        server_url = os.environ['KEYCLOAK_SERVER_URL'],
                        client_id = os.environ['KEYCLOAK_CLIENT'],
                        realm_name = os.environ['KEYCLOAK_REALM'],
                        client_secret_key = getsecret(name='keycloak_secret_key'))

@app.route('/')
def index():
    message = ""
    args = dict(request.args)
    authorize = args.get("authorize")
    
    if authorize == "no":
        message = "Vous n'êtes pas autorisé à utiliser cette application"
    
    return render_template('index.html', version = version, message = message)

@app.route('/login')
def login():
    # Get Code With Oauth Authorization Request
    try:
        auth_url = keycloak_openid.auth_url(
                    redirect_uri = os.environ['APP_URL'] + "/home",
                    scope="email",
                    state="")
    except Exception as err:
        print("[ERROR] - Login impossible - ", err)
    else:
        return redirect(auth_url, code=302)

@app.route('/logout')
def logout():
    keycloak_openid.logout(session['token']['refresh_token'])
    session.pop('token', None)
    
    return redirect("/")
     
@app.route('/home')
def home():
        if 'token' not in session:
            #Get code from url
            code = request.url.split("&")[2].split("=")[1]

            #Get token with code given by url
            token = keycloak_openid.token(
                            grant_type = 'authorization_code',
                            code = code,
                            redirect_uri = request.base_url)
            
            session['token'] = token

            #Get user info from token
            adminUserInfo = keycloak_openid.userinfo(token['access_token'])
            session['userinfo'] = adminUserInfo
        else:
            adminUserInfo = session['userinfo']
 
        if os.environ['KEYCLOAK_ADMIN_GROUP'] in adminUserInfo['groups']:
            return render_template('home.html', version = version, admin_name = adminUserInfo['firstName'] + ' ' + adminUserInfo['lastName'])
        else:
            keycloak_openid.logout(session['token']['refresh_token'])
            session.pop('token', None)
            return redirect("/?authorize=no", code=302)

@app.route('/skills/')
def skills():
    if session['token']:
        adminUserInfo = session['userinfo']
        usersToSort = {}
        usersToDisplay = {}
        groupsToDisplay = []
        
        lastName = ""
        firstName = ""
        appId = ""
        message = ""

        args = dict(request.args)
        lastName = args.get("lastName")
        firstName = args.get("firstName")
        appId = args.get("appId")

        if lastName or firstName or appId:
            usersResult = getusers(lastName, firstName, appId)

            if not usersResult["message"]: 
                users = usersResult["users"]

                for user in users:
                    authGroup = False
                    userAttributes = user["attributes"]
                    userGroupResult = getgroupsbyuser(user['id'])

                    if not userGroupResult["message"]:
                        #- Test if the ser is in the Elefan's user group -#
                        for group in userGroupResult["groups"]:
                            if group["path"] == os.environ["KEYCLOAK_AUTH_ELEFAN_GROUP_PATH"]:
                                authGroup = True

                        if authGroup:
                            user_groups = userGroupResult["groups"]
                            usersToSort[user['id']] = {'user': user, 'user_attributes': userAttributes, 'user_groups': user_groups}

                usersToDisplay = sorted(usersToSort.items(), key=get_lastName)

            else:
                message = usersResult["message"]

            groupsResult = getGroupsByName(os.environ['KEYCLOAK_GROUPS_PATH'])

            if not groupsResult["message"]:
                groupsToDisplay = sorted(groupsResult["groups"]['subGroups'], key=lambda d: d['name'])
            else:
                message = usersResult["message"]

        return render_template('skills.html', version = version, admin_name = adminUserInfo['firstName'] + ' ' + adminUserInfo['lastName'], users_to_display = dict(usersToDisplay), groups = groupsToDisplay, lastName = lastName, firstName = firstName, message = message) 
    else:
        return redirect("/index", code=302) 

@app.route('/users/')
def users():
    if session['token']:
        adminUserInfo = session['userinfo']
        usersToSort = {}
        usersToDisplay = {}
        groupsToDisplay = []
        
        lastName = ""
        firstName = ""
        appId = ""
        message = ""

        args = dict(request.args)
        lastName = args.get("lastName")
        firstName = args.get("firstName")
        appId = args.get("appId")

        #- Make the list of attributes
        attributes = os.environ['KEYCLOAK_USER_ATTRIBUTES'].split(',')

        if lastName or firstName or appId:
            usersResult = getusers(lastName, firstName, appId)

            if not usersResult["message"]: 
                users = usersResult["users"]

                for user in users:
                    authGroup = False
                    userAttributes = user["attributes"]

                    #- Initialize each attribute if not exist
                    for attribute in attributes:
                        if not attribute in userAttributes:
                            userAttributes[attribute] = ''
     
                    userGroupResult = getgroupsbyuser(user['id'])

                    if not userGroupResult["message"]:
                        #- Test if the ser is in the Elefan's user group -#
                        for group in userGroupResult["groups"]:
                            if group["path"] == os.environ["KEYCLOAK_AUTH_ELEFAN_GROUP_PATH"]:
                                authGroup = True

                        if authGroup:
                            user_groups = userGroupResult["groups"]
                            usersToSort[user['id']] = {'user': user, 'user_attributes': userAttributes, 'user_groups': user_groups}

                usersToDisplay = sorted(usersToSort.items(), key=get_lastName)

            else:
                message = usersResult["message"]

            groupsResult = getGroupsByName(os.environ['KEYCLOAK_GROUPS_ADMIN_PATH'])

            if not groupsResult["message"]:
                groupsToDisplay = sorted(groupsResult["groups"]['subGroups'], key=lambda d: d['name'])
            else:
                message = usersResult["message"]

        return render_template('users.html', version = version, admin_name = adminUserInfo['firstName'] + ' ' + adminUserInfo['lastName'], users_to_display = dict(usersToDisplay), groups = groupsToDisplay, lastName = lastName, firstName = firstName, message = message) 
    else:
        return redirect("/index", code=302) 

###----- API PART -----###
@app.route('/addGroup/', methods=('GET', 'POST'))
def addGroupToUser():
    if request.method == "POST":
        datas = request.get_json()
        addGroup(datas['user'], datas['group'])

    return ("ok")

@app.route('/removeGroup/', methods=('GET', 'POST'))
def removeGroupToUser():
    if request.method == "POST":
        datas = request.get_json()
        removeGroup(datas['user'], datas['group'])

    return ("ok")

@app.route('/apinewuser/', methods=('GET', 'POST'))
def addUser():
    if request.method == "POST":
        datas = request.get_json()
        result = adduser(datas['email'], datas['firstName'], datas['lastName'], datas['attributes'])
        if result == "error":
            return 'error'
        else:
            return result

@app.route('/apimodifyuser/', methods=('GET', 'POST'))
def modifyUser():
    if request.method == "POST":
        datas = request.get_json() 
        result = updateuser(datas['id'], datas['payload'])
        if result == "error":
            return 'error'
        else:
            return result
        
if __name__ == "__main__":
        app.run()