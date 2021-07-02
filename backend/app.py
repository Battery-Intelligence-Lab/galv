from galvanalyser import create_config, make_celery
import flask
from flask_jwt_extended import JWTManager
import flask_cors

import os

app = flask.Flask(__name__)

app.config.from_mapping(
    create_config(),
)

JWTManager(app)

celery = make_celery(app)

# ensure the instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass


with app.app_context():
    # Import parts of our core Flask app
    from galvanalyser import routes

# match redash secret_key
app.secret_key = os.getenv('REDASH_COOKIE_SECRET')
print('set session key to ', app.secret_key)

# Initializes CORS so that the api can talk to the react app
cors = flask_cors.CORS()
cors.init_app(app)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
