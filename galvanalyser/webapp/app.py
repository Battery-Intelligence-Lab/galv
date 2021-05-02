from galvanalyserapp import init_app
import flask_cors

import os

app = init_app()

# match redash secret_key
app.secret_key = os.getenv('REDASH_COOKIE_SECRET')
print('set session key to ', app.secret_key)

# Initializes CORS so that the api can talk to the react app
cors = flask_cors.CORS()
cors.init_app(app)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
