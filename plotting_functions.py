# plotting functions

import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
from FinanceTracker import FinanceTracker

# given a dataframe df, plot a bar chart of the expenses per month
# dataframe must have the columns 'Fecha' and 'Importe'
def plot_monthly_expenses(df):
    """
    Create a bar chart of the monthly expenses.

    :param df: DataFrame with columns 'Fecha' and 'Importe'
    :return: Plotly figure    
    """
    if df.empty:
        return go.Figure()
    # Ensure 'Fecha' is in datetime format
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    # Group by month and sum expenses
    df_monthly = df.groupby(df['Fecha'].dt.to_period('M'))['Importe'].sum().reset_index()
    df_monthly['Fecha'] = df_monthly['Fecha'].dt.to_timestamp()  # Convert period to timestamp for Plotly
    df_monthly['Positive_Total'] = df_monthly['Importe'].abs()
    # hide legend


    # Create the bar chart
    fig = px.bar(
        df_monthly,
        x='Fecha',
        y='Positive_Total',
        color=df_monthly['Importe'].apply(lambda x: x < 0),
        color_discrete_map={False: 'rgb(31, 119, 180)', True: 'rgb(214, 39, 40)'},
        title=f'Monthly Expenses',
        labels={'Fecha': 'Month', 'Importe': 'Amount (€)'}
    )
    fig.update_layout(barmode='group', showlegend=False, bargap=0, bargroupgap=0.1, title_x=0.5)
    fig.update_yaxes(title='')
    fig.update_xaxes(title='')

    total = round(df_monthly['Importe'].sum())
    return fig, total

def plot_category_expenses(df, field="Categoria"):
    # Compute category expenses and prepare for plotting
    category_expenses = df.groupby(field)['Importe'].sum().reset_index()
    category_expenses['Positive_Total'] = category_expenses['Importe'].abs()
    category_expenses = category_expenses.sort_values(by='Positive_Total', ascending=False)
    filtered_tracker = FinanceTracker()
    filtered_tracker.data = df
    total_expense, total_earning = filtered_tracker.get_total_expenses_earnings()
    total_overall = total_earning+total_expense
    
    fig_category = px.bar(
        category_expenses, 
        x=field, 
        y='Positive_Total', 
        color=category_expenses['Importe'].apply(lambda x: x < 0), 
        color_discrete_map={False: 'rgb(31, 119, 180)', True: 'rgb(214, 39, 40)'}, 
        title=f"Category Expenses"
    )
    fig_category.update_traces(hovertemplate='%{x}: %{y:.2f}€<extra></extra>')
    fig_category.update_layout(barmode='group', showlegend=False, bargap=0, bargroupgap=0.1, title_x=0.5)
    fig_category.update_yaxes(title='')
    fig_category.update_xaxes(title='')

    total = round(category_expenses['Importe'].sum())
    return fig_category, total

def daily_candlestick(daily_expenses):
    daily_expenses['Cumulative'] = daily_expenses['Total'].cumsum()
    daily_expenses['Daily_Change'] = daily_expenses['Total'].diff().fillna(0)
    daily_expenses['Open'] = daily_expenses['Cumulative'].shift(1).fillna(0)
    daily_expenses['Close'] = daily_expenses['Cumulative']
    daily_expenses['High'] = daily_expenses[['Open', 'Close']].max(axis=1)
    daily_expenses['Low'] = daily_expenses[['Open', 'Close']].min(axis=1)

    fig_cumulative = go.Figure(data=[go.Candlestick(x=daily_expenses['Fecha'],
                                                    open=daily_expenses['Open'],
                                                    high=daily_expenses['High'],
                                                    low=daily_expenses['Low'],
                                                    close=daily_expenses['Close'],
                                                    increasing_line_color='green',
                                                    increasing_fillcolor='green',
                                                    decreasing_line_color='red',
                                                    decreasing_fillcolor='red',
                                                    opacity=1.0)])
    fig_cumulative.update_layout(xaxis_rangeslider_visible=False)
    fig_cumulative.update_layout(title='Cambio Diario', title_x=0.5, showlegend=False)
    fig_cumulative.update_xaxes(title='Date')

    return fig_cumulative