from website import create_app
from authlib.integrations.flask_client import OAuth

app = create_app() # create app instance

# Debugging
import os

# Enable insecure transport for development
os.environ['AUTHLIB_INSECURE_TRANSPORT'] = 'true'



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))  # Usa a porta definida pelo Railway
