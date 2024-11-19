from website import create_app
from authlib.integrations.flask_client import OAuth

app = create_app() # create app instance

# Debugging
import os

# Enable insecure transport for development
os.environ['AUTHLIB_INSECURE_TRANSPORT'] = 'true'


if __name__ == '__main__':
    app.run(debug=True) # runs app
