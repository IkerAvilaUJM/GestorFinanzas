import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from movements import *

app = dash.Dash(__name__)

### ----------------------------------------- Load data ------------------------------------------ ###

### ---------------------------------------------------------------------------------------------- ###


# Load the data from the Excel file with the movements, this should be changed later select file by user
file = "Movimientos Kutxabank/2023-04.xls"
df = pd.read_excel(file, skiprows=6)
df = df.dropna(how='all')
column_names = ["concepto", "fecha valor", "importe"]
df = df[column_names]

# Load the category map from the JSON file
finance_tracker = FinanceTracker()
finance_tracker.load_category_map()
categories = finance_tracker.categories
dropdown_options = [{'label': option.capitalize(), 'value': option.lower()} for option in categories]




### ----------------------------------------- App layout ---------------------------------------- ###
# The layout of the app is defined here, it is the structure of the web page
### ---------------------------------------------------------------------------------------------- ###

# Path to the folder containing your local font files
local_font_path = "fonts/"

# Define CSS for custom font
custom_font_css = f'''
@font-face {{
    font-family: 'VarieraDemo';
    src: url('/{local_font_path}VarieraDemoRegular.ttf') format('truetype');
    font-weight: normal;
    font-style: normal;
}}
body {{
    font-family: 'VarieraDemo', sans-serif;
}}
'''

# Apply custom font CSS directly in the app layout
app.layout = html.Div(style={'margin': '3%', 'font-family': 'VarieraDemo, sans-serif'}, children=[

    html.H1("Gestor de finanzas personales", style={'text-align': 'center'}),

    html.Div([
        # Left half containing dcc.Markdown components
        html.Div([
            dcc.Markdown('''
                Concepto: {}
            '''.format(df.iloc[0]["concepto"]), style={'marginRight': '20px'}),
            dcc.Markdown('''
                Cantidad: {}
            '''.format(df.iloc[0]["importe"]), style={'marginRight': '20px'}),
            dcc.Markdown('''
                Fecha: {}
            '''.format(df.iloc[0]["fecha valor"]), style={'marginRight': '20px'}),
        ], style={'flex': '1'}),  # Set the left half to take up 50% of the container width

        # Right half containing the dcc.Dropdown
        html.Div([
            dcc.Markdown('''
                Escoge categoría para este movimiento:
            '''),
            dcc.Dropdown(
                id="slct_year",
                options=dropdown_options,
                multi=False,
                value=2015,
                style={'width': "100%"}
            ),
            html.Button('Añadir  Movimiento', id='button-añadirMovimiento'),
        ], style={'flex': '1'})  # Set the right half to take up 50% of the container width
    ], style={'display': 'flex', 
              'border': '1px solid black', 'padding': '10px', 'margin': '10px',
              'border-radius': '5px'})  # Use flexbox to arrange the divs side by side
    ,


    html.Br(),

    dcc.Graph(id='my_bee_map', figure={})

])

# ------------------------------------------------------------------------------

if __name__ == '__main__':
    app.run_server(debug=True)
