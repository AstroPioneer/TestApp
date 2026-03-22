import os
import logging
from dash import Dash, html, dcc, callback, Output, Input, ClientsideFunction
from usethatapp.webapps import get_product


logging.basicConfig(level=logging.DEBUG)
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
        return "Loading..."
    try:
        logger.debug(f"data keys = {data.keys() if isinstance(data, dict) else 'not a dict'}")
        product = get_product(
            data['message'],
            public_key_path=os.getenv('UTA_PUBLIC_KEY_FILE'),
            private_key_path=os.getenv('PRIVATE_KEY_FILE')
        )
        return product
    except Exception as e:
        import traceback
        logger.error(f"Exception: {traceback.format_exc()}")
        return str(e)

server = app.server

if __name__ == "__main__":
    app.run(debug=True)
