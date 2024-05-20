from dash import html, dcc
from dash.dependencies import Input, Output
from app import app
from sidebar import sidebar
from pages import home, add_month, page1, page2

# Define the content layout
content = html.Div(id="page-content", children=[], style={"margin-left": "18rem", "margin-right": "2rem", "padding": "2rem 1rem"})

app.layout = html.Div([
    dcc.Location(id="url"),
    sidebar,
    content
])

@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def render_page_content(pathname):
    if pathname == "/":
        return home.layout
    elif pathname == "/add-month":
        return add_month.layout
    elif pathname == "/page-1":
        return page1.layout
    elif pathname == "/page-2":
        return page2.layout
    return html.Div([
        html.H1("404: Not found", className="text-danger"),
        html.Hr(),
        html.P(f"The pathname {pathname} was not recognised...")
    ])

if __name__ == '__main__':
    app.run_server(debug=True)
