import dash
import dash_bootstrap_components as dbc
from FinanceTracker import FinanceTracker
from datetime import datetime

# Initialize the tracker to an empty tracker if there is no file or file is empty
try:
    from FinanceTracker import FinanceTracker
    tracker = FinanceTracker()
    tracker.load_tracker('tracker.json')
except (FileNotFoundError, EOFError):
    tracker = FinanceTracker()
    tracker.save_tracker('tracker.json')

if tracker.data.empty:
    tracker = FinanceTracker()
    # add a sample transaction
    tracker.add_movement("Tracker init", str(datetime.today()).split()[0], 0.0, "Otros")
    tracker.save_tracker('tracker.json')

# Initialize the Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    assets_folder='assets',  # Explicitly define assets folder
    title='Gestor de Finanzas Personales'
)
server = app.server  # Expose the server variable for deployments

if __name__ == '__main__':
    from index import main
    main()
