from dash.dependencies import Input, Output, State
from app import app
from layout import layout
from sidebar import sidebar_items, SIDEBAR_STYLE, SIDEBAR_HIDDEN_STYLE
from pages import eliminar_mes, home, add_month, page1
from dash import html

app.layout = layout

def register_callbacks(app):
    @app.callback(
        Output("sidebar", "style"),
        Output("page-content", "style"),
        Output("sidebar-header", "style"),
        Output("sidebar-header", "children"),
        [Output({"type": "nav-link", "index": i}, "children") for i in range(len(sidebar_items))],
        [Input("sidebar-toggle", "n_clicks")],
        [State("sidebar", "style"), State("page-content", "style")]
    )
    def toggle_sidebar(n_clicks, current_sidebar_style, current_content_style):
        if n_clicks % 2 == 1:
            new_sidebar_style = SIDEBAR_HIDDEN_STYLE
            new_content_style = current_content_style.copy()
            new_content_style["margin-left"] = "5rem"
            header_text = "🦊"
            header_style = {"font-size": "2rem", "text-align": "center"}  # Adjust font size as needed
            nav_texts = [item[2] for item in sidebar_items]
        else:
            new_sidebar_style = SIDEBAR_STYLE
            new_content_style = current_content_style.copy()
            new_content_style["margin-left"] = "18rem"
            header_text = "🦊 Gestor"
            header_style = {"font-size": "1.5rem", "text-align": "left"}  # Adjust font size as needed
            nav_texts = [item[0] for item in sidebar_items]
        return [new_sidebar_style, new_content_style, header_style, header_text] + nav_texts

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
        elif pathname == "/delete_month":
            return eliminar_mes.layout
        return html.Div([
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised...")
        ])

def main():
    register_callbacks(app)
    app.run_server(debug=True)

if __name__ == '__main__':
    main()
