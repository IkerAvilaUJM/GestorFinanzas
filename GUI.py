import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
from FinanceTracker import *
from time import sleep

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
next_importe = float(df["importe"].iloc[i]) if not df.empty else ""

# Load the finance tracker
finance_tracker = FinanceTracker()
categories = finance_tracker.categories
dropdown_options = [{'label': option.capitalize(), 'value': option.lower()} for option in categories]
dropdown_options = sorted(dropdown_options, key=lambda x: x['label'])

# Initialize the plot for expenses in each categorie
# Filter out rows where the total expense is zero
non_zero_expenses = finance_tracker.total_expenses[finance_tracker.total_expenses['total'] != 0]
# Plotly Express bar plot
fig_categories = px.bar(non_zero_expenses, x=non_zero_expenses.index, y='total', title='Expenses with Non-Zero Values')

# Initialize the plot with the sum of expenes and earnings
fig_total = px.bar(x=["Total"], y=[finance_tracker.total], title="Total Gastos e Ingresos")
# Get maximum and minimum y-value from fig_categories
if fig_categories.data:
    # Get maximum y-value from fig_categories
    max_y = fig_categories.data[0].y.max()
    min_y = fig_categories.data[0].y.min()
else:
    max_y = 0
    min_y = 0
# Set the layout of fig_total
fig_total.update_layout(
    yaxis=dict(range=[min_y, max_y], title='',),  # Set y-axis range to match fig_categories
)




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

    html.Div([
        # Left half containing dcc.Markdown components
        html.Div([
            dcc.Graph(id='categorie_graph', figure=fig_categories),
        ], style={'flex': '8'}),  # Set the left half to take up 50% of the container width

        # Right half containing the dcc.Dropdown
        html.Div([
            dcc.Graph(id='total_graph', figure=fig_total),
           ], style={'flex': '2'})  # Set the right half to take up 50% of the container width
    ], style={'display': 'flex', })  # Use flexbox to arrange the divs side by side

])



# ------------------------------------------------------------------------------
# Button callback to add movement
# ------------------------------------------------------------------------------

# Callback to handle adding a new movement when the button is clicked
@app.callback(
    Output(component_id='categorie_graph', component_property='figure'),
    Output(component_id='total_graph', component_property='figure'),
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
    if i < len(df):
        next_concepto = df["concepto"].iloc[i]
        next_fecha = df["fecha valor"].iloc[i]
        next_importe = float(df["importe"].iloc[i])
    else:
        # Handle end of DataFrame (reset to initial values or take appropriate action)
        next_concepto = ""
        next_fecha = ""
        next_importe = 0.0

    # Filter out rows where the total expense is zero
    non_zero_expenses = finance_tracker.total_expenses[finance_tracker.total_expenses['total'] != 0]

    # Plotly Express bar plot
    fig_categories = px.bar(non_zero_expenses, x=non_zero_expenses.index, y='total', title='Expenses with Non-Zero Values')
    # Initialize the plot with the sum of expenes and earnings
    fig_total = px.bar(x=["Total"], y=[finance_tracker.total], title="Total Gastos e Ingresos")
    # Get maximum and minimum y-value from fig_categories
    if fig_categories.data:
    # Get maximum y-value from fig_categories
        max_y = fig_categories.data[0].y.max()
        min_y = fig_categories.data[0].y.min()
    else:
        max_y = 0
        min_y = 0
    # Set the layout of fig_total
    fig_total.update_layout(
        yaxis=dict(range=[min_y, max_y], title='',),  # Set y-axis range to match fig_categories
    )

    # Return an empty figure for now
    return fig_categories, fig_total

@app.callback(
    Output(component_id='concepto_text', component_property='children'),
    Output(component_id='fecha_text', component_property='children'),
    Output(component_id='importe_text', component_property='children'),
    [Input(component_id='button-add-movement', component_property='n_clicks')]
)
def update_displayed_values(n_clicks):
    sleep(0.1) # not good practice, but otherwise the text sometimes doesn't update
    global next_concepto, next_fecha, next_importe, i  # declaring as global variables

    if not n_clicks:
        return "Concepto: " + str(next_concepto), "Fecha: " + str(next_fecha), "Importe: " + str(next_importe)

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
