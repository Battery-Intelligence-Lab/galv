import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from galvanalyser.webapp.pages import all_layouts
import dash_table

from galvanalyser.database.experiment.experiments_row import ExperimentsRow

def log(text):
    with open("/tmp/log.txt", "a") as myfile:
        myfile.write(text + "\n")

experiment_selector = html.Div(
    [
        html.P("placeholder experiment selector"),
        html.Button(
            id="main_get_experiments",
            type="button",
            children="Get Experiments",
        ),
    ]
)
experiment_list = html.Div(
    [
        html.P("placeholder experiment list"),
        dcc.RadioItems(id="main_experiments"),
        dash_table.DataTable(id='table',row_selectable="single",
    columns=[{"name": i, "id": i} for i in ["id", "name","date", "type"]],
    data=[{"hello":"aa","world":"bb","id":1}])
    ]
)
data_ranges = html.Div([html.P("placeholder data ranges"), html.P(id="main_selected_experiment")])
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


def register_callbacks(app, config):
    @app.callback(
        Output("table", "data"),
        [Input("main_get_experiments", "n_clicks")]
    )
    def get_experiments(n_clicks):
        log("in get_experiments")
        options = []
        if n_clicks:
            try:
                conn = config["get_db_connection_for_current_user"]()
                experiments = ExperimentsRow.select_all_experiments(conn)
                options = [{"id": exp.id,
                            "name": exp.name, "date": exp.date, "type": exp.experiment_type} for exp in experiments]
            finally:
                conn.close()
        return options
    
    @app.callback(
        Output("main_selected_experiment", "children"),
        [ Input("table", "selected_row_ids")]
    )
    def experiment_selected(selected_row_ids):
        return f"Selected: {selected_row_ids}"


