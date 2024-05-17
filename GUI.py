import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
from movements import *

app = dash.Dash(__name__)

### ----------------------------------------- Load data ------------------------------------------ ###
# Here load the data
### ---------------------------------------------------------------------------------------------- ###


# Load the data from the Excel file with the movements, this should be changed later select file by user
file = "Movimientos Kutxabank/2023-04.xls"
df = pd.read_excel(file, skiprows=6)
df = df.dropna(how='all')
column_names = ["concepto", "fecha valor", "importe"]
df = df[column_names]

i = 0
# Initialize global variables with initial values
next_concepto = df["concepto"].iloc[i] if not df.empty else ""
next_fecha = df["fecha valor"].iloc[i] if not df.empty else ""
next_importe = df["importe"].iloc[i] if not df.empty else ""

# Load the finance tracker
finance_tracker = FinanceTracker()
categories = finance_tracker.categories
dropdown_options = [{'label': option.capitalize(), 'value': option.lower()} for option in categories]
dropdown_options = sorted(dropdown_options, key=lambda x: x['label'])

# initialize the figure plot-bar
fig = px.bar(finance_tracker.total_expenses, x=finance_tracker.total_expenses.index, y=['total'], title='Expenses')




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
            dcc.Markdown(id='concepto_text', children="Concepto: "+str(next_concepto)),  # Placeholder for concepto text
            dcc.Markdown(id='fecha_text', children="Fecha: "+str(next_fecha)),  # Placeholder for fecha text
            dcc.Markdown(id='importe_text', children="Importe: "+str(next_importe)),  # Placeholder for importe text
        ], style={'flex': '1'}),  # Set the left half to take up 50% of the container width

        # Right half containing the dcc.Dropdown
        html.Div([
            dcc.Markdown('''
                Escoge categoría para este movimiento:
            '''),
            dcc.Dropdown(
                id="select_category",
                options=dropdown_options,
                multi=False,
                value=2015,
                style={'width': "100%"}
            ),
            html.Button('Añadir  Movimiento', id='button-add-movement'),
        ], style={'flex': '1'})  # Set the right half to take up 50% of the container width
    ], style={'display': 'flex', 
              'border': '1px solid black', 'padding': '10px', 'margin': '10px',
              'border-radius': '5px'})  # Use flexbox to arrange the divs side by side
    ,

    html.Br(),

    dcc.Graph(id='month_graph', figure=fig)

])



# ------------------------------------------------------------------------------
# Button callback to add movement
# ------------------------------------------------------------------------------

# Callback to handle adding a new movement when the button is clicked
@app.callback(
    Output(component_id='month_graph', component_property='figure'),
    Output(component_id='concepto_text', component_property='children'),
    Output(component_id='fecha_text', component_property='children'),
    Output(component_id='importe_text', component_property='children'),
    [Input(component_id='button-add-movement', component_property='n_clicks')],
    [State(component_id='select_category', component_property='value')]
)
def add_movement(n_clicks, selected_category):
    global next_concepto, next_fecha, next_importe, i  # declaring as global variables

    if not n_clicks:
        return dash.no_update

    if selected_category is None:
        return dash.no_update

    # Call the create_movement function with the appropriate arguments
    finance_tracker.add_movement(next_concepto, next_fecha, next_importe, selected_category)

    # Update next_concepto, next_fecha, and next_importe to the next row in the DataFrame
    i += 1
    next_concepto = df["concepto"].iloc[i]
    next_fecha = df["fecha valor"].iloc[i]
    next_importe = df["importe"].iloc[i]

    # Plotly Express bar plot
    fig = px.bar(finance_tracker.total_expenses, x=finance_tracker.total_expenses.index, y=['total'], title='Expenses')

    # Return an empty figure for now
    return fig

@app.callback(
    Output(component_id='concepto_text', component_property='children'),
    Output(component_id='fecha_text', component_property='children'),
    Output(component_id='importe_text', component_property='children'),
    [Input(component_id='button-add-movement', component_property='n_clicks')]
)
def update_displayed_values(n_clicks):
    global next_concepto, next_fecha, next_importe, i  # declaring as global variables

    if not n_clicks:
        return dash.no_update, dash.no_update, dash.no_update

    # Update the displayed values with the updated global variables
    concepto_text = f"Concepto: {next_concepto}"
    fecha_text = f"Fecha: {next_fecha}"
    importe_text = f"Importe: {next_importe}"

    return concepto_text, fecha_text, importe_text


# ------------------------------------------------------------------------------
# Run the app
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)
