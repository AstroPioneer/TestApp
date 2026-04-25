import os
import logging
from collections import deque
from dash import Dash, html, dcc, callback, Output, Input, ClientsideFunction
from usethatapp.webapps import get_version


# In-memory log buffer used to display log messages in the UI.
LOG_BUFFER = deque(maxlen=1000)


class DequeLogHandler(logging.Handler):
    def emit(self, record):
        try:
            LOG_BUFFER.append(self.format(record))
        except Exception:
            pass


logging.basicConfig(level=logging.DEBUG)
_log_handler = DequeLogHandler()
_log_handler.setLevel(logging.DEBUG)
_log_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
logging.getLogger().addHandler(_log_handler)
logger = logging.getLogger(__name__)


app = Dash(__name__, external_scripts=[
    "https://cdn.jsdelivr.net/gh/UseThatApp/cdn@latest/usethatapp.js"
])

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.H1("Your App Version"),
    html.Div(id="version-display", children="free", style={
        "fontSize": "24px",
        "fontWeight": "bold",
        "margin": "20px 0",
        "padding": "10px",
        "backgroundColor": "#f0f0f0",
        "borderRadius": "5px",
        "display": "inline-block"
    }),
    html.Br(),
    html.Button("Update Version", id="update-button", n_clicks=0, style={
        "fontSize": "16px",
        "padding": "10px 20px",
        "cursor": "pointer",
        "marginTop": "10px"
    }),
    dcc.Store(id='access-level-store', data=None, storage_type='memory'),
    html.H2("Logs", style={"marginTop": "40px"}),
    dcc.Textarea(
        id="log-textarea",
        value="",
        readOnly=True,
        style={
            "width": "90%",
            "height": "800px",
            "fontFamily": "monospace",
            "fontSize": "12px",
            "padding": "10px",
            "backgroundColor": "#111",
            "color": "#0f0",
            "whiteSpace": "pre",
            "overflow": "auto",
        },
    ),
    dcc.Interval(id="log-interval", interval=1000, n_intervals=0),
], style={
    "textAlign": "center",
    "fontFamily": "Arial, sans-serif",
    "padding": "50px"
})

app.clientside_callback(
    ClientsideFunction(namespace='clientside', function_name='requestAccessLevel'),
    Output("access-level-store", "data"),
    Input('update-button', 'n_clicks'),
    Input('url', 'pathname')
)

@callback(
    Output("version-display", "children"),
    Input("access-level-store", "data")
)
def display_access_level(data):
    logger.debug(f"data received = {data}")

    if data is None:
        return "No Data.."
    try:
        logger.debug(f"data keys = {data.keys() if isinstance(data, dict) else 'not a dict'}")
        version = get_version(
            data,
            public_key_path=os.getenv('UTA_PUBLIC_KEY_FILE'),
            private_key_path=os.getenv('PRIVATE_KEY_FILE')
        )
        logger.debug(f"version = {version}")
        return version
    except Exception as e:
        import traceback
        logger.error(f"Exception: {traceback.format_exc()}")
        return str(e)

server = app.server


@callback(
    Output("log-textarea", "value"),
    Input("log-interval", "n_intervals"),
)
def update_logs(_n):
    return "\n".join(LOG_BUFFER)


if __name__ == "__main__":
    app.run(debug=True)
