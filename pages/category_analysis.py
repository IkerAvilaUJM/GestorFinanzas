from dash import html, dcc
import dash
from dash.dependencies import Input, Output
from app import app
import pandas as pd
from FinanceTracker import FinanceTracker
from plotting_functions import *
import plotly.express as px
import plotly.graph_objects as go

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
concepts = tracker_global.get_concepts()

layout = html.Div([
    # Title
    html.H1('Category Analysis', style={'textAlign': 'center', 'marginBottom': '20px'}),
    
    # Dropdown for selecting category
    html.Div([
        html.Label('Select Category:', style={'marginRight': '10px'}),
        dcc.Dropdown(
            id='category-dropdown',
            options=categories,
            placeholder='Choose a category',
            style={'width': '40%', 'display': 'inline-block', 'marginRight': '20px'}
        ),
    ], style={'marginBottom': '30px'}),

    # Bar chart for displaying monthly expenses for the selected category
    dcc.Graph(
        id='expenses-bar-chart-category',
        style={'height': '400px'}
    ),

    # Dropdown for selecting concept based on selected category
    html.Div([
        html.Label('Select Concept:', style={'marginRight': '10px'}),
        dcc.Dropdown(
            id='concept-dropdown',
            options=concepts,
            placeholder='Choose a concept',
            style={'width': '40%', 'display': 'inline-block', 'marginRight': '20px'}
        ),
    ], style={'marginBottom': '30px'}),

    # Bar chart for displaying monthly expenses for the selected concept
    dcc.Graph(
        id='expenses-bar-chart-concept',
        style={'height': '400px'}
    ),

    # Dropdown for selecting a month
    html.Div([
        html.Label('Select Month:', style={'marginRight': '10px'}),
        dcc.Dropdown(
            id='month-dropdown-category',
            options=[],
            placeholder='Choose a month',
            style={'width': '40%', 'display': 'inline-block', 'marginRight': '20px'}
        ),
    ], style={'marginBottom': '30px'}),

    # Bar chart for displaying expenses for the selected month
    dcc.Graph(
        id='expenses-bar-chart-month',
        style={'height': '400px'}
    ),
])

# Callback to update the concepts dropdown based on the selected category
@app.callback(
    Output('concept-dropdown', 'options'),
    Input('category-dropdown', 'value')
)
def update_concepts_dropdown(selected_category):
    if selected_category:
        tracker_category = tracker_global.detail_category(selected_category)
        concepts = tracker_category.get_concepts()
        return concepts
    return []

# Callback to update the month dropdown based on the selected category
@app.callback(
    Output('month-dropdown-category', 'options'),
    Input('category-dropdown', 'value')
)
def update_month_dropdown(selected_category):
    if selected_category:
        tracker_category = tracker_global.detail_category(selected_category)
        # Extract unique months from the data
        df = tracker_category.data
        df['Fecha'] = pd.to_datetime(df['Fecha'])
        months = df['Fecha'].dt.to_period('M').unique()
        month_options = [{'label': month.strftime('%Y-%m'), 'value': str(month)} for month in months]
        return month_options
    return []

# Callback to update the bar chart for the selected category
@app.callback(
    Output('expenses-bar-chart-category', 'figure'),
    Input('category-dropdown', 'value')
)
def update_category_bar_chart(selected_category):
    if not selected_category:
        return go.Figure()

    # Load data for the selected category
    tracker_category = tracker_global.detail_category(selected_category)
    df = tracker_category.data
    
    fig, total = plot_monthly_expenses(df)
    fig.update_layout(title=f'Expenses for {selected_category}: {total}€', title_x=0.5)

    return fig

# Callback to update the bar chart for the selected concept
@app.callback(
    Output('expenses-bar-chart-concept', 'figure'),
    Input('category-dropdown', 'value'),
    Input('concept-dropdown', 'value')
)
def update_concept_bar_chart(selected_category, selected_concept):
    if not selected_category or not selected_concept:
        return go.Figure()

    # Load data for the selected category
    tracker_category = tracker_global.detail_category(selected_category)
    df = tracker_category.data

    # Filter by selected concept
    df = df[df['Concepto'] == selected_concept]
    
    fig, total = plot_monthly_expenses(df)
    fig.update_layout(title=f'Expenses for {selected_concept}: {total}€', title_x=0.5)

    return fig

# Callback to update the bar chart for the selected month
@app.callback(
    Output('expenses-bar-chart-month', 'figure'),
    Input('category-dropdown', 'value'),
    Input('month-dropdown-category', 'value')  # Updated to use the correct month dropdown ID
)
def update_month_bar_chart(selected_category, selected_month):
    if not selected_category or not selected_month:
        return go.Figure()

    tracker_category = tracker_global.detail_category(selected_category)
    df = tracker_category.data

    # Ensure 'Fecha' is in datetime format
    df['Fecha'] = pd.to_datetime(df['Fecha'])

    # Convert selected_month to period if it's not already
    selected_month_period = pd.to_datetime(selected_month).to_period('M')

    # Filter by selected month
    filtered_df = df[df['Fecha'].dt.to_period('M') == selected_month_period]

    fig, total = plot_category_expenses(filtered_df)
    fig.update_layout(title=f'Expenses for {selected_month}: {total}€', title_x=0.5)

    return fig


