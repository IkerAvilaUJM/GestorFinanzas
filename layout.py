from dash import html, dcc
import dash_bootstrap_components as dbc
from sidebar import sidebar

# Define the content layout
content = html.Div(id="page-content", children=[], style={"margin-left": "18rem", "margin-right": "2rem", "padding": "2rem 1rem"})

layout = html.Div([
    dcc.Location(id="url"),
    sidebar,
    content
])
