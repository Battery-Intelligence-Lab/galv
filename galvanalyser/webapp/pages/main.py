import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, ClientsideFunction
from galvanalyser.webapp.pages import all_layouts
import dash_table

from galvanalyser.database.experiment.experiments_row import ExperimentsRow
from galvanalyser.database.experiment.metadata_row import MetaDataRow
import psycopg2
from galvanalyser.webapp.datahandling import data_server


def log(text):
    with open("/tmp/log.txt", "a") as myfile:
        myfile.write(text + "\n")


graph_section = html.Div(
    [
        dcc.Graph(id="main-graph"),
        html.Div(id="graph_update_dummy", hidden=True),
    ]
)

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
        html.Form(
            children=[
                dash_table.DataTable(
                    id="experiment_table",
                    row_selectable="single",
                    columns=[
                        {"name": i, "id": i}
                        for i in ["id", "name", "date", "type"]
                    ],
                    # data=[{"hello":"aa","world":"bb","id":1}]
                )
            ]
        ),
    ]
)
data_ranges = html.Div(
    [
        html.P("placeholder data ranges"),
        html.P(id="main_selected_experiment"),
        html.Form(
            children=[
                dash_table.DataTable(
                    id="metadata_table",
                    row_selectable="multi",
                    columns=[
                        {"name": i, "id": i}
                        for i in [
                            "label_name",
                            "samples_from",
                            "samples_to",
                            "info",
                        ]
                    ],
                    # data=[{"hello":"aa","world":"bb","id":1}]
                )
            ]
        ),
        html.Button(
            id="btn_add_data_range_to_plot",
            type="button",
            children="Plot Data Range",
        ),
    ]
)
plotting_controls = html.Div(
    [
        html.P("placeholder plotting_controls"),
        html.Form(
            children=[
                dash_table.DataTable(
                    id="plot_ranges_table",
                    row_selectable="multi",
                    columns=[
                        {"name": i, "id": i}
                        for i in [
                            "experiment",
                            "label_name",
                            "samples_from",
                            "samples_to",
                            "info",
                        ]
                    ],
                    # data=[{"hello":"aa","world":"bb","id":1}]
                )
            ]
        ),
    ]
)

layout = html.Div(
    [
        graph_section,
        experiment_selector,
        experiment_list,
        data_ranges,
        plotting_controls,
    ]
)

all_layouts.append(layout)


def register_callbacks(app, config):
    @app.callback(
        Output("experiment_table", "data"),
        [Input("main_get_experiments", "n_clicks")],
    )
    def get_experiments(n_clicks):
        log("in get_experiments")
        options = []
        if n_clicks:
            conn = None
            try:
                conn = config["get_db_connection_for_current_user"]()
                experiments = ExperimentsRow.select_all_experiments(conn)
                options = [
                    {
                        "id": exp.id,
                        "name": exp.name,
                        "date": exp.date,
                        "type": exp.experiment_type,
                    }
                    for exp in experiments
                ]
            finally:
                if conn:
                    conn.close()
        return options

    @app.callback(
        [
            Output("main_selected_experiment", "children"),
            Output("metadata_table", "data"),
        ],
        [Input("experiment_table", "selected_row_ids")],
    )
    def experiment_selected(selected_row_ids):
        info_line = f"Selected: {selected_row_ids}"
        table_rows = []
        conn = None
        try:
            conn = config["get_db_connection_for_current_user"]()
            if selected_row_ids:
                selected_row_id = selected_row_ids[0]
                try:
                    metadatas = MetaDataRow.select_from_experiment_id(
                        selected_row_id, conn
                    )
                    table_rows = [
                        {
                            "id": f"{selected_row_id}:{m.label_name}",
                            "experiment": selected_row_id,
                            "label_name": m.label_name,
                            "samples_from": m.lower_bound,
                            "samples_to": m.upper_bound,
                            "info": m.info,
                        }
                        for m in metadatas
                    ]
                except psycopg2.errors.InsufficientPrivilege:
                    info_line = f"Permission denied when retrieving metadata for experiment id {selected_row_ids}"
        finally:
            if conn:
                conn.close()
        return info_line, table_rows

    @app.callback(
        Output("plot_ranges_table", "data"),
        [Input("btn_add_data_range_to_plot", "n_clicks")],
        [
            State("metadata_table", "selected_rows"),
            State("metadata_table", "data"),
        ],
    )
    def add_data_range_to_plot(n_clicks, selected_rows, table_rows):
        results = []
        if n_clicks and selected_rows:
            for row_idx in selected_rows:
                results.append(table_rows[row_idx])
        return results

    app.clientside_callback(
        ClientsideFunction(
            namespace="clientside_graph", function_name="update_graph_trigger"
        ),
        [Output("graph_update_dummy", "children")],
        [Input("plot_ranges_table", "data")],
    )

    data_server.register_handlers(app, config)
