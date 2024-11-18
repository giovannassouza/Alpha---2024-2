from website import create_app
from authlib.integrations.flask_client import OAuth

app = create_app() # create app instance

if __name__ == '__main__':
    app.run(debug=True) # runs app
