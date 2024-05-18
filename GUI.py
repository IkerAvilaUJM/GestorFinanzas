import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
from FinanceTracker import FinanceTracker
import base64
import io
import json

# Initialize the Dash app
app = dash.Dash(__name__)

# Initialize the FinanceTracker object and load the concept-to-category mapping
tracker = FinanceTracker()
try:
    tracker.load_concept_to_category('concept_to_category.json')
except FileNotFoundError:
    pass

# Initialize the list of possible categories:
categories = ['Alquiler', 'Sueldo', 'Comida Uni', 'Comer fuera', 'Ropa', 'Ocio', 'Transporte', 
              'Supermercado', 'Deportes', 'Beca', 'Paga', 'Regalos', 'Fiesta', 'Viaje', 'Bares',
              'Café', 'Farmacia', 'Libros', 'Médico', 'Material', 'Peluquería', 'Teléfono',
              'Otros', 'Cine', 'Gasolina', 'Casa', 'Suscripciones', 'Bollería', 'Inversiones']

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

app.layout = html.Div(style={'margin': '3%', 'font-family': 'VarieraDemo, sans-serif'}, children=[
    html.H1("Gestor de Finanzas Personales", style={'textAlign': 'center'}),
    
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select a Kutxabank Excel File')
        ]),
        style={
            'width': '50%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': 'auto'
        },
        multiple=False
    ),
    
    html.Div(id='file-upload-status', style={'textAlign': 'center'}),
    
    html.Div(id='none-category-box', style={
        'width': '50%',
        'margin': 'auto',
        'border': '1px solid black',
        'padding': '20px',
        'borderRadius': '5px'
    }),
    
    dcc.Dropdown(  # Define the dropdown component
        id='category-dropdown',  # Assign an ID
        options=[{'label': c, 'value': c} for c in categories],
        placeholder='Select a category'
    ),
    
    html.Button('Update Category', id='update-category-button', style={'display': 'block', 'margin': 'auto'}),
    
    html.Div([
        dcc.Graph(id='expenses-per-category', style={'width': '40%'}),
        dcc.Graph(id='expenses-per-day', style={'width': '40%'}),
        dcc.Graph(id='total-expenses-earnings', style={'width': '20%'})
    ], style={'display': 'flex', 'justifyContent': 'space-around'})
])


@app.callback(
    Output('file-upload-status', 'children'),
    Output('none-category-box', 'children'),
    Output('expenses-per-category', 'figure'),
    Output('expenses-per-day', 'figure'),
    Output('total-expenses-earnings', 'figure'),
    Input('upload-data', 'contents'),
    Input('update-category-button', 'n_clicks'),
    State('upload-data', 'filename'),
    State('category-dropdown', 'value'),
    State('none-category-box', 'children')
)
def update_tracker(contents, n_clicks, filename, category, none_category_box):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Check which action has trigered the update method, choosing an excel, or updating a category
    if triggered_id == 'upload-data' and contents is not None:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        with open(filename, "wb") as f:
            f.write(decoded)
        
        tracker.fill_from_excel_kutxabank(filename)
        file_status = "File uploaded and processed successfully"

    elif triggered_id == 'update-category-button' and category is not None:
        # Accessing directly the nested Div and Dropdown components
        none_category_text_children = none_category_box['props']['children']
        if none_category_text_children:
            # Extracting the concept from the first Div component
            current_concept = none_category_text_children[0]['props']['children'].split(": ")[1]
            tracker.update_category(current_concept, category)
            file_status = "Category updated successfully"
        else:
            file_status = "No items with None category available."



    else:
        return "", "", {}, {}, {}
    
    # If after update there are concepts with None category, a new concept appears in the textbox
    none_category_df = tracker.data[tracker.data["Categoria"].isna()]
    if none_category_df.empty:
        none_category_box = "No more items with None category."
    else:
        next_none_category = none_category_df.iloc[0]
        none_category_box = html.Div([
            html.Div(f"Concepto: {next_none_category['Concepto']}"),
            html.Div(f"Fecha: {next_none_category['Fecha']}"),
            html.Div(f"Importe: {next_none_category['Importe']}")
        ])
    
    if not tracker.data.empty:
        # Get data for category expenses
        category_expenses = tracker.get_category_expenses().reset_index()
        # Make negative values positive and create a new column for color
        category_expenses['Positive_Total'] = category_expenses['Total'].abs()
        # Create a new column to determine bar color
        category_expenses['Color'] = ['rgb(214, 39, 40)' if x < 0 else 'rgb(31, 119, 180)' for x in category_expenses['Total'].values]
        # Create the bar plot
        fig_category = px.bar(category_expenses, x='Categoria', y='Positive_Total', color=category_expenses['Total'].apply(lambda x: x < 0), color_discrete_map={False: 'rgb(31, 119, 180)', True: 'rgb(214, 39, 40)'}, title='Total por categoría')
        fig_category.update_layout(barmode='group', showlegend=False, bargap=0, bargroupgap=0.1)  # Adjust bargap and bargroupgap for thicker bars
        # Center the category labels below the bars
        fig_category.update_xaxes(tickmode='array', tickvals=list(range(len(category_expenses))), ticktext=category_expenses['Categoria'], tickangle=45, tickfont=dict(size=10))        
        # Get data for daily expenses
        daily_expenses = tracker.get_daily_expenses().reset_index()
        fig_daily = px.line(daily_expenses, x='Fecha', y='Total', title='Expenses per Day')
        
        # Get total expenses and earnings
        total_expenses, total_earnings = tracker.get_total_expenses_earnings()
        
        # Calculate total savings
        total_savings = total_earnings + total_expenses
        
        # Create bar plot for expenses and earnings
        fig_total = go.Figure()
        fig_total.add_trace(go.Bar(x=['Expenses'], y=[-total_expenses], name='Expenses', marker_color='rgb(214, 39, 40)'))
        fig_total.add_trace(go.Bar(x=['Earnings'], y=[total_earnings], name='Earnings', marker_color='rgb(31, 119, 180)'))
        fig_total.update_layout(title=f'Ahorro Total: ${total_savings:.2f}', 
                                barmode='group', showlegend=False)
        fig_total.update_xaxes(title='Type')
        fig_total.update_yaxes(title='Amount')

    else:
        # Default plots for empty data
        fig_category = px.bar(title='Expenses per Category')
        fig_daily = px.line(title='Expenses per Day')
        fig_total = go.Figure()
    
    tracker.save_concept_to_category('concept_to_category.json')
    return file_status, none_category_box, fig_category, fig_daily, fig_total

if __name__ == '__main__':
    app.run_server(debug=True)