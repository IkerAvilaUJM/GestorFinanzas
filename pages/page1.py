from dash import html, dcc
import dash
from dash.dependencies import Input, Output
from app import app
import pandas as pd
from FinanceTracker import FinanceTracker
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
    df['Fecha'] = pd.to_datetime(df['Fecha'])

    # Group by month and sum expenses
    df_monthly = df.groupby(df['Fecha'].dt.to_period('M'))['Importe'].sum().reset_index()
    df_monthly['Fecha'] = df_monthly['Fecha'].dt.to_timestamp()  # Convert period to timestamp for Plotly
    df_monthly['Positive_Total'] = df_monthly['Importe'].abs()
    df_monthly['Color'] = ['rgb(214, 39, 40)' if x < 0 else 'rgb(31, 119, 180)' for x in df_monthly['Importe'].values]

    # Create the bar chart
    fig = px.bar(
        df_monthly,
        x='Fecha',
        y='Positive_Total',
        color=df_monthly['Importe'].apply(lambda x: x < 0),
        color_discrete_map={False: 'rgb(31, 119, 180)', True: 'rgb(214, 39, 40)'},
        title=f'Monthly Expenses for {selected_category}',
        labels={'Fecha': 'Month', 'Importe': 'Amount (€)'}
    )
    fig.update_layout(barmode='group', title_x=0.5)
    fig.update_yaxes(title='')
    fig.update_xaxes(title='')

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
    df['Fecha'] = pd.to_datetime(df['Fecha'])

    # Group by month and sum expenses
    df_monthly = df.groupby(df['Fecha'].dt.to_period('M'))['Importe'].sum().reset_index()
    df_monthly['Fecha'] = df_monthly['Fecha'].dt.to_timestamp()
    df_monthly['Positive_Total'] = df_monthly['Importe'].abs()
    df_monthly['Color'] = ['rgb(214, 39, 40)' if x < 0 else 'rgb(31, 119, 180)' for x in df_monthly['Importe'].values]

    # Create the bar chart
    fig = px.bar(
        df_monthly,
        x='Fecha',
        y='Positive_Total',
        color=df_monthly['Importe'].apply(lambda x: x < 0),
        color_discrete_map={False: 'rgb(31, 119, 180)', True: 'rgb(214, 39, 40)'},
        title=f'Monthly Expenses for {selected_category}',
        labels={'Fecha': 'Month', 'Importe': 'Amount (€)'}
    )
    fig.update_layout(barmode='group', title_x=0.5)
    fig.update_yaxes(title='')
    fig.update_xaxes(title='')

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

    # Debugging: Check the selected month and the data's available months
    print(f"Selected Month: {selected_month}")
    print(f"Available Months in Data: {df['Fecha'].dt.to_period('M').unique()}")

    # Convert selected_month to period if it's not already
    selected_month_period = pd.to_datetime(selected_month).to_period('M')

    # Filter by selected month
    filtered_df = df[df['Fecha'].dt.to_period('M') == selected_month_period]

    # Debugging: Check if the filtered DataFrame is empty
    print(f"Filtered Data for {selected_month_period}: {filtered_df.shape[0]} records found")

    # If no records are found, return an empty figure
    if filtered_df.empty:
        return go.Figure()

    # Group by concept and sum expenses
    df_monthly = filtered_df.groupby('Concepto')['Importe'].sum().reset_index()
    df_monthly['Positive_Total'] = df_monthly['Importe'].abs()
    df_monthly['Color'] = ['rgb(214, 39, 40)' if x < 0 else 'rgb(31, 119, 180)' for x in df_monthly['Importe'].values]
    df_monthly = df_monthly.sort_values(by='Positive_Total', ascending=False)

    fig = px.bar(
        df_monthly,
        x='Concepto',
        y='Positive_Total',
        color=df_monthly['Importe'].apply(lambda x: x < 0),
        color_discrete_map={False: 'rgb(31, 119, 180)', True: 'rgb(214, 39, 40)'},
        title=f"Total Expenses in {selected_month}",
        labels={'Concepto': 'Concept', 'Positive_Total': 'Amount (€)'}
    )

    fig.update_traces(hovertemplate='%{x}: %{y:.2f}€<extra></extra>')
    fig.update_layout(barmode='group', showlegend=False, bargap=0, bargroupgap=0.1, title_x=0.5)

    return fig


