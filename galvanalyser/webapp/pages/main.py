import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, ClientsideFunction
from galvanalyser.webapp.pages import all_layouts
import dash_table

from galvanalyser.database.experiment.dataset_row import DatasetRow
from galvanalyser.database.experiment.range_label_row import RangeLabelRow
import galvanalyser.database.experiment.timeseries_data_column as TimeseriesDataColumn
import psycopg2
from galvanalyser.webapp.datahandling import data_server
from galvanalyser_dash_components import GalvanalyserLegend

# Reference for selection interaction https://dash.plot.ly/interactive-graphing
# Plotly python reference https://plot.ly/python/reference/
# Plotly js reference https://plot.ly/javascript/reference/
# and https://dash.plot.ly/dash-core-components
# also https://raw.githubusercontent.com/plotly/plotly.py/master/packages/python/plotly/plotly/graph_objs/__init__.py
# and https://github.com/plotly/dash-core-components/blob/dev/dash_core_components/Graph.py
# and https://github.com/plotly/dash-html-components/blob/master/dash_html_components/Div.py
def log(text):
    with open("/tmp/log.txt", "a") as myfile:
        myfile.write(text + "\n")


dataset_selector = html.Div(
    [
        html.P("placeholder dataset selector"),
        html.Button(
            id="main_get_dataset", type="button", children="Get Dataset"
        ),
    ]
)
dataset_list = html.Div(
    [
        html.P("placeholder dataset list"),
        dcc.RadioItems(id="main_dataset"),
        html.Form(
            children=[
                dash_table.DataTable(
                    id="dataset_table",
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
        html.P(id="main_selected_dataset"),
        html.Form(
            children=[
                dash_table.DataTable(
                    id="metadata_table",
                    row_selectable="multi",
                    columns=[
                        {"name": i, "id": i}
                        for i in [
                            "label_name",
                            "column",
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
                        {
                            "name": i,
                            "id": i,
                            "editable": True if i == "offset" else False,
                        }
                        for i in [
                            "dataset_id",
                            "label_name",
                            "column",
                            "samples_from",
                            "samples_to",
                            "info",
                            "offset",
                        ]
                    ],
                    # data=[{"hello":"aa","world":"bb","id":1}]
                )
            ]
        ),
        html.Button(
            id="btn_remove_data_range_from_plot",
            type="button",
            children="Remove Data Range",
        ),
        html.Button(
            id="btn_apply_offset_to_data_range",
            type="button",
            children="Apply offset",
        ),
    ]
)
tab_graph_content = html.Div(
    id="tab_graph_content",
    children=[
        dcc.Graph(
            id="main-graph",
            figure={"layout": {"clickmode": "event+select"}},
            config={
                "displaylogo": False,
                "responsive": True,
                "fillFrame": False,
                #'modeBarButtonsToAdd': [{'name':x }for x in ['select2d','lasso2d']]
            },
        ),
        html.Div(id="graph_update_dummy", hidden=True),
    ],
)

tab_dataset_content = html.Div(
    id="tab_dataset_content",
    children=[dataset_selector, dataset_list, data_ranges],
    hidden=True,
)

tab_legend_content = html.Div(
    id="tab_legend_content",
    children=[html.P("placeholder legend content"), plotting_controls, 
    GalvanalyserLegend(id='my-first-legend', graphId="main-graph",
        entries=[{"foo":x} for x in ["foo", "bar", "spam", "eggs", "harry", "bear"]],
        label='my-label')
    ],
)

tab_export_content = html.Div(
    id="tab_export_content",
    children=[html.P("placeholder export content")],
    hidden=True,
)

main_tabs_container = html.Div(
    id="main_tabs_container",
    children=[
        dcc.Tabs(
            id="main_tabs",
            value="tab_graph",
            children=[
                dcc.Tab(label="Plotting", value="tab_graph"),
                dcc.Tab(label="Select Dataset", value="tab_dataset"),
            ],
        ),
        html.Div(
            id="main_tabs_content",
            children=[tab_graph_content, tab_dataset_content],
        ),
    ],
)

side_tabs_container = html.Div(
    id="side_tabs_container",
    children=[
        dcc.Tabs(
            id="side_tabs",
            value="tab_legend",
            children=[
                dcc.Tab(label="Legend", value="tab_legend"),
                dcc.Tab(label="Export", value="tab_export"),
            ],
        ),
        html.Div(
            id="side_tabs_content",
            children=[tab_legend_content, tab_export_content],
        ),
    ],
)


layout = html.Div(
    id="main_page_container",
    children=[main_tabs_container, side_tabs_container],
)

all_layouts.extend(
    [
        layout,
        tab_graph_content,
        tab_dataset_content,
        tab_legend_content,
        tab_export_content,
    ]
)


def register_callbacks(app, config):
    @app.callback(
        [
            Output("tab_graph_content", "hidden"),
            Output("tab_dataset_content", "hidden"),
        ],
        [Input("main_tabs", "value")],
    )
    def render_main_tabs_content(tab):
        if tab == "tab_graph":
            return False, True
        elif tab == "tab_dataset":
            return True, False

    @app.callback(
        [
            Output("tab_legend_content", "hidden"),
            Output("tab_export_content", "hidden"),
        ],
        [Input("side_tabs", "value")],
    )
    def render_main_tabs_content(tab):
        if tab == "tab_legend":
            return False, True
        elif tab == "tab_export":
            return True, False

    @app.callback(
        Output("dataset_table", "data"),
        [Input("main_get_dataset", "n_clicks")],
    )
    def get_dataset(n_clicks):
        log("in get_dataset")
        options = []
        if n_clicks:
            conn = None
            try:
                conn = config["get_db_connection_for_current_user"]()
                dataset = DatasetRow.select_all_dataset(conn)
                options = [
                    {
                        "id": exp.id,
                        "name": exp.name,
                        "date": exp.date,
                        "type": exp.dataset_type,
                    }
                    for exp in dataset
                ]
            finally:
                if conn:
                    conn.close()
        return options

    @app.callback(
        [
            Output("main_selected_dataset", "children"),
            Output("metadata_table", "data"),
            Output("metadata_table", "selected_rows"),
        ],
        [Input("dataset_table", "selected_row_ids")],
    )
    def dataset_selected(selected_row_ids):
        info_line = f"Selected: {selected_row_ids}"
        table_rows = []
        conn = None
        try:
            conn = config["get_db_connection_for_current_user"]()
            # populate columns properly, don't include "test_time"
            # available_columns = ["volts", "amps"]
            if selected_row_ids:
                selected_row_id = selected_row_ids[0]
                available_columns = TimeseriesDataColumn.select_experiment_columns(
                    selected_row_id, conn
                )
                try:
                    metadatas = RangeLabelRow.select_from_dataset_id(
                        selected_row_id, conn
                    )
                    table_rows = [
                        {
                            "id": f"{selected_row_id}:{col}:{m.label_name}",
                            "dataset_id": selected_row_id,
                            "label_name": m.label_name,
                            "column": col[1],
                            "column_id": col[0],
                            "samples_from": m.lower_bound,
                            "samples_to": m.upper_bound,
                            "info": m.info,
                            "offset": 0.0,
                        }
                        for m in metadatas
                        for col in available_columns
                    ]
                except psycopg2.errors.InsufficientPrivilege:
                    info_line = f"Permission denied when retrieving metadata for dataset id {selected_row_ids}"
        finally:
            if conn:
                conn.close()
        return info_line, table_rows, []

    @app.callback(
        [
            Output("plot_ranges_table", "data"),
            Output("plot_ranges_table", "selected_rows"),
        ],
        [
            Input("btn_add_data_range_to_plot", "n_clicks"),
            Input("btn_remove_data_range_from_plot", "n_clicks"),
            Input("btn_apply_offset_to_data_range", "n_clicks"),
        ],
        [
            State("metadata_table", "selected_rows"),
            State("metadata_table", "data"),
            State("plot_ranges_table", "data"),
            State("plot_ranges_table", "selected_rows"),
            State("main-graph", "relayoutData"),
        ],
    )
    def add_data_range_to_plot(
        add_n_clicks,
        remove_n_clicks,
        offset_n_clicks,
        metadata_selected_rows,
        metadata_table_rows,
        plotted_table_rows,
        plotted_selected_rows,
        graph_relayout_data,
    ):
        results = plotted_table_rows if plotted_table_rows is not None else []
        ctx = dash.callback_context
        if ctx.triggered:
            button_id = ctx.triggered[0]["prop_id"].split(".")[0]
            if (
                button_id == "btn_add_data_range_to_plot"
                and add_n_clicks
                and metadata_selected_rows
            ):
                for row_idx in metadata_selected_rows:
                    if metadata_table_rows[row_idx] not in results:
                        results.append(metadata_table_rows[row_idx])
            if (
                button_id == "btn_remove_data_range_from_plot"
                and add_n_clicks
                and plotted_selected_rows
            ):
                reverse_index_list = sorted(
                    plotted_selected_rows, reverse=True
                )
                for row_idx in reverse_index_list:
                    del results[row_idx]
                plotted_selected_rows = []
            if (
                button_id == "btn_apply_offset_to_data_range"
                and offset_n_clicks
                and plotted_selected_rows
                and graph_relayout_data
            ):
                log(repr(graph_relayout_data))
                for row_idx in plotted_selected_rows:
                    results[row_idx]["offset"] = graph_relayout_data.get(
                        "xaxis.range[0]", 0.0
                    )
        return results, plotted_selected_rows or []

    app.clientside_callback(
        ClientsideFunction(
            namespace="clientside_graph", function_name="update_graph_trigger"
        ),
        [Output("graph_update_dummy", "children")],
        [Input("plot_ranges_table", "data")],
    )

    data_server.register_handlers(app, config)
