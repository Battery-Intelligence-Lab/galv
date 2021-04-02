from galvanalyserapp import init_app, init_db
from galvanalyserapp.database.user import User
from flask_login import LoginManager
from flask_talisman import Talisman

import os

config = init_db()
app = init_app(config)

# match redash secret_key
app.secret_key = os.getenv('REDASH_COOKIE_SECRET')
print('set session key to ', app.secret_key)

Talisman(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    print('LOAD USER')
    return User.get(user_id, config.get_redash_db_connection())

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
