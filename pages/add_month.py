from dash import html, dcc
import dash
from dash.dependencies import Input, Output, State
from app import app
from FinanceTracker import FinanceTracker
from plotting_functions import *
import plotly.express as px
import plotly.graph_objects as go
import base64
import io

# Initialize the FinanceTracker object and load the concept-to-category mapping
tracker = FinanceTracker()
tracker_global = FinanceTracker()
try:
    tracker_global.load_tracker('tracker.json')
except FileNotFoundError:
    pass

try:
    tracker.load_concept_to_category('concept_to_category.json')
except FileNotFoundError:
    pass

categories = tracker_global.get_categories()

# Layout
layout = html.Div([
    html.H1("Añadir Mes", style={'textAlign': 'center'}),
    
    html.Div(style={'height': '20px'}),  # Adding vertical spacing
    
    html.Div([
        html.Div([
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                'Arrastra y suelta o ',
                html.A('selecciona un archivo Excel de Kutxabank')
                ]),
            style={
                'width': '100%',
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
    
            html.Div(id='file-upload-status', style={'textAlign': 'center', 'marginTop': '20px'}),
            html.Div(id='none-category-box', style={
                'width': '100%',
                'margin': '20px auto',
                'border': '1px solid black',
                'padding': '20px',
                'borderRadius': '5px'
            }),
            html.Div([
                dcc.Dropdown(
                    id='category-dropdown',
                    options=[{'label': c, 'value': c} for c in categories],
                    placeholder='Selecciona una categoría',
                    style={'width': '50%',
                           'height': '38px'}
                ),
                # New category input field
                dcc.Input(
                    id='new-category-input',
                    type='text',
                    placeholder='Crear Nueva Categoría',
                    style={
                        'width': '50%',
                        'borderRadius': '5px',
                        'height': '38px',
                        }
                ),
            ], style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'flex-start', 'marginBottom': '20px'}),
            
            html.Div(
                html.Button('Añadir Concepto', id='update-category-button', style={
                    'backgroundColor': '#007bff',
                    'color': 'white',
                    'border': 'none',
                    'padding': '10px 20px',
                    'borderRadius': '5px',
                    'fontSize': '16px',
                    'cursor': 'pointer'
                }),
                style={'display': 'flex', 'justifyContent': 'center'}
            ),
        ], style={'flex': '2', 'marginRight': '20px', 'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'center'}),
        
        html.Div([
            dcc.Graph(id='total-expenses-earnings', style={'height': '400px', 'maxWidth': '300px'})
        ], style={'flex': '1', 'display': 'flex', 'alignItems': 'center', 'maxWidth': '300px'}),
    ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginTop': '20px'}),
    
    html.Div([
        dcc.Graph(id='expenses-per-category', style={'flex': '1'}),
    ], style={'marginTop': '20px'}),
    
    html.Div([
        dcc.Graph(id='cumulative-expenses', style={'height': '400px'}),
    ], style={'marginTop': '20px'}),
    
    html.Button('Confirmar y Añadir Mes', id='update-global-tracker-button', style={
        'display': 'block',
        'margin': '20px auto',
        'backgroundColor': '#28a745',
        'color': 'white',
        'border': 'none',
        'padding': '10px 20px',
        'borderRadius': '5px',
        'fontSize': '16px',
        'cursor': 'pointer'
    }),
])

@app.callback(
    Output('file-upload-status', 'children'),
    Output('none-category-box', 'children'),
    Output('expenses-per-category', 'figure'),
    Output('cumulative-expenses', 'figure'),
    Output('total-expenses-earnings', 'figure'),
    Output('new-category-input', 'value'),  # Clear the input field after use
    Output('category-dropdown', 'options'),  # Update dropdown options
    Input('upload-data', 'contents'),
    Input('update-category-button', 'n_clicks'),
    Input('update-global-tracker-button', 'n_clicks'),
    State('upload-data', 'filename'),
    State('category-dropdown', 'value'),
    State('new-category-input', 'value'),  # Get input field value
    State('none-category-box', 'children')
)
def update_tracker(contents, n_clicks_update, n_clicks_global, filename, dropdown_category, input_category, none_category_box):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Initialize file status
    file_status = ""
    
    if triggered_id == 'upload-data' and contents is not None:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        with open(filename, "wb") as f:
            f.write(decoded)
        
        global tracker
        tracker = FinanceTracker()
        tracker.load_concept_to_category('concept_to_category.json')
        tracker.fill_from_excel_kutxabank(filename)
        file_status = "Archivo cargado correctamente"
    
    # Add concept
    elif triggered_id == 'update-category-button':
        # Prioritize input category if provided
        category = input_category if input_category else dropdown_category
        
        if category:
            # Get the current concept from the "none-category-box"
            none_category_text_children = none_category_box['props']['children']
            if none_category_text_children:
                current_concept = none_category_text_children[0]['props']['children'].split(": ")[1]
                tracker.update_category(current_concept, category)
                file_status = "Categoría actualizada correctamente"
                
                # Add new category if it's not already in the dropdown
                if input_category and input_category not in tracker.get_categories():
                    tracker.add_category(input_category)  # Add to tracker if necessary
            else:
                file_status = "No hay más conceptos sin categoría"
        else:
            file_status = "Por favor, selecciona o ingresa una categoría"
    
    elif triggered_id == 'update-global-tracker-button':
        tracker_global = FinanceTracker()
        tracker_global.load_tracker('tracker.json')
        tracker_global += tracker
        tracker_global.save_tracker('tracker.json')
        file_status = "Global tracker actualizado y guardado"
        tracker = FinanceTracker()
        return "", "", {}, {}, {}, "", []
    
    none_category_df = tracker.data[tracker.data["Categoria"].isna()]
    if none_category_df.empty:
        none_category_box = "No hay más conceptos sin categoría."
    else:
        next_none_category = none_category_df.iloc[0]
        none_category_box = html.Div([
            html.Div(f"Concepto: {next_none_category['Concepto']}"),
            html.Div(f"Fecha: {next_none_category['Fecha']}"),
            html.Div(f"Importe: {next_none_category['Importe']}")
        ])
    
    # Generate plots
    if not tracker.data.empty:
        df = tracker.data

        # Category Expenses Plot
        fig_category, total = plot_category_expenses(df)

        # Daily Expenses Change Plot (as Candlestick)
        daily_expenses = tracker.get_daily_expenses().reset_index()
        fig_cumulative = daily_candlestick(daily_expenses)
        
        # Total Expenses and Earnings Plot
        total_expenses, total_earnings = tracker.get_total_expenses_earnings()
        total_savings = total_earnings + total_expenses

        fig_total = go.Figure()
        fig_total.add_trace(go.Bar(x=['Gastos'], y=[-total_expenses], name='Gastos', marker_color='rgb(214, 39, 40)'))
        fig_total.add_trace(go.Bar(x=['Cobros'], y=[total_earnings], name='Cobros', marker_color='rgb(31, 119, 180)'))
        fig_total.update_traces(hovertemplate='%{x}: %{y:.2f}€<extra></extra>')
        fig_total.update_layout(title=f'Ahorro Total: ${total_savings:.2f}', barmode='group', showlegend=False, title_x=0.5)
        fig_total.update_xaxes(title='Type')
    
    else:
        fig_category = px.bar(title='Expenses per Category')
        fig_category.update_yaxes(title='')
        fig_cumulative = px.line(title='Cumulative Expenses')
        fig_cumulative.update_yaxes(title='')
        fig_total = go.Figure()
        fig_total.update_yaxes(title='')

    tracker.save_concept_to_category('concept_to_category.json')
    
    # Get updated category list for the dropdown
    categories = tracker.get_categories()
    dropdown_options = [{'label': c, 'value': c} for c in categories]
    
    # Clear input field after processing
    return file_status, none_category_box, fig_category, fig_cumulative, fig_total, "", dropdown_options
