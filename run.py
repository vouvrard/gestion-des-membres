import os
import keycloakapp
from keycloakapp import app

if __name__ == "__main__":
        app.run(host = '0.0.0.0', port = os.environ['APP_PORT'])