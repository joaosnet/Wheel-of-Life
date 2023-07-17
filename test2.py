import tkinter as tk
import threading
import webbrowser
import random

import plotly.graph_objs as go
import dash_html_components as html
import dash_core_components as dcc
import plotly.io as pio

from dash import Dash
from dash.dependencies import Output, Input


class DashThread(threading.Thread):

    def __init__(self, data_list):

        threading.Thread.__init__(self)
        self.data_list = data_list

        self.app = Dash(__name__)

        # Initialize an empty graph
        self.app.layout = html.Div(
            [
                dcc.Graph(id="live-graph", animate=True),
                dcc.Interval(
                    id="graph-update",
                    interval=1 * 1000,
                ),
            ]
        )

        @self.app.callback(
            Output("live-graph", "figure"), [Input("graph-update", "n_intervals")]
        )
        def update_graph(n):
            data = [
                go.Scatter(
                    x=list(range(len(self.data_list[symbol]))),
                    y=self.data_list[symbol],
                    mode="lines+markers",
                    name=symbol,
                )
                for symbol in self.data_list.keys()
            ]
            fig = go.Figure(data=data)

            # Update x-axis range to show last 120 data points
            fig.update_xaxes(range=[max(0, n - 120), n])

            return fig

    def run(self):
        self.app.run_server(debug=False)


class PlotlyWindow(tk.Toplevel):

    def __init__(self, parent, fig):
        tk.Toplevel.__init__(self, parent)
        self.parent = parent
        self.title("Plotly Graph")
        self.geometry("800x600")

        # Convert the Plotly figure to JSON
        fig_json = pio.to_json(fig)

        # Create a Dash app with the Plotly graph
        app = Dash(__name__)
        app.layout = html.Div(
            [
                dcc.Graph(id="plotly-graph", figure=fig),
            ]
        )

        # Run the Dash app in a separate thread
        dash_thread = threading.Thread(target=app.run_server, kwargs={"debug": False})
        dash_thread.start()

        # Embed the Dash app in the tkinter window
        self.embed = html.Iframe(
            srcDoc=app.index_string,
            width="100%",
            height="100%",
            style={"border": "none", "overflow": "hidden"},
        )
        self.embed.pack(side="top", fill="both", expand=True)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        self.destroy()


class App:

    def __init__(self, root):
        self.root = root
        self.data_list = {"ETHUSDT": [], "BTCUSD": [], "BNBUSDT": []}

        # Start the Dash application in a separate thread
        dash_thread = DashThread(self.data_list)
        dash_thread.start()

        # Open Dash app in web browser
        webbrowser.open("http://localhost:8050")

        # Start the price generation in tkinter after Dash app is launched
        self.root.after(1000, self.generate_prices)

    def generate_prices(self):
        for symbol in self.data_list.keys():
            new_price = random.randint(1, 100)  # Generate random price
            self.data_list[symbol].append(new_price)  # Store the price in list

        # Schedule the function to run again after 1 second
        self.root.after(1000, self.generate_prices)

        # Open a new window with the Plotly graph
        fig = go.Figure(data=[go.Scatter(x=[1, 2, 3], y=[4, 5, 6])])
        plotly_window = PlotlyWindow(self.root, fig)


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()