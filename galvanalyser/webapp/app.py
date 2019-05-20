import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from flask import session, escape, request, redirect, url_for
import flask


app = dash.Dash(
    __name__,
    external_stylesheets=["https://codepen.io/chriddyp/pen/bWLwgP.css"],
)
app.server.secret_key = b'sdfg_5#y2L"F4Q8z\n\xec]/'


@app.server.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session["username"] = request.form["username"]
        return redirect("/")
    return """
        <form method="post">
            <p><input type=text name=username>
            <p><input type=submit value=Login>
        </form>
    """


url_bar_and_content_div = html.Div(
    [
        html.Div(id="placeholder"),
        html.Div(id="placeholder2"),
        dcc.Location(id="url", refresh=False),
        html.Div(id="page-content"),
    ]
)

layout_index = html.Div(
    [
        dcc.Link('Navigate to "/page-1"', href="/page-1"),
        html.Br(),
        dcc.Link('Navigate to "/page-2"', href="/page-2"),
        dcc.Input(id="input-username", type="text", value=""),
        html.Button(id="submit-user-button", n_clicks=0, children="Submit"),
    ]
)

layout_page_1 = html.Div(
    [
        html.H2("Page 1"),
        dcc.Input(id="input-1-state", type="text", value="Montreal"),
        dcc.Input(id="input-2-state", type="text", value="Canada"),
        html.Button(id="submit-button", n_clicks=0, children="Submit"),
        html.Div(id="output-state"),
        html.Br(),
        dcc.Link('Navigate to "/"', href="/"),
        html.Br(),
        dcc.Link('Navigate to "/page-2"', href="/page-2"),
    ]
)

layout_page_2 = html.Div(
    [
        html.H2("Page 2"),
        dcc.Dropdown(
            id="page-2-dropdown",
            options=[{"label": i, "value": i} for i in ["LA", "NYC", "MTL"]],
            value="LA",
        ),
        html.Div(id="page-2-display-value"),
        html.Br(),
        dcc.Link('Navigate to "/"', href="/"),
        html.Br(),
        dcc.Link('Navigate to "/page-1"', href="/page-1"),
    ]
)


def serve_layout():
    print("in serve_layout")
    if flask.has_request_context():
        print("flask.has_request_context")
        return url_bar_and_content_div
    print("!flask.has_request_context")
    return html.Div(
        [url_bar_and_content_div, layout_index, layout_page_1, layout_page_2]
    )


app.layout = serve_layout


def get_session_state():
    print("in get_session_state")
    if "username" in session:
        return html.Div("Logged in as %s" % escape(session["username"]))
    return html.Div("You are not logged in")


# Index callbacks
@app.callback(
    [Output("page-content", "children"), Output("placeholder", "children")],
    [Input("url", "pathname")],
)
def display_page(pathname):
    print("in display_page")
    if pathname == "/page-1":
        return layout_page_1, get_session_state()
    elif pathname == "/page-2":
        return layout_page_2, get_session_state()
    else:
        return layout_index, get_session_state()


@app.callback(
    Output("placeholder2", "children"),
    [Input("submit-user-button", "n_clicks")],
    [State("input-username", "value")],
)
def login_submit(n_clicks, input1):
    print("in login_submit")
    print(n_clicks)
    if n_clicks > 0:
        session["username"] = input1
    return get_session_state()


# Page 1 callbacks
@app.callback(
    Output("output-state", "children"),
    [Input("submit-button", "n_clicks")],
    [State("input-1-state", "value"), State("input-2-state", "value")],
)
def update_output(n_clicks, input1, input2):
    return (
        "The Button has been pressed {} times,"
        'Input 1 is "{}",'
        'and Input 2 is "{}"'
    ).format(n_clicks, input1, input2)


# Page 2 callbacks
@app.callback(
    Output("page-2-display-value", "children"),
    [Input("page-2-dropdown", "value")],
)
def display_value(value):
    print("display_value")
    return 'You have selected "{}"'.format(value)


if __name__ == "__main__":
    print("running")
    app.run_server(debug=True, host="0.0.0.0")
