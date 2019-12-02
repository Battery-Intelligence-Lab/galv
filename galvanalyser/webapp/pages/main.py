import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, ClientsideFunction
from dash.exceptions import PreventUpdate
from galvanalyser.webapp.pages import all_layouts
import dash_table

from galvanalyser.database.experiment.dataset_row import DatasetRow
from galvanalyser.database.experiment.range_label_row import RangeLabelRow
from galvanalyser.database.user_data.range_label_row import (
    RangeLabelRow as UserRangeLabelRow,
)
import galvanalyser.database.experiment.timeseries_data_column as TimeseriesDataColumn
from galvanalyser.database.experiment.timeseries_data_row import (
    TimeseriesDataRow,
    TEST_TIME_COLUMN_ID,
)
import psycopg2
from galvanalyser.webapp.datahandling import data_server
from galvanalyser_dash_components import GalvanalyserLegend
from galvanalyser.webapp.colours import (
    D3 as colours_D3,
    Light24 as colours_Light24,
)
import sys

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


dataset_filter = html.Div(
    [
        html.P("Dataset Filters"),  # populate these from the db
        html.Span(
            title="% matches 0 or more characters\n_ matches any single character",
            children=[
                "Name Like: ",
                dcc.Input(
                    "dataset_name_filter",
                    type="text",
                    placeholder="Dataset name",
                    persistence=True,
                    persistence_type="memory",
                ),
            ],
        ),
        html.Span(
            title="Selection range is limited based on displayed datasets",
            children=[
                "Date From: ",
                dcc.DatePickerSingle(
                    id="dataset_date_from_filter",
                    display_format="YYYY MM DD",
                    clearable=True,
                    persistence=True,
                    persistence_type="memory",
                ),
                "Date To: ",
                dcc.DatePickerSingle(
                    id="dataset_date_to_filter",
                    display_format="YYYY MM DD",
                    clearable=True,
                    persistence=True,
                    persistence_type="memory",
                ),
            ],
        ),
        html.Span(
            title="Available options are limited based on displayed datsets",
            children=[
                "Type: ",
                dcc.Dropdown(
                    id="dataset_machine_type_filter",
                    multi=True,
                    persistence=True,
                    persistence_type="memory",
                    placeholder="Search by machine type",
                    style={
                        "width": "auto",
                        "display": "table-cell",
                        "min-width": "220px",
                    },
                ),
            ],
        ),
    ]
)
dataset_selector = html.Div(
    [
        dataset_filter,
        html.Button(
            id="main_get_dataset", type="button", children="Get Datasets"
        ),
    ]
)
dataset_list = html.Div(
    [
        html.P("Dataset list"),
        dcc.RadioItems(id="main_dataset"),
        html.Form(
            children=[
                dcc.Loading(
                    id="dataset_range_table_loading",
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
                    ],
                )
            ]
        ),
    ]
)
data_ranges = html.Div(
    [
        html.P("Data ranges"),
        html.P(id="main_selected_dataset"),
        html.Form(
            children=[
                dcc.Loading(
                    id="dataset_range_table_loading",
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
                                    "user_created",
                                ]
                            ],
                            # data=[{"hello":"aa","world":"bb","id":1}]
                        )
                    ],
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
range_editor = html.Div(
    children=[
        html.Button(
            id="btn_show_hide_range_editor",
            type="button",
            children="Show Range Editor",
        ),
        html.Div(
            id="range_editor",
            hidden=True,
            children=[
                html.P("Range Editor"),
                html.P(
                    children=[
                        "Range for Dataset:",
                        dcc.Dropdown(id="range_dataset_dropdown"),
                    ]
                ),
                html.Button(
                    id="btn_custom_range_from_view",
                    type="button",
                    children="Use Current Chart Range",
                ),
                html.P(
                    children=[
                        "From: ",
                        dcc.Input(
                            id="custom_range_from_value",
                            type="number",
                            value="0",
                        ),
                        html.Br(),
                        "Closest lower sample number: ",
                        html.Span(id="custom_range_from_display", children=""),
                    ]
                ),
                html.P(
                    children=[
                        "To: ",
                        dcc.Input(
                            id="custom_range_to_value",
                            type="number",
                            value="0",
                        ),
                        html.Br(),
                        "Closest higher sample number: ",
                        html.Span(id="custom_range_to_display", children=""),
                    ]
                ),
                html.P(
                    children=[
                        "Range Name: ",
                        dcc.Input(
                            id="custom_range_name",
                            type="text",
                            value="",
                            placeholder="Enter name for range",
                        ),
                        html.Button(
                            id="btn_save_custom_range",
                            type="button",
                            children="Save Custom Range",
                        ),
                        html.Button(
                            id="btn_update_custom_range",
                            type="button",
                            children="Update Custom Range",
                        ),
                    ]
                ),
                html.P(id="create_range_result", children=""),
            ],
        ),
    ]
)
plotting_controls = html.Div(
    [
        range_editor,
        html.Button(
            id="btn_set_reference_value_to_view",
            type="button",
            children="Set Reference Value to View",
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
                "editable": True,
                #'modeBarButtonsToAdd': [{'name':x }for x in ['select2d','lasso2d']],
                "modeBarButtonsToRemove": ["toImage"],
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
    children=[
        plotting_controls,
        GalvanalyserLegend(
            id="my-first-legend", graphId="main-graph", label="my-label"
        ),
    ],
)

tab_export_content = html.Div(
    id="tab_export_content",
    children=[
        html.Div(
            children=[
                "Export format",
                dcc.RadioItems(
                    id="export-format-options",
                    options=[
                        {"label": "PNG", "value": "png"},
                        {"label": "SVG", "value": "svg"},
                        {"label": "JPG", "value": "jpg"},
                        {"label": "WEBP", "value": "webp"},
                    ],
                    value="png",
                ),
            ]
        ),
        html.Div(
            children=[
                "Width",
                dcc.Input(
                    id="export-width-input", type="number", value="1920"
                ),
            ]
        ),
        html.Div(
            children=[
                "Height",
                dcc.Input(
                    id="export-height-input", type="number", value="1080"
                ),
            ]
        ),
        html.Div(
            children=[
                "Scale",
                dcc.Input(id="export-scale-input", type="number", value="1.0"),
            ]
        ),
        html.Div(
            children=[
                "File name",
                dcc.Input(
                    id="export-filename-input",
                    placeholder="(without extension)",
                    type="text",
                    value="",
                ),
            ]
        ),
        html.Button(
            id="btn_export_image", type="button", children="Save Image"
        ),
        html.Div(id="export_plot_dummy", hidden=True),
    ],
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
        [
            Output("dataset_table", "data"),
            Output("dataset_date_from_filter", "min_date_allowed"),
            Output("dataset_date_from_filter", "max_date_allowed"),
            Output("dataset_date_to_filter", "min_date_allowed"),
            Output("dataset_date_to_filter", "max_date_allowed"),
            Output("dataset_date_from_filter", "initial_visible_month"),
            Output("dataset_date_to_filter", "initial_visible_month"),
            Output("dataset_machine_type_filter", "options"),
        ],
        [Input("main_get_dataset", "n_clicks")],
        [
            State("dataset_name_filter", "value"),
            State("dataset_date_from_filter", "date"),
            State("dataset_date_to_filter", "date"),
            State("dataset_machine_type_filter", "value"),
        ],
    )
    def get_dataset(
        n_clicks,
        name_filter,
        date_min_filter,
        date_max_filter,
        machine_type_filter,
    ):
        log("in get_dataset")
        dataset_rows = []
        min_date = None
        max_date = None
        machine_type_options = []
        if n_clicks:
            conn = None
            try:
                conn = config["get_db_connection_for_current_user"]()
                dataset = DatasetRow.select_filtered_dataset(
                    conn,
                    name_filter,
                    date_min_filter,
                    date_max_filter,
                    machine_type_filter,
                )
                dataset_rows = [
                    {
                        "id": exp.id,
                        "name": exp.name,
                        "date": exp.date,
                        "type": exp.dataset_type,
                    }
                    for exp in dataset
                ]
                dates = [row["date"] for row in dataset_rows]
                if len(dates) > 0:
                    min_date = min(dates)
                    max_date = max(dates)
                machine_type_options = [
                    {"label": machine_type, "value": machine_type}
                    for machine_type in {row["type"] for row in dataset_rows}
                ]
            finally:
                if conn:
                    conn.close()
        return (
            dataset_rows,
            min_date,
            max_date,
            min_date,
            max_date,
            min_date,
            max_date,
            machine_type_options,
        )

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
        # TODO handle filtering of label ranges here
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
                            "id": f"{selected_row_id}:{m.id}:{col}:{m.label_name}",
                            "dataset_id": selected_row_id,
                            "label_name": m.label_name,
                            "column": col[1],
                            "column_id": col[0],
                            "samples_from": m.lower_bound,
                            "samples_to": m.upper_bound - 1,
                            "start_time": TimeseriesDataRow.select_from_dataset_id_column_id_and_sample_no(
                                selected_row_id,
                                TEST_TIME_COLUMN_ID,
                                m.lower_bound,
                                conn,
                            ).value,
                            "end_time": TimeseriesDataRow.select_from_dataset_id_column_id_and_sample_no(
                                selected_row_id,
                                TEST_TIME_COLUMN_ID,
                                m.upper_bound - 1,
                                conn,
                            ).value,
                            "info": m.info,
                            "user_created": m.user_created,
                            "offset": 0.0,
                            "colour": "#000000",
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
            Output("my-first-legend", "requested_ranges"),
            Output("range_dataset_dropdown", "options"),
            Output("range_dataset_dropdown", "value"),
        ],
        [
            Input("btn_add_data_range_to_plot", "n_clicks"),
            Input("my-first-legend", "n_updated"),
        ],
        [
            State("metadata_table", "selected_rows"),
            State("metadata_table", "data"),
            State("my-first-legend", "requested_ranges"),
            State("main-graph", "relayoutData"),
            State("dataset_table", "data"),
            State("range_dataset_dropdown", "value"),
        ],
    )
    def add_data_range_to_plot(
        add_n_clicks,
        legend_n_updated,
        metadata_selected_rows,
        metadata_table_rows,
        plotted_table_rows,
        graph_relayout_data,
        dataset_table_data,
        range_dataset_value,
    ):
        requested_ranges = (
            plotted_table_rows if plotted_table_rows is not None else []
        )
        current_range_ids = set(range["id"] for range in requested_ranges)
        ctx = dash.callback_context
        if ctx.triggered:
            button_id = ctx.triggered[0]["prop_id"].split(".")[0]
            if (
                button_id == "btn_add_data_range_to_plot"
                and add_n_clicks
                and metadata_selected_rows
            ):
                for row_idx in metadata_selected_rows:
                    if (
                        metadata_table_rows[row_idx]["id"]
                        not in current_range_ids
                    ):
                        requested_ranges.append(metadata_table_rows[row_idx])
        # Graph colours
        dataset_ids = sorted(
            list(set(row["dataset_id"] for row in requested_ranges))
        )
        dataset_columns = {id: set() for id in dataset_ids}
        for row in requested_ranges:
            dataset_columns[row["dataset_id"]].add(row["column_id"])
        total_plots = 0
        plot_colour_indices = {}
        for dataset_id in dataset_ids:
            dataset_columns[dataset_id] = sorted(
                list(dataset_columns[dataset_id])
            )
            for column_id in dataset_columns[dataset_id]:
                plot_colour_indices[(dataset_id, column_id)] = total_plots
                total_plots = total_plots + 1
        if total_plots < 10:
            colours = colours_D3
        else:
            colours = colours_Light24
        for row in requested_ranges:
            row["colour"] = colours[
                plot_colour_indices[(row["dataset_id"], row["column_id"])]
            ]
        # Custom range dataset dropdown population
        dataset_names = {row["id"]: row["name"] for row in dataset_table_data}
        range_options = [
            {"label": dataset_names[id_], "value": id_} for id_ in dataset_ids
        ]
        if len(dataset_ids) > 0 and (
            range_dataset_value is None or range_dataset_value == ""
        ):
            range_dataset_value = dataset_ids[0]
        return (requested_ranges, range_options, range_dataset_value)

    @app.callback(
        [Output("my-first-legend", "reference_value")],
        [Input("btn_set_reference_value_to_view", "n_clicks")],
        [
            State("main-graph", "relayoutData"),
            State("my-first-legend", "reference_value"),
        ],
    )
    def set_reference_value_to_view(
        set_ref_n_clicks, graph_relayout_data, current_reference_value
    ):
        reference_value = current_reference_value
        ctx = dash.callback_context
        if ctx.triggered:
            button_id = ctx.triggered[0]["prop_id"].split(".")[0]
            if (
                button_id == "btn_set_reference_value_to_view"
                and set_ref_n_clicks
                and graph_relayout_data
            ):
                log(repr(graph_relayout_data))
                reference_value = graph_relayout_data.get(
                    "xaxis.range[0]", 0.0
                )
        return (reference_value,)

    app.clientside_callback(
        ClientsideFunction(
            namespace="plot_export", function_name="export_plot"
        ),
        [Output("export_plot_dummy", "children")],
        [Input("btn_export_image", "n_clicks")],
        [
            State("main-graph", "id"),
            State("export-format-options", "value"),
            State("export-width-input", "value"),
            State("export-height-input", "value"),
            State("export-scale-input", "value"),
            State("export-filename-input", "value"),
        ],
    )

    @app.callback(
        [
            Output("btn_show_hide_range_editor", "children"),
            Output("range_editor", "hidden"),
        ],
        [Input("btn_show_hide_range_editor", "n_clicks")],
        [State("range_editor", "hidden")],
    )
    def toggle_range_editor(n_clicks, editor_hidden):
        hide_editor = True
        if n_clicks:
            hide_editor = not editor_hidden
        button_label = (
            "Show Range Editor" if hide_editor else "Hide Range Editor"
        )
        return (button_label, hide_editor)

    # This is clientside to avoid shipping all the plot data back to the server
    # just to get the current xaxis range
    app.clientside_callback(
        ClientsideFunction(
            namespace="custom_range", function_name="get_from_plot_view"
        ),
        [
            Output("custom_range_from_value", "value"),
            Output("custom_range_to_value", "value"),
        ],
        [Input("btn_custom_range_from_view", "n_clicks")],
        [
            State("main-graph", "id"),
            State("custom_range_from_value", "value"),
            State("custom_range_to_value", "value"),
        ],
    )

    @app.callback(
        [Output("custom_range_from_display", "children")],
        [
            Input("custom_range_from_value", "value"),
            Input("range_dataset_dropdown", "value"),
        ],
    )
    def update_range_from_sample_no(xaxis_value, dataset_id):
        # query db for value
        conn = None
        try:
            conn = config["get_db_connection_for_current_user"]()
            return (
                TimeseriesDataColumn.select_closest_record_no_above_or_below(
                    dataset_id,
                    TEST_TIME_COLUMN_ID,
                    xaxis_value,
                    conn,
                    below=True,
                ),
            )
        except:
            raise PreventUpdate
        finally:
            if conn:
                conn.close()

    @app.callback(
        [Output("custom_range_to_display", "children")],
        [
            Input("custom_range_to_value", "value"),
            Input("range_dataset_dropdown", "value"),
        ],
    )
    def update_range_to_sample_no(xaxis_value, dataset_id):
        # query db for value
        conn = None
        try:
            conn = config["get_db_connection_for_current_user"]()
            return (
                TimeseriesDataColumn.select_closest_record_no_above_or_below(
                    dataset_id,
                    TEST_TIME_COLUMN_ID,
                    xaxis_value,
                    conn,
                    below=False,
                ),
            )
        except:
            raise PreventUpdate
        finally:
            if conn:
                conn.close()

    @app.callback(
        [Output("create_range_result", "children")],
        [
            Input("btn_save_custom_range", "n_clicks"),
            Input("btn_update_custom_range", "n_clicks"),
        ],
        [
            State("custom_range_from_display", "children"),
            State("custom_range_to_display", "children"),
            State("custom_range_name", "value"),
            State("range_dataset_dropdown", "value"),
        ],
    )
    def save_custom_range(
        btn_save_n_clicks,
        btn_update_n_clicks,
        from_sample_no,
        to_sample_no,
        range_name,
        dataset_id,
    ):
        result = ""
        conn = None
        ctx = dash.callback_context
        if ctx.triggered:
            button_id = ctx.triggered[0]["prop_id"].split(".")[0]
            if (
                button_id == "btn_save_custom_range" and btn_save_n_clicks
            ) or (
                button_id == "btn_update_custom_range" and btn_update_n_clicks
            ):
                if len(range_name) == 0:
                    return ("Range name is required",)
                try:
                    conn = config["get_db_connection_for_current_user"]()
                    conn.autocommit = True
                    username = config["get_current_user_name"]()
                    user_range_label = UserRangeLabelRow(
                        dataset_id=dataset_id,
                        label_name=range_name,
                        created_by=username,
                        lower_bound=from_sample_no,
                        upper_bound=to_sample_no,
                        access=[username],
                    )
                    if button_id == "btn_save_custom_range":
                        user_range_label.insert(conn)
                        result = f'"Created range: {range_name} between [{from_sample_no},{to_sample_no})'
                    else:
                        change_count = user_range_label.update(conn)
                        if change_count == 1:
                            result = f'"Updated range: {range_name} between [{from_sample_no},{to_sample_no})'
                        else:
                            result = "Named range doesn't exist. Use save button to create it."
                except psycopg2.errors.UniqueViolation:
                    result = (
                        "Range already exists, use update button to modify it."
                    )
                except:
                    result = "Failed to create range"
                    log(f"Exception:\n{repr(sys.exc_info())}")
                finally:
                    if conn:
                        conn.close()
        return (result,)

    data_server.register_handlers(app, config)
