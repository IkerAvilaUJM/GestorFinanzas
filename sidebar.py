from dash import html, dcc
import dash_bootstrap_components as dbc

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
    "transition": "width 0.3s ease-in-out",
}

SIDEBAR_HIDDEN_STYLE = SIDEBAR_STYLE.copy()
SIDEBAR_HIDDEN_STYLE["width"] = "4rem"
SIDEBAR_HIDDEN_STYLE["padding"] = "2rem 0.5rem"

sidebar_items = [
    ("🏠 Inicio", "/", "🏠"),
    ("➕ Añadir Mes", "/add-month", "➕"),
    ("📂 Gestionar Categorías", "/page-1", "📂"),
    ("🗑️ Eliminar mes", "/delete_month", "🗑️"),
]

sidebar = html.Div(
    [
        html.Button(
            "☰",
            id="sidebar-toggle",
            n_clicks=0,
            style={
                "background": "none",
                "border": "none",
                "color": "inherit",
                "padding": "0.5rem 1rem",
                "font-size": "1.5rem",
                "cursor": "pointer",
            },
        ),
        html.H2("Gestor", id="sidebar-header", className="display-4", style={"font-size": "1.5rem"}),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink(item[0], href=item[1], active="exact", id={"type": "nav-link", "index": i})
                for i, item in enumerate(sidebar_items)
            ],
            vertical=True,
            pills=True,
        ),
    ],
    id="sidebar",
    style=SIDEBAR_STYLE,
)
