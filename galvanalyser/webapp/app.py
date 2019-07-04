import galvanalyser.webapp.pages as pages
import dash
import flask
import flask_login
from flask_login import current_user

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output


url_bar_and_content_div = html.Div(
    [
        html.Div(id="placeholder"),
        html.Div(id="placeholder2"),
        dcc.Location(id="url", refresh=False),
        html.Div(id="page-content"),
        html.Div(id='output-state'),
    ]
)


if __name__ == "__main__":
    layouts = [url_bar_and_content_div] + pages.all_layouts
    #pages.login.add_layouts(layouts)
    #pages.main.add_layouts(layouts)

    def serve_layout():
        print("in serve_layout")
        if flask.has_request_context():
            print("flask.has_request_context")
            if current_user.is_authenticated:
                return url_bar_and_content_div
            else:
                return pages.login.layout
        print("!flask.has_request_context")
        return html.Div(layouts)

    app = dash.Dash(
    __name__,
    external_stylesheets=["https://codepen.io/chriddyp/pen/bWLwgP.css"],
    )

    app.config.supress_callback_exceptions = True
    #app.renderer = '''
    #var renderer = new DashRenderer(request_hooks);
    #'''

    login_manager = flask_login.LoginManager()

    login_manager.init_app(app.server)
    app.layout = serve_layout

    @app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
    def display_page(pathname):
        if pathname == '/login':
            return pages.login.layout_login
        elif pathname == '/apps/app2':
            return pages.main.layout
        else:
            return '404'
    pages.login.register_callbacks(app, login_manager)
    pages.main.register_callbacks(app)


    print("running")
    # TODO read this from an external file
    app.server.secret_key = b'sdfg_5#y2L"F4Q8z\n\xec]/'
    app.run_server(debug=True, host="0.0.0.0")
