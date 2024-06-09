from dash import html, dcc, Input, Output
import plotly.express as px
import plotly.graph_objects as go
from app import app
from FinanceTracker import FinanceTracker
import pandas as pd
import locale

# Set the locale to Spanish
locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

# Sample Data
tracker_global = FinanceTracker()

tracker_global.load_tracker('tracker.json')
df = tracker_global.data
# Ensure 'Fecha' is in datetime format
df['Fecha'] = pd.to_datetime(df['Fecha'])

# Layout
layout = html.Div([
    html.H1("Panel de Análisis Financiero", style={'textAlign': 'center'}),

    # Date Picker
    html.Div([
        html.Label("Seleccionar Rango de Fechas:", style={'fontSize': '18px', 'marginRight': '10px'}),
        dcc.DatePickerRange(
            id='date-picker-range',
            start_date=df['Fecha'].min().date(),
            end_date=df['Fecha'].max().date(),
            display_format='YYYY-MM-DD'
        ),
    ], style={'textAlign': 'center', 'margin': '20px', 'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center'}),

    # Category Expenses Plot
    html.Div([
        dcc.Graph(id='category-expenses')
    ], style={'marginTop': '30px'}),

    # Daily Expenses Change Plot
    html.Div([
        dcc.Graph(id='daily-expenses-change')
    ], style={'marginTop': '30px'}),

    # Monthly Expenses Change Plot
    html.Div([
        dcc.Graph(id='monthly-expenses-change')
    ], style={'marginTop': '30px'})
])


# Callback to update the category expenses plot, daily expenses change plot, and monthly expenses change plot
@app.callback(
    [Output('category-expenses', 'figure'),
     Output('daily-expenses-change', 'figure'),
     Output('monthly-expenses-change', 'figure')],
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_plots(start_date, end_date):
    # Load Data
    tracker_global = FinanceTracker()

    tracker_global.load_tracker('tracker.json')
    df = tracker_global.data
    # Ensure 'Fecha' is in datetime format
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    # Convert start_date and end_date to datetime
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    if start_date is None or end_date is None:
        filtered_df = df
    else:
        filtered_df = df[(df['Fecha'] >= start_date) & (df['Fecha'] <= end_date)]

    filtered_tracker = FinanceTracker()
    filtered_tracker.data = filtered_df
    total_expense, total_earning = filtered_tracker.get_total_expenses_earnings()
    total_overall = total_earning+total_expense

    # Category Expenses Plot
    category_expenses = filtered_tracker.get_category_expenses().reset_index()
    category_expenses['Positive_Total'] = category_expenses['Total'].abs()
    category_expenses['Color'] = ['rgb(214, 39, 40)' if x < 0 else 'rgb(31, 119, 180)' for x in category_expenses['Total'].values]
    category_expenses = category_expenses.sort_values(by='Positive_Total', ascending=False)
    fig_category = px.bar(category_expenses, x='Categoria', y='Positive_Total', color=category_expenses['Total'].apply(lambda x: x < 0), 
                          color_discrete_map={False: 'rgb(31, 119, 180)', True: 'rgb(214, 39, 40)'}, title=f'Total: {total_overall:.0f}€')
    fig_category.update_traces(hovertemplate='%{x}: %{y:.2f}€<extra></extra>')
    fig_category.update_layout(barmode='group', showlegend=False, bargap=0, bargroupgap=0.1, title_x=0.5)
    fig_category.update_yaxes(title='')
    fig_category.update_xaxes(title='')

    # Daily Expenses Change Plot (Candlestick)
    daily_expenses = tracker_global.get_daily_expenses().reset_index()
    daily_expenses = daily_expenses[(daily_expenses['Fecha'] >= start_date) & (daily_expenses['Fecha'] <= end_date)]
    daily_expenses['Cumulative'] = daily_expenses['Total'].cumsum()
    daily_expenses['Daily_Change'] = daily_expenses['Total'].diff().fillna(0)
    daily_expenses['Open'] = daily_expenses['Cumulative'].shift(1).fillna(0)
    daily_expenses['Close'] = daily_expenses['Cumulative']
    daily_expenses['High'] = daily_expenses[['Open', 'Close']].max(axis=1)
    daily_expenses['Low'] = daily_expenses[['Open', 'Close']].min(axis=1)

    fig_cumulative_daily = go.Figure(data=[go.Candlestick(x=daily_expenses['Fecha'],
                                                          open=daily_expenses['Open'],
                                                          high=daily_expenses['High'],
                                                          low=daily_expenses['Low'],
                                                          close=daily_expenses['Close'],
                                                          increasing_line_color='green',
                                                          increasing_fillcolor='green',
                                                          decreasing_line_color='red',
                                                          decreasing_fillcolor='red',
                                                          opacity=1.0)])

    fig_cumulative_daily.update_layout(xaxis_rangeslider_visible=False)
    fig_cumulative_daily.update_layout(title='Cambio Diario', title_x=0.5, showlegend=False)
    fig_cumulative_daily.update_yaxes(title='')
    fig_cumulative_daily.update_xaxes(title='Fecha')

    # Monthly Expenses Change Plot (Candlestick)
    daily_expenses['Fecha'] = pd.to_datetime(daily_expenses['Fecha'])  # Ensure it's datetime for resampling
    monthly_expenses = daily_expenses.set_index('Fecha').resample('ME').agg({
        'Total': 'sum',
        'Cumulative': 'last',
        'High': 'max',
        'Low': 'min'
    }).reset_index()
    monthly_expenses['Daily_Change'] = monthly_expenses['Total'].diff().fillna(0)
    monthly_expenses['Open'] = monthly_expenses['Cumulative'].shift(1).fillna(0)
    monthly_expenses['Close'] = monthly_expenses['Cumulative']
    monthly_expenses['High'] = monthly_expenses[['Open', 'Close', 'High']].max(axis=1)
    monthly_expenses['Low'] = monthly_expenses[['Open', 'Close', 'Low']].min(axis=1)

    # Format dates in Spanish for monthly expenses
    monthly_expenses['Fecha'] = monthly_expenses['Fecha'].dt.strftime('%B %Y').str.capitalize()

    fig_cumulative_monthly = go.Figure(data=[go.Candlestick(x=monthly_expenses['Fecha'],
                                                            open=monthly_expenses['Open'],
                                                            high=monthly_expenses['High'],
                                                            low=monthly_expenses['Low'],
                                                            close=monthly_expenses['Close'],
                                                            increasing_line_color='green',
                                                            increasing_fillcolor='green',
                                                            decreasing_line_color='red',
                                                            decreasing_fillcolor='red',
                                                            opacity=1.0)])
    # Add text annotations for total savings/expending of the month
    for i, row in monthly_expenses.iterrows():
        fig_cumulative_monthly.add_annotation(
            x=row['Fecha'],
            y=row['High'],
            text=f"{row['Total']:.2f}€",
            showarrow=False,
            yshift=10,
            font=dict(color="black")
        )
    
    fig_cumulative_monthly.update_layout(
        xaxis_rangeslider_visible=False,
        title='Cambio Mensual',
        title_x=0.5,
        showlegend=False
    )
    fig_cumulative_monthly.update_yaxes(title='')
    fig_cumulative_monthly.update_xaxes(title='Fecha')

    return fig_category, fig_cumulative_daily, fig_cumulative_monthly
