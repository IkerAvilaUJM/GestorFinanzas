import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output, State
import base64
import io
import json
from FinanceTracker import FinanceTracker
import plotly.graph_objects as go

# Load the data for the example sidebar graphs
df = pd.read_csv('https://raw.githubusercontent.com/Coding-with-Adam/Dash-by-Plotly/master/Bootstrap/Side-Bar/iranian_students.csv')

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True, title='Gestor Finanzas')


# Styling the sidebar
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# Padding for the page content
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

# Define the sidebar layout
sidebar = html.Div(
    [
        html.H2("Sidebar", className="display-4"),
        html.Hr(),
        html.P(
            "Navigation", className="lead"
        ),
        dbc.Nav(
            [
                dbc.NavLink("Home", href="/", active="exact"),
                dbc.NavLink("Añadir Mes", href="/add-month", active="exact"),
                dbc.NavLink("Page 1", href="/page-1", active="exact"),
                dbc.NavLink("Page 2", href="/page-2", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

# Define the content layout
content = html.Div(id="page-content", children=[], style=CONTENT_STYLE)

app.layout = html.Div([
    dcc.Location(id="url"),
    sidebar,
    content
])

# Initialize the FinanceTracker object and load the concept-to-category mapping
tracker = FinanceTracker()
try:
    tracker.load_concept_to_category('concept_to_category.json')
except FileNotFoundError:
    pass

# Initialize the list of possible categories
categories = ['Alquiler', 'Sueldo', 'Comida Uni', 'Comer fuera', 'Ropa', 'Ocio', 'Transporte', 
              'Supermercado', 'Deportes', 'Beca', 'Paga', 'Regalos', 'Fiesta', 'Viaje', 'Bares',
              'Café', 'Farmacia', 'Libros', 'Médico', 'Material', 'Peluquería', 'Teléfono',
              'Otros', 'Cine', 'Gasolina', 'Casa', 'Suscripciones', 'Bollería', 'Inversiones', 'Tecnología',
              'Comision Banco']

# Define the "añadir mes" layout
add_month_layout = html.Div(style={'margin': '3%', 'font-family': 'VarieraDemo, sans-serif'}, children=[
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
    
    dcc.Dropdown(
        id='category-dropdown',
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
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def render_page_content(pathname):
    if pathname == "/":
        return [
            html.H1('Home', style={'textAlign':'center'}),
            html.P("This is the home page.")
        ]
    elif pathname == "/add-month":
        return add_month_layout
    elif pathname == "/page-1":
        return [
            html.H1('Page 1', style={'textAlign':'center'}),
            html.P("This is page 1.")
        ]
    elif pathname == "/page-2":
        return [
            html.H1('Page 2', style={'textAlign':'center'}),
            html.P("This is page 2.")
        ]
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )

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
    
    if triggered_id == 'upload-data' and contents is not None:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        with open(filename, "wb") as f:
            f.write(decoded)
        
        global tracker
        tracker = FinanceTracker()
        tracker.load_concept_to_category('concept_to_category.json')
        tracker.fill_from_excel_kutxabank(filename)
        file_status = "File uploaded and processed successfully"
    elif triggered_id == 'update-category-button' and category is not None:
        none_category_text_children = none_category_box['props']['children']
        if none_category_text_children:
            current_concept = none_category_text_children[0]['props']['children'].split(": ")[1]
            tracker.update_category(current_concept, category)
            file_status = "Category updated successfully"
        else:
            file_status = "No items with None category available."
    else:
        return "", "", {}, {}, {}
    
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
        category_expenses = tracker.get_category_expenses().reset_index()
        category_expenses['Positive_Total'] = category_expenses['Total'].abs()
        category_expenses['Color'] = ['rgb(214, 39, 40)' if x < 0 else 'rgb(31, 119, 180)' for x in category_expenses['Total'].values]
        fig_category = px.bar(category_expenses, x='Categoria', y='Positive_Total', color=category_expenses['Total'].apply(lambda x: x < 0), 
                              color_discrete_map={False: 'rgb(31, 119, 180)', True: 'rgb(214, 39, 40)'}, title='Total por categoría')
        fig_category.update_layout(barmode='group', showlegend=False, bargap=0, bargroupgap=0.1)
        
        daily_expenses = tracker.get_daily_expenses().reset_index()
        fig_daily = px.line(daily_expenses, x='Fecha', y='Total', title='Expenses per Day')
        
        total_expenses, total_earnings = tracker.get_total_expenses_earnings()
        total_savings = total_earnings + total_expenses
        
        fig_total = go.Figure()
        fig_total.add_trace(go.Bar(x=['Expenses'], y=[-total_expenses], name='Expenses', marker_color='rgb(214, 39, 40)'))
        fig_total.add_trace(go.Bar(x=['Earnings'], y=[total_earnings], name='Earnings', marker_color='rgb(31, 119, 180)'))
        fig_total.update_layout(title=f'Ahorro Total: ${total_savings:.2f}', barmode='group', showlegend=False)
        fig_total.update_xaxes(title='Type')
        fig_total.update_yaxes(title='Amount')
    else:
        fig_category = px.bar(title='Expenses per Category')
        fig_daily = px.line(title='Expenses per Day')
        fig_total = go.Figure()
    
    tracker.save_concept_to_category('concept_to_category.json')
    return file_status, none_category_box, fig_category, fig_daily, fig_total

if __name__ == '__main__':
    app.run_server(debug=True)
