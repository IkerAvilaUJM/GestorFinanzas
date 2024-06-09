from dash import html, dcc, Input, Output, callback_context
import plotly.express as px
import plotly.graph_objects as go
from app import app
from FinanceTracker import FinanceTracker
import pandas as pd
import locale
from datetime import datetime

# Set the locale to Spanish
locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

# Initialize the tracker and load data
tracker_global = FinanceTracker()
tracker_global.load_tracker('tracker.json')
df = tracker_global.data

# Ensure 'Fecha' is in datetime format
df['Fecha'] = pd.to_datetime(df['Fecha'])

# Extract unique years and create month name mapping
years = df['Fecha'].dt.year.unique()
months = {
    1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio',
    7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
}

# Layout
layout = html.Div([
    html.H1("Eliminar Mes de Datos", style={'textAlign': 'center'}),
    
    # Year and Month Dropdowns
    html.Div([
        html.Label("Seleccionar Año:", style={'fontSize': '18px', 'marginRight': '10px'}),
        dcc.Dropdown(
            id='year-dropdown',
            options=[{'label': str(year), 'value': year} for year in years],
            value=years[0]
        ),
    ], style={'textAlign': 'center', 'margin': '20px'}),
    
    html.Div([
        html.Label("Seleccionar Mes:", style={'fontSize': '18px', 'marginRight': '10px'}),
        dcc.Dropdown(
            id='month-dropdown',
            options=[{'label': month, 'value': num} for num, month in months.items()],
            value=1
        ),
    ], style={'textAlign': 'center', 'margin': '20px'}),
    
    # Bar Chart
    dcc.Graph(id='expenses-bar-chart'),
    
    # Eliminar Button
    html.Div([
        html.Button('Eliminar', id='eliminar-button', n_clicks=0, style={
            'backgroundColor': 'red',
            'color': 'white',
            'fontSize': '20px',
            'padding': '10px 20px',
            'border': 'none',
            'borderRadius': '5px',
            'cursor': 'pointer'
        })
    ], style={'textAlign': 'center', 'margin': '20px'})
])

# Callback to update bar chart
@app.callback(
    Output('expenses-bar-chart', 'figure'),
    Input('year-dropdown', 'value'),
    Input('month-dropdown', 'value')
)
def update_bar_chart(selected_year, selected_month):
    # Initialize the tracker and load data
    tracker_global = FinanceTracker()
    tracker_global.load_tracker('tracker.json')
    df = tracker_global.data

    # Ensure 'Fecha' is in datetime format
    df['Fecha'] = pd.to_datetime(df['Fecha'])

    filtered_df = df[(df['Fecha'].dt.year == selected_year) & (df['Fecha'].dt.month == selected_month)]
    if filtered_df.empty:
        return go.Figure()
    
    # Compute category expenses and prepare for plotting
    category_expenses = filtered_df.groupby('Categoria')['Importe'].sum().reset_index()
    category_expenses['Positive_Total'] = category_expenses['Importe'].abs()
    category_expenses['Color'] = ['rgb(214, 39, 40)' if x < 0 else 'rgb(31, 119, 180)' for x in category_expenses['Importe'].values]
    category_expenses = category_expenses.sort_values(by='Positive_Total', ascending=False)
    filtered_tracker = FinanceTracker()
    filtered_tracker.data = filtered_df
    total_expense, total_earning = filtered_tracker.get_total_expenses_earnings()
    total_overall = total_earning+total_expense
    
    fig_category = px.bar(
        category_expenses, 
        x='Categoria', 
        y='Positive_Total', 
        color=category_expenses['Importe'].apply(lambda x: x < 0), 
        color_discrete_map={False: 'rgb(31, 119, 180)', True: 'rgb(214, 39, 40)'}, 
        title=f"Total en {months[selected_month]} {selected_year} : {total_overall:.0f}"
    )
    fig_category.update_traces(hovertemplate='%{x}: %{y:.2f}€<extra></extra>')
    fig_category.update_layout(barmode='group', showlegend=False, bargap=0, bargroupgap=0.1, title_x=0.5)
    fig_category.update_yaxes(title='')
    fig_category.update_xaxes(title='')
    
    return fig_category

# Callback to delete data
@app.callback(
    Output('url', 'href'),  # Dummy output, not used
    Input('eliminar-button', 'n_clicks'),
    Input('year-dropdown', 'value'),
    Input('month-dropdown', 'value')
)
def delete_month_data(n_clicks, selected_year, selected_month):
    # Initialize the tracker and load data
    tracker_global = FinanceTracker()
    tracker_global.load_tracker('tracker.json')
    df = tracker_global.data

    # Ensure 'Fecha' is in datetime format
    df['Fecha'] = pd.to_datetime(df['Fecha'])

    if n_clicks > 0:
        df = df[~((df['Fecha'].dt.year == selected_year) & (df['Fecha'].dt.month == selected_month))]
        tracker_global.data = df
        if df.empty:
            tracker_global.add_movement("Tracker init", str(datetime.today()).split()[0], 0.0, "Otros")
        tracker_global.save_tracker('tracker.json')
        return "/delete_month"
