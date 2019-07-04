import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import ClientsideFunction, Input, Output, State
# https://github.com/plotly/dash/search?q=no_update&unscoped_q=no_update
from dash import no_update
from dash.exceptions import PreventUpdate
from flask import redirect
import flask
import flask_login
import psycopg2

def log(text):
    with open("/tmp/log.txt", "a") as myfile:
        myfile.write(text+"\n")


db_conf = {
    "database_name": "galvanalyser", 
    "database_port": 5432,
    "database_host": "postgres"
}

layout_login = html.Div(children=[
    html.Div(id="login-refresh-dummy", hidden=True),
    html.Form(#action='login', method='post',
    children=[
    dcc.Input(id="input-username", type="text", value="", name="username"),
    dcc.Input(id="input-password", type="password", value="", name="password"),
    html.Button(id="input-submit", type="button", children="Login"),
  ]),
  html.Div(id="login-status", hidden=False, children="")
])

def add_layouts(layouts):
    layouts.append(layout_login)

def register_callbacks(app, login_manager):
    @login_manager.unauthorized_handler
    def unauthorized_handler():
        redirect("/")
    
    @login_manager.user_loader
    def user_loader(id_str):
        conn = None
        try:
            username, password = id_str.split(':', 1)
            conn = psycopg2.connect(
                host=db_conf["database_host"],
                port=db_conf["database_port"],
                database=db_conf["database_name"],
                user=username,
                password=password,
            )
            user = User()
            user.id = id_str
            return user
        except:
            pass
            #psycopg2.OperationalError: FATAL:  the database system is starting up
        finally:
            if conn:
                conn.close()
        return

    @app.callback(
    Output("login-status", "children"),
    [Input("input-submit", "n_clicks")],
    [State("input-username", "value"), State("input-password", "value")],
    )
    def login_handler(n_clicks, username, password):
        if n_clicks:
            id_str = f"{username}:{password}"
            user = user_loader(id_str)
            if user:
                flask_login.login_user(user)
                return "Login Success"
            else:
                return "Login Failed"
        else:
            raise PreventUpdate

    app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='redirect'
    ),
    [Output("url-page1a", "children")],
    [Input('url-page1', 'children')]
    )

    app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='login_refresh'
    ),
    [Output("login-refresh-dummy", "children")],
    [Input('login-status', 'children')]
    )

    @app.server.route('/logout')
    def logout():
        flask_login.logout_user()
        return redirect("/")

class User(flask_login.UserMixin):
    pass