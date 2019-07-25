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
from galvanalyser.webapp.pages import all_layouts


def log(text):
    with open("/tmp/log.txt", "a") as myfile:
        myfile.write(text + "\n")


db_conf = {
    "database_name": "galvanalyser",
    "database_port": 5432,
    "database_host": "postgres",
}

layout = html.Div(
    children=[
        html.Div(id="login_refresh_dummy", hidden=True),
        html.Form(  # action='login', method='post',
            children=[
                dcc.Input(
                    id="login_input_username",
                    type="text",
                    value="",
                    name="username",
                ),
                dcc.Input(
                    id="login_input_password",
                    type="password",
                    value="",
                    name="password",
                ),
                dcc.Checklist(
                    id="login_input_remember",
                    options=[{"label": "Remember me?", "value": "True"}],
                    value=[],
                ),
                html.Button(
                    id="login_input_submit", type="button", children="Login"
                ),
            ]
        ),
        html.Div(id="login_status", hidden=False, children=""),
    ]
)

all_layouts.append(layout)

# def add_layouts(layouts):
#    layouts.append(layout_login)


def register_callbacks(app, config, login_manager):
    @login_manager.unauthorized_handler
    def unauthorized_handler():
        return redirect("/")

    @login_manager.user_loader
    def user_loader(id_str):
        conn = None
        try:
            username, password = id_str.split(":", 1)
            conn = psycopg2.connect(
                host=config["db_conf"]["database_host"],
                port=config["db_conf"]["database_port"],
                database=config["db_conf"]["database_name"],
                user=username,
                password=password,
            )
            user = User()
            user.id = id_str
            return user
        except:
            pass
            # psycopg2.OperationalError: FATAL:  the database system is starting up
        finally:
            if conn:
                conn.close()
        return

    @app.callback(
        Output("login_status", "children"),
        [
            Input("login_input_submit", "n_clicks"),
            Input("login_input_password", "n_submit"),
        ],
        [
            State("login_input_username", "value"),
            State("login_input_password", "value"),
            State("login_input_remember", "value"),
        ],
    )
    def login_handler(n_clicks, n_submit, username, password, remember):
        if n_clicks or n_submit:
            id_str = f"{username}:{password}"
            user = user_loader(id_str)
            log(repr(remember))
            if user:
                flask_login.login_user(user, remember=bool(remember))
                return "Login Success"
            else:
                return "Login Failed"
        else:
            raise PreventUpdate

    app.clientside_callback(
        ClientsideFunction(
            namespace="clientside_login", function_name="login_refresh"
        ),
        [Output("login_refresh_dummy", "children")],
        [Input("login_status", "children")],
    )

    @app.server.route("/logout")
    def logout():
        flask_login.logout_user()
        return redirect("/")


class User(flask_login.UserMixin):
    pass
