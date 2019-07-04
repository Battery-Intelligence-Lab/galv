import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output


layout = html.Div([
    html.H3('App 1'),
    dcc.Dropdown(
        id='app-1-dropdown',
        options=[
            {'label': 'App 1 - {}'.format(i), 'value': i} for i in [
                'NYC', 'MTL', 'LA'
            ]
        ]
    ),
    html.Div(id='app-1-display-value'),
    dcc.Link('Go to App 2', href='/apps/app2'),
    html.Button(id="page2-button", type="button", children="Login")
])

def add_layouts(layouts):
    layouts.append(layout)

def register_callbacks(app):
    @app.callback(
        Output('app-1-display-value', 'children'),
        [Input('app-1-dropdown', 'value')])
    def display_value(value):
        return 'You have selected "{}"'.format(value)

    @app.callback(
    [Output("url", "pathname")],
    [Input("page2-button", "n_clicks")],
    )
    def login_handler(n_clicks):
        return False, "/login"