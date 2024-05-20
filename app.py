import dash
import dash_bootstrap_components as dbc

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True, title='Gestor de Finanzas Personales')

server = app.server  # Expose the server variable for deployments
