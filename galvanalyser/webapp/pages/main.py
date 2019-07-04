import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from galvanalyser.webapp.pages import all_layouts

experiment_selector = html.Div([html.P("placeholder experiment selector")])
experiment_list = html.Div(
    [
        html.P("placeholder experiment list"),
        dcc.RadioItems(id="main_experiments"),
    ]
)
data_ranges = html.Div([html.P("placeholder data ranges")])
plotting_controls = html.Div([html.P("placeholder plotting_controls")])

layout = html.Div(
    [
        dcc.Graph(id="main-graph"),
        experiment_selector,
        experiment_list,
        data_ranges,
        plotting_controls,
    ]
)

all_layouts.append(layout)

# def add_layouts(layouts):
#    layouts.append(layout)


def register_callbacks(app):
    @app.callback(
        Output("app-1-display-value", "children"),
        [Input("app-1-dropdown", "value")],
    )
    def display_value(value):
        return 'You have selected "{}"'.format(value)

    @app.callback(
        [Output("url", "pathname")], [Input("page2-button", "n_clicks")]
    )
    def login_handler(n_clicks):
        return False, "/login"
